from pyforth.core import DEFINED_XT_R, State
from pyforth.compiler.utils import fatal


def xt_c_colon(state: State, _) -> None:
    if state.control_stack:
        fatal(f": inside Control stack: {state.control_stack}")
    label = state.next_word()
    state.control_stack.append(("COLON", label))  # flag for following ";"


def xt_c_semi(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No : for ; to match")
    word, label = state.control_stack.pop()
    if word != "COLON":
        fatal(": not balanced with ;")
    assert isinstance(label, str)
    state.runtime_execution_tokens[label] = code[:]  # Save word definition in rDict
    code.clear()
