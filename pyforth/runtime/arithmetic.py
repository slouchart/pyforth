from pyforth.core import STACK
from .utils import pure_stack_operation


@pure_stack_operation
def xt_r_add(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a + b)


@pure_stack_operation
def xt_r_mul(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a * b)


@pure_stack_operation
def xt_r_sub(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a - b)


@pure_stack_operation
def xt_r_div(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a // b)


@pure_stack_operation
def xt_r_mod(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(a % b)

