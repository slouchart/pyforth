from __future__ import annotations

import re
from typing import cast, Generator, Final, TYPE_CHECKING

from pyforth.abc import DEFINED_XT, NATIVE_XT, POINTER, WORD, XT, ForthRuntimeError, XT_ATOM
from pyforth.abc import Compiler, ForthCompilationError, State
from pyforth.runtime import load_dictionary
from pyforth.runtime.fixed_point import parse_to_fp

from ._compiler import _Compiler


class _InnerInterpreter(State):

    _DEFAULT_PROMPT: Final[str] = 'Forth> '
    _CONTINUATION_PROMPT: Final[str] = '... '

    def __init__(
        self,
        heap_size: int,
        precision: int,
        input_code: str = '',

    ):
        self._prompt: str = self._DEFAULT_PROMPT
        self._interactive: bool = False
        self._is_compiling: bool = False  # set by colon, reset by semicolon
        self._execution_contextes: list[list[DEFINED_XT | POINTER]] = []
        self._input_buffer: str = input_code
        self.heap = [0] * heap_size
        self._precision: int = precision
        self._last_created_word: WORD = ''

        self._dictionary: dict[WORD, XT] = {}
        load_dictionary(self._dictionary, source_pkg='pyforth.runtime')
        self._compiler = _Compiler(self)

    @property
    def compiler(self) -> Compiler:
        return self._compiler

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
        return self._dictionary

    def execute(self, code: DEFINED_XT) -> None:
        self._set_execution_context(code)
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
        return not self.instruction_pointer < len(self.current_defined_execution_token)

    def _next_exec_token(self) -> NATIVE_XT:
        func = cast(NATIVE_XT, self.current_execution_token)
        self._set_instruction_pointer(self.instruction_pointer + 1)
        return func

    @property
    def instruction_pointer(self) -> POINTER:
        return cast(POINTER, self._execution_contextes[-1][1])

    def _set_instruction_pointer(self, p: POINTER) -> None:
        self._execution_contextes[-1][1] = p

    @property
    def current_defined_execution_token(self) -> DEFINED_XT:
        return cast(DEFINED_XT, self._execution_contextes[-1][0])

    @property
    def current_execution_token(self) -> XT_ATOM:
        return cast(DEFINED_XT, self._execution_contextes[-1][0])[self.instruction_pointer]

    def _set_execution_context(self, code: DEFINED_XT) -> None:
        self._execution_contextes.append([code, 0])

    def _reset_execution_context(self) -> tuple[DEFINED_XT, POINTER]:
        code, p = cast(tuple[DEFINED_XT, POINTER], self._execution_contextes.pop())
        return code, p

    def reset(self, heap_fence: POINTER) -> None:
        self.input_code = ''
        self.ds = []
        self.rs = []
        self._last_created_word = ''
        self.next_heap_address = heap_fence

        assert not self.is_compiling
        self._compiler = _Compiler(self)
