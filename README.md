Q. design a program that either launch an interactive console or deals with a file.
A. a package 'pyforth' with a __main__ module. Needs to be installed.

Q. implement a basic arithmetic system in RevPolNot for signed integers
A. +, -, *, / (int div), mod (%), need a stack


Q. implement basic stack ops SWAP, DUP, DROP, OVER
A. easy

Q. implement comparison ops <, =, >, 0<, 0=
A. let's see, easy, the framework for unary, binary, n-ary operators is there

Q. implement conditional control structure <bool> IF <opt1> ELSE <opt2> THEN[|ENDIF] <suite>
A. Ok, need a second stack, the return stack and two primitives 0=JUMP and JUMP

Q. implement BEGIN <code> <bool> UNTIL, BEGIN <code> <bool> WHILE <code> REPEAT
A. Should work the same

Q. implement BEGIN [LEAVE] AGAIN
A. LEAVE is tricky, we need a return stack properly configured by the new primitive RPUSH during compile time so
the interpreter gets the correct jump address. Any word that ends a loop must set the arg to RPUSH for the BEGIN 
it depends on.

Q. implement DO <code> LOOP, I and J
A. 10 0 DO  I .  LOOP --> 0123456789

Q. implement word definition
A. like make_op but with code

https://www.complang.tuwien.ac.at/forth/gforth/Docs-html/Review-_002d-elements-of-a-Forth-system.html#Review-_002d-elements-of-a-Forth-system
https://sifflez.org/lectures/ASE/C3.pdf
https://vfxforth.com/arena/ProgramForth.pdf

1. We don't need a compiler AND an interpreter
2. Forth is both a VM and an interpreter, the interpreter is the VM
3. we need a dictionary to store word either natives or user-defined
4. we need a data stack and a return stack
5. buffer for I/O (sys.stdin and sys.stdout come handy)
6. we need a data structure for user variables (effect of STORE a.k.a. ! and GET a.k.a. @)
7. and a loop for the interpreter that reads tokens from a generator
8. tells whether that token is a word in the dictionary
9. if yes, compile that word if in compile mode and word is not immediate
10. or execute that word
11. if no, push that word if is a literal and not in compile mode
12. or mark that word as a literal to postpone the push
13. if word is not a literal and not in the dictionary, raise an error
14. rinse and repeat

CREATE <word> 
1. "is a parsing word" (meaning it absorbs the next word), this is interpretation semantics
2. it creates a new entry in the dictionary with an allocated address
3. when <word> is executed, it leaves its address on the data stack

we need a way to know the most-recently defined word

https://www.openbookproject.net/py4fun/forth/forth.html

