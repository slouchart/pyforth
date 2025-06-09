from __future__ import annotations
import re
from pathlib import Path
from typing import cast, Sequence

from .runtime.utils import fatal
from .core import DATA_STACK, DEFINED_XT, NATIVE_XT, POINTER, RETURN_STACK, WORD, XT
from .core import ForthCompilationError, State
from .runtime import execution_tokens, execute, push



class _InterpreterState(State):
    def __init__(
        self,
        parent: Interpreter,
        input_code: str = '',
        prompt="... ",
        interactive: bool = True
    ):
        self.input_code: str = input_code
        self.prompt: str = prompt
        self.interpreter: Interpreter = parent
        self.interactive: bool = interactive
        self._is_compiling: bool = False  # set by colon, reset by semicolon
        self._execution_contextes: list[list[DEFINED_XT | POINTER]] = []

    def next_word(self) -> WORD:
        while not self.words:
            if self.input_code:
                lin = self.input_code
                self.input_code = ""
            else:
                if self.interactive:
                    lin = input(self.prompt) + " "
                else:
                    lin = "bye"
            self.tokenize(lin)

        word = self.words[0]
        if word == "bye":
            raise StopIteration
        self.words = self.words[1:]
        return word

    @property
    def execution_tokens(self) -> dict[WORD, XT]:
        return execution_tokens

    def tokenize(self, s):
        """clip comments, split to list of words
        """
        self.words += (
            re.sub("#.*\n", "\n", s + "\n").lower().split()
        )  # Use "#" for comment to end of line

    def execute_as(self, code: DEFINED_XT) -> None:
        self.interpreter.execute(code)

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
        self.prompt = "...    "

    def reset_compile_flag(self) -> None:
        assert self.is_compiling
        self._is_compiling = False
        self.prompt = "Forth> "

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
            code: str = ' '.join(stream.readlines())
            interactive_flag = self.state.interactive
            self.state.interactive = False
            self.run(input_code=code)
            self.state.interactive = interactive_flag

    def __init__(self, interactive: bool = True) -> None:
        self.state: _InterpreterState = _InterpreterState(parent=self, interactive=interactive)
        self._heap_fence: int = 0
        self._bootstrap()
        self._heap_fence = self.state.next_heap_address  # protect vars & cons defined in bootstrap

    def reset(self) -> None:
        self.state.input_code = ''
        self.state.ds = []
        self.state.rs = []
        self.state.control_stack = []
        self.state.words = []
        self.state.last_created_word = ''
        self.state.next_heap_address = self._heap_fence
        self.state.prompt = "Forth> "

        assert not self.state.is_compiling
        self.state.current_definition = []

    @property
    def words(self) -> Sequence[WORD]:
        return list(execution_tokens)

    @property
    def data_stack(self) -> DATA_STACK:
        return self.state.ds

    @property
    def return_stack(self) -> RETURN_STACK:
        return self.state.rs

    def run(self, input_code: str = '') -> None:

        self.reset()
        if input_code:
            self.state.input_code = input_code

        while True:
            try:
                word: WORD = self.state.next_word()
                self.interpret(word)
            except StopIteration:
                return None
            except ForthCompilationError as condition:
                if self.state.interactive:
                    print(condition)
                    break
                raise condition from None

    def interpret(self, word: WORD) -> None:

        # loop as in https://www.forth.org/lost-at-c.html [figure 1.]
        found, immediate, xt = self._search_word(word)
        if found:
            if immediate:
                assert xt is not None
                self._execute_immediate(xt)
            elif self.state.is_compiling:  #  state entered with : and exited by ;
                assert xt is not None
                self.state.current_definition += self._compile_address(word, xt)
            else:
                assert xt is not None
                self._execute_immediate(xt)
        else:
            if self.is_literal(word):
                action: DEFINED_XT = [push, self.state.word_to_int(word)]
                if self.state.is_compiling:
                    self.state.current_definition += action
                else:
                    self.execute(action)
            else:  # defer
                if self.state.is_compiling:
                    self.state.current_definition += self._deferred_definition(word)
                else:
                    fatal(f"Unknown word: {word!r}")

    def _execute_immediate(self, func: XT) -> None:
        if isinstance(func, list):
            self.execute(cast(DEFINED_XT, func))  # TODO needs rework
        else:
            assert callable(func)
            func(self.state)

    def execute(self, code: DEFINED_XT) -> None:
        self.state.set_execution_context(code)  # TODO could be a context manager
        while not self.state.past_end_of_code:
            func: NATIVE_XT = self.state.next_exec_token()
            new_inst_ptr: POINTER | None = func(self.state)
            if new_inst_ptr is not None:
                self.state.set_instruction_pointer(new_inst_ptr)
        self.state.reset_execution_context()

    @staticmethod
    def _search_word(word: WORD) -> tuple[bool, bool, XT | None]:

        xt: XT | None = execution_tokens.get(word)

        found: bool = xt is not None
        immediate: bool = xt is not None and hasattr(xt, '_immediate') and getattr(xt, '_immediate') is True
        return found, immediate, xt

    @staticmethod
    def _compile_address(word: WORD, xt_r: XT) -> DEFINED_XT:
        if isinstance(xt_r, list):
            return Interpreter._deferred_definition(word)

        return [xt_r, ]  # push builtin for runtime

    @staticmethod
    def _deferred_definition(word: WORD) -> DEFINED_XT:
        return [execute, word]
