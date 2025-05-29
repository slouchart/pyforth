import pytest


@pytest.mark.parametrize(
    'program, tos', [
        ('1 2 +', 3),
        ('1 2 -', -1),
        ('3 2 *', 6),
        ('9 4 / ', 2),
        ('17 3 MOD ', 2),
        ('1 1+ ', 2),
        ('3 DUP NEGATE + ', 0)
    ]
)
def test_arithmetic(interpreter, program, tos):
    interpreter.run(program)
    assert len(interpreter.data_stack) > 0
    assert tos == interpreter.data_stack[0]


@pytest.fixture(scope='function')
def oracle(interpreter):
    def get_result_stack(program):
        interpreter.run(program)
        return interpreter.data_stack[:]
    return get_result_stack


@pytest.mark.parametrize(
    'program, res', [
        ('1 2', '1 2'),
        ('1 DUP', '1 1'),
        ('1 2 SWAP', '2 1'),
        ('3 2 1 DROP', '3 2'),
        ('3 2 OVER', '3 2 3'),
        ('1 2 3 ROT', '2 3 1'),
        ('1 2 2DUP', '1 2 1 2'),
        ('1 2 3 4 2SWAP', '3 4 1 2'),
        ('1 2 3 4 2DROP', '1 2'),
        ('1 2 3 4 2OVER', '1 2 3 4 1 2')
    ]
)
def test_stack_ops(interpreter, program, res, oracle):
    interpreter.run(program)
    assert interpreter.data_stack == oracle(res)


@pytest.mark.parametrize(
    'program, res', [
        ('1 2 <', 1),
        ('2 1 <', 0),
        ('1 2 >', 0),
        ('2 1 >', 1),
        ('1 1 =', 1),
        ('-1 0<', 1),
        ('0 0=', 1),
        ('1 0=', 0),
        ('1 0>', 1),
        ('-1 0>', 0)
    ]
)
def test_num_cmp(interpreter, program, res):
    interpreter.run(program)
    assert interpreter.data_stack[0] == res


@pytest.mark.parametrize(
    'program, res', [
        ('1 1 and', 1),
        ('1 0 and', 0),
        ('0 1 or', 1),
        ('0 0 or', 0),
        ('0 invert', 1),
        ('1 invert', 0),
        ('1 0 xor', 1),
        ('1 1 xor', 0)
    ]
)
def test_bool_ops(interpreter, program, res):
    interpreter.run(program)
    assert interpreter.data_stack[0] == res


@pytest.mark.parametrize(
    'program, dstack_res, rstack_res', [
        ('11 >R', [], [11]),
        ('11 >R R>', [11], []),
        ('11 >R R@', [11], [11]),
    ]
)
def test_stacks_ops(interpreter, program, dstack_res, rstack_res):
    interpreter.run(program)
    assert interpreter.data_stack == dstack_res
    assert interpreter.return_stack == rstack_res


@pytest.mark.parametrize(
    'program, res', [
        ('CR', '\n'),
        ('42 .', '42'),
        ('65 emit', 'A'),
    ]
)
def test_output(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == res
    assert interpreter.data_stack == []
