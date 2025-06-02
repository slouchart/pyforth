from pyforth.core import ForthCompilationError


def fatal(msg: str) -> None:
    raise ForthCompilationError(msg)
