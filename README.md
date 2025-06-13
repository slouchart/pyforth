Notes
=====

This my second or third attempt at writing a Forth pseudo-compiler in Python.

I took most of my inspiration from Chris Meyers and Fred Obermann article (https://www.openbookproject.net/py4fun/forth/forth.html)

Fixed-point computing
=====================

Modern Forth compilers come with a floating-point stack and a bunch of F-prefixed words to deal with it.
I am wanting to keep things simple. Thus, I'm using a integer fixed-point representation of decimal numbers.
A global interpreter variable aptly named ``PRECISION`` contains a value between 0 and +inf (practically 15 is enough)
and represent the place of the decimal point.

I use float built-in type ``float`` and the ``math`` module to emulate converting back and forth (pun) from 
integer and float and to compute special functions.


Backlog
=======

Features
--------

* implement ['] and "compile," for the sake of completion, can't grasp how it works, though
* refactoring: reduce the number of primitives, aim to define compiling words as DEFINED_XT
  candidates: BEGIN, IF, ELSE, THEN, AGAIN, WHILE, REPEAT, UNTIL, DO, LOOP, [COMPILE] 
* test memory management (arrays & strings)

Documentation
-------------
* docstrings for runtime execution tokens


Bugs
----

* Interpreter variables addresses are hard-coded.


Integration
-----------
* add a pyproject.toml 
* automate testing with tox for 3.10, 3.11, 3.12 and 3.13
* add black, flake8, pylint and mypy steps
* add test coverage

References
==========

https://www.complang.tuwien.ac.at/forth/gforth/Docs-html/Review-_002d-elements-of-a-Forth-system.html#Review-_002d-elements-of-a-Forth-system
https://sifflez.org/lectures/ASE/C3.pdf
https://vfxforth.com/arena/ProgramForth.pdf
https://www.openbookproject.net/py4fun/forth/forth.html
https://www.complang.tuwien.ac.at/forth/gforth/Docs-html/Displaying-characters-and-strings.html#Displaying-characters-and-strings
