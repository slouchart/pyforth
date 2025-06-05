from pyforth.core import DEFINED_XT_R, State
from pyforth.compiler.utils import fatal, set_exit_jmp_address
from pyforth.runtime import primitives


def xt_c_colon(state: State, _) -> None:
    if state.control_stack:
        fatal(f": inside Control stack: {state.control_stack}")
    label = state.next_word()
    state.control_stack.append(("COLON", label, ()))  # flag for following ";"


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


def xt_c_exit(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("EXIT outside block")
    word, label, _ = state.control_stack.pop()
    if word in ('IF', 'WHILE'):
        xt_c_exit(state, code)
        state.control_stack.append((word, label, _))
    else:
        if word not in ('COLON', 'BEGIN', 'DO'):
            fatal(f"EXIT: Unexpected block structure {word}")
        code.append(primitives.xt_r_jmp)
        state.control_stack.append((word, label, ('EXIT', len(code))))
        code.append(0)
