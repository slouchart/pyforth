import sys
from typing import Final

from pyforth.core import State, LITERAL, POINTER, WORD
from .primitives import xt_r_push
from .utils import flush_stdout, compiling_word, fatal

QUOTE: Final[str] = r'"'


@compiling_word
def xt_c_dot_quote(state: State) -> None:
    value: str = parse_string(state, until=QUOTE)

    @flush_stdout
    def xt_r_dot_quote(*_) -> None:
        sys.stdout.write(value)

    if state.is_compiling:
        state.current_definition += [xt_r_dot_quote,]
    else:
        xt_r_dot_quote(state)


@compiling_word
def xt_c_s_quote(state: State) -> None:
    value: str = parse_string(state, until=QUOTE)

    def xt_r_s_quote(_state: State) -> None:
        cells: list[int] = [ord(c) for c in value]
        start: int = _state.next_heap_address
        _state.next_heap_address += len(cells)
        for offset, cell in enumerate(cells):
            _state.heap[start + offset] = cells[offset]
        _state.ds.append(start)
        _state.ds.append(len(value))

    if state.is_compiling:
        state.current_definition += [xt_r_s_quote,]
    else:
        xt_r_s_quote(state)


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


def xt_r_char(state: State) -> None:
    word: WORD = state.next_word(preserve_case=True)
    state.ds.append(ord(word[0]))


@compiling_word
def xt_c_bracket_char(state: State) -> None:
    if not state.is_compiling:
        fatal("[CHAR] Interpreting a compile-only word")

    word: WORD = state.next_word()
    state.current_definition += [xt_r_push, ord(word[0])]
