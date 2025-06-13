\ Forth is written in Forth

: variable create 0 , ;
: constant create , does> @ ;
: cells 1 * ;

variable base
: binary 2 base ! ;
: decimal 10 base ! ;
: hex 16 base ! ;
decimal

-1 constant true
0 constant false

variable precision
5 precision !


: dup 0 pick ;
: over 1 pick ;
: rot >r swap r> swap ;
: 1+ 1 + ;
: negate 0 swap - ;
: abs dup 0 < if negate then ;
: 2dup over over ;
: 2drop drop drop ;
: 2swap rot >r rot r> ;
: 2>r swap >r >r ;
: 2r> r> r> swap ;
: 2over 2>r 2dup 2r> 2swap ;
: <> = invert ;
: 0< 0 < ;
: 0= 0 = ;
: 0> 0 > ;
: 0<> 0= invert ;
: >= < invert ;
: <= > invert ;

: stack? depth 0<> ;

: cr 10 emit ;
: bl 32 ;
: space bl emit ;
: spaces dup 0<> if 0 do space loop then ;

: .s depth 0> if depth 0 do i pick . bl emit loop then ;
: clear begin stack? while drop repeat ;
