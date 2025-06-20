import operator

from pyforth.annotations import STACK
from .utils import pure_stack_operation, define_word, intercept_stack_error


@define_word("and")
@intercept_stack_error
@pure_stack_operation
def xt_r_and(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a & b)


@define_word("or")
@intercept_stack_error
@pure_stack_operation
def xt_r_or(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a | b)


@define_word("invert")
@intercept_stack_error
@pure_stack_operation
def xt_r_invert(ds: STACK) -> None:
    a = ds.pop()
    ds.append(operator.invert(a))


@define_word("xor")
@intercept_stack_error
@pure_stack_operation
def xt_r_xor(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(operator.xor(a, b))
