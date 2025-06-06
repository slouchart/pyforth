import sys

from pyforth.core import State
from .utils import pass_state_only


@pass_state_only
def xt_r_dot_f(state: State) -> None:
    value: int = state.ds.pop()
    precision: int = state.precision
    sys.stdout.write(fp_to_str(value, precision))
    if state.interactive:
        sys.stdout.write("\n")
        sys.stdout.flush()


def fp_to_str(f: int, precision: int) -> str:
    negative: bool = f < 0
    int_p: int = abs(f) // 10**precision
    frac_p: int = abs(f) % 10**precision
    fmt: str = '{:0' + str(precision) + 'd}'
    result: str = ('-' if negative else '') + str(int_p) + '.' + fmt.format(frac_p)
    return result


@pass_state_only
def xt_r_f_mul(state: State) -> None:
    b: int = state.ds.pop()
    a: int = state.ds.pop()
    precision: int = state.precision
    result: int = a * b // 10**precision
    state.ds.append(result)


@pass_state_only
def xt_r_f_div(state: State) -> None:
    b: int = state.ds.pop()
    a: int = state.ds.pop()
    precision: int = state.precision
    result: int = (a * 10**precision) // b
    state.ds.append(result)
