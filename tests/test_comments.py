import pytest


@pytest.mark.parametrize(
    'program, res', [
        (r'1 dup . \ this a comment', '1')
    ]
)
def test_eof_comments(interpreter, program, res, capsys):
    interpreter.run(input_code=program)
    captured = capsys.readouterr()
    assert captured.out == res


@pytest.mark.parametrize(
    'program, res', [
        (': main ( n -- n n n ) dup dup ; 1 main .s', '1 1 1 ')
    ]
)
def test_inline_comments(interpreter, program, res, capsys):
    interpreter.run(input_code=program)
    captured = capsys.readouterr()
    assert captured.out.strip("\n") == res
