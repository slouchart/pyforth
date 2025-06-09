from pyforth.core import POINTER, State

from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word, fatal, set_exit_jmp_address


@compiling_word
def xt_c_begin(state: State) -> None:
    if not state.is_compiling:
        fatal("BEGIN: not in compile mode")
    code = state.current_definition
    state.control_stack.append(("BEGIN", len(code), ()))  # flag for following UNTIL/REPEAT


@compiling_word
def xt_c_until(state: State) -> None:
    if not state.is_compiling:
        fatal("UNTIL: not in compile mode")
    if not state.control_stack:
        fatal("No BEGIN for UNTIL to match")
    word, slot, exit_ = state.control_stack.pop()
    if word != "BEGIN":
        fatal(f"UNTIL preceded by {word} (not BEGIN)")

    code = state.current_definition
    code.append(primitives.xt_r_jz)
    code.append(slot)
    set_exit_jmp_address(exit_, code)


@compiling_word
def xt_c_while(state: State) -> None:
    if not state.is_compiling:
        fatal("WHILE: not in compile mode")

    code = state.current_definition
    code.append(primitives.xt_r_jz)
    state.control_stack.append(("WHILE", len(code), ()))  # flag for following REPEAT
    code.append(0)  # to be filled in by REPEAT


@compiling_word
def xt_c_repeat(state: State) -> None:

    if not state.is_compiling:
        fatal("REPEAT: not in compile mode")
    if not state.control_stack:
        fatal("No WHILE for REPEAT to match")
    word, slot2, _ = state.control_stack.pop()
    if word != "WHILE":
        fatal(f"REPEAT preceded by {word} (not WHILE)")
    assert isinstance(slot2, POINTER)

    if not state.control_stack:
        fatal('No BEGIN for REPEAT to match')

    word, slot1, exit_ = state.control_stack.pop()
    if word != 'BEGIN':
        fatal(f"WHILE-REPEAT preceded by {word} (not BEGIN)")

    code = state.current_definition
    code.append(primitives.xt_r_jmp)
    code.append(slot1)

    code[slot2] = len(code)  # close JNZ for WHILE

    set_exit_jmp_address(exit_, code)


@compiling_word
def xt_c_again(state: State) -> None:
    if not state.is_compiling:
        fatal("AGAIN: not in compile mode")
    if not state.control_stack:
        fatal("No BEGIN for AGAIN to match")
    word, slot, exit_ = state.control_stack.pop()
    if word != "BEGIN":
        fatal(f"AGAIN preceded by {word} (not BEGIN)")

    code = state.current_definition
    code.append(primitives.xt_r_jmp)
    code.append(slot)

    set_exit_jmp_address(exit_, code)
