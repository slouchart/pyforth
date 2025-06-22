\ Forth is written in Forth

: variable create 0 , ;
: constant create , does> @ ;
: cells 1 * ;

variable base \ usually takes the zeroth address
: binary 2 base ! ;
: decimal 10 base ! ;
: hex 16 base ! ;
decimal

-1 constant true
0 constant false

: rot >r swap r> swap ;
: nip swap drop ;
: tuck swap over ;
: 1+ 1 + ;
: 1- 1 - ;
: 2* 1 LSHIFT ;
: 2/ 1 RSHIFT ;
: negate 0 swap - ;
: abs dup 0 < if negate then ;
: min 2dup < if else swap then drop ;
: max 2dup > if else swap then drop ;
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
: ?dup dup 0<> if dup then ;

: do [compile] 2>r postpone begin ; immediate
: unloop 2r> 2drop ;
: loop
  [compile] r>
  [compile] 1+
  [compile] r@
  [compile] swap
  [compile] dup
  [compile] >r
  [compile] =
  postpone until
  [compile] unloop
; immediate

: _unwind_loop r> r> ;
: _rewind_loop rot rot >r >r ;
: i r@ ;
: j _unwind_loop i _rewind_loop ;
: k _unwind_loop j _rewind_loop ;

: cr 10 emit ;
: bl 32 ;
: space bl emit ;
: spaces dup 0<> if 0 do space loop then ;

: .s stack? if depth 0 do depth i - 1- pick . bl emit loop cr then ;
: clear begin stack? while drop repeat ;

: fabs abs ;
: fsincos dup fsin swap fcos ;
: /mod 2dup / >r mod r> swap ;
: m* * ;
: */ * / ;
: */mod * /mod ;

\ Aliases because in Python int and char are the same
: c, , ;
: c@ @ ;
: c! ! ;

: count ( c-addr0 -- c-addr1 u )
  \ no need to implement in Python
   dup @
   swap 1+
   swap
;
