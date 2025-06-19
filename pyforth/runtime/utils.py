import re
import sys
from functools import wraps, partial
from typing import Callable, Optional, Any, cast

from pyforth.core import NATIVE_XT, POINTER, STACK, State, WORD, StackUnderflowError
from pyforth.core import ForthCompilationError


def define_word(word: WORD, xt: Any | None = None) -> Any:

    def decorator(f: Any) -> Any:
        setattr(f, '_word', word)
        return f

    if xt is None:
        return decorator
    return decorator(xt)


def fatal(msg: str) -> None:
    raise ForthCompilationError(msg)


def flush_stdout(func: NATIVE_XT) -> NATIVE_XT:
    @wraps(func)
    def wrapper(state: State) -> None:
        func(state)
        if state.interactive:
            sys.stdout.flush()

    return wrapper


def bool2forth(value: Any) -> int:
    return -1 if bool(value) else 0


def pass_both_stacks(func: Callable[[STACK, STACK], None]) -> NATIVE_XT:

    @wraps(func)
    def wrapper(state: State, *_) -> None:
        func(state.ds, state.rs)

    return wrapper


def pure_stack_operation(func: Callable[[STACK], None]) -> NATIVE_XT:

    @wraps(func)
    def wrapper(state: State) -> None:
        func(state.ds)

    return wrapper


def compiling_word(func: NATIVE_XT) -> NATIVE_XT:

    @wraps(func)
    def wrapper(state: State) -> Optional[POINTER]:
        return func(state)

    setattr(wrapper, '_immediate', True)

    return wrapper


def intercept_stack_error(func: NATIVE_XT) -> NATIVE_XT:

    @wraps(func)
    def wrapper(state: State) -> Optional[POINTER]:
        try:
            return func(state)
        except IndexError as err:
            if "pop from empty list" in str(err).lower():
                raise StackUnderflowError("Stack underflow error") from None
        return None

    return cast(NATIVE_XT, wrapper)
