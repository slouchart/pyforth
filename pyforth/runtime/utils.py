import sys
from functools import wraps
from typing import Callable, Optional, Any, cast

from pyforth.abc import State
from pyforth.annotations import NATIVE_XT, POINTER, STACK, WORD
from pyforth.exceptions import ForthCompilationError, StackUnderflowError


# TODO precise annotations needed here
def define_word(word: WORD, xt: Any | None = None) -> Any:

    def decorator(f: Any) -> Any:
        assert callable(f)
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


def immediate_word(func: NATIVE_XT) -> NATIVE_XT:
    @wraps(func)
    def wrapper(state: State) -> Optional[POINTER]:
        return func(state)

    setattr(wrapper, '_immediate', True)

    return wrapper

def compile_only(func) -> NATIVE_XT:

    @wraps(func)
    def wrapper(state: State) -> Optional[POINTER]:
        if not state.is_compiling:
            name: WORD = getattr(func, '_word', '')
            prefix: str = f'{name.upper()}: ' if name else ''
            fatal(prefix + f"compile-only word outside compilation context")
        return func(state, state.compiler)

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


def roll_any_stack(stack: list[Any], depth: int) -> None:
    assert depth >= 0
    temp_stack = []
    for inx in range(depth):
        temp_stack.append(stack.pop())
    elem = stack.pop()
    while temp_stack:
        stack.append(temp_stack.pop())
    stack.append(elem)


def parse_to_fp(word: WORD, precision: int) -> int:
    # 1. could be an integer?
    try:
        int(word)
        raise ValueError(f"{word!r} Not a decimal number representation")
    except ValueError as exc:
        if "Not a decimal number representation" in str(exc):
            raise exc from None
        # 2. try to convert into float
        f: float = float(word)
        apparent_precision: int = 0
        while round(f) != f:
            f *= 10
            apparent_precision += 1

        # 3. adjust precision
        div_or_mul = 1 if apparent_precision < precision else -1
        while apparent_precision != precision:
            if div_or_mul > 0:
                f *= 10
            else:
                f /= 10
            apparent_precision += div_or_mul

        return int(round(f))
