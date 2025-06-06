from functools import wraps
from typing import Callable, Optional, Any

from pyforth.core import DEFINED_XT_R, NATIVE_XT_R, POINTER, STACK, State


def bool2forth(value: Any) -> int:
    return -1 if bool(value) else 0


def pass_both_stacks(func: Callable[[STACK, STACK], None]) -> NATIVE_XT_R:

    @wraps(func)
    def wrapper(state: State, *_) -> None:
        func(state.ds, state.rs)

    return wrapper


def pass_data_stack(func: Callable[[STACK, DEFINED_XT_R, POINTER], Optional[POINTER]]) -> NATIVE_XT_R:

    @wraps(func)
    def wrapper(state: State, code: DEFINED_XT_R, p: POINTER) -> Optional[POINTER]:
        return func(state.ds, code, p)

    return wrapper


def pass_no_state(func: Callable[[DEFINED_XT_R, POINTER], Optional[POINTER]]) -> NATIVE_XT_R:

    @wraps(func)
    def wrapper(_: State, code: DEFINED_XT_R, p: POINTER) -> Optional[POINTER]:
        return func(code, p)

    return wrapper


def pure_stack_operation(func: Callable[[STACK], None]) -> NATIVE_XT_R:

    @wraps(func)
    def wrapper(state: State, *_) -> None:
        func(state.ds)

    return wrapper


def pass_state_only(func: Callable[[State], Optional[POINTER]]) -> NATIVE_XT_R:

    @wraps(func)
    def wrapper(state: State, *_) -> Optional[POINTER]:
        return func(state)

    return wrapper


def compiling_word(func: Callable[[State, DEFINED_XT_R], None]) -> NATIVE_XT_R:

    @wraps(func)
    def wrapper(state: State, code: DEFINED_XT_R, *_) -> None:
        func(state, code)

    return wrapper
