INCLUDE "hardware.inc"
INCLUDE "input.inc"

SECTION "Input WRAM", WRAM0

wJoyCurrent::
    ds 1
wJoyPrevious::
    ds 1
wJoyPressed::
    ds 1

SECTION "Input", ROM0

; Clears all input state. Call once before the first Input_Update.
Input_Init::
    xor a
    ld [wJoyCurrent], a
    ld [wJoyPrevious], a
    ld [wJoyPressed], a
    ld a, P1F_GET_NONE
    ldh [rP1], a
    ret

; Polls both joypad groups and updates the frame input state.
; Output bits use the PAD_* masks from input.inc. Hardware active-low
; values are converted to active-high values before being stored.
; Clobbers: AF, BC
Input_Update::
    ld a, [wJoyCurrent]
    ld [wJoyPrevious], a

    ld a, P1F_GET_DPAD
    ldh [rP1], a
    ldh a, [rP1]
    ldh a, [rP1]
    cpl
    and $0F
    ld c, a

    ld a, P1F_GET_BUTTONS
    ldh [rP1], a
    ldh a, [rP1]
    ldh a, [rP1]
    cpl
    and $0F
    swap a
    or c
    ld c, a
    ld [wJoyCurrent], a

    ld a, P1F_GET_NONE
    ldh [rP1], a

    ld a, [wJoyPrevious]
    cpl
    and c
    ld [wJoyPressed], a
    ret
