from typing import cast, Optional
from pyforth.core import DefinedExecutionToken, DEFINED_XT, POINTER, LITERAL, State, WORD, ForthCompilationError, XT
from pyforth.runtime.utils import compiling_word, fatal, set_exit_jmp_address, intercept_stack_error


def xt_r_create(state: State) -> None:
    state.last_created_word = label = state.next_word()
    # when created word is run, pushes its address
    state.execution_tokens[label] = DefinedExecutionToken([xt_r_push, state.next_heap_address])


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
        state.instruction_pointer + 1
    )[state.ds.pop()]


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
        state.execute(xt_r)
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
    state.current_definition = DefinedExecutionToken()  # prepare code definition


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
    state.last_created_word = label
    set_exit_jmp_address(exit_, state.current_definition)
    state.execution_tokens[label] = DefinedExecutionToken(state.current_definition[:]) # Save word definition in rDict
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


@compiling_word
def xt_c_postpone(state: State) -> None:
    if not state.is_compiling:
        fatal("POSTPONE: Not in compile mode")
    word: WORD = state.next_word()
    xt: XT | None = state.execution_tokens.get(word)
    if xt is None:
        fatal(f"POSTPONE: unknown word {word!r}")
    assert xt is not None  # so mypy is happy...
    state.current_definition += compile_address(word, xt)


def xt_r_immediate(state: State) -> None:
    if state.is_compiling:
        fatal("IMMEDIATE: In compile mode")
    word: WORD = state.last_created_word
    xt: XT | None = state.execution_tokens.get(word)
    if xt is None:
        fatal(f"IMMEDIATE: unknown word {word!r}")
    setattr(xt, '_immediate', True)


@compiling_word
def xt_c_recurse(state: State) -> None:
    if not state.is_compiling:
        fatal("RECURSE outside definition")

    index: int = 1
    current_def: WORD = ''
    while index <= len(state.control_stack):
        colon, word, *_ = state.control_stack[-index]
        if colon == 'COLON':
            current_def = cast(WORD, word)
            break
        index += 1
    else:
        fatal(f"RECURSE: control stack error")

    state.current_definition += [xt_r_run, current_def]


def xt_r_tick(state: State):
    word: WORD = state.next_word()
    addr: POINTER | None = get_word_address(state.execution_tokens, word)
    assert addr is not None
    state.ds.append(addr)


@intercept_stack_error
def xt_r_execute(state: State) -> Optional[POINTER]:
    xt_addr: POINTER = state.ds.pop()
    word_and_xt = get_word_from_address(state.execution_tokens, xt_addr)
    assert word_and_xt is not None
    return execute_immediate(state, word_and_xt[1])


@compiling_word
def xt_c_bracket_compile(state: State) -> None:
    if not state.is_compiling:
        fatal("[COMPILE] outside definition")
    word: WORD = state.next_word()
    state.current_definition += [xt_c_compile, word]


@compiling_word
def xt_c_compile(state: State) -> POINTER:
    assert state.is_compiling
    word: WORD = state.loaded_code[state.instruction_pointer]
    state.current_definition += deferred_definition(word)
    return state.instruction_pointer + 1


def execute_immediate(state: State, func: XT) -> Optional[POINTER]:
    if isinstance(func, list):
        return state.execute(cast(DEFINED_XT, func))  # TODO needs rework
    else:
        assert callable(func)
        return func(state)


def get_word_from_address(words: dict[WORD, XT], addr: POINTER) -> tuple[WORD, XT] | None:
    for index, (word, xt) in enumerate(words.items()):
        if index == addr:
            return word, xt
    fatal(f"Cannot find word from address: {addr!r}")
    return None


def get_word_address(words: dict[WORD, XT], word: WORD) -> POINTER | None:
    for addr, (label, xt) in enumerate(words.items()):
        if label == word:
            return addr
    fatal(f"Unknown word: {word!r}")
    return None


def search_word(words: dict[WORD, XT], word: WORD) -> tuple[bool, bool, XT | None]:

    xt: XT | None = words.get(word)

    found: bool = xt is not None
    immediate: bool = xt is not None and hasattr(xt, '_immediate') and getattr(xt, '_immediate') is True
    return found, immediate, xt


def compile_address(word: WORD, xt_r: XT) -> DEFINED_XT:
    if isinstance(xt_r, list):
        return deferred_definition(word)

    return DefinedExecutionToken([xt_r, ])  # push builtin for runtime


def deferred_definition(word: WORD) -> DEFINED_XT:
    return DefinedExecutionToken([xt_r_run, word])
