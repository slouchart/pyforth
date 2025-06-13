from pyforth.core import State
from pyforth.runtime.utils import intercept_stack_error


@intercept_stack_error
def xt_r_allot(state: State) -> None:
    """reserve n words for last create"""
    nb_cells = state.ds.pop()
    assert isinstance(nb_cells, int)
    state.next_heap_address += nb_cells


@intercept_stack_error
def xt_r_at(state: State) -> None:
    state.ds.append(state.heap[state.ds.pop()])  # get heap @ address


@intercept_stack_error
def xt_r_bang(state: State) -> None:
    a = state.ds.pop()
    state.heap[a] = state.ds.pop()  # set heap @ address


@intercept_stack_error
def xt_r_coma(state: State) -> None:  # push tos into heap
    state.heap[state.next_heap_address] = state.ds.pop()
    state.next_heap_address += 1


def xt_r_here(state: State) -> None:  # push next heap address onto tos
    state.ds.append(state.next_heap_address)
