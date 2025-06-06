from pyforth.core import DEFINED_XT_R, State, POINTER
from pyforth.compiler.utils import fatal, set_exit_jmp_address
from pyforth.runtime import primitives
from pyforth.runtime.utils import pass_state_only, compiling_word


@pass_state_only
def xt_c_colon(state: State) -> None:
    if state.control_stack:
        fatal(f": inside Control stack: {state.control_stack}")
    label = state.next_word()
    state.control_stack.append(("COLON", label, ()))  # flag for following ";"


@compiling_word
def xt_c_semi(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No : for ; to match")
    word, label, exit_, *_ = state.control_stack.pop()
    if word != "COLON":
        fatal(": not balanced with ;")
    assert isinstance(label, str)
    set_exit_jmp_address(exit_, code)
    state.runtime_execution_tokens[label] = code[:]  # Save word definition in rDict
    code.clear()


@compiling_word
def xt_c_exit(state: State, code: DEFINED_XT_R) -> None:

    def _exit(_state: State, _code: DEFINED_XT_R):
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

    _exit(state, code)
