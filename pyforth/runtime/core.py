import importlib
import inspect
from pyforth.core import WORD, XT

modules = (
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


def load_dictionary(dictionary: dict[WORD, XT]):
    for module_name in modules:
        module = importlib.import_module(f".{module_name}", package="pyforth.runtime")
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if hasattr(obj, "_word"):
                dictionary[getattr(obj, "_word")] = obj
