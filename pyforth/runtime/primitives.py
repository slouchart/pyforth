from typing import cast
from pyforth.core import DEFINED_XT, POINTER, LITERAL, State, WORD, ForthCompilationError


def xt_r_create(state: State) -> None:
    state.last_created_word = label = state.next_word()
    # when created word is run, pushes its address
    state.runtime_execution_tokens[label] = [xt_r_push, state.next_heap_address]


def xt_r_does(state: State) -> POINTER:
    assert isinstance(state.runtime_execution_tokens[state.last_created_word], list)
    xt_r: DEFINED_XT = cast(DEFINED_XT, state.runtime_execution_tokens[state.last_created_word])
    xt_r += state.loaded_code[state.instruction_pointer:]  # rest of words belong to created words runtime
    return len(state.loaded_code)  # jump p over these


def xt_r_jmp(state: State) -> POINTER:
    return cast(POINTER, state.loaded_code[state.instruction_pointer])


def xt_r_jz(state: State) -> POINTER:
    return (
        cast(POINTER, state.loaded_code[state.instruction_pointer]),
        state.instruction_pointer + 1)[state.ds.pop()]


def xt_r_jnz(state: State) -> POINTER:
    return (
        state.instruction_pointer + 1,
        cast(POINTER, state.loaded_code[state.instruction_pointer])
    )[state.ds.pop()]


def xt_r_push(state: State) -> POINTER:
    state.ds.append(cast(LITERAL, state.loaded_code[state.instruction_pointer]))
    return state.instruction_pointer + 1


def xt_r_run(state: State) -> POINTER:
    p: POINTER = state.instruction_pointer
    word: WORD = cast(WORD, state.loaded_code[p])
    try:
        xt_r: DEFINED_XT = cast(DEFINED_XT, state.runtime_execution_tokens[word])
        state.execute_as(xt_r)
        return p + 1
    except KeyError:
        raise ForthCompilationError(f"Undefined word {word!r}") from None


def xt_r_push_rs(state: State) -> POINTER:
    state.rs.append(cast(LITERAL, state.loaded_code[state.instruction_pointer]))
    return state.instruction_pointer + 1


def xt_r_drop_rs(state: State) -> None:
    state.rs.pop()
    return None
