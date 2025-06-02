from pyforth.core import DEFINED_XT_R, POINTER, State

from pyforth.runtime import primitives

from pyforth.compiler.utils import fatal


def xt_c_begin(state: State, code: DEFINED_XT_R) -> None:
    state.control_stack.append(("BEGIN", len(code)))  # flag for following UNTIL/REPEAT
    code.append(primitives.xt_r_push_rs)
    code.append(0)  # pointer for EXIT to be set by AGAIN | UNTIL | REPEAT



def xt_c_until(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No BEGIN for UNTIL to match")
    word, slot = state.control_stack.pop()
    if word != "BEGIN":
        fatal(f"UNTIL preceded by {word} (not BEGIN)")

    code.append(primitives.xt_r_drop_rs)
    code.append(primitives.xt_r_jz)
    code.append(slot)
    code[slot+1] = len(code)  # set pointer for EXIT


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

    if not state.control_stack:
        fatal('No BEGIN for REPEAT to match')

    word, slot1 = state.control_stack.pop()
    if word != 'BEGIN':
        fatal(f"WHILE-REPEAT preceded by {word} (not BEGIN)")

    code.append(primitives.xt_r_drop_rs)
    code.append(primitives.xt_r_jmp)
    code.append(slot1)
    code.append(primitives.xt_r_jmp)  # jump over the next xt
    slot3 = len(code)
    code.append(0)

    code[slot2] = len(code)  # close JNZ for WHILE
    code.append(primitives.xt_r_drop_rs)  # landing address for WHILE

    code[slot1+1] = len(code)  # landing address for EXIT
    code[slot3] = len(code)


def xt_c_again(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No BEGIN for AGAIN to match")
    word, slot = state.control_stack.pop()
    if word != "BEGIN":
        fatal(f"AGAIN preceded by {word} (not BEGIN)")

    code.append(primitives.xt_r_drop_rs)
    code.append(primitives.xt_r_jmp)
    code.append(slot)

    code[slot+1] = len(code)  # landing address for EXIT
