from pyforth.core import STACK
from .utils import pure_stack_operation


@pure_stack_operation
def xt_r_eq(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(int(a == b))


@pure_stack_operation
def xt_r_gt(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(int(a > b))


@pure_stack_operation
def xt_r_lt(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(int(a < b))
