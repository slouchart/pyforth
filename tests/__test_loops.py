import pytest


@pytest.mark.parametrize(
    'program, res', [
        pytest.param('0 begin 1 + DUP DUP . 2 = until', '12'),
        pytest.param('0 begin 1 + DUP 3 < while DUP . repeat', '12'),
        pytest.param('begin leave 0 again', ''),
        pytest.param('0 begin 1 + DUP DUP . 2 = IF LEAVE ENDIF again', '12', ),
        pytest.param('begin leave 1 dup until', ''),
        pytest.param('begin 1 while leave repeat', '')
    ]
)
def test_undef_loops(compiler, interpreter, program, res, capsys):
    code = compiler.enter_compile_mode(program)
    interpreter.run(code, compiler.words)
    captured = capsys.readouterr()
    assert captured.out.rstrip() == res


@pytest.mark.parametrize(
    'program, res', [
        pytest.param('1 0 DO 0 . LOOP', '0'),
        pytest.param('10 0 DO  I .  LOOP', '0123456789'),
        pytest.param('10 0 DO  I DUP . 5 = IF LEAVE ENDIF LOOP', '012345', )
    ]
)
def test_def_loops(compiler, interpreter, program, res, capsys):
    code = compiler.enter_compile_mode(program)
    interpreter.run(code, compiler.words)
    captured = capsys.readouterr()
    assert captured.out.rstrip() == res
