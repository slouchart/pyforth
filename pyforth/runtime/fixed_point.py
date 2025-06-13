import decimal
import sys
from decimal import Decimal, InvalidOperation, getcontext

from pyforth.core import State, WORD, ForthCompilationError
from .utils import flush_stdout, intercept_stack_error


@intercept_stack_error
@flush_stdout
def xt_r_dot_f(state: State) -> None:
    value: int = state.ds.pop()
    precision: int = state.precision
    sys.stdout.write(fp_to_str(value, precision))


def fp_to_str(f: int, precision: int) -> str:
    negative: bool = f < 0
    int_p: int = abs(f) // 10**precision
    frac_p: int = abs(f) % 10**precision
    fmt: str = '{:0' + str(precision) + 'd}'
    result: str = ('-' if negative else '') + str(int_p) + '.' + fmt.format(frac_p)
    return result


def xt_r_f_literal(state: State) -> None:  # TODO need rework, semantics are wrong
    word: WORD = state.next_word()
    precision: int = state.precision
    value: int = parse_to_fp(word, precision)
    state.ds.append(value)


def parse_to_fp(word: WORD, precision: int) -> int:
    # 1. could be an integer?
    try:
        int(word)
        raise ValueError(f"{word!r} Not a decimal number representation")
    except ValueError as exc:
        if "Not a decimal number representation" in str(exc):
            raise exc from None
        # 2. try to convert into float
        f: float = float(word)
        apparent_precision: int = 0
        while round(f) != f:
            f *= 10
            apparent_precision += 1

        # 3. adjust precision
        div_or_mul = 1 if apparent_precision < precision else -1
        while apparent_precision != precision:
            if div_or_mul > 0:
                f *= 10
            else:
                f /= 10
            apparent_precision += div_or_mul

        return int(round(f))


@intercept_stack_error
def xt_r_f_mul(state: State) -> None:
    b: int = state.ds.pop()
    a: int = state.ds.pop()
    precision: int = state.precision
    result: int = a * b // 10**precision
    state.ds.append(result)


@intercept_stack_error
def xt_r_f_div(state: State) -> None:
    b: int = state.ds.pop()
    a: int = state.ds.pop()
    precision: int = state.precision
    result: int = (a * 10**precision) // b
    state.ds.append(result)
