from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import TypeAlias, Optional


WORD: TypeAlias = str
POINTER: TypeAlias = int
STACK: TypeAlias = list
LITERAL: TypeAlias = int
DATA_STACK = STACK[LITERAL]
RETURN_STACK = STACK[LITERAL]
CONTROL_STRUCT = tuple[WORD, POINTER | WORD, tuple[WORD, POINTER] | tuple[()]]
CONTROL_STACK = STACK[CONTROL_STRUCT]
NATIVE_XT = Callable[["State"], Optional[POINTER]]
DEFINED_XT = list[NATIVE_XT | LITERAL | WORD]
XT = NATIVE_XT | DEFINED_XT


class ForthCompilationError(BaseException):
    pass


class State(ABC):

    input_code: str = ''
    ds: DATA_STACK = []
    rs: RETURN_STACK = []
    control_stack: CONTROL_STACK = []
    heap: list[LITERAL] = [0] * 20
    next_heap_address: int = 0
    words: Sequence[WORD] = []
    last_created_word: WORD = ''
    current_definition: DEFINED_XT = []
    prompt: str = ""
    interactive: bool = False

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
    def runtime_execution_tokens(self) -> dict[WORD, XT]: ...

    @abstractmethod
    def next_word(self) -> WORD: ...

    @abstractmethod
    def tokenize(self, s) -> None: ...

    @abstractmethod
    def execute_as(self, code: DEFINED_XT) -> None: ...

    @property
    @abstractmethod
    def instruction_pointer(self) -> POINTER: ...

    @abstractmethod
    def set_instruction_pointer(self, p: POINTER) -> None: ...

    @property
    @abstractmethod
    def loaded_code(self) -> DEFINED_XT: ...
