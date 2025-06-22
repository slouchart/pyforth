from pyforth.abc import State, Compiler
from pyforth.runtime import primitives
from pyforth.runtime.utils import compile_only, define_word, immediate_word

@define_word('cs-roll')
@compile_only
def xt_c_cs_roll(state: State, compiler: Compiler):
    compiler.control_stack_roll(state.ds.pop())


@define_word('cs-open-orig-if')
@immediate_word
@compile_only
def xt_c_if(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jz)
    compiler.control_structure_open_orig()


@define_word('cs-open-orig-always')
@immediate_word
@compile_only
def xt_c_ahead(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jmp)
    compiler.control_structure_open_orig()


@define_word('cs-close-orig')
@immediate_word
@compile_only
def xt_c_then(_: State, compiler: Compiler) -> None:
    compiler.control_struct_close_orig()  # close JZ for IF or JMP for ELSE


@define_word("cs-open-dest")
@immediate_word
@compile_only
def xt_c_begin(_: State, compiler: Compiler) -> None:
    compiler.control_structure_open_dest()


@define_word("cs-close-dest-if")
@immediate_word
@compile_only
def xt_c_until(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jz)
    compiler.control_structure_close_dest()


@define_word("cs-close-dest-always")
@immediate_word
@compile_only
def xt_c_again(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jmp)
    compiler.control_structure_close_dest()
