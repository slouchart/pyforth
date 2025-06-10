from pyforth.core import STACK
from .utils import pure_stack_operation, intercept_stack_error


@intercept_stack_error
@pure_stack_operation
def xt_r_add(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a + b)


@intercept_stack_error
@pure_stack_operation
def xt_r_mul(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a * b)


@intercept_stack_error
@pure_stack_operation
def xt_r_sub(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a - b)


@intercept_stack_error
@pure_stack_operation
def xt_r_div(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a // b)


@intercept_stack_error
@pure_stack_operation
def xt_r_mod(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a % b)
