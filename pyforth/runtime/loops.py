from typing import cast

from pyforth.core import POINTER, State, Compiler

from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word, fatal, define_word


@define_word("begin")
@compiling_word
def xt_c_begin(_: State, compiler: Compiler) -> None:
    compiler.control_structure_init_open_dest()


@define_word("until")
@compiling_word
def xt_c_until(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jz)
    compiler.control_structure_close_open_dest()


@define_word("while")
@compiling_word
def xt_c_while(_: State, compiler: Compiler) -> None:
    # as POSTPONE IF
    compiler.compile_to_current_definition(primitives.xt_r_jz)
    compiler.control_structure_init_open_orig()

    # as 1 CS-ROLL
    compiler.control_stack_roll(1)


@define_word("repeat")
@compiling_word
def xt_c_repeat(_: State, compiler: Compiler) -> None:

    # as POSTPONE AGAIN
    compiler.compile_to_current_definition(primitives.xt_r_jmp)
    compiler.control_structure_close_open_dest()

    # as a new word TBD
    compiler.control_struct_close_open_orig()  # close JNZ for WHILE


@define_word("again")
@compiling_word
def xt_c_again(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jmp)
    compiler.control_structure_close_open_dest()