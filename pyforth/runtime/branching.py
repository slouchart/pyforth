from typing import cast

from pyforth.core import POINTER, State, Compiler
from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word, define_word


@define_word('if')
@compiling_word
def xt_c_if(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jz)
    compiler.control_structure_init_open_orig()


@define_word('else')
@compiling_word
def xt_c_else(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jmp)
    compiler.control_structure_init_open_orig()

    compiler.control_stack_roll(1)  # swap CS TOS & NOS
    compiler.control_struct_close_open_orig() # close JZ for IF


@define_word('then')
@compiling_word
def xt_c_then(_: State, compiler: Compiler) -> None:
    compiler.control_struct_close_open_orig()  # close JZ for IF or JMP for ELSE
