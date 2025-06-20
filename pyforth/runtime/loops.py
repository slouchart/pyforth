from pyforth.core import State, Compiler

from pyforth.runtime import primitives
from pyforth.runtime.utils import compile_only, define_word, immediate_word


@define_word("begin")
@immediate_word
@compile_only
def xt_c_begin(_: State, compiler: Compiler) -> None:
    compiler.control_structure_init_open_dest()


@define_word("until")
@immediate_word
@compile_only
def xt_c_until(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jz)
    compiler.control_structure_close_open_dest()


@define_word("while")
@immediate_word
@compile_only
def xt_c_while(_: State, compiler: Compiler) -> None:
    # as IF
    compiler.compile_to_current_definition(primitives.xt_r_jz)
    compiler.control_structure_init_open_orig()

    # as 1 CS-ROLL
    compiler.control_stack_roll(1)


@define_word("repeat")
@immediate_word
@compile_only
def xt_c_repeat(_: State, compiler: Compiler) -> None:

    # as AGAIN
    compiler.compile_to_current_definition(primitives.xt_r_jmp)
    compiler.control_structure_close_open_dest()

    # as THEN
    compiler.control_struct_close_open_orig()  # close JNZ for WHILE


@define_word("again")
@immediate_word
@compile_only
def xt_c_again(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jmp)
    compiler.control_structure_close_open_dest()