import math
import sys
from typing import Callable

from pyforth.abc import State
from pyforth.annotations import WORD, NATIVE_XT
from pyforth.exceptions import ForthRuntimeError
from .utils import flush_stdout, intercept_stack_error, define_word, parse_to_fp


@define_word("precision")
def xt_r_get_precision(state: State) -> None:
    state.ds.append(state.precision)


@define_word("set-precision")
@intercept_stack_error
def xt_r_set_precision(state: State) -> None:
    state.set_precision(state.ds.pop())


@define_word("f.")
@intercept_stack_error
@flush_stdout
def xt_r_f_dot(state: State) -> None:
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


@define_word("f*")
@intercept_stack_error
def xt_r_f_mul(state: State) -> None:
    b: int = state.ds.pop()
    a: int = state.ds.pop()
    precision: int = state.precision
    result: int = a * b // 10**precision
    state.ds.append(result)


@define_word("f/")
@intercept_stack_error
def xt_r_f_div(state: State) -> None:
    b: int = state.ds.pop()
    a: int = state.ds.pop()
    precision: int = state.precision
    result: int = (a * 10**precision) // b
    state.ds.append(result)


def _math_func_factory(func: Callable[[float], float], word: WORD) -> NATIVE_XT:
    def wrapped(state: State) -> None:
        x: float = state.ds.pop() / 10 ** state.precision
        try:
            y: float = func(x)
            result: int = parse_to_fp(str(y), state.precision)
            state.ds.append(result)
        except ValueError as e:
            if "math domain error" in str(e):
                raise ForthRuntimeError(str(e)) from None
            raise

    return define_word(word, intercept_stack_error(wrapped))


@define_word("f**")
@intercept_stack_error
def xt_r_f_power(state: State) -> None:
    exponent: float = state.ds.pop() / 10 ** state.precision
    base: float = state.ds.pop() / 10 ** state.precision
    z: float = base ** exponent
    result: int = parse_to_fp(str(z), state.precision)
    state.ds.append(result)


xt_r_f_sqrt = _math_func_factory(math.sqrt, "fsqrt")
xt_r_f_exp = _math_func_factory(math.exp, "fexp")
xt_r_f_ln = _math_func_factory(math.log, "flog")
xt_r_f_log = _math_func_factory(math.log10, "flog10")
xt_r_f_sin = _math_func_factory(math.sin, "fsin")
xt_r_f_cos = _math_func_factory(math.cos, "fcos")
xt_r_f_tan = _math_func_factory(math.tan, "ftan")
xt_r_f_sinh = _math_func_factory(math.sinh, "fsinh")
xt_r_f_cosh = _math_func_factory(math.cosh, "fcosh")
xt_r_f_tanh = _math_func_factory(math.tanh, "ftanh")
xt_r_f_asin = _math_func_factory(math.asin, "fasin")
xt_r_f_acos = _math_func_factory(math.acos, "facos")
xt_r_f_atan = _math_func_factory(math.atan, "fatan")
xt_r_f_acosh = _math_func_factory(math.acosh, "facosh")
xt_r_f_asinh = _math_func_factory(math.asinh, "fasinh")
xt_r_f_atanh = _math_func_factory(math.atanh, "fatanh")


@define_word("fatan2")
@intercept_stack_error
def xt_r_f_atan2(state: State) -> None:
    x: float = state.ds.pop() / 10 ** state.precision
    y: float = state.ds.pop() / 10 ** state.precision
    z: float = math.atan2(y, x)
    result: int = parse_to_fp(str(z), state.precision)
    state.ds.append(result)
