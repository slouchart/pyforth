import sys

from pyforth.core import STACK, State

from .utils import pass_both_stacks


@pass_both_stacks
def xt_r_dump(ds: STACK, rs: STACK) -> None:
    print(f"state.ds = {ds}")
    print(f"state.rs = {rs}")


def xt_r_dot(state: State) -> None:
    value: int = state.ds.pop()
    sys.stdout.write(state.int_to_str(value))
    if state.interactive:
        sys.stdout.write("\n")
        sys.stdout.flush()


def xt_r_emit(state: State) -> None:
    sys.stdout.write(chr(state.ds.pop()))
    if state.interactive:
        sys.stdout.write("\n")
        sys.stdout.flush()
