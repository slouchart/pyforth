from typing import cast

from pyforth.core import POINTER, State, Compiler

from pyforth.runtime import primitives
from pyforth.runtime.utils import compiling_word, fatal, define_word


@define_word("begin")
@compiling_word
def xt_c_begin(_: State, compiler: Compiler) -> None:
    dest: POINTER = compiler.compile_to_current_definition()
    compiler.control_stack.append(dest)  # flag for following UNTIL/REPEAT


@define_word("until")
@compiling_word
def xt_c_until(_: State, compiler: Compiler) -> None:
    dest = compiler.control_stack.pop()
    compiler.compile_to_current_definition(
        [
            primitives.xt_r_jz,
            dest
        ]
    )


@define_word("while")
@compiling_word
def xt_c_while(_: State, compiler: Compiler) -> None:
    dest: POINTER = cast(POINTER, compiler.control_stack.pop())
    orig: POINTER = compiler.compile_to_current_definition(primitives.xt_r_jz)
    compiler.control_stack.append(orig)  # flag for following REPEAT
    compiler.compile_to_current_definition(0)  # to be filled in by REPEAT
    compiler.control_stack.append(dest)


@define_word("repeat")
@compiling_word
def xt_c_repeat(_: State, compiler: Compiler) -> None:
    dest: POINTER = cast(POINTER, compiler.control_stack.pop())
    compiler.compile_to_current_definition(
        [
            primitives.xt_r_jmp,
            dest
        ]
    )
    compiler.control_struct_close_open_orig()  # close JNZ for WHILE


@define_word("again")
@compiling_word
def xt_c_again(_: State, compiler: Compiler) -> None:
    compiler.compile_to_current_definition(primitives.xt_r_jmp)
    compiler.control_structure_close_open_dest()