from pyforth.core import DEFINED_XT_R, POINTER, State
from pyforth.compiler.utils import fatal
from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word


@compiling_word
def xt_c_if(state: State, code: DEFINED_XT_R) -> None:
    code.append(primitives.xt_r_jz)
    state.control_stack.append(("IF", len(code), ()))  # flag for following Then or Else
    code.append(0)  # slot to be filled in


@compiling_word
def xt_c_else(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No IF for ELSE to match")
    word, slot, _ = state.control_stack.pop()
    if word != "IF":
        fatal(f"ELSE preceded by {word} (not IF)")
    assert isinstance(slot, POINTER)
    code.append(primitives.xt_r_jmp)
    state.control_stack.append(("ELSE", len(code), ()))  # flag for following THEN
    code.append(0)  # slot to be filled in
    code[slot] = len(code)  # close JZ for IF


@compiling_word
def xt_c_then(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No IF or ELSE for THEN to match")
    word, slot, _ = state.control_stack.pop()
    if word not in ("IF", "ELSE"):
        fatal(f"THEN preceded by {word} (not IF or ELSE)")
    assert isinstance(slot, POINTER)
    code[slot] = len(code)  # close JZ for IF or JMP for ELSE
