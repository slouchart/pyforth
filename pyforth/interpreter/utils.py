from pyforth.annotations import LITERAL, WORD
from pyforth.exceptions import ForthCompilationError
from pyforth.runtime.utils import parse_to_fp

def is_literal(word: WORD, base: int) -> bool:
    try:
        int(word, base=base)
        return True
    except ValueError as exc:
        if 'invalid literal' in str(exc):
            # maybe it's a decimal a.k.a. fixed point literal
            try:
                float(word)
                return True
            except ValueError:
                pass
    return False


def int_to_str(value: LITERAL, base: int) -> str:
    match base:
        case 10:
            return str(value)
        case 16:
            return hex(value)[2:].upper()
        case 2:
            return bin(value)[2:].upper()
        case _:
            raise ValueError(f"Unsupported numeric basis: {base!r}")


def word_to_int(word: WORD, base: int, precision: int) -> int:
    try:
        return parse_to_fp(word, precision=precision)
    except ValueError:
        try:
            return int(word, base=base)
        except ValueError:
            raise ForthCompilationError(f"Cannot parse {word!r} as a literal") from None
