    .data

input_addr:      .word  0x80
output_addr:     .word  0x84

sum_hi:          .word  0x00               ; старшие 32 бита
sum_lo:          .word  0x00               ; младшие 32 бита
cur:             .word  0x00               ; текущее слово
const_1:         .word  0x01               ; +1
minus_1:         .word  0xffff_ffff        ; -1

    .text

_start:
    load_imm     0
    store        sum_hi
    store        sum_lo

loop:
    load         input_addr
    load_acc
    store        cur

    beqz         done

    clc
    load         sum_lo
    add          cur
    store        sum_lo

    bcc          sign_extend
    load         sum_hi
    add          const_1
    store        sum_hi

sign_extend:
    load         cur
    bgez         loop
    load         sum_hi
    add          minus_1                    ; hi <- hi + 0xFFFFFFFF  (= hi - 1)
    store        sum_hi
    jmp          loop

done:
    load         sum_hi
    store_ind    output_addr
    load         sum_lo
    store_ind    output_addr
    halt