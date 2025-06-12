def test_recurse_factorial(interpreter):
    program: str = """
    : fact  ( n -- n! ) 
      dup 2 < if drop 1 exit then
      dup 1 - recurse *
      ;
    0 fact
    1 fact
    2 fact
    3 fact
    4 fact
    5 fact 
    """
    interpreter.run(program)
    assert interpreter.data_stack == [1, 1, 2, 6, 24, 120]
