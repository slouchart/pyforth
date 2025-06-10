import sys
from typing import Final

from pyforth.core import State, LITERAL, POINTER
from .utils import flush_stdout, compiling_word


QUOTE: Final[str] = r'"'


@compiling_word
def xt_c_dot_quote(state: State) -> None:
    value: str = parse_string(state)

    @flush_stdout
    def xt_r_dot_quote(*_) -> None:
        sys.stdout.write(value)

    if state.is_compiling:
        state.current_definition += [xt_r_dot_quote,]
    else:
        xt_r_dot_quote(state)


@compiling_word
def xt_c_s_quote(state: State) -> None:
    value: str = parse_string(state)

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


def parse_string(state: State) -> str:
    c: str = state.next_char()
    s: str = ''
    while c and c != QUOTE:
        s += c
        c = state.next_char()
    return s
