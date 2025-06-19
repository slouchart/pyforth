from pyforth.core import POINTER, State

from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word, fatal, define_word


@define_word("begin")
@compiling_word
def xt_c_begin(state: State) -> None:
    dest: POINTER = state.compile_to_current_definition()
    state.control_stack.append(dest)  # flag for following UNTIL/REPEAT


@define_word("until")
@compiling_word
def xt_c_until(state: State) -> None:
    dest = state.control_stack.pop()
    state.compile_to_current_definition(
        [
            primitives.xt_r_jz,
            dest
        ]
    )


@define_word("while")
@compiling_word
def xt_c_while(state: State) -> None:
    dest: POINTER = state.control_stack.pop()
    orig: POINTER = state.compile_to_current_definition(primitives.xt_r_jz)
    state.control_stack.append(orig)  # flag for following REPEAT
    state.compile_to_current_definition(0)  # to be filled in by REPEAT
    state.control_stack.append(dest)


@define_word("repeat")
@compiling_word
def xt_c_repeat(state: State) -> None:

    dest: POINTER = state.control_stack.pop()
    orig = state.control_stack.pop()
    state.compile_to_current_definition(
        [
            primitives.xt_r_jmp,
            dest
        ]
    )
    state.close_jump_address(orig)  # close JNZ for WHILE


@define_word("again")
@compiling_word
def xt_c_again(state: State) -> None:
    dest = state.control_stack.pop()
    state.compile_to_current_definition(
        [
            primitives.xt_r_jmp,
            dest
        ]
    )
