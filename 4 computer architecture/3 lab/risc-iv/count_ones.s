.text

    
_start:
    lui   sp, 1
    lw    a0, 0x80(zero)

    jal   ra, popcount
    sw    a0, 0x84(zero)
    halt


popcount:
    beqz  a0, popcount_base

popcount_rec:
    addi  sp, sp, -8             ; выдел кадр стека
    sw    ra, 0(sp)
    andi  t0, a0, 1              ; t0 <- младш бит n
    sw    t0, 4(sp)
    srli  a0, a0, 1
    jal   ra, popcount
    lw    t0, 4(sp)
    add   a0, a0, t0
    lw    ra, 0(sp)
    addi  sp, sp, 8              ; освобод кадр стека
    jr    ra

popcount_base:
    mv    a0, zero
    jr    ra