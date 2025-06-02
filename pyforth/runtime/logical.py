import operator

from pyforth.core import STACK
from .utils import pure_stack_operation


@pure_stack_operation
def xt_r_and(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(operator.and_(a, b))


@pure_stack_operation
def xt_r_or(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(operator.or_(a, b))


@pure_stack_operation
def xt_r_invert(ds: STACK) -> None:
    a = ds.pop()
    ds.append(operator.not_(a))


@pure_stack_operation
def xt_r_xor(ds: STACK) -> None:
    b = ds.pop()
    a = ds.pop()
    ds.append(operator.xor(a, b))
