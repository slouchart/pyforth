from pyforth.core import State
from pyforth.runtime.utils import intercept_stack_error, define_word


@define_word("allot")
@intercept_stack_error
def xt_r_allot(state: State) -> None:
    """reserve n words for last create"""
    nb_cells = state.ds.pop()
    assert isinstance(nb_cells, int)
    state.next_heap_address += nb_cells


@define_word("@")
@intercept_stack_error
def xt_r_fetch(state: State) -> None:
    state.ds.append(state.heap[state.ds.pop()])  # get heap @ address


@define_word("!")
@intercept_stack_error
def xt_r_store(state: State) -> None:
    a = state.ds.pop()
    state.heap[a] = state.ds.pop()  # set heap @ address


@define_word(",")
@intercept_stack_error
def xt_r_coma(state: State) -> None:  # push tos into heap
    state.heap[state.next_heap_address] = state.ds.pop()
    state.next_heap_address += 1


@define_word("here")
def xt_r_here(state: State) -> None:  # push next heap address onto tos
    state.ds.append(state.next_heap_address)
