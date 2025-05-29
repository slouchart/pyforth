from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import TypeAlias, Optional


WORD: TypeAlias = str
POINTER: TypeAlias = int
STACK: TypeAlias = list
LITERAL: TypeAlias = int
DATA_STACK = STACK[LITERAL]
RETURN_STACK = STACK[LITERAL]
CONTROL_STRUCT = tuple[WORD, POINTER | WORD]
CONTROL_STACK = STACK[CONTROL_STRUCT]
NATIVE_XT_R = Callable[["State", list, int], Optional[POINTER]]
DEFINED_XT_R = list[NATIVE_XT_R | LITERAL | WORD]
XT_R = NATIVE_XT_R | DEFINED_XT_R
XT_C = Callable[["State", DEFINED_XT_R], None]


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
    prompt: str = ""
    interactive: bool = False

    @abstractmethod
    def next_word(self) -> WORD: ...

    @abstractmethod
    def tokenize(self, s) -> None: ...

    @abstractmethod
    def execute_as(self, code: DEFINED_XT_R) -> None: ...
