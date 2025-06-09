import sys

from pyforth.core import State
from .utils import flush_stdout


@flush_stdout
def xt_r_dot_quote(state: State) -> None:
    value: str = parse_string(state)
    sys.stdout.write(value)


def xt_r_s_quote(state: State) -> None:
    value: str = parse_string(state)
    cells: list[int] = [len(value)] + [ord(c) for c in value]
    start: int = state.next_heap_address
    state.next_heap_address += len(cells)
    for offset, cell in enumerate(cells):
        state.heap[start + offset] = cells[offset]
    state.ds.append(start)
    state.ds.append(len(value))


def parse_string(state: State) -> str:
    c: str = state.next_char()
    s: str = ''
    while c and c != '"':
        s += c
        c = state.next_char()

    return s
