from typing import Final

from pyforth.core import State
from .strings import parse_string
from .utils import compiling_word, define_word

RIGHT_PAREN: Final[str] = ')'


@define_word("\\")
@compiling_word
def xt_c_eol_comment(state: State) -> None:
    _ = parse_string(state, until="\n")
    return None


@define_word("(")
@compiling_word
def xt_c_definition_comment(state: State) -> None:
    _ = parse_string(state, until=RIGHT_PAREN)
    return None
