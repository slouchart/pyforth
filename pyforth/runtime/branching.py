from pyforth.core import POINTER, State
from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word, define_word


@define_word('if')
@compiling_word
def xt_c_if(state: State) -> None:
    orig: POINTER = state.compile_to_current_definition(primitives.xt_r_jz)
    state.control_stack.append(orig)  # flag for following Then or Else
    state.compile_to_current_definition(0)  # slot to be filled in


@define_word('else')
@compiling_word
def xt_c_else(state: State) -> None:
    orig1 = state.control_stack.pop()
    orig2: POINTER = state.compile_to_current_definition(primitives.xt_r_jmp)
    state.control_stack.append(orig2)  # flag for following THEN
    state.compile_to_current_definition(0)  # slot to be filled in
    state.close_jump_address(orig1) # close JZ for IF


@define_word('then')
@compiling_word
def xt_c_then(state: State) -> None:
    orig = state.control_stack.pop()
    state.close_jump_address(orig)  # close JZ for IF or JMP for ELSE
