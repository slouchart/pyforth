from pyforth.core import DEFINED_XT_R, POINTER, State, CONTROL_STACK
from pyforth.compiler.utils import fatal, set_exit_jmp_address

from pyforth.runtime import arithmetic, comparison, stacks, primitives
from pyforth.runtime.stacks import xt_r_to_rs


def _current_nested_count(cs: CONTROL_STACK) -> int:
    return len(
        [item for item in cs if item[0] == 'DO']
    )

def xt_c_do(state: State, code: DEFINED_XT_R) -> None:
    code += [
        stacks.xt_r_swap,
        stacks.xt_r_to_rs,  # push limit to rs
        stacks.xt_r_to_rs  # push starting index to rs
    ]
    state.control_stack.append(("DO", len(code), ()))  # flag for next LOOP


def xt_c_loop(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No DO for LOOP to match")
    word, slot, exit_, *_ = state.control_stack.pop()
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
        primitives.xt_r_jz, slot, # back to DO or pass
    ]

    set_exit_jmp_address(exit_, code)
    code += [
        stacks.xt_r_from_rs,  # LOOP cleanup
        stacks.xt_r_from_rs,
        stacks.xt_r_drop,
        stacks.xt_r_drop,
    ]


def xt_c_loop_index_i(state: State, code: DEFINED_XT_R) -> None:
    nb_nested_do_loops: int = _current_nested_count(state.control_stack)
    match nb_nested_do_loops:
        case 1:
            code += [stacks.xt_r_rs_at]
        case 2:
            code += [
                stacks.xt_r_from_rs, stacks.xt_r_from_rs,
                stacks.xt_r_rs_at,
                stacks.xt_r_rot, stacks.xt_r_rot,
                stacks.xt_r_to_rs, xt_r_to_rs
            ]
        case _:
            fatal(f"Loop index I usage: Unsupported level of nested DO..LOOP {nb_nested_do_loops}")


def xt_c_loop_index_j(state: State, code: DEFINED_XT_R) -> None:
    nb_nested_do_loops: int = _current_nested_count(state.control_stack)
    match nb_nested_do_loops:
        case 2:
            code += [stacks.xt_r_rs_at]
        case _:
            fatal(f"Loop index J usage: Unsupported level of nested DO..LOOP {nb_nested_do_loops}")
