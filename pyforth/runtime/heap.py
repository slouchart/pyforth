from pyforth.core import State

from .utils import pass_state_only


@pass_state_only
def xt_r_allot(state: State) -> None:
    """reserve n words for last create"""
    nb_cells = state.ds.pop()
    assert isinstance(nb_cells, int)
    state.next_heap_address += nb_cells


@pass_state_only
def xt_r_at(state: State) -> None:
    state.ds.append(state.heap[state.ds.pop()])  # get heap @ address


@pass_state_only
def xt_r_bang(state: State) -> None:
    a = state.ds.pop()
    state.heap[a] = state.ds.pop()  # set heap @ address


@pass_state_only
def xt_r_coma(state: State) -> None:  # push tos into heap
    state.heap[state.next_heap_address] = state.ds.pop()
    state.next_heap_address += 1

