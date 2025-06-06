import pytest


from pyforth.runtime.fixed_point import parse_to_fp


@pytest.mark.parametrize(
    'program, res', [
        ('100000 .f', '1.00000'),
        ('123 .f', '0.00123'),
        ('400001 .f', '4.00001'),
        ('-3 .f', '-0.00003'),
        ('-5012345 .f', '-50.12345'),
    ]
)
def test_dot_fixed_point(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == res


@pytest.mark.parametrize(
    'program, res', [
        ('3 precision ! 200 300 f* .f', '0.060'),
        ('3 precision ! 1234 5678 f* .f', '7.006')
    ]
)
def test_f_mul(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == res


@pytest.mark.parametrize(
    'program, res', [
        ('3 precision ! 200 300 f/ .f', '0.666'),
        ('3 precision ! 5678 1234 f/ .f', '4.601')
    ]
)
def test_f_div(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == res


@pytest.mark.parametrize(
    'word, precision, result', [
        ('1', 3, 1000),
        ('1.23', 3, 1230),
        ('1.239', 2, 124),
        ('1.232', 2, 123),
        ('0.0025', 3, 2),
        ('-0.235', 2, -24),
        ('-4.888', 3, -4888),
        ('-4.8882', 3, -4888),
        ('-4.8889', 3, -4889),
        ('-4.8885', 3, -4888),
    ]
)
def test_parse_to_fp(word, precision, result):
    assert parse_to_fp(word, precision) == result
