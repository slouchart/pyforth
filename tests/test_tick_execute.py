import pytest


@pytest.mark.parametrize(
    'program, data_stack', [
        ("1 ' dup execute +", [2]),
        ("1 2 ' swap execute -", [1])
    ]
)
def test_tick_execute(interpreter, program, data_stack):
    interpreter.run(program)
    assert interpreter.data_stack == data_stack


@pytest.mark.parametrize(
    'program, data_stack', [
        ("""
        : ?if 
        [compile] dup
        postpone if 
        ; immediate
        
        : main ?if 1 else 2 then ;
        0 main +
        1 main +
        """, [2, 2])
    ]
)
def test_bracket_compile(interpreter, program, data_stack):
    interpreter.run(program)
    assert interpreter.data_stack == data_stack


@pytest.mark.parametrize(
    'program, data_stack', [
        (r"""
        : ?if 
        [compile] dup \ could achieve the same with ['] dup compile,
        postpone if 
        ; immediate

        : main ?if 1 else 2 then ;
        0 main +
        1 main +
        """, [2, 2])
    ]
)
def test_bracket_tick_then_compile_comma(interpreter, program, data_stack):
    interpreter.run(program)
    assert interpreter.data_stack == data_stack
