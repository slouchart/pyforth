import pytest


@pytest.mark.parametrize(
    'program, word, data_stack, return_stack', [
        (": 2+ 2 + ; 3 2+", '2+', [5], []),
        (": NEG 0 SWAP - ; 7 NEG", "NEG", [-7], [])
    ]
)
def test_basic_define(interpreter, program, word, data_stack, return_stack):
    interpreter.run(program)
    assert interpreter.data_stack == data_stack
    assert interpreter.return_stack == return_stack


@pytest.mark.parametrize(
    'program, data_stack, return_stack', [
        pytest.param(': MAIN 0 IF 1 ELSE 2 THEN DUP ; MAIN', [2, 2], [], ),
        pytest.param(': MAIN 1 IF 1 ELSE 2 THEN DUP ; MAIN', [1, 1], []),
        pytest.param(': MAIN 1 IF 2 THEN ; MAIN', [2], [], ),
        pytest.param(': MAIN IF 2 THEN DUP ; 3 0 MAIN', [3, 3], [], ),
        pytest.param(': MAIN IF DROP 2 THEN DUP ; 3 1 MAIN', [2, 2], []),
    ]
)
def test_branching_structures(interpreter, program, data_stack, return_stack):
    interpreter.run(program)
    assert interpreter.data_stack == data_stack
    assert interpreter.return_stack == return_stack


@pytest.mark.parametrize(
    'program, data_stack, return_stack, res', [
        pytest.param(': MAIN 1 begin dup . 1+ 2dup < until 2drop ; 3 MAIN', [], [], '123',),
        pytest.param(': main 0 begin DUP 3 < while 1+ dup . repeat drop ; main', [], [], '123')
    ]
)
def test_indefinite_loops(interpreter, program, data_stack, return_stack, res, capsys):
    interpreter.run(program)
    assert interpreter.data_stack == data_stack
    assert interpreter.return_stack == return_stack
    captured = capsys.readouterr()
    assert captured.out == res


@pytest.mark.parametrize(
    'program, data_stack, return_stack, res', [
        pytest.param(': MAIN 4 1 do i . loop ; MAIN', [], [], '123',),
    ]
)
def test_definite_loops(interpreter, program, data_stack, return_stack, res, capsys):
    interpreter.run(program)
    assert interpreter.data_stack == data_stack
    assert interpreter.return_stack == return_stack
    captured = capsys.readouterr()
    assert captured.out == res
