import sys
from functools import wraps
from typing import Callable, Optional, Any, cast

from pyforth.core import DEFINED_XT, NATIVE_XT, POINTER, STACK, State, WORD, StackUnderflowError
from pyforth.core import ForthCompilationError



def fatal(msg: str) -> None:
    raise ForthCompilationError(msg)


def flush_stdout(func: NATIVE_XT) -> NATIVE_XT:
    @wraps(func)
    def wrapper(state: State) -> None:
        func(state)
        if state.interactive:
            sys.stdout.flush()

    return wrapper


def set_exit_jmp_address(exit_: tuple[WORD, POINTER] | tuple[()], code: DEFINED_XT) -> None:
    if exit_:
        word, slot = exit_
        if word != "EXIT":
            fatal(f"Unexpected word in place of EXIT: {word!r}")
        code[slot] = len(code)


def bool2forth(value: Any) -> int:
    return -1 if bool(value) else 0


def pass_both_stacks(func: Callable[[STACK, STACK], None]) -> NATIVE_XT:

    @wraps(func)
    def wrapper(state: State, *_) -> None:
        func(state.ds, state.rs)

    return wrapper


def pass_data_stack(func: Callable[[STACK], Optional[POINTER]]) -> NATIVE_XT:

    @wraps(func)
    def wrapper(state: State) -> Optional[POINTER]:
        return func(state.ds)

    return wrapper


def pure_stack_operation(func: Callable[[STACK], None]) -> NATIVE_XT:

    @wraps(func)
    def wrapper(state: State) -> None:
        func(state.ds)

    return wrapper


def compiling_word(func: Callable[[State], Optional[POINTER]]) -> NATIVE_XT:

    @wraps(func)
    def wrapper(state: State) -> Optional[POINTER]:
        return func(state)

    setattr(wrapper, '_immediate', True)

    return wrapper


def intercept_stack_error(func: NATIVE_XT) -> NATIVE_XT:

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except IndexError as err:
            if "pop from empty list" in str(err).lower():
                raise StackUnderflowError("Stack underflow error") from None

    return cast(NATIVE_XT, wrapper)
