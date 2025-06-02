import sys

from pyforth.core import STACK, State

from .utils import pure_stack_operation, pass_state_only


@pure_stack_operation
def xt_r_dump(ds: STACK) -> None:
    print(f"state.ds = {ds}")


@pass_state_only
def xt_r_dot(state: State) -> None:
    sys.stdout.write(str(state.ds.pop()))
    if state.interactive:
        sys.stdout.write("\n")
        sys.stdout.flush()


@pass_state_only
def xt_r_emit(state: State) -> None:
    sys.stdout.write(chr(state.ds.pop()))
    if state.interactive:
        sys.stdout.write("\n")
        sys.stdout.flush()
