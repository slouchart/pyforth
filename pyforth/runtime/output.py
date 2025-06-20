import sys

from pyforth.abc import State
from pyforth.annotations import STACK

from .utils import pass_both_stacks, flush_stdout, intercept_stack_error, define_word


@define_word("dump")
@pass_both_stacks
def xt_r_dump(ds: STACK, rs: STACK) -> None:
    print(f"state.ds = {ds}")
    print(f"state.rs = {rs}")


@define_word(".")
@intercept_stack_error
@flush_stdout
def xt_r_dot(state: State) -> None:
    value: int = state.ds.pop()
    sys.stdout.write(state.int_to_str(value))


@define_word("emit")
@intercept_stack_error
@flush_stdout
def xt_r_emit(state: State) -> None:
    sys.stdout.write(chr(state.ds.pop()))
