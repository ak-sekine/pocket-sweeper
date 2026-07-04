INCLUDE "graphics.inc"
INCLUDE "input.inc"

; Development-only mine placement check. Set to 0 before final release.
DEF DEBUG_SHOW_MINES EQU 0

DEF CELL_MINE_BIT    EQU 4

SECTION "Board WRAM", WRAM0

wBoard::
    ds BOARD_MAX_CELLS
wMinesPlaced::
    ds 1
IF DEBUG_SHOW_MINES
wDebugMinesDrawPending::
    ds 1
wDebugDrawRow::
    ds 1
ENDC
wBoardGenX::
    ds 1
wBoardGenY::
    ds 1
wBoardCellCount::
    ds 1

SECTION "Board", ROM0

Board_Init::
    xor a
    ld [wMinesPlaced], a
IF DEBUG_SHOW_MINES
    ld [wDebugMinesDrawPending], a
    ld [wDebugDrawRow], a
ENDC
    call Board_UpdateCellCount
    xor a
    ld hl, wBoard
    ld b, BOARD_MAX_CELLS
.clear:
    ld [hli], a
    dec b
    jr nz, .clear
    ret

Board_UpdateCellCount:
    ld a, [wBoardHeight]
    and a
    jr z, .zero
    ld b, a
    xor a
    ld c, a
    ld a, [wBoardWidth]
    and a
    jr z, .zero
.addRow:
    add c
    ld c, a
    ld a, b
    dec a
    ld b, a
    jr z, .done
    ld a, [wBoardWidth]
    jr .addRow
.done:
    ld a, c
    ld [wBoardCellCount], a
    ret
.zero:
    xor a
    ld [wBoardCellCount], a
    ret

Board_UpdateDebugDisplay::
IF DEBUG_SHOW_MINES
    ld a, [wDebugMinesDrawPending]
    and a
    ret z
    call Board_DebugDrawNextRow
    ld a, [wDebugDrawRow]
    ld b, a
    ld a, [wBoardHeight]
    cp b
    ret c
    ret nz
    xor a
    ld [wDebugMinesDrawPending], a
    ld [wDebugDrawRow], a
ENDC
    ret

Board_PlaceMinesIfNeeded::
    ld a, [wMinesPlaced]
    and a
    ret nz

    call Board_UpdateCellCount
    call Random_SeedFromFrameCounter
    call Board_GetCursorIndex
    ld e, a
    ld a, [wMineCount]
    ld d, a

.placeNext:
    call Board_RandomCellIndex
    cp e
    jr z, .placeNext

    ld c, a
    ld b, 0
    ld hl, wBoard
    add hl, bc
    bit CELL_MINE_BIT, [hl]
    jr nz, .placeNext

    set CELL_MINE_BIT, [hl]
    dec d
    jr nz, .placeNext

    call Board_GenerateNumbers

    ld a, 1
    ld [wMinesPlaced], a
IF DEBUG_SHOW_MINES
    ld [wDebugMinesDrawPending], a
    xor a
    ld [wDebugDrawRow], a
ENDC
    ret

Board_GenerateNumbers:
    ld hl, wBoard
    ld a, [wBoardCellCount]
    ld b, a
.clearNumbers:
    ld a, [hl]
    and $F0
    ld [hli], a
    dec b
    jr nz, .clearNumbers

    ld hl, wBoard
    xor a
    ld [wBoardGenY], a
.row:
    xor a
    ld [wBoardGenX], a
.column:
    bit CELL_MINE_BIT, [hl]
    jr z, .nextCell
    push hl
    call Board_IncrementMineNeighbors
    pop hl
.nextCell:
    inc hl
    ld a, [wBoardGenX]
    inc a
    ld [wBoardGenX], a
    ld b, a
    ld a, [wBoardWidth]
    cp b
    jr nz, .column
    ld a, [wBoardGenY]
    inc a
    ld [wBoardGenY], a
    ld b, a
    ld a, [wBoardHeight]
    cp b
    jr nz, .row
    ret

Board_IncrementMineNeighbors:
    ld a, [wBoardGenY]
    and a
    jr z, .sameRow
    dec a
    call Board_IncrementNeighborRow

.sameRow:
    ld a, [wBoardGenY]
    call Board_IncrementSideNeighbors

    ld a, [wBoardGenY]
    inc a
    ld b, a
    ld a, [wBoardHeight]
    cp b
    ret z
    ld a, b
    call Board_IncrementNeighborRow
    ret

Board_IncrementNeighborRow:
    ld d, a
    ld a, [wBoardGenX]
    and a
    jr z, .center
    dec a
    ld e, a
    push de
    call Board_IncrementCellAtXY
    pop de
.center:
    ld a, [wBoardGenX]
    ld e, a
    push de
    call Board_IncrementCellAtXY
    pop de
    ld a, [wBoardGenX]
    inc a
    ld b, a
    ld a, [wBoardWidth]
    cp b
    ret z
    ld a, b
    ld e, a
    jp Board_IncrementCellAtXY

Board_IncrementSideNeighbors:
    ld d, a
    ld a, [wBoardGenX]
    and a
    jr z, .right
    dec a
    ld e, a
    push de
    call Board_IncrementCellAtXY
    pop de
.right:
    ld a, [wBoardGenX]
    inc a
    ld b, a
    ld a, [wBoardWidth]
    cp b
    ret z
    ld a, b
    ld e, a
    jp Board_IncrementCellAtXY

; Increments the low-nibble number at (E, D) unless that cell is a mine.
; Clobbers: AF, BC, HL
Board_IncrementCellAtXY:
    call Board_XYToIndex
    ld c, a
    ld b, 0
    ld hl, wBoard
    add hl, bc
    ld a, [hl]
    bit CELL_MINE_BIT, a
    ret nz
    ld b, a
    and $0F
    cp 8
    ret nc
    inc a
    ld c, a
    ld a, b
    and $F0
    or c
    ld [hl], a
    ret

; Converts board coordinates (E=x, D=y) to A = y * wBoardWidth + x.
; Clobbers: AF, B, C, H
Board_XYToIndex:
    ld a, [wBoardWidth]
    ld c, a
    ld a, d
    ld b, a
    xor a
.rowLoop:
    ld h, a
    ld a, b
    and a
    ld a, h
    jr z, .addX
    add c
    dec b
    jr .rowLoop
.addX:
    add e
    ret

; Returns the current cursor cell index in A.
; Clobbers: AF, B, C, D
Board_GetCursorIndex:
    ld a, [wBoardWidth]
    ld d, a
    ld a, [wCursorY]
    ld b, a
    xor a
    ld c, a
.addRow:
    ld a, b
    and a
    jr z, .addX
    ld a, c
    add d
    ld c, a
    dec b
    jr .addRow
.addX:
    ld a, [wCursorX]
    add c
    ret

; Returns a random board cell index within the current board cell count in A.
; Rejection keeps the distribution simple and bounded for valid cells.
Board_RandomCellIndex:
    call Random_Next
    and $7F
    ld b, a
    ld a, [wBoardCellCount]
    ld c, a
    ld a, b
    cp c
    jr nc, Board_RandomCellIndex
    ret

IF DEBUG_SHOW_MINES
; Debug-only: reveal one row per VBlank so VRAM writes stay bounded.
Board_DebugDrawNextRow:
    ld a, [wDebugDrawRow]
    ld d, a
    ld e, 0
    call Board_XYToIndex
    ld c, a
    ld b, 0
    ld hl, wBoard
    add hl, bc

    ld de, BG_MAP
    ld a, [wBoardBgY]
    ld b, a
    and a
    jr z, .addDebugOriginX
.advanceOriginRow:
    ld a, e
    add BG_MAP_WIDTH
    ld e, a
    jr nc, .nextOriginRow
    inc d
.nextOriginRow:
    dec b
    jr nz, .advanceOriginRow
.addDebugOriginX:
    ld a, [wBoardBgX]
    add e
    ld e, a
    jr nc, .originDone
    inc d
.originDone:
    ld a, [wDebugDrawRow]
    ld b, a
    and a
    jr z, .draw
.advanceBgRow:
    ld a, e
    add BG_MAP_WIDTH
    ld e, a
    jr nc, .nextBgRow
    inc d
.nextBgRow:
    dec b
    jr nz, .advanceBgRow
.draw:
    ld a, [wBoardWidth]
    ld c, a
.column:
    ld a, [hl]
    bit CELL_MINE_BIT, [hl]
    jr z, .drawNumber
    ld a, TILE_MINE
    jr .store
.drawNumber:
    and $0F
    add TILE_OPEN_0
.store:
    ld [de], a
    inc hl
    inc de
    dec c
    jr nz, .column
    ld a, [wDebugDrawRow]
    inc a
    ld [wDebugDrawRow], a
    ret
ENDC
