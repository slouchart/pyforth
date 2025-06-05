from pyforth.core import ForthCompilationError
from pyforth.core import WORD, POINTER, DEFINED_XT_R


def fatal(msg: str) -> None:
    raise ForthCompilationError(msg)


def set_exit_jmp_address(exit_: tuple[WORD, POINTER] | tuple[()], code: DEFINED_XT_R) -> None:
    if exit_:
        word, slot = exit_
        if word != "EXIT":
            fatal(f"Unexpected word in place of EXIT: {word!r}")
        code[slot] = len(code)
