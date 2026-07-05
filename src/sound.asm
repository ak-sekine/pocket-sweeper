INCLUDE "hardware.inc"

SECTION "Sound WRAM", WRAM0

wSoundPlaybackActive::
    ds 1

SECTION "Sound", ROM0

Sound_Init::
    ld a, %10000000
    ldh [rAUDENA], a
    ld a, %01110111
    ldh [rAUDVOL], a
    ld a, %11111111
    ldh [rAUDTERM], a
    xor a
    ld [wSoundPlaybackActive], a
    ret

Sound_PlayTestBgm::
    ld hl, TestBgm
    call hUGE_init
    ld a, 1
    ld [wSoundPlaybackActive], a
    ret

Sound_Update::
    ld a, [wSoundPlaybackActive]
    and a
    ret z
    jp hUGE_dosound
