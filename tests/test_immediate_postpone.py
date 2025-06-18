import pytest


@pytest.mark.parametrize(
    'program, res', [
        (
            """
            : ENDIF postpone then ; immediate
            : main true if 79 emit 107 emit endif ; 
            main
            """, "Ok"
        )
    ]
)
def test_immediate_postpone(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == "Ok"


@pytest.mark.parametrize(
    'program, res', [
        (
            """
            : def [compile] : ;
            : end postpone ; ; immediate
            def 5+ 5 + end
            1 5+ . 
            """, "6"
        )
    ]
)
def test_redefine(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == res
