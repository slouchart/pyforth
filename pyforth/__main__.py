import io
import sys

from .interpreter import Interpreter


if __name__ == "__main__":
    _input_code: str = ''
    if len(sys.argv) > 1:
        with io.open(sys.argv[1], mode='r', encoding='utf-8') as stream:
            _input_code = stream.read()  # load start file
    interpreter = Interpreter(interactive=True)
    interpreter.run(input_code=_input_code)
