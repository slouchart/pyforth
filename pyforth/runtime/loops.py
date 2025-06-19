from pyforth.core import POINTER, State

from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word, fatal, define_word


@define_word("begin")
@compiling_word
def xt_c_begin(state: State) -> None:
    if not state.is_compiling:
        fatal("BEGIN: not in compile mode")
    begin_pos: POINTER = state.compile_to_current_definition()
    state.control_stack.append(("BEGIN", begin_pos))  # flag for following UNTIL/REPEAT


@define_word("until")
@compiling_word
def xt_c_until(state: State) -> None:
    if not state.is_compiling:
        fatal("UNTIL: not in compile mode")
    if not state.control_stack:
        fatal("No BEGIN for UNTIL to match")
    cs_word, begin_pos = state.control_stack.pop()
    if cs_word != "BEGIN":
        fatal(f"UNTIL preceded by {cs_word} (not BEGIN)")

    state.compile_to_current_definition(
        [
            primitives.xt_r_jz,
            begin_pos
        ]
    )


@define_word("while")
@compiling_word
def xt_c_while(state: State) -> None:
    if not state.is_compiling:
        fatal("WHILE: not in compile mode")

    while_pos: POINTER = state.compile_to_current_definition(primitives.xt_r_jz)
    state.control_stack.append(("WHILE", while_pos))  # flag for following REPEAT
    state.compile_to_current_definition(0)  # to be filled in by REPEAT


@define_word("repeat")
@compiling_word
def xt_c_repeat(state: State) -> None:

    if not state.is_compiling:
        fatal("REPEAT: not in compile mode")
    if not state.control_stack:
        fatal("No WHILE for REPEAT to match")
    cs_word, while_pos = state.control_stack.pop()
    if cs_word != "WHILE":
        fatal(f"REPEAT preceded by {cs_word} (not WHILE)")
    assert isinstance(while_pos, POINTER)

    if not state.control_stack:
        fatal('No BEGIN for REPEAT to match')

    cs_word, begin_pos = state.control_stack.pop()
    if cs_word != 'BEGIN':
        fatal(f"WHILE-REPEAT preceded by {cs_word} (not BEGIN)")

    state.compile_to_current_definition(
        [
            primitives.xt_r_jmp,
            begin_pos
        ]
    )
    state.close_jump_address(while_pos)  # close JNZ for WHILE


@define_word("again")
@compiling_word
def xt_c_again(state: State) -> None:
    if not state.is_compiling:
        fatal("AGAIN: not in compile mode")
    if not state.control_stack:
        fatal("No BEGIN for AGAIN to match")
    cs_word, begin_pos = state.control_stack.pop()
    if cs_word != "BEGIN":
        fatal(f"AGAIN preceded by {cs_word} (not BEGIN)")

    state.compile_to_current_definition(
        [
            primitives.xt_r_jmp,
            begin_pos
        ]
    )
