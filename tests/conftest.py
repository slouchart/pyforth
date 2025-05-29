import pytest

from pyforth.interpreter import Interpreter


@pytest.fixture(scope='function')
def interpreter():
    interpreter = Interpreter(interactive=False)
    return interpreter
