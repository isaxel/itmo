    .text
    .org     0x200

_start:
    movea.l  0x800, A7                            ; init stack pointer

    jsr      p_init_buffer                        ; fill 0x00..0x3F with '_'

    move.l   0, D6                                ; D6 <- unique word count = 0

    jsr      p_scan                               ; tokenize + count; D0 = status
    cmp.l    -1, D0                               ; -1 => domain error
    beq      L__domain
    cmp.l    -2, D0                               ; -2 => overflow (line too long)
    beq      L__overflow

    cmp.l    0, D6                                ; no words at all -> empty result
    bne      L__render
    jsr      p_emit_empty                         ; buffer[0] <- 0  (empty C-string)
    halt

L__render:
    jsr      p_build_result                       ; render counts; D0 = status
    cmp.l    -2, D0                               ; -2 => result overflow
    beq      L__overflow
    halt

L__domain:
    jsr      p_emit_minus_one                     ; output port 0x84 <- -1
    halt

L__overflow:
    jsr      p_fill_overflow                      ; buffer <- 0xCC bytes
    halt

p_init_buffer:
    movea.l  0x00, A0                             ; A0 <- buffer pointer
    move.l   0x40, D0                             ; D0 <- bytes remaining
    move.l   0x5F, D1                             ; D1 <- '_'

p_init_buffer__loop:
    cmp.l    0, D0
    beq      p_init_buffer__done
    move.b   D1, (A0)+                            ; *A0++ <- '_'
    sub.l    1, D0
    jmp      p_init_buffer__loop

p_init_buffer__done:
    rts

p_emit_empty:
    movea.l  0x00, A0
    move.l   0, D0
    move.b   D0, (A0)                             ; terminator at start
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
    movea.l  0x80, A0                             ; input port
    move.l   0, D5                                ; current key = empty
    move.l   0, D4                                ; current word length = 0
    move.l   0, D3                                ; chars consumed = 0
    move.l   0, D2                                ; sticky error status: 0 = ok

p_scan__next:
    move.l   (A0), D0                             ; D0 <- next char from input

    cmp.l    0x0A, D0                             ; newline -> end of line
    beq      p_scan__eol

    ; once an error is latched, just drain the rest of the line.
    cmp.l    0, D2
    bne      p_scan__next

    ; line-length overflow check: count this char, fail if > 0x3F
    add.l    1, D3
    cmp.l    0x40, D3                             ; 64 chars means len > 63
    blt      p_scan__inrange
    move.l   -2, D2                               ; latch overflow, keep draining
    jmp      p_scan__next

p_scan__inrange:
    cmp.l    0x20, D0
    beq      p_scan__sep
    cmp.l    0x2C, D0
    beq      p_scan__sep
    cmp.l    0x2E, D0
    beq      p_scan__sep

    move.l   D4, D1                               ; D1 <- current length
    add.l    1, D1                                ; shift index = len+1 (bytes)
    move.l   D1, D7                               ; D7 <- byte index
    asl.l    3, D7                                ; D7 <- bit shift = index*8
    and.l    0xFF, D0                             ; keep low byte of char only
    asl.l    D7, D0                               ; position the char
    or.l     D0, D5                               ; merge into key
    move.l   D1, D4                               ; len <- len+1

    cmp.l    3, D4                                ; length must stay <= 3
    ble      p_scan__next
    move.l   -1, D2                               ; latch domain error, keep draining
    jmp      p_scan__next

p_scan__sep:
    jsr      p_flush_word                         ; finalize current word (if any)
    cmp.l    -1, D0                               ; flush reported domain error?
    bne      p_scan__next
    move.l   -1, D2                               ; latch it, keep draining
    jmp      p_scan__next

p_scan__eol:
    cmp.l    0, D2
    bne      p_scan__report
    jsr      p_flush_word                         ; finalize trailing word (if any)
    cmp.l    -1, D0
    bne      p_scan__ok
    move.l   -1, D0                               ; domain error from final flush
    rts

p_scan__ok:
    move.l   0, D0                                ; success
    rts

p_scan__report:
    move.l   D2, D0                               ; return latched error (-1 or -2)
    rts

p_flush_word:
    cmp.l    0, D4                                ; empty word -> nothing to do
    bne      p_flush_word__go
    move.l   0, D0
    rts

p_flush_word__go:
    ; finalize key: place length in byte0
    move.l   D5, D1                               ; D1 <- chars
    or.l     D4, D1                               ; byte0 := length (chars use byte1..3)
    ; D1 is now the complete packed key
    jsr      p_lookup_or_add                      ; in D1=key ; out D0 status
    ; reset current word
    move.l   0, D5
    move.l   0, D4
    rts

p_lookup_or_add:
    move.l   D2, -(A7)                            ; preserve caller's D2
    move.l   D3, -(A7)                            ; preserve caller's D3 (char count)
    movea.l  0x100, A2                            ; word table base
    movea.l  0x140, A3                            ; count table base
    move.l   0, D2                                ; index = 0

p_lookup_or_add__scan:
    cmp.l    D6, D2                               ; index == count -> not found
    bge      p_lookup_or_add__append
    move.l   D2, D3                               ; D3 <- byte offset = index*4
    asl.l    2, D3
    move.l   0(A2,D3), D0                         ; D0 <- key[index] (indexed mode)
    cmp.l    D1, D0                               ; equal to current key?
    beq      p_lookup_or_add__hit
    add.l    1, D2                                ; index++
    jmp      p_lookup_or_add__scan

p_lookup_or_add__hit:
    move.l   0(A3,D3), D0                         ; D0 <- count[index]
    add.l    1, D0
    move.l   D0, 0(A3,D3)                         ; count[index]++
    move.l   0, D0                                ; success
    jmp      p_lookup_or_add__done

p_lookup_or_add__append:
    cmp.l    12, D6                               ; already 12 unique -> error
    bge      p_lookup_or_add__domain
    move.l   D2, D3                               ; D3 <- byte offset = index*4
    asl.l    2, D3
    move.l   D1, 0(A2,D3)                         ; key[index] <- new key
    move.l   1, D0
    move.l   D0, 0(A3,D3)                         ; count[index] <- 1
    add.l    1, D6                                ; unique++
    move.l   0, D0
    jmp      p_lookup_or_add__done

p_lookup_or_add__domain:
    move.l   -1, D0

p_lookup_or_add__done:
    move.l   (A7)+, D3                            ; restore caller's D3
    move.l   (A7)+, D2                            ; restore caller's D2
    rts

p_build_result:
    movea.l  0x140, A2                            ; count table base
    movea.l  0x00, A1                             ; buffer write pointer
    movea.l  0x84, A6                             ; output port (stream result bytes)
    move.l   0, D2                                ; index = 0
    move.l   0x40, D3                             ; remaining bytes in buffer

p_build_result__loop:
    cmp.l    D6, D2                               ; done all words?
    bge      p_build_result__term

    cmp.l    0, D2                                ; need a space separator first?
    beq      p_build_result__num                  ; no space before first number
    ; write a separating space (needs >=1 byte and still room for NUL later)
    cmp.l    1, D3
    ble      p_build_result__ovf                  ; not enough room
    move.l   0x20, D0
    move.b   D0, (A1)+                            ; space -> buffer
    move.l   D0, (A6)                             ; space -> output port 0x84
    sub.l    1, D3

p_build_result__num:
    move.l   D2, D1                               ; D1 <- byte offset = index*4
    asl.l    2, D1
    move.l   0(A2,D1), D0                         ; D0 <- count[index] (indexed mode)
    jsr      p_put_uint                           ; render D0 -> buffer ; updates A1,D3
    cmp.l    -2, D0                               ; overflow during render?
    beq      p_build_result__ovf
    add.l    1, D2                                ; index++
    jmp      p_build_result__loop

p_build_result__term:
    cmp.l    0, D3                                ; need 1 byte for NUL terminator
    beq      p_build_result__ovf
    move.l   0, D0
    move.b   D0, (A1)                             ; write NUL terminator
    move.l   0, D0
    rts

p_build_result__ovf:
    move.l   -2, D0
    rts

p_put_uint:
    move.l   D6, -(A7)                            ; preserve D6 across this routine
    move.l   D2, -(A7)                            ; preserve caller's D2 (index)
    move.l   D5, -(A7)                            ; scratch save
    move.l   0, D2                                ; digit count = 0

    ; special-case zero
    cmp.l    0, D0
    bne      p_put_uint__extract
    move.l   0, D1
    move.l   D1, -(A7)                            ; push single digit '0' value
    add.l    1, D2
    jmp      p_put_uint__emit

p_put_uint__extract:
    cmp.l    0, D0
    beq      p_put_uint__emit
    move.l   D0, D5                               ; D5 <- value
    move.l   10, D1
    div.l    D1, D0                               ; D0 <- value / 10
    ; remainder = value - (value/10)*10
    move.l   D0, D1                               ; D1 <- quotient
    mul.l    10, D1                               ; D1 <- quotient*10
    move.l   D5, D7                               ; D7 <- original value
    sub.l    D1, D7                               ; D7 <- remainder digit
    move.l   D7, -(A7)                            ; push digit
    add.l    1, D2                                ; digit count++
    jmp      p_put_uint__extract

p_put_uint__emit:
    cmp.l    0, D2                                ; all digits emitted?
    beq      p_put_uint__done
    ; ensure space: need 1 byte now and still leave >=1 for NUL -> D3 > 1
    cmp.l    1, D3
    ble      p_put_uint__ovf
    move.l   (A7)+, D1                            ; pop a digit value
    add.l    0x30, D1                             ; to ASCII '0'..'9'
    move.b   D1, (A1)+                            ; digit -> buffer
    move.l   D1, (A6)                             ; digit -> output port 0x84
    sub.l    1, D3
    sub.l    1, D2
    jmp      p_put_uint__emit

p_put_uint__done:
    move.l   (A7)+, D5                            ; restore scratch
    move.l   (A7)+, D2                            ; restore caller's D2
    move.l   (A7)+, D6                            ; restore D6
    move.l   0, D0
    rts

p_put_uint__ovf:
    ; pop any remaining pushed digits to keep the stack balanced
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