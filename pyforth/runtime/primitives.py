from typing import cast, Optional
from pyforth.core import DEFINED_XT, LITERAL, POINTER, WORD, XT, Compiler
from pyforth.core import DefinedExecutionToken, ForthCompilationError, State
from pyforth.runtime.utils import compiling_word, fatal, intercept_stack_error, define_word, immediate_word


@define_word("create")
def xt_r_create(state: State) -> None:
    label = state.next_word()
    # when created word is run, pushes its address
    state.execution_tokens[label] = DefinedExecutionToken([xt_r_push, state.next_heap_address])
    state.reveal_created_word(label)


@define_word("does>")
def xt_r_does(state: State) -> POINTER:
    assert isinstance(state.execution_tokens[state.last_created_word], list)
    ref_xt: DEFINED_XT = cast(DEFINED_XT, state.execution_tokens[state.last_created_word])
    # rest of words belong to created words runtime
    ref_xt += state.current_defined_execution_token[state.instruction_pointer:]
    return len(state.current_defined_execution_token)  # jump p over these


def xt_r_jmp(state: State) -> POINTER:
    return cast(POINTER, state.current_execution_token)


def xt_r_jz(state: State) -> POINTER:
    return (
        cast(POINTER, state.current_execution_token),
        state.instruction_pointer + 1
    )[state.ds.pop()]


def xt_r_jnz(state: State) -> POINTER:
    return (
        state.instruction_pointer + 1,
        cast(POINTER, state.current_execution_token)
    )[state.ds.pop()]


def xt_r_push(state: State) -> POINTER:
    state.ds.append(cast(LITERAL, state.current_execution_token))
    return state.instruction_pointer + 1


def xt_r_run(state: State) -> POINTER:
    p: POINTER = state.instruction_pointer  # save current IP
    word: WORD = cast(WORD, state.current_execution_token)
    try:
        xt_r: DEFINED_XT = cast(DEFINED_XT, state.execution_tokens[word])
        state.execute(xt_r)
        return p + 1
    except KeyError:
        raise ForthCompilationError(f"Undefined word {word!r}") from None


def xt_r_push_rs(state: State) -> POINTER:
    state.rs.append(cast(LITERAL, state.current_execution_token))
    return state.instruction_pointer + 1


def xt_r_drop_rs(state: State) -> None:
    state.rs.pop()
    return None


@define_word(":")
@immediate_word
def xt_c_colon(state: State) -> None:
    if state.is_compiling:
        fatal(f"COLON: Already compiling a definition")

    state.set_compile_flag()  # enter "compile" mode
    state.compiler.prepare_current_definition(state.next_word())  # prepare code definition


@define_word(";")
@compiling_word
def xt_c_semi(state: State, compiler: Compiler) -> None:
    if not state.is_compiling:
        fatal("SEMICOLON: Not in compile mode")

    compiler.complete_current_definition()
    state.reset_compile_flag()


@define_word("exit")
def xt_r_exit(state: State) -> POINTER:
    ptr: POINTER = len(state.current_defined_execution_token)
    return ptr


@define_word("postpone")
@compiling_word
def xt_c_postpone(state: State, compiler: Compiler) -> None:
    if not state.is_compiling:
        fatal("POSTPONE: Not in compile mode")
    word: WORD = state.next_word()
    xt: XT | None = state.execution_tokens.get(word)
    if xt is None:
        fatal(f"POSTPONE: unknown word {word!r}")
    assert xt is not None  # so mypy is happy...
    compiler.compile_to_current_definition(compile_address(word, xt))


@define_word("immediate")
def xt_r_immediate(state: State) -> None:
    if state.is_compiling:
        fatal("IMMEDIATE: In compile mode")
    word: WORD = state.last_created_word
    xt: XT | None = state.execution_tokens.get(word)
    if xt is None:
        fatal(f"IMMEDIATE: unknown word {word!r}")
    setattr(xt, '_immediate', True)


@define_word("recurse")
@compiling_word
def xt_c_recurse(state: State, compiler: Compiler) -> None:
    if not state.is_compiling:
        fatal("RECURSE outside definition")

    compiler.compile_to_current_definition(
        [
            xt_r_run,
            compiler.get_current_definition_as_word()
        ]
    )


@define_word("'")
def xt_r_tick(state: State):
    word: WORD = state.next_word()
    addr: POINTER | None = get_word_address(state.execution_tokens, word)
    assert addr is not None
    state.ds.append(addr)


@define_word("execute")
@intercept_stack_error
def xt_r_execute(state: State) -> Optional[POINTER]:
    xt_addr: POINTER = state.ds.pop()
    word_and_xt = get_word_from_address(state.execution_tokens, xt_addr)
    assert word_and_xt is not None
    return execute_immediate(state, word_and_xt[1])


@define_word("[compile]")
@compiling_word
def xt_c_bracket_compile(state: State, compiler: Compiler) -> None:
    if not state.is_compiling:
        fatal("[COMPILE] outside definition")

    word: WORD = state.next_word()
    found, immediate, xt = search_word(state.execution_tokens, word)
    if found:
        if immediate:
            compiler.compile_to_current_definition(xt)
        else:
            assert xt is not None
            def _xt(_state: State) -> None:
                _state.compiler.compile_to_current_definition(compile_address(word, xt))
            compiler.compile_to_current_definition(_xt)
    else:
        raise ForthCompilationError(f"Unknown word: {word!r}")


def execute_immediate(state: State, func: XT) -> Optional[POINTER]:
    if isinstance(func, list):
        return state.execute(cast(DEFINED_XT, func))
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
