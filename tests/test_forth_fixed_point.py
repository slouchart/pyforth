import pytest


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
