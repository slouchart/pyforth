from typing import cast

from pyforth.core import POINTER, State, Compiler

from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word, fatal, define_word


@define_word("begin")
@compiling_word
def xt_c_begin(state: State) -> None:
    compiler: Compiler = state.compiler
    dest: POINTER = compiler.compile_to_current_definition()
    compiler.control_stack.append(dest)  # flag for following UNTIL/REPEAT


@define_word("until")
@compiling_word
def xt_c_until(state: State) -> None:
    compiler: Compiler = state.compiler
    dest = compiler.control_stack.pop()
    compiler.compile_to_current_definition(
        [
            primitives.xt_r_jz,
            dest
        ]
    )


@define_word("while")
@compiling_word
def xt_c_while(state: State) -> None:
    compiler: Compiler = state.compiler
    dest: POINTER = cast(POINTER, compiler.control_stack.pop())
    orig: POINTER = compiler.compile_to_current_definition(primitives.xt_r_jz)
    compiler.control_stack.append(orig)  # flag for following REPEAT
    compiler.compile_to_current_definition(0)  # to be filled in by REPEAT
    compiler.control_stack.append(dest)


@define_word("repeat")
@compiling_word
def xt_c_repeat(state: State) -> None:

    compiler: Compiler = state.compiler
    dest: POINTER = cast(POINTER, compiler.control_stack.pop())
    orig: POINTER = cast(POINTER, compiler.control_stack.pop())
    compiler.compile_to_current_definition(
        [
            primitives.xt_r_jmp,
            dest
        ]
    )
    compiler.close_jump_address(orig)  # close JNZ for WHILE


@define_word("again")
@compiling_word
def xt_c_again(state: State) -> None:
    compiler: Compiler = state.compiler
    dest = compiler.control_stack.pop()
    compiler.compile_to_current_definition(
        [
            primitives.xt_r_jmp,
            dest
        ]
    )
