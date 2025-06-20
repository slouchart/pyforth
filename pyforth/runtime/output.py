import sys

from pyforth.abc import State
from pyforth.annotations import STACK

from .utils import pass_both_stacks, flush_stdout, intercept_stack_error, define_word
from ..interpreter.utils import int_to_str


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
    sys.stdout.write(int_to_str(value, state.base))


@define_word("emit")
@intercept_stack_error
@flush_stdout
def xt_r_emit(state: State) -> None:
    sys.stdout.write(chr(state.ds.pop()))
