INCLUDE "hardware.inc"
INCLUDE "graphics.inc"

SECTION "Graphics", ROM0

GraphicsInit::
    call DisableLCD
    call LoadTiles
    call DrawTitleScreen
    call ClearOAM

    xor a
    ldh [rSCX], a
    ldh [rSCY], a
    ; BG palette: color numbers 0-3 map from lightest to darkest.
    ld a, %11100100
    ldh [rBGP], a
    ; Cursor Sprite palette: color 0 is transparent, color 1 is lightest.
    ld a, %11100001
    ldh [rOBP0], a
    ld a, LCDCF_ON | LCDCF_BG8000 | LCDCF_OBJON | LCDCF_BG9800 | LCDCF_BGON
    ldh [rLCDC], a
    ret

Graphics_ResetPlayfield::
    call Graphics_ResetPlayfieldLCDOff
    jp EnableLCD

Graphics_ResetPlayfieldLCDOff::
    call DisableLCD
    call LoadGameTiles
    call ClearOAM
    call ClearBGMap
    call DrawStatusBar
    call DrawClosedBoard
    jp ClearEndMessageRow

Graphics_DrawTitleScreen::
    call DisableLCD
    call LoadTiles
    call ClearOAM
    call DrawTitleScreen
    jp EnableLCD

Graphics_DrawDifficultySelectScreen::
    call DisableLCD
    call ClearOAM
    call ClearBGMap
    call DrawDifficultySelectScreen
    jp EnableLCD

Graphics_DisableLCD::
    jp DisableLCD

Graphics_EnableLCD::
    jp EnableLCD

Graphics_ClearOAM::
    jp ClearOAM

Graphics_DrawStatusBar::
    jp DrawStatusBar

DisableLCD:
    ldh a, [rLCDC]
    bit 7, a
    ret z
.waitVBlank:
    ldh a, [rLY]
    cp 144
    jr c, .waitVBlank
    xor a
    ldh [rLCDC], a
    ret

LoadTiles:
    call LoadGameTiles

    ld hl, TitleTiles
    ld de, $8000 + TILE_TITLE_BASE * TILE_BYTES
    ld bc, TitleTilesEnd - TitleTiles
    call CopyBytes

    ret

LoadGameTiles:
    ld hl, Tiles
    ld de, $8000
    ld bc, GAME_BG_TILE_COUNT * TILE_BYTES
    call CopyBytes

    ; TILE_BLANK is a generated blank background tile used to clear the tile map.
    xor a
    ld hl, $8000 + TILE_BLANK * TILE_BYTES
    ld b, TILE_BYTES
.clearBlankTile:
    ld [hli], a
    dec b
    jr nz, .clearBlankTile

    ld hl, Tiles + GAME_BG_TILE_COUNT * TILE_BYTES
    ld de, $8000 + TILE_PAUSE_TOP_LEFT * TILE_BYTES
    ld bc, PAUSE_FRAME_TILE_COUNT * TILE_BYTES
    call CopyBytes

    ; Font tiles are ordered as 0-9, colon, A-Z, then project symbols.
    ld hl, FontTiles
    ld de, $8000 + TILE_DIGIT_0 * TILE_BYTES
    ld bc, FONT_UI_BEFORE_CURSOR_TILE_COUNT * TILE_BYTES
    call CopyBytes

    ; Cursor Sprite tiles are stored separately from BG tiles at VRAM tiles 52-55.
    ld hl, CursorTiles
    ld de, $8000 + TILE_CURSOR_TL * TILE_BYTES
    ld bc, CURSOR_TILE_COUNT * TILE_BYTES
    call CopyBytes

    ld hl, FontTiles + FONT_UI_BEFORE_CURSOR_TILE_COUNT * TILE_BYTES
    ld de, $8000 + TILE_LETTER_U * TILE_BYTES
    ld bc, FONT_UI_AFTER_CURSOR_TILE_COUNT * TILE_BYTES
    jp CopyBytes

EnableLCD:
    ld a, LCDCF_ON | LCDCF_BG8000 | LCDCF_OBJON | LCDCF_BG9800 | LCDCF_BGON
    ldh [rLCDC], a
    ret

CopyBytes:
    ld a, [hli]
    ld [de], a
    inc de
    dec bc
    ld a, b
    or c
    jr nz, CopyBytes
    ret

ClearBGMap:
    ld hl, BG_MAP
    ld bc, BG_MAP_WIDTH * BG_MAP_HEIGHT
    ld a, TILE_BLANK
.loop:
    ld [hli], a
    dec bc
    ld d, a
    ld a, b
    or c
    ld a, d
    jr nz, .loop
    ret

ClearOAM:
    xor a
    ld hl, OAM_BASE
    ld b, OAM_SIZE
.loop:
    ld [hli], a
    dec b
    jr nz, .loop
    ret

DrawTitleScreen:
    call ClearBGMap
    call DrawTitleLogo
    call DrawPressStartText
    jp DrawCopyrightText

DrawDifficultySelectScreen:
    ld hl, SelectLevelText
    ld de, BG_MAP + DIFFICULTY_TITLE_Y * BG_MAP_WIDTH + DIFFICULTY_TITLE_X
    call DrawText

    ld hl, EasyText
    ld de, BG_MAP + DIFFICULTY_EASY_Y * BG_MAP_WIDTH + DIFFICULTY_ITEM_X
    call DrawText

    ld hl, NormalText
    ld de, BG_MAP + DIFFICULTY_NORMAL_Y * BG_MAP_WIDTH + DIFFICULTY_ITEM_X
    call DrawText

    ld hl, HardText
    ld de, BG_MAP + DIFFICULTY_HARD_Y * BG_MAP_WIDTH + DIFFICULTY_ITEM_X
    call DrawText

    ld hl, BG_MAP + DIFFICULTY_EASY_Y * BG_MAP_WIDTH + DIFFICULTY_CURSOR_X
    ld a, TILE_BLACK_RIGHT_TRIANGLE
    ld [hl], a
    ret

DrawTitleLogo:
    ld hl, TitleMap
    ld de, BG_MAP + TITLE_LOGO_BG_Y * BG_MAP_WIDTH + TITLE_LOGO_BG_X
    ld b, TITLE_LOGO_HEIGHT
.row:
    ld c, TITLE_LOGO_WIDTH
.column:
    ld a, [hli]
    add TILE_TITLE_BASE
    ld [de], a
    inc de
    dec c
    jr nz, .column
    ld a, e
    add BG_MAP_WIDTH - TITLE_LOGO_WIDTH
    ld e, a
    jr nc, .nextRow
    inc d
.nextRow:
    dec b
    jr nz, .row
    ret

DrawPressStartText:
    ld hl, PressStartText
    ld de, BG_MAP + TITLE_PRESS_START_Y * BG_MAP_WIDTH + TITLE_PRESS_START_X
    jp DrawText

DrawCopyrightText:
    ld hl, CopyrightText
    ld de, BG_MAP + TITLE_COPYRIGHT_Y * BG_MAP_WIDTH + TITLE_COPYRIGHT_X
    jp DrawText

DrawText:
    ld a, [hli]
    cp $FF
    ret z
    ld [de], a
    inc de
    jr DrawText

DrawStatusBar:
    ld hl, StatusText
    ld de, BG_MAP + STATUS_BG_Y * BG_MAP_WIDTH + STATUS_BG_X
.loop:
    ld a, [hli]
    cp $FF
    ret z
    ld [de], a
    inc de
    jr .loop

DrawClosedBoard:
    call GetBoardBgAddress
    ld a, [wBoardHeight]
    ld b, a
.row:
    ld a, [wBoardWidth]
    ld c, a
    ld a, TILE_CLOSED
.column:
    ld [hli], a
    dec c
    jr nz, .column
    ld a, [wBoardWidth]
    ld e, a
    ld a, BG_MAP_WIDTH
    sub e
    ld e, a
    ld d, 0
    add hl, de
    dec b
    jr nz, .row
    ret

GetBoardBgAddress:
    ld hl, BG_MAP
    ld a, [wBoardBgY]
    and a
    jr z, .addX
.addRow:
    ld bc, BG_MAP_WIDTH
    add hl, bc
    dec a
    jr nz, .addRow
.addX:
    ld a, [wBoardBgX]
    ld c, a
    ld b, 0
    add hl, bc
    ret

ClearEndMessageRow:
    ld hl, BG_MAP + 14 * BG_MAP_WIDTH
    ld b, 20
    ld a, TILE_BLANK
.loop:
    ld [hli], a
    dec b
    jr nz, .loop
    ret

ClearTitleScreenAreas::
    call ClearTitleLogoArea
    call ClearPressStartRow
    jp ClearCopyrightRow

ClearTitleLogoArea:
    ld hl, BG_MAP + TITLE_LOGO_BG_Y * BG_MAP_WIDTH + TITLE_LOGO_BG_X
    ld b, TITLE_LOGO_HEIGHT
.row:
    ld c, TITLE_LOGO_WIDTH
    ld a, TILE_BLANK
.column:
    ld [hli], a
    dec c
    jr nz, .column
    ld de, BG_MAP_WIDTH - TITLE_LOGO_WIDTH
    add hl, de
    dec b
    jr nz, .row
    ret

ClearPressStartRow:
    ld hl, BG_MAP + TITLE_PRESS_START_Y * BG_MAP_WIDTH
    jr ClearTitleTextRow

ClearCopyrightRow:
    ld hl, BG_MAP + TITLE_COPYRIGHT_Y * BG_MAP_WIDTH

ClearTitleTextRow:
    ld b, TITLE_TEXT_ROW_WIDTH
    ld a, TILE_BLANK
.loop:
    ld [hli], a
    dec b
    jr nz, .loop
    ret

StatusText:
    db TILE_LETTER_A + 'M' - 'A', TILE_LETTER_A + 'I' - 'A'
    db TILE_LETTER_A + 'N' - 'A', TILE_LETTER_A + 'E' - 'A'
    db TILE_COLON, TILE_DIGIT_0 + 0, TILE_DIGIT_0 + 0, TILE_DIGIT_0 + 0
    db TILE_BLANK
    db TILE_LETTER_A + 'T' - 'A', TILE_LETTER_A + 'I' - 'A'
    db TILE_LETTER_A + 'M' - 'A', TILE_LETTER_A + 'E' - 'A'
    db TILE_COLON, TILE_DIGIT_0 + 0, TILE_DIGIT_0 + 0, TILE_DIGIT_0 + 0, $FF

PressStartText:
    db TILE_LETTER_A + 'P' - 'A', TILE_LETTER_A + 'R' - 'A'
    db TILE_LETTER_A + 'E' - 'A', TILE_LETTER_A + 'S' - 'A'
    db TILE_LETTER_A + 'S' - 'A', TILE_BLANK
    db TILE_LETTER_A + 'S' - 'A', TILE_LETTER_A + 'T' - 'A'
    db TILE_LETTER_A + 'A' - 'A', TILE_LETTER_A + 'R' - 'A'
    db TILE_LETTER_A + 'T' - 'A', $FF

SelectLevelText:
    db TILE_LETTER_A + 'S' - 'A', TILE_LETTER_A + 'E' - 'A'
    db TILE_LETTER_A + 'L' - 'A', TILE_LETTER_A + 'E' - 'A'
    db TILE_LETTER_A + 'C' - 'A', TILE_LETTER_A + 'T' - 'A'
    db TILE_BLANK
    db TILE_LETTER_A + 'L' - 'A', TILE_LETTER_A + 'E' - 'A'
    db TILE_LETTER_V, TILE_LETTER_A + 'E' - 'A'
    db TILE_LETTER_A + 'L' - 'A', $FF

EasyText:
    db TILE_LETTER_A + 'E' - 'A', TILE_LETTER_A + 'A' - 'A'
    db TILE_LETTER_A + 'S' - 'A', TILE_LETTER_Y, $FF

NormalText:
    db TILE_LETTER_A + 'N' - 'A', TILE_LETTER_A + 'O' - 'A'
    db TILE_LETTER_A + 'R' - 'A', TILE_LETTER_A + 'M' - 'A'
    db TILE_LETTER_A + 'A' - 'A', TILE_LETTER_A + 'L' - 'A', $FF

HardText:
    db TILE_LETTER_A + 'H' - 'A', TILE_LETTER_A + 'A' - 'A'
    db TILE_LETTER_A + 'R' - 'A', TILE_LETTER_A + 'D' - 'A', $FF

CopyrightText:
    db TILE_COPYRIGHT
    db TILE_DIGIT_0 + 2, TILE_DIGIT_0 + 0, TILE_DIGIT_0 + 2, TILE_DIGIT_0 + 6
    db TILE_BLANK
    db TILE_LETTER_A + 'A' - 'A', TILE_LETTER_A + 'K' - 'A'
    db TILE_LETTER_A + 'I' - 'A', TILE_LETTER_A + 'H' - 'A'
    db TILE_LETTER_A + 'I' - 'A', TILE_LETTER_A + 'R' - 'A'
    db TILE_LETTER_A + 'O' - 'A', TILE_BLANK
    db TILE_LETTER_A + 'S' - 'A', TILE_LETTER_A + 'E' - 'A'
    db TILE_LETTER_A + 'K' - 'A', TILE_LETTER_A + 'I' - 'A'
    db TILE_LETTER_A + 'N' - 'A', TILE_LETTER_A + 'E' - 'A', $FF

SECTION "Graphics Data", ROM0

Tiles:
    INCBIN "obj/tiles.2bpp"
TilesEnd:

FontTiles:
    INCBIN "obj/font.2bpp"

CursorTiles:
    INCBIN "obj/cursor.2bpp"

TitleTiles:
    INCBIN "obj/title_tiles.2bpp"
TitleTilesEnd:

TitleMap:
    INCBIN "obj/title_map.bin"
