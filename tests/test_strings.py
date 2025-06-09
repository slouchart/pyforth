import pytest


@pytest.mark.parametrize(
    'program, res', [
        ('." Hello, world!"', "Hello, world!"),
    ]
)
def test_string_output(interpreter, program, res, capsys):
    interpreter.run(program)
    captured = capsys.readouterr()
    assert captured.out == res


@pytest.mark.parametrize(
    'program, res, data_stack', [
        ('s" Hello, world!"', "Hello, world!", [4, 13]),
    ]
)
def test_string_output(interpreter, program, res, data_stack):
    interpreter.run(program)
    assert interpreter.data_stack == data_stack
    s: str = ''
    for inx in range(data_stack[0]+1, data_stack[0] + data_stack[1] + 1):
        s += chr(interpreter.state.heap[inx])
    assert res == s
