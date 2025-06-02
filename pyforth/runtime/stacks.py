
from pyforth.core import STACK
from .utils import pass_both_stacks, pure_stack_operation



@pure_stack_operation
def xt_r_depth(ds: STACK) -> None:
    ds.append(len(ds))


@pure_stack_operation
def xt_r_swap(ds: STACK) -> None:
    a = ds.pop()
    b = ds.pop()
    ds.append(a)
    ds.append(b)


@pure_stack_operation
def xt_r_dup(ds: STACK) -> None:
    ds.append(ds[-1])


@pure_stack_operation
def xt_r_drop(ds: STACK) -> None:
    ds.pop()


@pure_stack_operation
def xt_r_over(ds: STACK) -> None:
    ds.append(ds[-2])


@pure_stack_operation
def xt_r_rot(ds: STACK) -> None:
    first = ds.pop()
    second = ds.pop()
    third = ds.pop()
    ds += [second, first, third]


@pass_both_stacks
def xt_r_to_rs(ds: STACK, rs: STACK) -> None:
    rs.append(ds.pop())


@pass_both_stacks
def xt_r_from_rs(ds: STACK, rs: STACK) -> None:
    ds.append(rs.pop())


@pass_both_stacks
def xt_r_rs_at(ds: STACK, rs: STACK) -> None:
    ds.append(rs[-1])
