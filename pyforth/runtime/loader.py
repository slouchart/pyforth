import importlib
import inspect
from typing import Final, Sequence

from pyforth.abc import WORD, XT


MODULES: Final[Sequence[str]] = (
    'arithmetic',
    'branching',
    'comments',
    'comparison',
    'doloop',
    'heap',
    'logical',
    'loops',
    'output',
    'primitives',
    'stacks',
    'fixed_point',
    'strings',
)


def load_dictionary(
    dictionary: dict[WORD, XT],
    modules: Sequence[str] = MODULES,
    source_pkg: str = ''
):
    for module_name in modules:
        module = importlib.import_module(f".{module_name}", package=source_pkg)
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if hasattr(obj, "_word"):
                dictionary[getattr(obj, "_word")] = obj
