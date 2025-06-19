from pyforth.core import STACK, LITERAL
from .utils import pass_both_stacks, pure_stack_operation, intercept_stack_error, define_word


@define_word("depth")
@intercept_stack_error
@pure_stack_operation
def xt_r_depth(ds: STACK) -> None:
    ds.append(len(ds))


@define_word("swap")
@intercept_stack_error
@pure_stack_operation
def xt_r_swap(ds: STACK) -> None:
    a = ds.pop()
    b = ds.pop()
    ds.append(a)
    ds.append(b)


@define_word("dup")
@intercept_stack_error
@pure_stack_operation
def xt_r_dup(ds: STACK) -> None:
    ds.append(ds[-1])


@define_word("over")
@intercept_stack_error
@pure_stack_operation
def xt_r_over(ds: STACK) -> None:
    ds.append(ds[-2])


@define_word("drop")
@intercept_stack_error
@pure_stack_operation
def xt_r_drop(ds: STACK) -> None:
    ds.pop()


@define_word("rot")
@intercept_stack_error
@pure_stack_operation
def xt_r_rot(ds: STACK) -> None:
    first = ds.pop()
    second = ds.pop()
    third = ds.pop()
    ds += [second, first, third]


@define_word(">r")
@intercept_stack_error
@pass_both_stacks
def xt_r_to_rs(ds: STACK, rs: STACK) -> None:
    rs.append(ds.pop())


@define_word("r>")
@intercept_stack_error
@pass_both_stacks
def xt_r_from_rs(ds: STACK, rs: STACK) -> None:
    ds.append(rs.pop())


@define_word("r@")
@intercept_stack_error
@pass_both_stacks
def xt_r_rs_at(ds: STACK, rs: STACK) -> None:
    ds.append(rs[-1])


@define_word("pick")
@intercept_stack_error
@pure_stack_operation
def xt_r_pick(ds: STACK) -> None:
    index: LITERAL = ds.pop()
    value = ds[-(1+index)]
    ds.append(value)
