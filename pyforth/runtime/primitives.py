from typing import cast
from pyforth.core import DEFINED_XT, POINTER, LITERAL, State, WORD, ForthCompilationError
from pyforth.runtime.utils import compiling_word, fatal, set_exit_jmp_address


def xt_r_create(state: State) -> None:
    state.last_created_word = label = state.next_word()
    # when created word is run, pushes its address
    state.execution_tokens[label] = [xt_r_push, state.next_heap_address]


def xt_r_does(state: State) -> POINTER:
    assert isinstance(state.execution_tokens[state.last_created_word], list)
    xt_r: DEFINED_XT = cast(DEFINED_XT, state.execution_tokens[state.last_created_word])
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
        xt_r: DEFINED_XT = cast(DEFINED_XT, state.execution_tokens[word])
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


@compiling_word
def xt_c_colon(state: State) -> None:
    if state.is_compiling:
        fatal(f"COLON: Already compiling a definition")
    if state.control_stack:
        fatal(f": inside Control stack: {state.control_stack}")
    label = state.next_word()
    state.control_stack.append(("COLON", label, ()))  # flag for following ";"
    state.set_compile_flag()  # enter "compile" mode
    state.current_definition = []  # prepare code definition


@compiling_word
def xt_c_semi(state: State) -> None:
    if not state.is_compiling:
        fatal("SEMICOLON: Not in compile mode")
    if not state.control_stack:
        fatal("No : for ; to match")
    word, label, exit_, *_ = state.control_stack.pop()
    if word != "COLON":
        fatal(": not balanced with ;")
    assert isinstance(label, str)
    set_exit_jmp_address(exit_, state.current_definition)
    state.execution_tokens[label] = state.current_definition[:]  # Save word definition in rDict
    state.current_definition.clear()
    state.reset_compile_flag()


@compiling_word
def xt_c_exit(state: State) -> None:

    def _exit(_state: State, _code: DEFINED_XT):
        if not _state.control_stack:
            fatal("EXIT outside block")
        word, label, _ = _state.control_stack.pop()
        if word in ('IF', 'WHILE'):
            _exit(_state, _code)
            _state.control_stack.append((word, label, _))
        else:
            if word not in ('COLON', 'BEGIN', 'DO'):
                fatal(f"EXIT: Unexpected block structure {word}")
            _code.append(xt_r_jmp)
            _state.control_stack.append((word, label, ('EXIT', len(_code))))
            _code.append(0)

    _exit(state, state.current_definition)
