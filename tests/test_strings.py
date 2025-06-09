import pytest


@pytest.mark.parametrize(
    'program, res', [
        ('." Hello, world!"', "Hello, world!"),
    ]
)
def test_string_output(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == res


@pytest.mark.parametrize(
    'program, res', [
        ('s" Hello, world!" type', "Hello, world!"),
    ]
)
def test_string_output(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == res
