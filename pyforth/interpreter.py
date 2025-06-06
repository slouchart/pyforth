from __future__ import annotations
import re
from pathlib import Path
from typing import cast, Sequence

from .compiler import primitives, branching, loops, doloop
from .core import DATA_STACK, DEFINED_XT_R, NATIVE_XT_R, POINTER, RETURN_STACK, WORD, XT_C, XT_R
from .core import ForthCompilationError, State
from .runtime import runtime_execution_tokens, execute, push


_compilation_tokens: dict[WORD, XT_C] = {
    ":": primitives.xt_c_colon,
    ";": primitives.xt_c_semi,
    "if": branching.xt_c_if,
    "else": branching.xt_c_else,
    "then": branching.xt_c_then,
    "begin": loops.xt_c_begin,
    'again': loops.xt_c_again,
    "until": loops.xt_c_until,
    "while": loops.xt_c_while,
    "repeat": loops.xt_c_repeat,
    "do": doloop.xt_c_do,
    "loop": doloop.xt_c_loop,
    'exit': primitives.xt_c_exit,
    'i': doloop.loop_index_factory(1, 'i'),
    'j': doloop.loop_index_factory(2, 'j'),
    'k': doloop.loop_index_factory(3, 'k'),
}


class _InterpreterState(State):
    def __init__(
        self,
        parent: Interpreter,
        input_code: str = '',
        prompt="... ",
        interactive: bool = True
    ):
        self.input_code: str = input_code
        self.prompt: str = prompt
        self.interpreter: Interpreter = parent
        self.interactive: bool = interactive

    def next_word(self) -> WORD:
        while not self.words:
            if self.input_code:
                lin = self.input_code
                self.input_code = ""
            else:
                if self.interactive:
                    lin = input(self.prompt) + " "
                else:
                    lin = "bye"
            self.tokenize(lin)

        word = self.words[0]
        if word == "bye":
            raise StopIteration
        self.words = self.words[1:]
        return word

    @property
    def runtime_execution_tokens(self) -> dict[WORD, XT_R]:
        return runtime_execution_tokens

    def tokenize(self, s):
        """clip comments, split to list of words
        """
        self.words += (
            re.sub("#.*\n", "\n", s + "\n").lower().split()
        )  # Use "#" for comment to end of line

    def execute_as(self, code: DEFINED_XT_R) -> None:
        self.interpreter.execute(code)

    @property
    def base(self) -> int:
        return self.heap[0]

    @property
    def precision(self) -> int:
        return self.heap[3]

    def int_to_str(self, value: int) -> str:
        match self.base:
            case 10:
                return str(value)
            case 16:
                return hex(value)[2:].upper()
            case 2:
                return bin(value)[2:].upper()
            case _:
                raise ValueError(f"Unsupported numeric basis: {self.base!r}")

    def word_to_int(self, word: WORD) -> int:
        return int(word, base=self.base)


class Interpreter:

    def is_literal(self, word: str) -> bool:
        try:
            int(word, base=self.state.base)
            return True
        except ValueError:
            pass
        return False

    def _bootstrap(self) -> None:
        extension_path = Path(__file__).parent / 'core.forth'
        with extension_path.open(mode='r') as stream:
            code: str = ' '.join(stream.readlines())
            interactive_flag = self.state.interactive
            self.state.interactive = False
            self.run(input_code=code)
            self.state.interactive = interactive_flag

    def __init__(self, interactive: bool = True) -> None:
        self.state: State = _InterpreterState(parent=self, interactive=interactive)
        self._heap_fence: int = 0
        self._bootstrap()
        self._heap_fence = self.state.next_heap_address  # protect vars & cons defined in bootstrap

    def reset(self) -> None:
        self.state.input_code = ''
        self.state.ds = []
        self.state.rs = []
        self.state.control_stack = []
        self.state.words = []
        self.state.last_created_word = ''
        self.state.next_heap_address = self._heap_fence

    @property
    def words(self) -> Sequence[WORD]:
        return list(runtime_execution_tokens) + list(_compilation_tokens)

    @property
    def data_stack(self) -> DATA_STACK:
        return self.state.ds

    @property
    def return_stack(self) -> RETURN_STACK:
        return self.state.rs

    def run(self, input_code: str = '') -> None:

        self.reset()
        if input_code:
            self.state.input_code = input_code

        while True:
            try:
                code: DEFINED_XT_R | None = self.compile()  # compile/run from user
                if code is None:
                    if self.state.interactive:
                        print(" ")
                    break
                self.execute(code)
            except ForthCompilationError as condition:
                if self.state.interactive:
                    print(condition)
                    break
                raise condition from None

    def compile(self) -> DEFINED_XT_R | None:
        code: DEFINED_XT_R = []
        self.state.prompt = "Forth> "
        while True:
            try:
                word: WORD = self.state.next_word()  # get next word
            except StopIteration:
                return None

            assert word
            c_xt: XT_C | None = _compilation_tokens.get(word)  # Is there a compile time action ?
            r_xt: XT_R | None = runtime_execution_tokens.get(word)  # Is there a runtime action ?

            if c_xt:
                c_xt(self.state, code)  # run at compile time
            elif r_xt:
                if isinstance(r_xt, list):
                    code += [execute, word]
                else:
                    code.append(r_xt)  # push builtin for runtime
            else:
                # Number to be pushed onto ds at runtime
                if self.is_literal(word):
                    code += [push, self.state.word_to_int(word)]
                else:  # defer
                    code += [execute, word]

            if not self.state.control_stack:  # check end of compilation
                return code

            self.state.prompt = "...    "

    def execute(self, code: DEFINED_XT_R) -> None:
        inst_ptr: POINTER = 0
        while inst_ptr < len(code):
            func: NATIVE_XT_R = cast(NATIVE_XT_R, code[inst_ptr])
            inst_ptr += 1
            new_inst_ptr: POINTER | None = func(self.state, code, inst_ptr)
            if new_inst_ptr is not None:
                inst_ptr = new_inst_ptr
