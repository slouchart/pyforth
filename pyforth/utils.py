from .core import ForthCompilationError, LITERAL


def fatal(msg: str) -> None:
    raise ForthCompilationError(msg)


def is_literal(word: str) -> bool:
    try:
        int(word)
        return True
    except ValueError:
        pass
    return False
