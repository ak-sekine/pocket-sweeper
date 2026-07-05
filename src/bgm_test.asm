INCLUDE "hUGE.inc"

SECTION "Test BGM", ROM0

TestBgm::
    db 6
    dw TestBgmOrderCount
    dw TestBgmOrder1, TestBgmOrder2, TestBgmOrder3, TestBgmOrder4
    dw TestBgmDutyInstruments, TestBgmWaveInstruments, TestBgmNoiseInstruments
    dw TestBgmRoutines
    dw TestBgmWaves

TestBgmOrderCount:
    db 2

TestBgmOrder1:
    dw TestBgmPattern1
TestBgmOrder2:
    dw TestBgmPattern2
TestBgmOrder3:
    dw TestBgmPattern3
TestBgmOrder4:
    dw TestBgmPattern4

TestBgmPattern1:
    dn C_4, 1, $000
    REPT 7
        dn ___, 0, $000
    ENDR
    dn E_4, 1, $000
    REPT 7
        dn ___, 0, $000
    ENDR
    dn G_4, 1, $000
    REPT 7
        dn ___, 0, $000
    ENDR
    dn C_5, 1, $000
    REPT 7
        dn ___, 0, $000
    ENDR
    REPT 32
        dn ___, 0, $000
    ENDR

TestBgmPattern2:
    dn C_3, 2, $000
    REPT 15
        dn ___, 0, $000
    ENDR
    dn G_3, 2, $000
    REPT 15
        dn ___, 0, $000
    ENDR
    REPT 32
        dn ___, 0, $000
    ENDR

TestBgmPattern3:
    REPT 64
        dn ___, 0, $000
    ENDR

TestBgmPattern4:
    REPT 64
        dn ___, 0, $000
    ENDR

TestBgmDutyInstruments:
TestBgmSquareLead:
    db 8
    db 128
    db 243
    dw 0
    db 128

TestBgmSquareBass:
    db 8
    db 128
    db 211
    dw 0
    db 128

TestBgmWaveInstruments:

TestBgmNoiseInstruments:

TestBgmRoutines:
    REPT 16
        dw TestBgmRoutineRet
    ENDR

TestBgmRoutineRet:
    ret

TestBgmWaves:
