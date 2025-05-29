import pytest


@pytest.mark.parametrize(
    'program, res', [
        ('1 IF 2 ELSE 3 THEN .', '2'),
        ('1 IF 2 THEN .', '2'),
        ('0 IF 2 ELSE 3 THEN .', '3'),
        ('0 IF 2 ELSE 3 ENDIF .', '3'),
        ('1 IF 2 ENDIF .', '2'),
        ('1 IF 2 . THEN', '2')
    ]
)
def test_if_else_then(compiler, interpreter, program, res, capsys):
    program = compiler.enter_compile_mode(program)
    interpreter.run(program, compiler.words)
    captured = capsys.readouterr()
    assert captured.out.rstrip() == res
