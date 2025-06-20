from pyforth.abc import State, Compiler
from pyforth.runtime import primitives
from pyforth.runtime.utils import compile_only, define_word, immediate_word


@define_word('if')
@immediate_word
@compile_only
def xt_c_if(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jz)
    compiler.control_structure_open_orig()


@define_word('else')
@immediate_word
@compile_only
def xt_c_else(_: State, compiler: Compiler) -> None:
    # as AHEAD (TBD)
    compiler.compile_to_current_definition(primitives.xt_r_jmp)
    compiler.control_structure_open_orig()

    # as 1 CS-ROLL
    compiler.control_stack_roll(1)  # swap CS TOS & NOS

    # as THEN
    compiler.control_struct_close_orig() # close JZ for IF


@define_word('then')
@immediate_word
@compile_only
def xt_c_then(_: State, compiler: Compiler) -> None:
    compiler.control_struct_close_orig()  # close JZ for IF or JMP for ELSE
