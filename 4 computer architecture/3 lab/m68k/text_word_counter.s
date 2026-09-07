.text
    .org     0x200

_start:
    movea.l  0x800, A7
    jsr      p_init_buffer
    move.l   0, D6
    jsr      p_scan
    cmp.l    -1, D0
    beq      L__domain
    cmp.l    -2, D0
    beq      L__overflow
    cmp.l    0, D6
    bne      L__render
    jsr      p_emit_empty
    halt

L__render:
    jsr      p_build_result
    cmp.l    -2, D0
    beq      L__overflow
    halt

L__domain:
    jsr      p_emit_minus_one
    halt

L__overflow:
    jsr      p_fill_overflow
    halt

p_init_buffer:
    movea.l  0x00, A0
    move.l   0x40, D0
    move.l   0x5F, D1

p_init_buffer__loop:
    cmp.l    0, D0
    beq      p_init_buffer__done
    move.b   D1, (A0)+
    sub.l    1, D0
    jmp      p_init_buffer__loop

p_init_buffer__done:
    rts

p_emit_empty:
    movea.l  0x00, A0
    move.l   0, D0
    move.b   D0, (A0)
    rts

p_emit_minus_one:
    movea.l  0x84, A1
    move.l   -1, D0
    move.l   D0, (A1)
    rts

p_fill_overflow:
    movea.l  0x00, A0
    move.l   0x40, D0
    move.l   0xCC, D1

p_fill_overflow__loop:
    cmp.l    0, D0
    beq      p_fill_overflow__done
    move.b   D1, (A0)+
    sub.l    1, D0
    jmp      p_fill_overflow__loop

p_fill_overflow__done:
    rts

p_scan:
    movea.l  0x80, A0
    move.l   0, D5
    move.l   0, D4
    move.l   0, D3
    move.l   0, D2

p_scan__next:
    move.l   (A0), D0
    cmp.l    0x0A, D0
    beq      p_scan__eol
    cmp.l    0, D2
    bne      p_scan__next
    add.l    1, D3
    cmp.l    0x40, D3
    blt      p_scan__inrange
    move.l   -2, D2
    jmp      p_scan__next

p_scan__inrange:
    cmp.l    0x20, D0
    beq      p_scan__sep
    cmp.l    0x2C, D0
    beq      p_scan__sep
    cmp.l    0x2E, D0
    beq      p_scan__sep
    move.l   D4, D1
    add.l    1, D1
    move.l   D1, D7
    asl.l    3, D7
    and.l    0xFF, D0
    asl.l    D7, D0
    or.l     D0, D5
    move.l   D1, D4
    cmp.l    3, D4
    ble      p_scan__next
    move.l   -1, D2
    jmp      p_scan__next

p_scan__sep:
    jsr      p_flush_word
    cmp.l    -1, D0
    bne      p_scan__next
    move.l   -1, D2
    jmp      p_scan__next

p_scan__eol:
    cmp.l    0, D2
    bne      p_scan__report
    jsr      p_flush_word
    cmp.l    -1, D0
    bne      p_scan__ok
    move.l   -1, D0
    rts

p_scan__ok:
    move.l   0, D0
    rts

p_scan__report:
    move.l   D2, D0
    rts

p_flush_word:
    cmp.l    0, D4
    bne      p_flush_word__go
    move.l   0, D0
    rts

p_flush_word__go:
    move.l   D5, D1
    or.l     D4, D1
    jsr      p_lookup_or_add
    move.l   0, D5
    move.l   0, D4
    rts

p_lookup_or_add:
    move.l   D2, -(A7)
    move.l   D3, -(A7)
    movea.l  0x100, A2
    movea.l  0x140, A3
    move.l   0, D2

p_lookup_or_add__scan:
    cmp.l    D6, D2
    bge      p_lookup_or_add__append
    move.l   D2, D3
    asl.l    2, D3
    move.l   0(A2,D3), D0
    cmp.l    D1, D0
    beq      p_lookup_or_add__hit
    add.l    1, D2
    jmp      p_lookup_or_add__scan

p_lookup_or_add__hit:
    move.l   0(A3,D3), D0
    add.l    1, D0
    move.l   D0, 0(A3,D3)
    move.l   0, D0
    jmp      p_lookup_or_add__done

p_lookup_or_add__append:
    cmp.l    12, D6
    bge      p_lookup_or_add__domain
    move.l   D2, D3
    asl.l    2, D3
    move.l   D1, 0(A2,D3)
    move.l   1, D0
    move.l   D0, 0(A3,D3)
    add.l    1, D6
    move.l   0, D0
    jmp      p_lookup_or_add__done

p_lookup_or_add__domain:
    move.l   -1, D0

p_lookup_or_add__done:
    move.l   (A7)+, D3
    move.l   (A7)+, D2
    rts

p_build_result:
    movea.l  0x140, A2
    movea.l  0x00, A1
    movea.l  0x84, A6
    move.l   0, D2
    move.l   0x40, D3

p_build_result__loop:
    cmp.l    D6, D2
    bge      p_build_result__term
    cmp.l    0, D2
    beq      p_build_result__num
    cmp.l    1, D3
    ble      p_build_result__ovf
    move.l   0x20, D0
    move.b   D0, (A1)+
    move.l   D0, (A6)
    sub.l    1, D3

p_build_result__num:
    move.l   D2, D1
    asl.l    2, D1
    move.l   0(A2,D1), D0
    jsr      p_put_uint
    cmp.l    -2, D0
    beq      p_build_result__ovf
    add.l    1, D2
    jmp      p_build_result__loop

p_build_result__term:
    cmp.l    0, D3
    beq      p_build_result__ovf
    move.l   0, D0
    move.b   D0, (A1)
    move.l   0, D0
    rts

p_build_result__ovf:
    move.l   -2, D0
    rts

p_put_uint:
    move.l   D6, -(A7)
    move.l   D2, -(A7)
    move.l   D5, -(A7)
    move.l   0, D2
    cmp.l    0, D0
    bne      p_put_uint__extract
    move.l   0, D1
    move.l   D1, -(A7)
    add.l    1, D2
    jmp      p_put_uint__emit

p_put_uint__extract:
    cmp.l    0, D0
    beq      p_put_uint__emit
    move.l   D0, D5
    move.l   10, D1
    div.l    D1, D0
    move.l   D0, D1
    mul.l    10, D1
    move.l   D5, D7
    sub.l    D1, D7
    move.l   D7, -(A7)
    add.l    1, D2
    jmp      p_put_uint__extract

p_put_uint__emit:
    cmp.l    0, D2
    beq      p_put_uint__done
    cmp.l    1, D3
    ble      p_put_uint__ovf
    move.l   (A7)+, D1
    add.l    0x30, D1
    move.b   D1, (A1)+
    move.l   D1, (A6)
    sub.l    1, D3
    sub.l    1, D2
    jmp      p_put_uint__emit

p_put_uint__done:
    move.l   (A7)+, D5
    move.l   (A7)+, D2
    move.l   (A7)+, D6
    move.l   0, D0
    rts

p_put_uint__ovf:
    cmp.l    0, D2
    beq      p_put_uint__ovf_restore
    move.l   (A7)+, D1
    sub.l    1, D2
    jmp      p_put_uint__ovf

p_put_uint__ovf_restore:
    move.l   (A7)+, D5
    move.l   (A7)+, D2
    move.l   (A7)+, D6
    move.l   -2, D0
    rts