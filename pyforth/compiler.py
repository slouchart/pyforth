from .core import DEFINED_XT_R, POINTER, State, XT_C
from .runtime import runtime_execution_tokens, xt_r_rs_at
from .runtime import (
    xt_r_jmp,
    xt_r_jz,
    xt_r_jnz,
    xt_r_to_rs,
    xt_r_swap,
    xt_r_from_rs,
    xt_r_push,
    xt_r_dup,
    xt_r_eq,
    xt_r_add,
    xt_r_drop,
)
from .utils import fatal


def xt_c_colon(state: State, _) -> None:
    if state.control_stack:
        fatal(": inside Control stack: %s" % state.control_stack)
    label = state.next_word()
    state.control_stack.append(("COLON", label))  # flag for following ";"


def xt_c_semi(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No : for ; to match")
    word, label = state.control_stack.pop()
    if word != "COLON":
        fatal(": not balanced with ;")
    assert isinstance(label, str)
    runtime_execution_tokens[label] = code[:]  # Save word definition in rDict
    while code:
        code.pop()


def xt_c_begin(state: State, code: DEFINED_XT_R) -> None:
    state.control_stack.append(("BEGIN", len(code)))  # flag for following UNTIL/REPEAT


def xt_c_until(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No BEGIN for UNTIL to match")
    word, slot = state.control_stack.pop()
    if word != "BEGIN":
        fatal("UNTIL preceded by %s (not BEGIN)" % word)
    code.append(xt_r_jz)
    code.append(slot)


def xt_c_if(state: State, code: DEFINED_XT_R) -> None:
    code.append(xt_r_jz)
    state.control_stack.append(("IF", len(code)))  # flag for following Then or Else
    code.append(0)  # slot to be filled in


def xt_c_else(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No IF for ELSE to match")
    word, slot = state.control_stack.pop()
    if word != "IF":
        fatal("ELSE preceded by %s (not IF)" % word)
    assert isinstance(slot, POINTER)
    code.append(xt_r_jmp)
    state.control_stack.append(("ELSE", len(code)))  # flag for following THEN
    code.append(0)  # slot to be filled in
    code[slot] = len(code)  # close JZ for IF


def xt_c_then(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No IF or ELSE for THEN to match")
    word, slot = state.control_stack.pop()
    if word not in ("IF", "ELSE"):
        fatal("THEN preceded by %s (not IF or ELSE)" % word)
    assert isinstance(slot, POINTER)
    code[slot] = len(code)  # close JZ for IF or JMP for ELSE


def xt_c_while(state: State, code: DEFINED_XT_R) -> None:
    code.append(xt_r_jnz)
    state.control_stack.append(("WHILE", len(code)))  # flag for following REPEAT
    code.append(0)  # to be filled in by REPEAT


def xt_c_repeat(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No WHILE for REPEAT to match")
    word, slot2 = state.control_stack.pop()
    if word != "WHILE":
        fatal("REPEAT preceded by %s (not WHILE)" % word)
    assert isinstance(slot2, POINTER)

    proceed: bool = bool(state.control_stack)
    if proceed:
        word, slot1 = state.control_stack.pop()
        proceed = (word == 'BEGIN')
        if proceed:
            code.append(xt_r_jmp)
            code.append(slot1)

    if not proceed:
        fatal('No BEGIN for REPEAT to match')

    code[slot2] = len(code)  # close JNZ for WHILE


def xt_c_do(state: State, code: DEFINED_XT_R) -> None:
    code.append(xt_r_swap)
    code.append(xt_r_to_rs)  # push limit to rs
    code.append(xt_r_to_rs) # push starting index to rs
    state.control_stack.append(("DO", len(code)))  # flag for next LOOP


def xt_c_loop(state: State, code: DEFINED_XT_R) -> None:
    if not state.control_stack:
        fatal("No DO for LOOP to match")
    word, slot = state.control_stack.pop()
    if word != "DO":
        fatal("LOOP preceded by %s (not DO)" % word)
    assert isinstance(slot, POINTER)
    code += [
        xt_r_from_rs,
        xt_r_push, 1,
        xt_r_add,
        xt_r_rs_at,
        xt_r_swap,
        xt_r_dup,
        xt_r_to_rs,
        xt_r_eq,
        xt_r_jz, slot,
        xt_r_from_rs,
        xt_r_from_rs,
        xt_r_drop,
        xt_r_drop
    ]


compilation_tokens: dict[str, XT_C] = {
    ":": xt_c_colon,
    ";": xt_c_semi,
    "if": xt_c_if,
    "else": xt_c_else,
    "then": xt_c_then,
    "begin": xt_c_begin,
    "until": xt_c_until,
    "while": xt_c_while,
    "repeat": xt_c_repeat,
    "do": xt_c_do,
    "loop": xt_c_loop,
}
