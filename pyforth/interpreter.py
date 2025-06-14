from __future__ import annotations
import re
from pathlib import Path
from typing import cast, Sequence, Generator, Final

from .runtime.primitives import compile_address, deferred_definition, search_word
from .runtime.utils import fatal
from .core import DATA_STACK, DEFINED_XT, NATIVE_XT, POINTER, RETURN_STACK, WORD, XT, DefinedExecutionToken, \
    StackUnderflowError
from .core import ForthCompilationError, State
from .runtime import dictionary
from .runtime.primitives import xt_r_push, execute_immediate


class _InterpreterState(State):

    _DEFAULT_PROMPT: Final[str] = 'Forth> '
    _CONTINUATION_PROMPT: Final[str] = '... '

    def __init__(
        self,
        parent: Interpreter,
        input_code: str = '',
    ):
        self._prompt: str = self._DEFAULT_PROMPT
        self._interpreter: Interpreter = parent
        self._interactive: bool = False
        self._is_compiling: bool = False  # set by colon, reset by semicolon
        self._execution_contextes: list[list[DEFINED_XT | POINTER]] = []
        self._input_buffer: str = input_code

    @property
    def interactive(self) -> bool:
        return self._interactive

    @interactive.setter
    def interactive(self, flag: bool) -> None:
        self._interactive = flag

    @property
    def input_code(self) -> str:
        return self._input_buffer

    @input_code.setter
    def input_code(self, value: str) -> None:
        self._input_buffer = value + ' \n'

    def wait_for_input(self) -> Generator[str]:
        while True:
            if self.interactive and len(self._input_buffer.strip()) == 0:
                _raw_input: str = input(self._prompt) + " \n"
                self._input_buffer += _raw_input
            yield self._input_buffer

    def next_char(self) -> str:
        s: str = next(self.wait_for_input())
        s, self._input_buffer = s[0], s[1:]
        return s

    def next_word(self) -> WORD:
        word: WORD = ''
        s: str = next(self.wait_for_input())
        match = re.match(r'\s*(\S+)\s+', s)
        if match is not None:
            word = match.group(1).lower().strip()
            self._input_buffer = self._input_buffer[match.span()[1]:]
            if word == "bye":
                raise StopIteration

        if not word and not self._interactive:
            raise StopIteration

        return word

    @property
    def execution_tokens(self) -> dict[WORD, XT]:
        return dictionary

    def execute_as(self, code: DEFINED_XT) -> None:
        self._interpreter.execute(code)

    @property
    def base(self) -> int:
        return self.heap[0]

    @property
    def precision(self) -> int:
        return self.heap[3]

    def int_to_str(self, value: int) -> str:
        match self.base:
            case 10:
                return str(value)
            case 16:
                return hex(value)[2:].upper()
            case 2:
                return bin(value)[2:].upper()
            case _:
                raise ValueError(f"Unsupported numeric basis: {self.base!r}")

    def word_to_int(self, word: WORD) -> int:
        return int(word, base=self.base)

    def set_compile_flag(self) -> None:
        assert not self.is_compiling
        self._is_compiling = True
        self._prompt = self._CONTINUATION_PROMPT

    def reset_compile_flag(self) -> None:
        assert self.is_compiling
        self._is_compiling = False
        self._prompt = self._DEFAULT_PROMPT

    @property
    def is_compiling(self) -> bool:
        return self._is_compiling

    @property
    def past_end_of_code(self) -> bool:
        return not self.instruction_pointer < len(self.loaded_code)

    def next_exec_token(self) -> NATIVE_XT:
        func = cast(NATIVE_XT, self.loaded_code[self.instruction_pointer])
        self.set_instruction_pointer(self.instruction_pointer + 1)
        return func

    @property
    def instruction_pointer(self) -> POINTER:
        return cast(POINTER, self._execution_contextes[-1][1])

    def set_instruction_pointer(self, p: POINTER) -> None:
        self._execution_contextes[-1][1] = p

    @property
    def loaded_code(self) -> DEFINED_XT:
        return cast(DEFINED_XT, self._execution_contextes[-1][0])

    def set_execution_context(self, code: DEFINED_XT) -> None:
        self._execution_contextes.append([code, 0])

    def reset_execution_context(self) -> tuple[DEFINED_XT, POINTER]:
        code, p = cast(tuple[DEFINED_XT, POINTER], self._execution_contextes.pop())
        return code, p


class Interpreter:

    def is_literal(self, word: str) -> bool:
        try:
            int(word, base=self.state.base)
            return True
        except ValueError:
            pass
        return False

    def _bootstrap(self) -> None:
        extension_path = Path(__file__).parent / 'core.forth'
        with extension_path.open(mode='r') as stream:
            code: str = ' \n'.join(stream.readlines())
            self.state.interactive = False
            self.run(input_code=code)

    def __init__(self) -> None:
        self.state: _InterpreterState = _InterpreterState(parent=self)
        self._heap_fence: int = 0
        self._bootstrap()
        self._heap_fence = self.state.next_heap_address  # protect vars & cons defined in bootstrap

    def reset(self) -> None:
        self.state.input_code = ''
        self.state.ds = []
        self.state.rs = []
        self.state.control_stack = []
        self.state.last_created_word = ''
        self.state.next_heap_address = self._heap_fence

        assert not self.state.is_compiling
        self.state.current_definition = DefinedExecutionToken()

    @property
    def words(self) -> Sequence[WORD]:
        return list(dictionary)

    @property
    def data_stack(self) -> DATA_STACK:
        return self.state.ds

    @property
    def return_stack(self) -> RETURN_STACK:
        return self.state.rs

    def run(self, input_code: str = '', interactive: bool = False) -> None:

        self.reset()
        self.state.interactive = interactive

        if input_code:
            self.state.input_code = input_code

        while True:
            try:
                word: WORD = self.state.next_word()
                if word:
                    self.interpret(word)
            except StopIteration:
                return None
            except (ForthCompilationError, StackUnderflowError) as condition:
                if self.state.interactive:
                    print(condition)
                    continue
                raise condition from None

    def interpret(self, word: WORD) -> None:

        # loop as in https://www.forth.org/lost-at-c.html [figure 1.]
        found, immediate, xt = search_word(dictionary, word)
        if found:
            if immediate:
                assert xt is not None
                execute_immediate(self.state, xt)
            elif self.state.is_compiling:  #  state entered with : and exited by ;
                assert xt is not None
                self.state.current_definition += compile_address(word, xt)
            else:
                assert xt is not None
                execute_immediate(self.state, xt)
        else:
            if self.is_literal(word):
                action: DEFINED_XT = DefinedExecutionToken([xt_r_push, self.state.word_to_int(word)])
                if self.state.is_compiling:
                    self.state.current_definition += action
                else:
                    self.execute(action)
            else:  # defer
                if self.state.is_compiling:
                    self.state.current_definition += deferred_definition(word)
                else:
                    fatal(f"Unknown word: {word!r}")

    def execute(self, code: DEFINED_XT) -> None:
        self.state.set_execution_context(code)  # TODO could be a context manager
        while not self.state.past_end_of_code:
            func: NATIVE_XT = self.state.next_exec_token()
            new_inst_ptr: POINTER | None = func(self.state)
            if new_inst_ptr is not None:
                self.state.set_instruction_pointer(new_inst_ptr)
        self.state.reset_execution_context()
