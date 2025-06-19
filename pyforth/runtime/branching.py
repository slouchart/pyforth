from typing import cast

from pyforth.core import POINTER, State, Compiler
from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word, define_word


@define_word('if')
@compiling_word
def xt_c_if(state: State, compiler: Compiler) -> None:
    orig: POINTER = compiler.compile_to_current_definition(primitives.xt_r_jz)
    compiler.control_stack.append(orig)  # flag for following Then or Else
    compiler.compile_to_current_definition(0)  # slot to be filled in


@define_word('else')
@compiling_word
def xt_c_else(state: State, compiler: Compiler) -> None:
    orig1: POINTER = cast(POINTER, compiler.control_stack.pop())
    orig2: POINTER = compiler.compile_to_current_definition(primitives.xt_r_jmp)
    compiler.control_stack.append(orig2)  # flag for following THEN
    compiler.compile_to_current_definition(0)  # slot to be filled in
    compiler.close_jump_address(orig1) # close JZ for IF


@define_word('then')
@compiling_word
def xt_c_then(state: State, compiler: Compiler) -> None:
    orig: POINTER = cast(POINTER, compiler.control_stack.pop())
    compiler.close_jump_address(orig)  # close JZ for IF or JMP for ELSE
