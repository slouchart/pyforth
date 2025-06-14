from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeAlias, Optional, TypeVar, Generic

T = TypeVar('T')

class DefinedExecutionToken(Generic[T], list):
    """Needed to set an _immediate attribute to True/False"""
    pass


WORD: TypeAlias = str
POINTER: TypeAlias = int
STACK: TypeAlias = list
LITERAL: TypeAlias = int
DATA_STACK = STACK[LITERAL]
RETURN_STACK = STACK[LITERAL]
CONTROL_STRUCT = tuple[WORD, POINTER | WORD, tuple[WORD, POINTER] | tuple[()]]
CONTROL_STACK = STACK[CONTROL_STRUCT]
NATIVE_XT = Callable[["State"], Optional[POINTER]]
DEFINED_XT: TypeAlias = DefinedExecutionToken[NATIVE_XT | LITERAL | WORD]
XT = NATIVE_XT | DEFINED_XT


class ForthCompilationError(BaseException):
    pass


class StackUnderflowError(BaseException):
    pass


class State(ABC):

    ds: DATA_STACK = []
    rs: RETURN_STACK = []
    control_stack: CONTROL_STACK = []
    heap: list[LITERAL] = [0] * 20
    next_heap_address: int = 0
    last_created_word: WORD = ''
    current_definition: DefinedExecutionToken = DefinedExecutionToken()

    @property
    @abstractmethod
    def interactive(self) -> bool: ...

    def set_compile_flag(self) -> None: ...

    def reset_compile_flag(self) -> None: ...

    @property
    @abstractmethod
    def is_compiling(self) -> bool: ...

    @property
    @abstractmethod
    def base(self) -> int: ...

    @property
    @abstractmethod
    def precision(self) -> int: ...

    @abstractmethod
    def int_to_str(self, value: LITERAL) -> str: ...

    @abstractmethod
    def word_to_int(self, word: WORD) -> int: ...

    @property
    @abstractmethod
    def execution_tokens(self) -> dict[WORD, XT]: ...

    @abstractmethod
    def next_char(self) -> str: ...

    @abstractmethod
    def next_word(self) -> WORD: ...

    @abstractmethod
    def execute_as(self, code: DefinedExecutionToken) -> None: ...

    @property
    @abstractmethod
    def instruction_pointer(self) -> POINTER: ...

    @abstractmethod
    def set_instruction_pointer(self, p: POINTER) -> None: ...

    @property
    @abstractmethod
    def loaded_code(self) -> DefinedExecutionToken: ...
