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

Sound_PlaySfx::
    ld c, a
    add a
    ld e, a
    ld d, 0
    ld hl, SfxTable
    add hl, de
    ld a, [hl+]
    ld e, a
    ld a, [hl]
    ld d, a
    ld h, d
    ld l, e

    ld a, [hl+]
    ld b, a
    ld a, [hl+]
    ld e, a

    ld a, [wSoundSfxActive]
    and a
    jr z, .start
    ld a, [wSoundSfxPriority]
    cp e
    ret nc

    push hl
    push bc
    push de
    call Sound_UnmuteCurrentSfxChannel
    pop de
    pop bc
    pop hl

.start:
    ld a, c
    ld [wSoundSfxCurrentId], a
    ld a, e
    ld [wSoundSfxPriority], a
    ld a, b
    ld [wSoundSfxChannelKind], a
    ld a, [hl+]
    ld [wSoundSfxStepsRemaining], a
    inc hl
    ld a, l
    ld [wSoundSfxStepPtr], a
    ld a, h
    ld [wSoundSfxStepPtr + 1], a
    xor a
    ld [wSoundSfxWaitFrames], a
    ld a, 1
    ld [wSoundSfxActive], a
    ld a, [wSoundSfxChannelKind]
    ld b, a
    ld c, 1
    jp hUGE_mute_channel

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
    ld a, [wSoundSfxWaitFrames]
    and a
    jr z, .nextStep
    dec a
    ld [wSoundSfxWaitFrames], a
    ret

.nextStep:
    ld a, [wSoundSfxStepsRemaining]
    and a
    jp z, Sound_StopSfx

    ld a, [wSoundSfxStepPtr]
    ld l, a
    ld a, [wSoundSfxStepPtr + 1]
    ld h, a

    ld a, [wSoundSfxChannelKind]
    cp SFX_CH_NOISE
    jr z, .noiseStep

    ld a, [hl+]
    ld b, a
    ld a, [hl+]
    ldh [rAUD1SWEEP], a
    ld a, [hl+]
    ldh [rAUD1LEN], a
    ld a, [hl+]
    ldh [rAUD1ENV], a
    ld a, [hl+]
    ldh [rAUD1LOW], a
    ld a, [hl+]
    ldh [rAUD1HIGH], a
    jr .finishStep

.noiseStep:
    ld a, [hl+]
    ld b, a
    ld a, [hl+]
    ldh [rAUD4LEN], a
    ld a, [hl+]
    ldh [rAUD4ENV], a
    ld a, [hl+]
    ldh [rAUD4POLY], a
    ld a, [hl+]
    ldh [rAUD4GO], a

.finishStep:
    ld a, l
    ld [wSoundSfxStepPtr], a
    ld a, h
    ld [wSoundSfxStepPtr + 1], a
    ld a, b
    ld [wSoundSfxWaitFrames], a
    ld a, [wSoundSfxStepsRemaining]
    dec a
    ld [wSoundSfxStepsRemaining], a
    ret

Sound_StopSfx:
    ld a, [wSoundSfxActive]
    and a
    jr z, .clear
    call Sound_UnmuteCurrentSfxChannel

.clear:
    xor a
    ld [wSoundSfxCurrentId], a
    ld [wSoundSfxStepPtr], a
    ld [wSoundSfxStepPtr + 1], a
    ld [wSoundSfxWaitFrames], a
    ld [wSoundSfxPriority], a
    ld [wSoundSfxChannelKind], a
    ld [wSoundSfxStepsRemaining], a
    ld [wSoundSfxActive], a
    ret

Sound_UnmuteCurrentSfxChannel:
    ld a, [wSoundSfxChannelKind]
    ld b, a
    ld c, 0
    jp hUGE_mute_channel
