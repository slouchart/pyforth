from pyforth.core import State, XT, Compiler
from pyforth.runtime import arithmetic, comparison, stacks, primitives
from pyforth.runtime.utils import compiling_word, define_word


@define_word("do")
@compiling_word
def xt_c_do(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(
        [
            stacks.xt_r_swap,
            stacks.xt_r_to_rs,  # push limit to rs
            stacks.xt_r_to_rs  # push starting index to rs
        ]
    )
    compiler.control_structure_init_open_dest()  # flag for next LOOP


@define_word("loop")
@compiling_word
def xt_c_loop(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(
        [
            stacks.xt_r_from_rs,  # rs> inx
            primitives.xt_r_push, 1,  # inx++
            arithmetic.xt_r_add,
            stacks.xt_r_rs_at,    # rs@ limit
            stacks.xt_r_swap,     # ds: limit, index
            stacks.xt_r_dup,      # ds: limit, index, index
            stacks.xt_r_to_rs,    # rs: limit, index - ds: limit, index
            comparison.xt_r_eq,
            primitives.xt_r_jz,
        ]
    )
    compiler.control_structure_close_open_dest()  # back to DO or pass
    compiler.compile_to_current_definition(
        [
            stacks.xt_r_from_rs,  # UN-LOOP
            stacks.xt_r_from_rs,
            stacks.xt_r_drop,
            stacks.xt_r_drop,
        ]
    )


def loop_index_factory(expected_nested_level: int) -> XT:

    @compiling_word
    def xt_r_loop_index(_: State, compiler: Compiler) -> None:

        compiler.compile_to_current_definition(
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

    return xt_r_loop_index


i = define_word("i", loop_index_factory(1))
j = define_word("j", loop_index_factory(2))
k = define_word("k", loop_index_factory(3))
