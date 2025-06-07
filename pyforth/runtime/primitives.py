from typing import cast
from pyforth.core import DEFINED_XT_R, POINTER, LITERAL, STACK, State, WORD, ForthCompilationError
from .utils import pass_data_stack, pass_no_state, pass_state_only


@pass_state_only
def xt_r_create(state: State) -> None:
    state.last_created_word = label = state.next_word()
    # when created word is run, pushes its address
    state.runtime_execution_tokens[label] = [xt_r_push, state.next_heap_address]


def xt_r_does(state: State, code: DEFINED_XT_R, p: POINTER) -> POINTER:
    assert isinstance(state.runtime_execution_tokens[state.last_created_word], list)
    xt_r: DEFINED_XT_R = cast(DEFINED_XT_R, state.runtime_execution_tokens[state.last_created_word])
    xt_r += code[p:]  # rest of words belong to created word runtime
    return len(code)  # jump p over these


@pass_no_state
def xt_r_jmp(code: DEFINED_XT_R, p: POINTER) -> POINTER:
    return cast(POINTER, code[p])


@pass_data_stack
def xt_r_jz(ds: STACK, code: DEFINED_XT_R, p:POINTER) -> POINTER:
    return (cast(POINTER, code[p]), p + 1)[ds.pop()]


@pass_data_stack
def xt_r_jnz(ds: STACK, code: DEFINED_XT_R, p: POINTER) -> POINTER:
    return (p + 1, cast(POINTER, code[p]))[ds.pop()]


@pass_data_stack
def xt_r_push(ds: STACK, code: DEFINED_XT_R, p: POINTER) -> int:
    ds.append(cast(LITERAL, code[p]))
    return p + 1


def xt_r_run(state: State, code: DEFINED_XT_R, p: POINTER) -> POINTER:
    word: WORD = cast(WORD, code[p])
    try:
        xt_r: DEFINED_XT_R = cast(DEFINED_XT_R, state.runtime_execution_tokens[word])
        state.execute_as(xt_r)
        return p + 1
    except KeyError:
        raise ForthCompilationError(f"Undefined word {word!r}") from None


def xt_r_push_rs(state: State, code: DEFINED_XT_R, p: POINTER) -> POINTER:
    state.rs.append(cast(LITERAL, code[p]))
    return p + 1


@pass_state_only
def xt_r_drop_rs(state: State) -> None:
    state.rs.pop()
    return None
