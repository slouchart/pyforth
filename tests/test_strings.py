import pytest


@pytest.mark.parametrize(
    'program, res', [
        ('." Hello, world!"', "Hello, world!"),
        (': main ." Hello, world!" ;', ""),
        (': main ." Hello, world!" ; main', "Hello, world!")
    ]
)
def test_string_output(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == res


@pytest.mark.parametrize(
    'program, res', [
        ('s" Hello, world!" type', "Hello, world!"),
        (': main s" Hello, world!" type ; ', ""),
        (': main s" Hello, world!" type ; main', "Hello, world!"),
    ]
)
def test_string_output(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == res
