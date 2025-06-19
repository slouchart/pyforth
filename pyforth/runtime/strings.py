import sys
from typing import Final

from pyforth.core import State, LITERAL, POINTER, WORD, NATIVE_XT
from .primitives import xt_r_push
from .utils import flush_stdout, compiling_word, fatal, define_word, immediate_word

QUOTE: Final[str] = r'"'


@define_word('."')
@compiling_word
def xt_c_dot_quote(state: State) -> None:
    value: str = parse_string(state, until=QUOTE)

    @flush_stdout
    def xt_r_dot_quote(*_) -> None:
        sys.stdout.write(value)

    if state.is_compiling:
        state.compile_to_current_definition([xt_r_dot_quote,])
    else:
        xt_r_dot_quote(state)


@define_word('c"')
@compiling_word
def xt_c_char_quote(state: State) -> None:
    if not state.is_compiling:
        fatal("C\" Interpreting a compile-only word")
    value: str = parse_string(state, until=QUOTE)
    state.compile_to_current_definition([_store_string(value, counted=True)])


def _store_string(s: str, counted: bool = False) -> NATIVE_XT:

    def _xt(state: State) -> None:
        cells: list[int] = [ord(c) for c in s]
        start: int = state.next_heap_address
        state.next_heap_address += len(cells) + (1 if counted else 0)
        if counted:
            state.heap[start] = len(s)
        for offset, cell in enumerate(cells):
            state.heap[start + offset + (1 if counted else 0)] = cells[offset]
        state.ds.append(start)
        if not counted:
            state.ds.append(len(s))

    return _xt


@define_word('s"')
@immediate_word
def xt_c_s_quote(state: State) -> None:
    value: str = parse_string(state, until=QUOTE)

    if state.is_compiling:
        state.compile_to_current_definition([_store_string(value),])
    else:
        _store_string(value)(state)


@define_word("type")
@flush_stdout
def xt_r_type(state: State) -> None:
    count: LITERAL = state.ds.pop()
    addr: POINTER = state.ds.pop()
    s: str = ''.join(chr(state.heap[inx]) for inx in range(addr, addr+count))
    sys.stdout.write(s)


def parse_string(state: State, until: str) -> str:
    c: str = state.next_char()
    s: str = ''
    while c and c != until:
        s += c
        c = state.next_char()
    return s


@define_word("char")
def xt_r_char(state: State) -> None:
    word: WORD = state.next_word(preserve_case=True)
    state.ds.append(ord(word[0]))


@define_word("[char]")
@compiling_word
def xt_c_bracket_char(state: State) -> None:
    if not state.is_compiling:
        fatal("[CHAR] Interpreting a compile-only word")

    word: WORD = state.next_word(preserve_case=True)
    state.compile_to_current_definition([xt_r_push, ord(word[0])])
