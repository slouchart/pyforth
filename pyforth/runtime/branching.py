from pyforth.core import POINTER, State
from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word, fatal, define_word


@define_word('if')
@compiling_word
def xt_c_if(state: State) -> None:
    if not state.is_compiling:
        fatal("IF: not in compile mode")
    pos_if: POINTER = state.compile_to_current_definition(primitives.xt_r_jz)
    state.control_stack.append(("IF", pos_if))  # flag for following Then or Else
    state.compile_to_current_definition(0)  # slot to be filled in


@define_word('else')
@compiling_word
def xt_c_else(state: State) -> None:
    if not state.is_compiling:
        fatal("ELSE: not in compile mode")
    if not state.control_stack:
        fatal("No IF for ELSE to match")
    cs_word, pos_if = state.control_stack.pop()
    if cs_word != "IF":
        fatal(f"ELSE preceded by {cs_word} (not IF)")
    assert isinstance(pos_if, POINTER)

    pos_else: POINTER = state.compile_to_current_definition(primitives.xt_r_jmp)
    state.control_stack.append(("ELSE", pos_else))  # flag for following THEN
    state.compile_to_current_definition(0)  # slot to be filled in
    state.close_jump_address(pos_if) # close JZ for IF


@define_word('then')
@compiling_word
def xt_c_then(state: State) -> None:
    if not state.is_compiling:
        fatal("THEN: not in compile mode")
    if not state.control_stack:
        fatal("No IF or ELSE for THEN to match")
    cs_word, pre_pos = state.control_stack.pop()
    if cs_word not in ("IF", "ELSE"):
        fatal(f"THEN preceded by {cs_word} (not IF or ELSE)")
    assert isinstance(pre_pos, POINTER)

    state.close_jump_address(pre_pos)  # close JZ for IF or JMP for ELSE
