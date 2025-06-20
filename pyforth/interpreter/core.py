from __future__ import annotations

from pathlib import Path
from typing import Sequence, Final

from pyforth.runtime.primitives import compile_address, deferred_definition, search_word
from pyforth.runtime.utils import fatal

from pyforth.abc import DefinedExecutionToken
from pyforth.annotations import DATA_STACK, DEFINED_XT, RETURN_STACK, WORD, LITERAL
from pyforth.exceptions import ForthCompilationError, ForthRuntimeError, StackUnderflowError
from pyforth.runtime.primitives import xt_r_push, execute_immediate


DEFAULT_PRECISION: Final[int] = 5
MEMORY_SIZE: Final[int] = 64
EXTENSIONS: Sequence[str | Path] = (
    Path(__file__).parent / 'core.forth',
)


from ._inner import _InnerInterpreter


class Interpreter:

    def __init__(self, extensions: Sequence[str | Path] = EXTENSIONS) -> None:
        self._state: _InnerInterpreter = _InnerInterpreter(
            precision=DEFAULT_PRECISION,
            heap_size=MEMORY_SIZE
        )
        self._heap_fence: int = 0
        self._bootstrap(extensions)
        self._heap_fence = self._state.next_heap_address  # protect vars & cons defined in bootstrap

    @property
    def data_stack(self) -> DATA_STACK:
        return self._state.ds[:]

    @property
    def heap(self) -> Sequence[LITERAL]:
        return self._state.heap[self._heap_fence:][:]

    @property
    def return_stack(self) -> RETURN_STACK:
        return self._state.rs[:]

    @property
    def words(self) -> Sequence[WORD]:
        return list(self._state.execution_tokens)

    def run(self, input_code: str = '', interactive: bool = False) -> None:

        self._state.reset(self._heap_fence)
        self._state.interactive = interactive

        if input_code:
            self._state.input_code = input_code

        while True:
            try:
                word: WORD = self._state.next_word()
                if word:
                    self.interpret(word)
            except StopIteration:
                return None
            except (
                ForthCompilationError,
                StackUnderflowError,
                ForthRuntimeError
            ) as condition:
                if self._state.interactive:
                    print(condition)
                    continue
                raise condition from None

    def interpret(self, word: WORD) -> None:

        # loop as in https://www.forth.org/lost-at-c.html [figure 1.]
        found, immediate, xt = search_word(self._state.execution_tokens, word)
        if found:
            assert xt is not None
            if immediate:
                execute_immediate(self._state, xt)
            elif self._state.is_compiling:  #  state entered with : and exited by ;
                self._state.compiler.compile_to_current_definition(compile_address(word, xt))
            else:
                execute_immediate(self._state, xt)
        else:
            if self.is_literal(word):
                action: DEFINED_XT = DefinedExecutionToken([xt_r_push, self._state.word_to_int(word)])
                if self._state.is_compiling:
                    self._state.compiler.compile_to_current_definition(action)
                else:
                    self._state.execute(action)
            else:  # defer
                if self._state.is_compiling:
                    self._state.compiler.compile_to_current_definition(deferred_definition(word))
                else:
                    fatal(f"Unknown word: {word!r}")

    def is_literal(self, word: str) -> bool:
        try:
            int(word, base=self._state.base)
            return True
        except ValueError as exc:
            if 'invalid literal' in str(exc):
                # maybe it's a decimal a.k.a. fixed point literal
                try:
                    float(word)
                    return True
                except ValueError:
                    pass
        return False

    def _bootstrap(self, extensions: Sequence[str | Path]) -> None:
        self._state.interactive = False
        for extension in extensions:
            extension_path =  Path(extension)
            with extension_path.open(mode='r') as stream:
                code: str = ' \n'.join(stream.readlines())
                self.run(input_code=code)
