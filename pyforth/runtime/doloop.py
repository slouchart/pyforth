from pyforth.core import POINTER, State, CONTROL_STACK, XT
from pyforth.runtime import arithmetic, comparison, stacks, primitives
from pyforth.runtime.utils import compiling_word, fatal, define_word


def _current_nested_count(cs: CONTROL_STACK) -> int:
    return len(
        [item for item in cs if item[0] == 'DO']
    )


@define_word("do")
@compiling_word
def xt_c_do(state: State) -> None:
    if not state.is_compiling:
        fatal("DO: not in compile mode")

    slot = state.compile_to_current_definition(
        [
            stacks.xt_r_swap,
            stacks.xt_r_to_rs,  # push limit to rs
            stacks.xt_r_to_rs  # push starting index to rs
        ]
    )
    state.control_stack.append(("DO", slot))  # flag for next LOOP


@define_word("loop")
@compiling_word
def xt_c_loop(state: State) -> None:

    if not state.is_compiling:
        fatal("LOOP: not in compile mode")
    if not state.control_stack:
        fatal("No DO for LOOP to match")
    word, slot = state.control_stack.pop()
    if word != "DO":
        fatal(f"LOOP preceded by {word} (not DO)")
    assert isinstance(slot, POINTER)

    state.compile_to_current_definition(
        [
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
    )

    state.compile_to_current_definition(
        [
            stacks.xt_r_from_rs,  # UN-LOOP
            stacks.xt_r_from_rs,
            stacks.xt_r_drop,
            stacks.xt_r_drop,
        ]
    )


def loop_index_factory(expected_nested_level: int) -> XT:

    def func(state: State) -> None:

        if not state.is_compiling:
            fatal("INDEX: not in compile mode")

        nb_nested_do_loops: int = _current_nested_count(state.control_stack)

        if nb_nested_do_loops < expected_nested_level:
            fatal(f"Loop index usage: "
                  f"Unsupported level of nested DO..LOOP {nb_nested_do_loops}")

        state.compile_to_current_definition(
            [
                stacks.xt_r_from_rs,  # move around outermost do-loop params
                stacks.xt_r_from_rs,
            ] * (expected_nested_level - 1)
            + [stacks.xt_r_rs_at]    # reaching the one we need
            + [
                stacks.xt_r_rot, stacks.xt_r_rot,  # rearrange order
                stacks.xt_r_to_rs, stacks.xt_r_to_rs,  # put them back
            ] * (expected_nested_level - 1)
        )
    return compiling_word(func)


i = define_word("i", loop_index_factory(1))
j = define_word("j", loop_index_factory(2))
k = define_word("k", loop_index_factory(3))
