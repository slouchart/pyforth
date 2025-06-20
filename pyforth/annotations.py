from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .abc import State

WORD: TypeAlias = str
POINTER: TypeAlias = int
STACK: TypeAlias = list
LITERAL: TypeAlias = int
DATA_STACK = STACK[LITERAL]
RETURN_STACK = STACK[LITERAL]
NATIVE_XT = Callable[['State'], Optional[POINTER]]
XT_ATOM = NATIVE_XT | LITERAL | WORD
DEFINED_XT: TypeAlias = list[XT_ATOM]
XT = NATIVE_XT | DEFINED_XT
