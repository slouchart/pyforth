from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeAlias, Optional, TypeVar, Generic, Any

T = TypeVar('T')

class DefinedExecutionToken(list, Generic[T]):
    """Needed to set an _immediate attribute to True/False"""
    pass


WORD: TypeAlias = str
POINTER: TypeAlias = int
STACK: TypeAlias = list
LITERAL: TypeAlias = int
DATA_STACK = STACK[LITERAL]
RETURN_STACK = STACK[LITERAL]
NATIVE_XT = Callable[["State"], Optional[POINTER]]
XT_ATOM = NATIVE_XT | LITERAL | WORD
DEFINED_XT: TypeAlias = DefinedExecutionToken[XT_ATOM]
XT = NATIVE_XT | DEFINED_XT


class ForthCompilationError(BaseException):
    pass


class StackUnderflowError(BaseException):
    pass


class ForthRuntimeError(BaseException):
    pass


class Compiler(ABC):

    @abstractmethod
    def prepare_current_definition(self, word: WORD) -> None: ...

    @abstractmethod
    def get_current_definition_as_word(self) -> WORD: ...

    @abstractmethod
    def compile_to_current_definition(self, obj: Optional[Any] = None) -> POINTER: ...

    @abstractmethod
    def control_structure_init_open_dest(self) -> None: ...

    @abstractmethod
    def control_structure_init_open_orig(self) -> None: ...

    @abstractmethod
    def control_structure_close_open_dest(self) -> None: ...

    @abstractmethod
    def control_struct_close_open_orig(self) -> None: ...

    @abstractmethod
    def control_stack_roll(self, depth: int) -> None: ...

    @abstractmethod
    def complete_current_definition(self) -> None: ...


class State(ABC):

    ds: DATA_STACK = []
    rs: RETURN_STACK = []

    heap: list[LITERAL] = [0] * 20
    next_heap_address: int = 0

    @property
    @abstractmethod
    def compiler(self) -> Compiler: ...

    @property
    @abstractmethod
    def interactive(self) -> bool: ...

    @abstractmethod
    def set_compile_flag(self) -> None: ...

    @abstractmethod
    def reset_compile_flag(self) -> None: ...

    @property
    @abstractmethod
    def is_compiling(self) -> bool: ...

    @property
    @abstractmethod
    def last_created_word(self) -> WORD: ...

    @abstractmethod
    def reveal_created_word(self, word: WORD) -> None: ...

    @property
    @abstractmethod
    def base(self) -> int: ...

    @property
    @abstractmethod
    def precision(self) -> int: ...

    @abstractmethod
    def set_precision(self, u_val: int) -> None: ...

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
    def next_word(self, preserve_case: bool = False) -> WORD: ...

    @abstractmethod
    def execute(self, code: DefinedExecutionToken) -> None: ...

    @property
    @abstractmethod
    def instruction_pointer(self) -> POINTER: ...

    @property
    @abstractmethod
    def current_execution_token(self) -> XT_ATOM: ...

    @property
    @abstractmethod
    def current_defined_execution_token(self) -> DEFINED_XT: ...