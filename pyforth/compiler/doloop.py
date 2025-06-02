
from pyforth.core import DEFINED_XT_R, POINTER, State
from pyforth.compiler.utils import fatal


from pyforth.runtime import arithmetic, comparison, stacks, primitives


def xt_c_do(state: State, code: DEFINED_XT_R) -> None:
    code += [
        stacks.xt_r_swap,
        stacks.xt_r_to_rs,  # push limit to rs
        stacks.xt_r_to_rs  # push starting index to rs
    ]
    state.control_stack.append(("DO", len(code)))  # flag for next LOOP


def xt_c_loop(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No DO for LOOP to match")
    word, slot = state.control_stack.pop()
    if word != "DO":
        fatal(f"LOOP preceded by {word} (not DO)")
    assert isinstance(slot, POINTER)
    code += [
        stacks.xt_r_from_rs,  # rs> inx
        primitives.xt_r_push, 1,  # inx++
        arithmetic.xt_r_add,
        stacks.xt_r_rs_at,    # rs@ limit
        stacks.xt_r_swap,     # ds: limit, index
        stacks.xt_r_dup,      # ds: limit, index, index
        stacks.xt_r_to_rs,    # rs: limit, index - ds: limit, index
        comparison.xt_r_eq,
        primitives.xt_r_jz, slot, # do..loop
        stacks.xt_r_from_rs,  # cleanup
        stacks.xt_r_from_rs,
        stacks.xt_r_drop,
        stacks.xt_r_drop
    ]
