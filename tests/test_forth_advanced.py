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


def test_bootstrap(interpreter, capsys):
    assert 'abs' in interpreter.words
    interpreter.run(input_code='4 spaces')
    captured = capsys.readouterr()
    assert captured.out == ' '*4


@pytest.mark.parametrize(
    'program, data_stack, return_stack', [
        (': main begin dup 3 > if drop exit then dup 1 + again ; 1 main', [1, 2, 3], []),
        (': main dup exit 2 + ; 0 main', [0, 0], []),
        (': main begin dup 3 = if exit then 1 +  false until ; 1 main', [3], []),
        (': main begin dup 3 < while 1 + dup 3 = if exit then repeat ; 1 main', [3], []),
        (': main begin dup 3 = if exit then true while 1 + repeat ; 1 main', [3], [])
    ]
)
def test_exit_loops(interpreter, program, data_stack, return_stack):
    interpreter.run(program)
    assert interpreter.data_stack == data_stack
    assert interpreter.return_stack == return_stack


@pytest.mark.parametrize(
    'program, data_stack, return_stack', [
        (': main 1 1 do i 1 = if exit then loop ; main', [], [])
    ]
)
def test_exit_do_loop(interpreter, program, data_stack, return_stack):
    interpreter.run(program)
    assert interpreter.data_stack == data_stack
    assert interpreter.return_stack == return_stack



@pytest.mark.parametrize(
    'program, data_stack, return_stack', [
        pytest.param(': main 4 1 do 3 1 do i j + loop loop ; main ', [2, 3, 3, 4, 4, 5], [],),
        pytest.param(': main 4 1 do i 3 1 do j loop loop ; main ', [1, 1, 2, 2, 1, 2, 3, 1, 2], [],),
        (': main 4 1 do 3 1 do 2 1 do i j k + + loop loop loop ; main', [3, 4, 4, 5, 5, 6], [])
    ]
)
def test_nested_do_loops(interpreter, program, data_stack, return_stack):
    interpreter.run(program)
    assert interpreter.data_stack == data_stack
    assert interpreter.return_stack == return_stack
