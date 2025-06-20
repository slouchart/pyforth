from typing import cast

from pyforth.abc import Compiler, DefinedExecutionToken, State
from pyforth.annotations import DEFINED_XT, POINTER, STACK, WORD, XT_ATOM

from pyforth.runtime.utils import roll_any_stack


CONTROL_STRUCT = POINTER | WORD
CONTROL_STACK = STACK[CONTROL_STRUCT]


class _Compiler(Compiler):

    def __init__(self, state: State):
        self._interpreter: State = state
        self._control_stack: CONTROL_STACK = []
        self._current_definition: DefinedExecutionToken[XT_ATOM] = DefinedExecutionToken()

    def prepare_current_definition(self, word: WORD) -> None:
        assert self._interpreter.is_compiling
        assert not self._current_definition
        self._current_definition = DefinedExecutionToken()
        self._control_stack.append(word)

    def get_current_definition_as_word(self) -> WORD:
        word: WORD = cast(WORD, self._control_stack[0])
        assert isinstance(word, str)
        return word

    def compile_to_current_definition(self, obj = None) -> POINTER:
        if obj is None:
            return len(self._current_definition)

        if isinstance(obj, list):
            self._current_definition += obj
        else:
            self._current_definition.append(obj)

        return len(self._current_definition)

    def control_structure_init_open_dest(self) -> None:
        """pushes a dest pointer onto the CS, pointer to be later used by a closing word to jump back
           like in a DO...LOOP construct
        """
        self._control_stack.append(len(self._current_definition))

    def control_structure_init_open_orig(self) -> None:
        self._control_stack.append(len(self._current_definition))  # flag for following CS word
        self.compile_to_current_definition(0)  # slot to be filled in

    def control_structure_close_open_dest(self) -> None:
        self.compile_to_current_definition(self._control_stack.pop())

    def control_struct_close_open_orig(self) -> None:
        addr: POINTER = cast(POINTER, self._control_stack.pop())
        self._current_definition[addr] = len(self._current_definition)

    def control_stack_roll(self, depth: int) -> None:
        roll_any_stack(self._control_stack, depth)

    def complete_current_definition(self) -> None:
        interpreter = self._interpreter
        word: WORD = cast(WORD, self._control_stack.pop())
        new_xt: DefinedExecutionToken[XT_ATOM] = DefinedExecutionToken(self._current_definition[:])
        interpreter.reveal_created_word(word)
        interpreter.execution_tokens[interpreter.last_created_word] = cast(DEFINED_XT, new_xt)
        self._current_definition.clear()

