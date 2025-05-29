import sys

from .interpreter import Interpreter


if __name__ == "__main__":
    _input_code = ''
    if len(sys.argv) > 1:
        _input_code = open(sys.argv[1]).read()  # load start file
    interpreter = Interpreter(interactive=True)
    interpreter.run(input_code=_input_code)