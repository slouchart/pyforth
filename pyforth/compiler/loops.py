from pyforth.core import DEFINED_XT_R, POINTER, State

from pyforth.runtime import primitives

from pyforth.compiler.utils import fatal


def xt_c_begin(state: State, code: DEFINED_XT_R) -> None:
    state.control_stack.append(("BEGIN", len(code)))  # flag for following UNTIL/REPEAT


def xt_c_until(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No BEGIN for UNTIL to match")
    word, slot = state.control_stack.pop()
    if word != "BEGIN":
        fatal(f"UNTIL preceded by {word} (not BEGIN)")
    code.append(primitives.xt_r_jz)
    code.append(slot)


def xt_c_while(state: State, code: DEFINED_XT_R) -> None:
    code.append(primitives.xt_r_jz)
    state.control_stack.append(("WHILE", len(code)))  # flag for following REPEAT
    code.append(0)  # to be filled in by REPEAT


def xt_c_repeat(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No WHILE for REPEAT to match")
    word, slot2 = state.control_stack.pop()
    if word != "WHILE":
        fatal(f"REPEAT preceded by {word} (not WHILE)")
    assert isinstance(slot2, POINTER)

    proceed: bool = bool(state.control_stack)
    if proceed:
        word, slot1 = state.control_stack.pop()
        proceed = word == 'BEGIN'
        if proceed:
            code.append(primitives.xt_r_jmp)
            code.append(slot1)

    if not proceed:
        fatal('No BEGIN for REPEAT to match')

    code[slot2] = len(code)  # close JNZ for WHILE
