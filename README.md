Notes
=====

This my second or third attempt at writing a Forth pseudo-compiler in Python.

I took most of my inspiration from Chris Meyers and Fred Obermann article (https://www.openbookproject.net/py4fun/forth/forth.html)


Backlog
=======

Features
--------
* implement fixed points functions hyperbolic trig, inv of trig/hyperbolic
* implement ['] and "compile," for the sake of completion, can't grasp how it works, though
* refactoring: reduce the number of primitives, aim to define compiling words as DEFINED_XT
  candidates: BEGIN, IF, ELSE, THEN, AGAIN, WHILE, REPEAT, UNTIL, DO, LOOP, [COMPILE] 
* test memory management (arrays & strings)

Documentation
-------------
* docstrings for runtime execution tokens


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
