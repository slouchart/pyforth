from pyforth.core import POINTER, State
from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word, fatal, define_word


@define_word('if')
@compiling_word
def xt_c_if(state: State) -> None:
    if not state.is_compiling:
        fatal("IF: not in compile mode")
    slot = state.compile_to_current_definition(primitives.xt_r_jz)
    state.control_stack.append(("IF", slot))  # flag for following Then or Else
    state.compile_to_current_definition(0)  # slot to be filled in


@define_word('else')
@compiling_word
def xt_c_else(state: State) -> None:
    if not state.is_compiling:
        fatal("ELSE: not in compile mode")
    if not state.control_stack:
        fatal("No IF for ELSE to match")
    word, slot = state.control_stack.pop()
    if word != "IF":
        fatal(f"ELSE preceded by {word} (not IF)")
    assert isinstance(slot, POINTER)

    slot2 = state.compile_to_current_definition(primitives.xt_r_jmp)
    state.control_stack.append(("ELSE", slot2))  # flag for following THEN
    state.compile_to_current_definition(0)  # slot to be filled in
    state.close_jump_address(slot) # close JZ for IF


@define_word('then')
@compiling_word
def xt_c_then(state: State) -> None:
    if not state.is_compiling:
        fatal("THEN: not in compile mode")
    if not state.control_stack:
        fatal("No IF or ELSE for THEN to match")
    word, slot = state.control_stack.pop()
    if word not in ("IF", "ELSE"):
        fatal(f"THEN preceded by {word} (not IF or ELSE)")
    assert isinstance(slot, POINTER)

    state.close_jump_address(slot)  # close JZ for IF or JMP for ELSE
