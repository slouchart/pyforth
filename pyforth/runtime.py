import operator
import sys
from typing import cast
from .core import State, POINTER, DEFINED_XT_R, XT_R, WORD, LITERAL


def xt_r_add(state: State, *_) -> None:
    b = state.ds.pop()
    a = state.ds.pop()
    state.ds.append(a + b)


def xt_r_mul(state: State, *_) -> None:
    b = state.ds.pop()
    a = state.ds.pop()
    state.ds.append(a * b)


def xt_r_sub(state: State, *_) -> None:
    b = state.ds.pop()
    a = state.ds.pop()
    state.ds.append(a - b)


def xt_r_div(state: State, *_) -> None:
    b = state.ds.pop()
    a = state.ds.pop()
    state.ds.append(a // b)


def xt_r_mod(state: State, *_) -> None:
    b = state.ds.pop()
    a = state.ds.pop()
    state.ds.append(a % b)


def xt_r_eq(state: State, *_) -> None:
    b = state.ds.pop()
    a = state.ds.pop()
    state.ds.append(int(a == b))


def xt_r_gt(state: State, *_) -> None:
    b = state.ds.pop()
    a = state.ds.pop()
    state.ds.append(int(a > b))


def xt_r_lt(state: State, *_) -> None:
    b = state.ds.pop()
    a = state.ds.pop()
    state.ds.append(int(a < b))

def xt_r_and(state: State, *_) -> None:
    b = state.ds.pop()
    a = state.ds.pop()
    state.ds.append(operator.and_(a, b))

def xt_r_or(state: State, *_) -> None:
    b = state.ds.pop()
    a = state.ds.pop()
    state.ds.append(operator.or_(a, b))

def xt_r_invert(state: State, *_) -> None:
    a = state.ds.pop()
    state.ds.append(operator.not_(a))

def xt_r_xor(state: State, *_) -> None:
    b = state.ds.pop()
    a = state.ds.pop()
    state.ds.append(operator.xor(a, b))

def xt_r_swap(state: State, *_) -> None:
    a = state.ds.pop()
    b = state.ds.pop()
    state.ds.append(a)
    state.ds.append(b)


def xt_r_dup(state: State, *_) -> None:
    state.ds.append(state.ds[-1])


def xt_r_drop(state: State, *_) -> None:
    state.ds.pop()


def xt_r_over(state: State, *_) -> None:
    state.ds.append(state.ds[-2])


def xt_r_rot(state: State, *_) -> None:
    first = state.ds.pop()
    second = state.ds.pop()
    third = state.ds.pop()
    state.ds += [second, first, third]


def xt_r_dump(state: State, *_) -> None:
    print("state.ds = %s" % state.ds)


def xt_r_dot(state: State, *_) -> None:
    sys.stdout.write(str(state.ds.pop()))
    if state.interactive:
        sys.stdout.write("\n")
        sys.stdout.flush()


def xt_r_emit(state: State, *_) -> None:
    a = state.ds.pop()
    sys.stdout.write(chr(a))
    if state.interactive:
        sys.stdout.write("\n")
        sys.stdout.flush()


def xt_r_jmp(_: State, code: DEFINED_XT_R, p: POINTER) -> POINTER:
    return cast(POINTER, code[p])


def xt_r_jnz(state: State, code: DEFINED_XT_R, p:POINTER) -> POINTER:
    value: LITERAL = state.ds.pop()
    addr: POINTER = cast(POINTER, code[p])
    return (addr, p + 1)[value]


def xt_r_jz(state: State, code: DEFINED_XT_R, p: POINTER) -> POINTER:
    value: LITERAL = state.ds.pop()
    addr: POINTER = cast(POINTER, code[p])
    return (p + 1, addr)[value == 0]


def xt_r_run(state: State, code: DEFINED_XT_R, p: POINTER) -> POINTER:
    word = cast(WORD, code[p])
    xt_r: DEFINED_XT_R = cast(DEFINED_XT_R, runtime_execution_tokens[word])
    state.execute_as(xt_r)
    return p + 1


def xt_r_push(state: State, cod, p) -> int:
    state.ds.append(cod[p])
    return p + 1


def xt_r_create(state: State, *_) -> None:
    state.last_created_word = label = state.next_word()
    # when created word is run, pushes its address
    runtime_execution_tokens[label] = [xt_r_push, state.next_heap_address]


def xt_r_does(state: State, code: DEFINED_XT_R, p: POINTER) -> POINTER:
    assert isinstance(runtime_execution_tokens[state.last_created_word], list)
    xt_r: DEFINED_XT_R = cast(DEFINED_XT_R, runtime_execution_tokens[state.last_created_word])
    xt_r += code[p:]  # rest of words belong to created words runtime
    return len(code)  # jump p over these


def xt_r_allot(state: State, *_) -> None:
    """reserve n words for last create"""
    nb_cells = state.ds.pop()
    assert isinstance(nb_cells, int)
    state.next_heap_address += nb_cells


def xt_r_at(state: State, *_) -> None:
    state.ds.append(state.heap[state.ds.pop()])  # get heap @ address


def xt_r_bang(state: State, *_) -> None:
    a = state.ds.pop()
    state.heap[a] = state.ds.pop()  # set heap @ address


def xt_r_coma(state: State, *_) -> None:  # push tos into heap
    state.heap[state.next_heap_address] = state.ds.pop()
    state.next_heap_address += 1


def xt_r_to_rs(state: State, *_) -> None:
    state.rs.append(state.ds.pop())


def xt_r_from_rs(state: State, *_) -> None:
    state.ds.append(state.rs.pop())


def xt_r_rs_at(state: State, *_) -> None:
    state.ds.append(state.rs[-1])


runtime_execution_tokens: dict[str, XT_R] = {
    "+": xt_r_add,
    "-": xt_r_sub,
    "/": xt_r_div,
    'mod': xt_r_mod,
    "*": xt_r_mul,
    "over": xt_r_over,
    "dup": xt_r_dup,
    "swap": xt_r_swap,
    ".": xt_r_dot,
    "dump": xt_r_dump,
    "drop": xt_r_drop,
    'rot': xt_r_rot,
    "=": xt_r_eq,
    ">": xt_r_gt,
    "<": xt_r_lt,
    ",": xt_r_coma,
    "@": xt_r_at,
    "!": xt_r_bang,
    ">r": xt_r_to_rs,
    "r>": xt_r_from_rs,
    "r@": xt_r_rs_at,
    "allot": xt_r_allot,
    "create": xt_r_create,
    "does>": xt_r_does,
    "1+": [xt_r_push, 1, xt_r_add],
    "negate": [xt_r_push, 0, xt_r_swap, xt_r_sub],
    '2dup': [xt_r_over] * 2,
    '2drop': [xt_r_drop] * 2,
    '2swap': [xt_r_rot, xt_r_to_rs, xt_r_rot, xt_r_from_rs],
    '2>r': [xt_r_swap, xt_r_to_rs, xt_r_to_rs],
    '2r>': [xt_r_from_rs, xt_r_from_rs, xt_r_swap],
    '2over': [xt_r_run, '2>r', xt_r_run, '2dup', xt_r_run, '2r>', xt_r_run, '2swap'],
    '0<': [xt_r_push, 0, xt_r_lt],
    '0=': [xt_r_push, 0, xt_r_eq],
    '0>': [xt_r_push, 0, xt_r_gt],
    'and': xt_r_and,
    'or': xt_r_or,
    'invert': xt_r_invert,
    'xor': xt_r_xor,
    'emit': xt_r_emit,
    'cr': [xt_r_push, 10, xt_r_emit],
    'variable': [xt_r_create, xt_r_push, 0, xt_r_coma],
    'constant': [xt_r_create, xt_r_coma, xt_r_does, xt_r_at],
    'i': [xt_r_rs_at]
}

