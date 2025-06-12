from pyforth.core import State, DEFINED_XT
from pyforth.compiler.utils import fatal, set_exit_jmp_address
from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word


@compiling_word
def xt_c_colon(state: State) -> None:
    if state.is_compiling:
        fatal(f"COLON: Already compiling a definition")
    if state.control_stack:
        fatal(f": inside Control stack: {state.control_stack}")
    label = state.next_word()
    state.control_stack.append(("COLON", label, ()))  # flag for following ";"
    state.set_compile_flag()  # enter "compile" mode
    state.current_definition = []  # prepare code definition


@compiling_word
def xt_c_semi(state: State) -> None:
    if not state.is_compiling:
        fatal("SEMICOLON: Not in compile mode")
    if not state.control_stack:
        fatal("No : for ; to match")
    word, label, exit_, *_ = state.control_stack.pop()
    if word != "COLON":
        fatal(": not balanced with ;")
    assert isinstance(label, str)
    set_exit_jmp_address(exit_, state.current_definition)
    state.runtime_execution_tokens[label] = state.current_definition[:]  # Save word definition in rDict
    state.current_definition.clear()
    state.reset_compile_flag()


@compiling_word
def xt_c_exit(state: State) -> None:

    def _exit(_state: State, _code: DEFINED_XT):
        if not _state.control_stack:
            fatal("EXIT outside block")
        word, label, _ = _state.control_stack.pop()
        if word in ('IF', 'WHILE'):
            _exit(_state, _code)
            _state.control_stack.append((word, label, _))
        else:
            if word not in ('COLON', 'BEGIN', 'DO'):
                fatal(f"EXIT: Unexpected block structure {word}")
            _code.append(primitives.xt_r_jmp)
            _state.control_stack.append((word, label, ('EXIT', len(_code))))
            _code.append(0)

    _exit(state, state.current_definition)
