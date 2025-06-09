import pytest


@pytest.mark.parametrize(
    'program, res', [
        (
            """
            : ENDIF postpone then ; immediate
            : main true if 79 emit 107 emit endif ;  # write 'Ok' on stdout
            main
            """, "Ok"
        )
    ]
)
def test_immediate_postpone(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == "Ok"
