from typing import Final

from pyforth.core import DEFINED_XT_R, POINTER, State, CONTROL_STACK, XT_R
from pyforth.compiler.utils import fatal, set_exit_jmp_address

from pyforth.runtime import arithmetic, comparison, stacks, primitives
from pyforth.runtime.utils import compiling_word


def _current_nested_count(cs: CONTROL_STACK) -> int:
    return len(
        [item for item in cs if item[0] == 'DO']
    )


@compiling_word
def xt_c_do(state: State, code: DEFINED_XT_R) -> None:
    code += [
        stacks.xt_r_swap,
        stacks.xt_r_to_rs,  # push limit to rs
        stacks.xt_r_to_rs  # push starting index to rs
    ]
    state.control_stack.append(("DO", len(code), ()))  # flag for next LOOP


@compiling_word
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


MAX_NESTED_LOOPS: Final[int] = 3


def loop_index_factory(expected_nested_level: int, index_word: str) -> XT_R:

    def func(state: State, code: DEFINED_XT_R) -> None:

        nb_nested_do_loops: int = _current_nested_count(state.control_stack)

        if MAX_NESTED_LOOPS < nb_nested_do_loops < expected_nested_level:
            fatal(f"Loop index {index_word.upper()!r} usage: "
                  f"Unsupported level of nested DO..LOOP {nb_nested_do_loops}")

        code += [stacks.xt_r_from_rs,  # move around outermost do-loop params
                 stacks.xt_r_from_rs,] * (nb_nested_do_loops - expected_nested_level)
        code += [stacks.xt_r_rs_at]    # reaching the one we need
        code += [stacks.xt_r_rot, stacks.xt_r_rot,  # rearrange order
                 stacks.xt_r_to_rs, stacks.xt_r_to_rs,  # put them back
                 ] * (nb_nested_do_loops - expected_nested_level)

    return compiling_word(func)
