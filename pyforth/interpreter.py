from __future__ import annotations
import re
from pathlib import Path
from typing import cast, Sequence, Generator, Final

from .runtime.primitives import compile_address, deferred_definition, search_word
from .runtime.utils import fatal
from .core import DATA_STACK, DEFINED_XT, NATIVE_XT, POINTER, RETURN_STACK, WORD, XT, DefinedExecutionToken, \
    StackUnderflowError, LITERAL, ForthRuntimeError
from .core import ForthCompilationError, State
from .runtime import dictionary
from .runtime.primitives import xt_r_push, execute_immediate
from .runtime.fixed_point import parse_to_fp


DEFAULT_PRECISION: Final[int] = 5
MEMORY_SIZE: Final[int] = 64
EXTENSIONS: Sequence[str] = (
    'core.forth',
)


class _InnerInterpreter(State):

    _DEFAULT_PROMPT: Final[str] = 'Forth> '
    _CONTINUATION_PROMPT: Final[str] = '... '

    def __init__(
        self,
        parent: Interpreter,
        input_code: str = '',
        heap_size: int = MEMORY_SIZE
    ):
        self._prompt: str = self._DEFAULT_PROMPT
        self._interpreter: Interpreter = parent
        self._interactive: bool = False
        self._is_compiling: bool = False  # set by colon, reset by semicolon
        self._execution_contextes: list[list[DEFINED_XT | POINTER]] = []
        self._input_buffer: str = input_code
        self.heap = [0] * heap_size
        self._precision: int = DEFAULT_PRECISION
        self._last_created_word: WORD = ''
        self._current_definition: DefinedExecutionToken = DefinedExecutionToken()

    @property
    def current_definition(self) -> DefinedExecutionToken:
        return self._current_definition

    def prepare_current_definition(self) -> None:
        assert self.is_compiling
        assert not self._current_definition
        self._current_definition = DefinedExecutionToken()

    def close_jump_address(self, addr: POINTER) -> None:
        self._current_definition[addr] = len(self._current_definition)

    def compile_to_current_definition(self, obj) -> POINTER:
        if isinstance(obj, list):
            self._current_definition += obj
        else:
            self._current_definition.append(obj)
        return len(self._current_definition)

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

    def next_word(self, preserve_case: bool = False) -> WORD:
        word: WORD = ''
        s: str = next(self.wait_for_input())
        match = re.match(r'\s*(\S+)\s+', s)
        if match is not None:
            word = match.group(1).strip()
            if not preserve_case:
                word = word.lower()
            self._input_buffer = self._input_buffer[match.span()[1]:]
            if word == "bye":
                raise StopIteration

        if not word and not self._interactive:
            raise StopIteration

        return word

    @property
    def execution_tokens(self) -> dict[WORD, XT]:
        return dictionary

    def execute(self, code: DEFINED_XT) -> None:
        self._set_execution_context(code)  # TODO could be a context manager
        while not self.past_end_of_code:
            func: NATIVE_XT = self._next_exec_token()
            new_inst_ptr: POINTER | None = func(self)
            if new_inst_ptr is not None:
                self._set_instruction_pointer(new_inst_ptr)
        self._reset_execution_context()

    @property
    def base(self) -> int:
        return self.heap[0]

    @property
    def precision(self) -> int:
        return self._precision

    def set_precision(self, u_val: int) -> None:
        if u_val < 0:
            raise ForthRuntimeError("Precision mist be a positive integer")
        self._precision = u_val

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
        try:
            return parse_to_fp(word, precision=self.precision)
        except ValueError:
            try:
                return int(word, base=self.base)
            except ValueError:
                raise ForthCompilationError(f"Cannot parse {word!r} as a literal") from None

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
    def last_created_word(self) -> WORD:
        return self._last_created_word

    def reveal_created_word(self, word: WORD) -> None:
        self._last_created_word = word

    @property
    def past_end_of_code(self) -> bool:
        return not self.instruction_pointer < len(self.loaded_code)

    def _next_exec_token(self) -> NATIVE_XT:
        func = cast(NATIVE_XT, self.loaded_code[self.instruction_pointer])
        self._set_instruction_pointer(self.instruction_pointer + 1)
        return func

    @property
    def instruction_pointer(self) -> POINTER:
        return cast(POINTER, self._execution_contextes[-1][1])

    def _set_instruction_pointer(self, p: POINTER) -> None:
        self._execution_contextes[-1][1] = p

    @property
    def loaded_code(self) -> DEFINED_XT:
        return cast(DEFINED_XT, self._execution_contextes[-1][0])

    def _set_execution_context(self, code: DEFINED_XT) -> None:
        self._execution_contextes.append([code, 0])

    def _reset_execution_context(self) -> tuple[DEFINED_XT, POINTER]:
        code, p = cast(tuple[DEFINED_XT, POINTER], self._execution_contextes.pop())
        return code, p

    def reset(self, heap_fence: POINTER) -> None:
        self.input_code = ''
        self.ds = []
        self.rs = []
        self.control_stack = []
        self._last_created_word = ''
        self.next_heap_address = heap_fence

        assert not self.is_compiling
        self._current_definition = DefinedExecutionToken()


class Interpreter:

    def __init__(self, extensions: Sequence[str] = EXTENSIONS) -> None:
        self._state: _InnerInterpreter = _InnerInterpreter(parent=self)
        self._heap_fence: int = 0
        self._bootstrap(extensions)
        self._heap_fence = self._state.next_heap_address  # protect vars & cons defined in bootstrap

    @property
    def data_stack(self) -> DATA_STACK:
        return self._state.ds[:]

    @property
    def heap(self) -> Sequence[LITERAL]:
        return self._state.heap[self._heap_fence:][:]

    @property
    def return_stack(self) -> RETURN_STACK:
        return self._state.rs[:]

    @property
    def words(self) -> Sequence[WORD]:
        return list(dictionary)

    def run(self, input_code: str = '', interactive: bool = False) -> None:

        self._state.reset(self._heap_fence)
        self._state.interactive = interactive

        if input_code:
            self._state.input_code = input_code

        while True:
            try:
                word: WORD = self._state.next_word()
                if word:
                    self.interpret(word)
            except StopIteration:
                return None
            except (
                ForthCompilationError,
                StackUnderflowError,
                ForthRuntimeError
            ) as condition:
                if self._state.interactive:
                    print(condition)
                    continue
                raise condition from None

    def interpret(self, word: WORD) -> None:

        # loop as in https://www.forth.org/lost-at-c.html [figure 1.]
        found, immediate, xt = search_word(dictionary, word)
        if found:
            assert xt is not None
            if immediate:
                execute_immediate(self._state, xt)
            elif self._state.is_compiling:  #  state entered with : and exited by ;
                self._state.compile_to_current_definition(compile_address(word, xt))
            else:
                execute_immediate(self._state, xt)
        else:
            if self.is_literal(word):
                action: DEFINED_XT = DefinedExecutionToken([xt_r_push, self._state.word_to_int(word)])
                if self._state.is_compiling:
                    self._state.compile_to_current_definition(action)
                else:
                    self._state.execute(action)
            else:  # defer
                if self._state.is_compiling:
                    self._state.compile_to_current_definition(deferred_definition(word))
                else:
                    fatal(f"Unknown word: {word!r}")

    def is_literal(self, word: str) -> bool:
        try:
            int(word, base=self._state.base)
            return True
        except ValueError as exc:
            if 'invalid literal' in str(exc):
                # maybe it's a decimal a.k.a. fixed point literal
                try:
                    float(word)
                    return True
                except ValueError:
                    pass
        return False

    def _bootstrap(self, extensions: Sequence[str]) -> None:
        self._state.interactive = False
        for extension in extensions:
            extension_path = Path(__file__).parent / extension
            with extension_path.open(mode='r') as stream:
                code: str = ' \n'.join(stream.readlines())
                self.run(input_code=code)
