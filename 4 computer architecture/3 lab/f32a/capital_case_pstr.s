    .data

buffer:     .byte  '________________________________'

prev_alpha: .word  0          \ prev char was a letter
low_f:      .word  0          \ cur char is 'a'..'z'
up_f:       .word  0          \ cur char is 'A'..'Z'
cur:        .word  0
slen:       .word  0

    .text
    .org 0x100

_start:
    0 !p prev_alpha
    0x80 b!
    0x1 a!

read_loop:
    @b
    dup -10 + if read_done
    proc_title
    0x5f5f5f00 xor !+
    a -33 + if overflow
    read_loop ;

read_done:
    drop
    a -1 + !p slen

    @p buffer -256 and
    @p slen xor
    !p buffer

    @p slen if program_end

    0x84 b!
    0x1 a!
    @p slen -1 + >r

output_loop:
    @+ 0xff and !b
    next output_loop

program_end:
    halt

overflow:
    0x84 b!
    -858993460 !b             \ 0xCCCCCCCC
    halt

proc_title:
    !p cur

    @p cur -97 + -if proc_title__ge_a
    0 !p low_f
    proc_title__low_done ;

proc_title__ge_a:
    @p cur -123 + -if proc_title__not_low   \ cur > 'z'
    1 !p low_f
    proc_title__low_done ;

proc_title__not_low:
    0 !p low_f

proc_title__low_done:
    @p cur -65 + -if proc_title__ge_aa
    0 !p up_f
    proc_title__up_done ;

proc_title__ge_aa:
    @p cur -91 + -if proc_title__not_up      \ cur > 'Z'
    1 !p up_f
    proc_title__up_done ;

proc_title__not_up:
    0 !p up_f

proc_title__up_done:
    @p low_f if proc_title__try_up           \ not lower -> maybe upper
    @p prev_alpha if proc_title__make_up
    proc_title__finish ;

proc_title__make_up:
    @p cur -32 + !p cur
    proc_title__finish ;

proc_title__try_up:
    @p up_f if proc_title__finish            \ not a letter -> keep
    @p prev_alpha if proc_title__finish
    @p cur 32 + !p cur

proc_title__finish:
    @p low_f @p up_f xor !p prev_alpha
    @p cur
    ;