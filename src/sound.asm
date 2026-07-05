INCLUDE "hardware.inc"

SECTION "Sound WRAM", WRAM0

wSoundPlaybackActive::
    ds 1
wSoundSfxCurrentId::
    ds 1
wSoundSfxStepPtr::
    ds 2
wSoundSfxWaitFrames::
    ds 1
wSoundSfxPriority::
    ds 1
wSoundSfxChannelKind::
    ds 1
wSoundSfxStepsRemaining::
    ds 1
wSoundSfxActive::
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
    ld [wSoundSfxCurrentId], a
    ld [wSoundSfxStepPtr], a
    ld [wSoundSfxStepPtr + 1], a
    ld [wSoundSfxWaitFrames], a
    ld [wSoundSfxPriority], a
    ld [wSoundSfxChannelKind], a
    ld [wSoundSfxStepsRemaining], a
    ld [wSoundSfxActive], a
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
    jr z, .updateSfx
    call hUGE_dosound
.updateSfx:
    jp Sound_UpdateSfx

Sound_UpdateSfx:
    ld a, [wSoundSfxActive]
    and a
    ret z
    ret
