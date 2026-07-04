INCLUDE "graphics.inc"
INCLUDE "input.inc"

DEF BOARD_QUEUE_CAPACITY EQU BOARD_MAX_CELLS
DEF CELL_MINE_BIT    EQU 4
DEF CELL_OPENED_BIT  EQU 5
DEF CELL_FLAG_BIT    EQU 6
DEF GAME_OVER_TEXT_LEN EQU 9
DEF GAME_OVER_BG_X     EQU 5
DEF GAME_OVER_BG_Y     EQU 14
DEF CLEAR_TEXT_LEN     EQU 5
DEF CLEAR_BG_X         EQU 7
DEF CLEAR_BG_Y         EQU GAME_OVER_BG_Y
DEF STATUS_MINE_DIGITS_X EQU STATUS_BG_X + 5
DEF STATUS_TIME_DIGITS_X EQU STATUS_BG_X + 14
DEF ELAPSED_FRAMES_PER_SECOND EQU 60
DEF ELAPSED_TIME_MAX_HIGH EQU 3
DEF ELAPSED_TIME_MAX_LOW  EQU 231
DEF DEBUG_INITIAL_TIME EQU 0
IF DEBUG_INITIAL_TIME > 999
DEF DEBUG_INITIAL_TIME_CLAMPED EQU 999
ELSE
DEF DEBUG_INITIAL_TIME_CLAMPED EQU DEBUG_INITIAL_TIME
ENDC
DEF DEBUG_INITIAL_TIME_LOW EQU DEBUG_INITIAL_TIME_CLAMPED & $FF
DEF DEBUG_INITIAL_TIME_HIGH EQU DEBUG_INITIAL_TIME_CLAMPED >> 8
DEF PAUSE_MENU_X       EQU 1
DEF PAUSE_MENU_Y       EQU 6
DEF PAUSE_MENU_WIDTH   EQU 19
DEF PAUSE_MENU_HEIGHT  EQU 7
DEF PAUSE_MENU_RESUME  EQU 0
DEF PAUSE_MENU_RESTART EQU 1
DEF PAUSE_MENU_TITLE   EQU 2
DEF DIFFICULTY_EASY    EQU 0
DEF DIFFICULTY_NORMAL  EQU 1
DEF DIFFICULTY_HARD    EQU 2
DEF DIFFICULTY_EASY_WIDTH    EQU 8
DEF DIFFICULTY_EASY_HEIGHT   EQU 8
DEF DIFFICULTY_EASY_MINES    EQU 10
DEF DIFFICULTY_NORMAL_WIDTH  EQU 9
DEF DIFFICULTY_NORMAL_HEIGHT EQU 9
DEF DIFFICULTY_NORMAL_MINES  EQU 15
DEF DIFFICULTY_HARD_WIDTH    EQU 10
DEF DIFFICULTY_HARD_HEIGHT   EQU 10
DEF DIFFICULTY_HARD_MINES    EQU 20
DEF SCREEN_TILE_WIDTH        EQU 20

SECTION "Game WRAM", WRAM0

wGameDrawQueue::
    ds BOARD_QUEUE_CAPACITY
wGameDrawTileQueue::
    ds BOARD_QUEUE_CAPACITY
wGameDrawHead::
    ds 1
wGameDrawTail::
    ds 1
wOpenQueueX::
    ds BOARD_QUEUE_CAPACITY
wOpenQueueY::
    ds BOARD_QUEUE_CAPACITY
wOpenQueueHead::
    ds 1
wOpenQueueTail::
    ds 1
wGameWorkIndex::
    ds 1
wGameWorkCell::
    ds 1
wGameDrawTileValue::
    ds 1
wGameCenterX::
    ds 1
wGameCenterY::
    ds 1
wGameTriggeredMineIndex::
    ds 1
wGameMessageDrawIndex::
    ds 1
wGameOver::
    ds 1
wGameClear::
    ds 1
wGameRestartDrawPending::
    ds 1
wGameTitleDrawPending::
    ds 1
wGameDifficultySelectDrawPending::
    ds 1
wGameDifficultyCursorDrawPending::
    ds 1
wGamePauseDrawPending::
    ds 1
wGamePauseCursorDrawPending::
    ds 1
wGameResumeDrawPending::
    ds 1
wGameFlagCount::
    ds 1
wGameMineDrawPending::
    ds 1
wGameElapsedSecondsLow::
    ds 1
wGameElapsedSecondsHigh::
    ds 1
wGameElapsedFrameCount::
    ds 1
wGameElapsedRunning::
    ds 1
wGameTimeDrawPending::
    ds 1
wGameTitle::
    ds 1
wGameDifficultySelect::
    ds 1
wGameCurrentDifficulty::
    ds 1
wBoardWidth::
    ds 1
wBoardHeight::
    ds 1
wBoardBgX::
    ds 1
wBoardBgY::
    ds 1
wMineCount::
    ds 1
wGameDifficultySelection::
    ds 1
wGamePreviousDifficultySelection::
    ds 1
wGamePaused::
    ds 1
wGamePauseSelection::
    ds 1
wGamePreviousPauseSelection::
    ds 1

SECTION "Game", ROM0

Game_InitTitle::
    xor a
    ld [wGameDrawHead], a
    ld [wGameDrawTail], a
    ld [wOpenQueueHead], a
    ld [wOpenQueueTail], a
    ld [wGameMessageDrawIndex], a
    ld [wGameOver], a
    ld [wGameClear], a
    ld [wGameRestartDrawPending], a
    ld [wGameTitleDrawPending], a
    ld [wGameDifficultySelectDrawPending], a
    ld [wGameDifficultyCursorDrawPending], a
    ld [wGamePauseDrawPending], a
    ld [wGamePauseCursorDrawPending], a
    ld [wGameResumeDrawPending], a
    ld [wGameFlagCount], a
    ld [wGameMineDrawPending], a
    ld [wGameElapsedSecondsLow], a
    ld [wGameElapsedSecondsHigh], a
    ld [wGameElapsedFrameCount], a
    ld [wGameElapsedRunning], a
    ld [wGameTimeDrawPending], a
    ld [wGameDifficultySelect], a
    ld [wGameCurrentDifficulty], a
    ld [wBoardWidth], a
    ld [wBoardHeight], a
    ld [wBoardBgX], a
    ld [wBoardBgY], a
    ld [wMineCount], a
    ld [wGameDifficultySelection], a
    ld [wGamePreviousDifficultySelection], a
    ld [wGamePaused], a
    ld [wGamePauseSelection], a
    ld [wGamePreviousPauseSelection], a
    inc a
    ld [wGameTitle], a
    ret

Game_Init::
    xor a
    ld [wGameDrawHead], a
    ld [wGameDrawTail], a
    ld [wOpenQueueHead], a
    ld [wOpenQueueTail], a
    ld [wGameMessageDrawIndex], a
    ld [wGameOver], a
    ld [wGameClear], a
    ld [wGameRestartDrawPending], a
    ld [wGameTitleDrawPending], a
    ld [wGameDifficultySelectDrawPending], a
    ld [wGameDifficultyCursorDrawPending], a
    ld [wGamePauseDrawPending], a
    ld [wGamePauseCursorDrawPending], a
    ld [wGameResumeDrawPending], a
    ld [wGameFlagCount], a
    ld [wGameMineDrawPending], a
    ld a, DEBUG_INITIAL_TIME_LOW
    ld [wGameElapsedSecondsLow], a
    ld a, DEBUG_INITIAL_TIME_HIGH
    ld [wGameElapsedSecondsHigh], a
    xor a
    ld [wGameElapsedFrameCount], a
    ld [wGameElapsedRunning], a
    ld [wGameTimeDrawPending], a
    ld [wGameTitle], a
    ld [wGameDifficultySelect], a
    ld [wGameDifficultySelection], a
    ld [wGamePreviousDifficultySelection], a
    ld [wGamePaused], a
    ld [wGamePauseSelection], a
    ld [wGamePreviousPauseSelection], a
    ret

Game_UpdateDisplay::
    ld a, [wGameTitleDrawPending]
    and a
    jr z, .checkDifficultySelectDraw

    xor a
    ld [wGameTitleDrawPending], a
    jp Graphics_DrawTitleScreen

.checkDifficultySelectDraw:
    ld a, [wGameDifficultySelectDrawPending]
    and a
    jr z, .checkDifficultyCursorDraw

    xor a
    ld [wGameDifficultySelectDrawPending], a
    jp Graphics_DrawDifficultySelectScreen

.checkDifficultyCursorDraw:
    ld a, [wGameDifficultyCursorDrawPending]
    and a
    jr z, .checkRestartDraw

    xor a
    ld [wGameDifficultyCursorDrawPending], a
    jp Game_UpdateDifficultySelectCursor

.checkRestartDraw:
    ld a, [wGameResumeDrawPending]
    and a
    jr z, .checkPauseDraw

    xor a
    ld [wGameResumeDrawPending], a
    jp Game_RedrawPlayfieldAfterPause

.checkPauseDraw:
    ld a, [wGamePauseDrawPending]
    and a
    jr z, .checkRestartDrawPending

    xor a
    ld [wGamePauseDrawPending], a
    call Graphics_DisableLCD
    call Graphics_ClearOAM
    call Game_DrawPauseMenu
    jp Graphics_EnableLCD

.checkRestartDrawPending:
    ld a, [wGamePauseCursorDrawPending]
    and a
    jr z, .checkRestartDrawPendingFlag

    xor a
    ld [wGamePauseCursorDrawPending], a
    jp Game_UpdatePauseMenuCursor

.checkRestartDrawPendingFlag:
    ld a, [wGameRestartDrawPending]
    and a
    jr z, .updateQueuedCell

    ld a, [wGamePaused]
    and a
    ret nz

    xor a
    ld [wGameRestartDrawPending], a
    call Graphics_ResetPlayfieldLCDOff
    call Game_UpdateMineDisplay
    call Game_UpdateTimeDisplay
    jp Graphics_EnableLCD

.updateQueuedCell:
    ld a, [wGamePaused]
    and a
    ret nz

    ld a, [wGameMineDrawPending]
    and a
    jr z, .checkTimeDraw

    xor a
    ld [wGameMineDrawPending], a
    jp Game_UpdateMineDisplay

.checkTimeDraw:
    ld a, [wGameTimeDrawPending]
    and a
    jr z, .checkDrawQueue

    xor a
    ld [wGameTimeDrawPending], a
    jp Game_UpdateTimeDisplay

.checkDrawQueue:
    ld a, [wGameDrawHead]
    ld b, a
    ld a, [wGameDrawTail]
    cp b
    jp z, Game_UpdateEndMessage

    ld a, b
    ld c, a
    ld b, 0
    ld hl, wGameDrawQueue
    add hl, bc
    ld a, [hl]
    ld [wGameWorkIndex], a
    ld hl, wGameDrawTileQueue
    add hl, bc
    ld a, [hl]
    ld [wGameWorkCell], a

    ld a, [wGameDrawHead]
    inc a
    ld [wGameDrawHead], a

    call Game_GetBGAddressForWorkIndex
    ld a, [wGameWorkCell]
    and a
    jr nz, .useQueuedTile
    push hl
    call Game_GetTileForWorkIndex
    pop hl
    jr .storeTile
.useQueuedTile:
    dec a
.storeTile:
    ld [hl], a
    ret

Game_UpdateEndMessage:
    ld a, [wGameOver]
    and a
    jr z, .checkClear

    ld a, [wGameMessageDrawIndex]
    cp GAME_OVER_TEXT_LEN
    ret nc

    ld c, a
    ld b, 0
    ld hl, GameOverText
    add hl, bc
    ld a, [hl]
    ld hl, BG_MAP + GAME_OVER_BG_Y * BG_MAP_WIDTH + GAME_OVER_BG_X
    add hl, bc
    ld [hl], a

    ld a, [wGameMessageDrawIndex]
    inc a
    ld [wGameMessageDrawIndex], a
    ret

.checkClear:
    ld a, [wGameClear]
    and a
    ret z

    ld a, [wGameMessageDrawIndex]
    cp CLEAR_TEXT_LEN
    ret nc

    ld c, a
    ld b, 0
    ld hl, ClearText
    add hl, bc
    ld a, [hl]
    ld hl, BG_MAP + CLEAR_BG_Y * BG_MAP_WIDTH + CLEAR_BG_X
    add hl, bc
    ld [hl], a

    ld a, [wGameMessageDrawIndex]
    inc a
    ld [wGameMessageDrawIndex], a
    ret

Game_HandleInput::
    ld a, [wGameTitle]
    and a
    jr z, .checkEnded

    ld a, [wJoyPressed]
    and PAD_START
    ret z
    jp Game_EnterDifficultySelectFromTitle

.checkEnded:
    ld a, [wGameDifficultySelect]
    and a
    jp nz, Game_HandleDifficultySelectInput

    call Game_IsEnded
    jr z, .handlePlaying

    ld a, [wJoyPressed]
    and PAD_START
    ret z
    jp Game_ReturnToTitleAfterEnd

.handlePlaying:
    ld a, [wGamePaused]
    and a
    jp nz, Game_HandlePauseInput

    ld a, [wJoyPressed]
    and PAD_START
    jr z, .checkOpen
    jp Game_OpenPauseMenu

.checkOpen:
    ld a, [wJoyPressed]
    and PAD_A
    jr z, .checkFlag

    call Game_GetCursorIndex
    ld [wGameWorkIndex], a
    call Board_PlaceMinesIfNeeded
    call Game_OpenWorkIndex
    call Game_IsEnded
    ret nz
    call Game_CheckClear
    ret

.checkFlag:
    ld a, [wJoyPressed]
    and PAD_B
    ret z
    jp Game_ToggleCursorFlag

Game_OpenPauseMenu:
    xor a
    ld [wGameDrawHead], a
    ld [wGameDrawTail], a
    ld [wOpenQueueHead], a
    ld [wOpenQueueTail], a
    ld [wGamePauseSelection], a
    ld [wGamePreviousPauseSelection], a
    inc a
    ld [wGamePaused], a
    ld [wGamePauseDrawPending], a
    ret

Game_HandleDifficultySelectInput:
    ld a, [wJoyPressed]
    and PAD_B
    jp nz, Game_ReturnToTitleFromDifficultySelect

    ld a, [wJoyPressed]
    and PAD_UP
    jr z, .checkDown

    ld a, [wGameDifficultySelection]
    ld [wGamePreviousDifficultySelection], a
    and a
    jr z, .wrapUp
    dec a
    jr .storeSelection
.wrapUp:
    ld a, DIFFICULTY_HARD
    jr .storeSelection

.checkDown:
    ld a, [wJoyPressed]
    and PAD_DOWN
    jr z, .checkConfirm

    ld a, [wGameDifficultySelection]
    ld [wGamePreviousDifficultySelection], a
    cp DIFFICULTY_HARD
    jr z, .wrapDown
    inc a
    jr .storeSelection
.wrapDown:
    ld a, DIFFICULTY_EASY

.storeSelection:
    ld [wGameDifficultySelection], a
    ld a, 1
    ld [wGameDifficultyCursorDrawPending], a
    ret

.checkConfirm:
    ld a, [wJoyPressed]
    and PAD_A | PAD_START
    ret z
    jp Game_StartFromDifficultySelect

Game_HandlePauseInput:
    ld a, [wJoyPressed]
    and PAD_B
    jp nz, Game_ResumeFromPause

    ld a, [wJoyPressed]
    and PAD_UP
    jr z, .checkDown
    ld a, [wGamePauseSelection]
    and a
    ret z
    ld [wGamePreviousPauseSelection], a
    dec a
    ld [wGamePauseSelection], a
    ld a, 1
    ld [wGamePauseCursorDrawPending], a
    ret

.checkDown:
    ld a, [wJoyPressed]
    and PAD_DOWN
    jr z, .checkConfirm
    ld a, [wGamePauseSelection]
    cp PAUSE_MENU_TITLE
    ret nc
    ld [wGamePreviousPauseSelection], a
    inc a
    ld [wGamePauseSelection], a
    ld a, 1
    ld [wGamePauseCursorDrawPending], a
    ret

.checkConfirm:
    ld a, [wJoyPressed]
    and PAD_A | PAD_START
    ret z

    ld a, [wGamePauseSelection]
    cp PAUSE_MENU_RESTART
    jp z, Game_RestartFromPause
    cp PAUSE_MENU_TITLE
    jp z, Game_ReturnToTitleFromPause
    jp Game_ResumeFromPause

Game_ResumeFromPause:
    xor a
    ld [wGamePaused], a
    inc a
    ld [wGameResumeDrawPending], a
    ret

Game_RestartFromPause:
    ld a, [wGameCurrentDifficulty]
    push af
    call Game_Init
    pop af
    ld [wGameCurrentDifficulty], a
    call Game_ApplyCurrentDifficultySettings
    call Board_Init
    call Cursor_ResetPosition
    ld a, 1
    ld [wGameRestartDrawPending], a
    ret

Game_ReturnToTitleFromPause:
    call Game_InitTitle
    ld a, 1
    ld [wGameTitleDrawPending], a
    ret

Game_OpenWorkIndex:
    call Game_GetCellAddressForWorkIndex
    bit CELL_OPENED_BIT, [hl]
    ret nz
    bit CELL_FLAG_BIT, [hl]
    ret nz

    call Game_StartElapsedTime

    set CELL_OPENED_BIT, [hl]
    ld a, [hl]
    ld [wGameWorkCell], a
    bit CELL_MINE_BIT, a
    jp nz, Game_TriggerGameOver

    call Game_EnqueueDrawWorkIndexAuto

    ld a, [wGameWorkCell]
    and $0F
    ret nz

    call Game_InitOpenQueue
    ld a, [wCursorX]
    ld e, a
    ld a, [wCursorY]
    ld d, a
    call Game_EnqueueOpenXY
    jp Game_ProcessOpenQueue

Game_ProcessOpenQueue:
    ld a, [wOpenQueueHead]
    ld b, a
    ld a, [wOpenQueueTail]
    cp b
    ret z

    call Game_DequeueOpenXY
    call Game_OpenNeighborsOfCenter
    jr Game_ProcessOpenQueue

Game_OpenNeighborsOfCenter:
    ld a, [wGameCenterY]
    and a
    jr z, .sameRow
    dec a
    ld d, a
    call Game_OpenNeighborRow

.sameRow:
    ld a, [wGameCenterY]
    ld d, a
    call Game_OpenSideNeighbors

    ld a, [wGameCenterY]
    inc a
    ld b, a
    ld a, [wBoardHeight]
    cp b
    ret z
    ld d, b
    jp Game_OpenNeighborRow

Game_OpenNeighborRow:
    ld a, [wGameCenterX]
    and a
    jr z, .center
    dec a
    ld e, a
    push de
    call Game_TryOpenNeighbor
    pop de
.center:
    ld a, [wGameCenterX]
    ld e, a
    push de
    call Game_TryOpenNeighbor
    pop de
    ld a, [wGameCenterX]
    inc a
    ld b, a
    ld a, [wBoardWidth]
    cp b
    ret z
    ld e, b
    jp Game_TryOpenNeighbor

Game_OpenSideNeighbors:
    ld a, [wGameCenterX]
    and a
    jr z, .right
    dec a
    ld e, a
    push de
    call Game_TryOpenNeighbor
    pop de
.right:
    ld a, [wGameCenterX]
    inc a
    ld b, a
    ld a, [wBoardWidth]
    cp b
    ret z
    ld e, b
    jp Game_TryOpenNeighbor

Game_TryOpenNeighbor:
    ld a, [wBoardHeight]
    cp d
    ret z
    ret c
    ld a, [wBoardWidth]
    cp e
    ret z
    ret c
    call Game_XYToIndex
    ld [wGameWorkIndex], a
    call Game_GetCellAddressForWorkIndex
    bit CELL_OPENED_BIT, [hl]
    ret nz
    bit CELL_FLAG_BIT, [hl]
    ret nz
    bit CELL_MINE_BIT, [hl]
    ret nz

    set CELL_OPENED_BIT, [hl]
    ld a, [hl]
    ld [wGameWorkCell], a
    call Game_EnqueueDrawWorkIndexAuto

    ld a, [wGameWorkCell]
    and $0F
    ret nz
    jp Game_EnqueueOpenXY

Game_ToggleCursorFlag:
    call Game_GetCursorIndex
    ld [wGameWorkIndex], a
    call Game_GetCellAddressForWorkIndex
    bit CELL_OPENED_BIT, [hl]
    ret nz
    bit CELL_FLAG_BIT, [hl]
    jr nz, .clearFlag
    ld a, [wMineCount]
    ld b, a
    ld a, [wGameFlagCount]
    cp b
    ret nc

    set CELL_FLAG_BIT, [hl]
    ld a, [wGameFlagCount]
    inc a
    ld [wGameFlagCount], a
    ld a, 1
    ld [wGameMineDrawPending], a
    ld a, TILE_FLAG
    jr .draw

.clearFlag:
    res CELL_FLAG_BIT, [hl]
    ld a, [wGameFlagCount]
    and a
    jr z, .skipDecrementFlagCount
    dec a
    ld [wGameFlagCount], a
.skipDecrementFlagCount:
    ld a, 1
    ld [wGameMineDrawPending], a
    ld a, TILE_CLOSED

.draw:
    ld [wGameWorkCell], a
    jp Game_EnqueueDrawWorkIndexWithTile

Game_TriggerGameOver:
    ld a, 1
    ld [wGameOver], a

    xor a
    ld [wGameElapsedRunning], a
    ld [wGameDrawHead], a
    ld [wGameDrawTail], a
    ld [wGameMessageDrawIndex], a

    ld a, [wGameWorkIndex]
    ld [wGameTriggeredMineIndex], a
    xor a
    ld [wGameWorkIndex], a

.revealLoop:
    call Game_GetCellAddressForWorkIndex
    bit CELL_MINE_BIT, [hl]
    jr nz, .mineCell
    bit CELL_FLAG_BIT, [hl]
    jr nz, .wrongFlagCell
    jr .nextRevealCell

.mineCell:
    ld a, [wGameWorkIndex]
    ld b, a
    ld a, [wGameTriggeredMineIndex]
    cp b
    ld a, TILE_MINE
    jr nz, .enqueueRevealTile
    ld a, TILE_EXPLODED_MINE
    jr .enqueueRevealTile

.wrongFlagCell:
    ld a, TILE_WRONG_FLAG

.enqueueRevealTile:
    ld [wGameWorkCell], a
    call Game_EnqueueDrawWorkIndexWithTile

.nextRevealCell:
    ld a, [wGameWorkIndex]
    inc a
    ld [wGameWorkIndex], a
    ld b, a
    ld a, [wBoardCellCount]
    cp b
    ret z
    jr nc, .revealLoop
    ret

Game_IsOver::
    ld a, [wGameOver]
    and a
    ret

Game_IsEnded::
    ld a, [wGameOver]
    ld b, a
    ld a, [wGameClear]
    or b
    ld b, a
    ld a, [wGameRestartDrawPending]
    or b
    ret

Game_IsTitle::
    ld a, [wGameTitle]
    and a
    ret

Game_IsDifficultySelect::
    ld a, [wGameDifficultySelect]
    and a
    ret

Game_IsPaused::
    ld a, [wGamePaused]
    and a
    ret

Game_CheckClear:
    ld hl, wBoard
    ld a, [wBoardCellCount]
    ld b, a
    ld a, [wMineCount]
    ld c, a
    ld a, b
    sub c
    ld c, a
    ld e, 0
.checkCell:
    bit CELL_MINE_BIT, [hl]
    jr nz, .nextCell
    bit CELL_OPENED_BIT, [hl]
    jr z, .nextCell
    inc e
.nextCell:
    inc hl
    dec b
    jr nz, .checkCell
    ld a, e
    cp c
    jp z, Game_TriggerClear
    ret

Game_TriggerClear:
    ld a, 1
    ld [wGameClear], a

    xor a
    ld [wGameElapsedRunning], a
    xor a
    ld [wGameMessageDrawIndex], a
    ret

Game_RestartAfterEnd:
    call Board_Init
    call Cursor_ResetPosition
    call Game_Init
    ld a, 1
    ld [wGameRestartDrawPending], a
    ret

Game_ReturnToTitleAfterEnd:
    call Game_InitTitle
    ld a, 1
    ld [wGameTitleDrawPending], a
    ret

Game_EnterDifficultySelectFromTitle:
    xor a
    ld [wGameTitle], a
    ld [wGamePaused], a
    ld [wGameDifficultySelection], a
    ld [wGamePreviousDifficultySelection], a
    inc a
    ld [wGameDifficultySelect], a
    ld [wGameDifficultySelectDrawPending], a
    ret

Game_StartFromDifficultySelect:
    ld a, [wGameDifficultySelection]
    push af
    call Game_Init
    pop af
    ld [wGameCurrentDifficulty], a
    call Game_ApplyCurrentDifficultySettings
    call Board_Init
    call Cursor_ResetPosition
    ld a, 1
    ld [wGameRestartDrawPending], a
    ret

Game_ReturnToTitleFromDifficultySelect:
    call Game_InitTitle
    ld a, 1
    ld [wGameTitleDrawPending], a
    ret

Game_ApplyCurrentDifficultySettings:
    ld a, [wGameCurrentDifficulty]
    cp DIFFICULTY_NORMAL
    jr z, .normal
    cp DIFFICULTY_HARD
    jr z, .hard

    ld a, DIFFICULTY_EASY_WIDTH
    ld [wBoardWidth], a
    ld a, DIFFICULTY_EASY_HEIGHT
    ld [wBoardHeight], a
    ld a, DIFFICULTY_EASY_MINES
    ld [wMineCount], a
    jp Game_UpdateBoardBgOrigin

.normal:
    ld a, DIFFICULTY_NORMAL_WIDTH
    ld [wBoardWidth], a
    ld a, DIFFICULTY_NORMAL_HEIGHT
    ld [wBoardHeight], a
    ld a, DIFFICULTY_NORMAL_MINES
    ld [wMineCount], a
    jp Game_UpdateBoardBgOrigin

.hard:
    ld a, DIFFICULTY_HARD_WIDTH
    ld [wBoardWidth], a
    ld a, DIFFICULTY_HARD_HEIGHT
    ld [wBoardHeight], a
    ld a, DIFFICULTY_HARD_MINES
    ld [wMineCount], a
    jp Game_UpdateBoardBgOrigin

Game_UpdateBoardBgOrigin:
    ld a, SCREEN_TILE_WIDTH
    ld b, a
    ld a, [wBoardWidth]
    ld c, a
    ld a, b
    sub c
    srl a
    ld [wBoardBgX], a
    ld a, BOARD_BG_Y
    ld [wBoardBgY], a
    ret

Game_StartElapsedTime:
    ld a, [wGameElapsedRunning]
    and a
    ret nz

    inc a
    ld [wGameElapsedRunning], a
    xor a
    ld [wGameElapsedFrameCount], a
    ret

Game_UpdateElapsedTime::
    ld a, [wGamePaused]
    and a
    ret nz
    call Game_IsEnded
    ret nz
    ld a, [wGameElapsedRunning]
    and a
    ret z

    ld a, [wGameElapsedFrameCount]
    inc a
    cp ELAPSED_FRAMES_PER_SECOND
    jr nc, .oneSecondElapsed

    ld [wGameElapsedFrameCount], a
    ret

.oneSecondElapsed:
    xor a
    ld [wGameElapsedFrameCount], a
    jp Game_IncrementElapsedSecond

Game_IncrementElapsedSecond:
    ld a, [wGameElapsedSecondsHigh]
    cp ELAPSED_TIME_MAX_HIGH
    jr c, .increment
    jr nz, .atMax
    ld a, [wGameElapsedSecondsLow]
    cp ELAPSED_TIME_MAX_LOW
    jr c, .increment
.atMax:
    ret

.increment:
    ld hl, wGameElapsedSecondsLow
    inc [hl]
    jr nz, .markDrawPending
    inc hl
    inc [hl]
.markDrawPending:
    ld a, 1
    ld [wGameTimeDrawPending], a
    ret

Game_UpdateMineDisplay:
    ld hl, BG_MAP + STATUS_BG_Y * BG_MAP_WIDTH + STATUS_MINE_DIGITS_X
    ld a, TILE_DIGIT_0
    ld [hli], a

    ld a, [wMineCount]
    ld b, a
    ld a, [wGameFlagCount]
    ld c, a
    ld a, b
    sub c
    ld b, 0
.tensLoop:
    cp 10
    jr c, .storeDigits
    sub 10
    inc b
    jr .tensLoop
.storeDigits:
    ld c, a
    ld a, TILE_DIGIT_0
    add b
    ld [hli], a
    ld a, TILE_DIGIT_0
    add c
    ld [hl], a
    ret

Game_UpdateTimeDisplay:
    ld hl, BG_MAP + STATUS_BG_Y * BG_MAP_WIDTH + STATUS_TIME_DIGITS_X
    ld a, [wGameElapsedSecondsLow]
    ld l, a
    ld a, [wGameElapsedSecondsHigh]
    ld h, a
    ld b, 0
.hundredsLoop:
    ld a, h
    and a
    jr nz, .subtractHundred
    ld a, l
    cp 100
    jr c, .hundredsDone
.subtractHundred:
    ld a, l
    sub 100
    ld l, a
    ld a, h
    sbc a, 0
    ld h, a
    inc b
    jr .hundredsLoop

.hundredsDone:
    ld c, 0
    ld a, l
.tensLoop:
    cp 10
    jr c, .storeDigits
    sub 10
    inc c
    jr .tensLoop

.storeDigits:
    ld e, a
    ld hl, BG_MAP + STATUS_BG_Y * BG_MAP_WIDTH + STATUS_TIME_DIGITS_X
    ld a, TILE_DIGIT_0
    add b
    ld [hli], a
    ld a, TILE_DIGIT_0
    add c
    ld [hli], a
    ld a, TILE_DIGIT_0
    add e
    ld [hl], a
    ret

Game_DrawPauseMenu:
    call Game_ClearPauseMenu
    call Game_DrawPauseFrame

    ld de, BG_MAP + (PAUSE_MENU_Y + 1) * BG_MAP_WIDTH + PAUSE_MENU_X + 2
    ld hl, PauseResumeText
    ld c, PAUSE_MENU_RESUME
    call Game_DrawPauseMenuItem

    ld de, BG_MAP + (PAUSE_MENU_Y + 3) * BG_MAP_WIDTH + PAUSE_MENU_X + 2
    ld hl, PauseRestartText
    ld c, PAUSE_MENU_RESTART
    call Game_DrawPauseMenuItem

    ld de, BG_MAP + (PAUSE_MENU_Y + 5) * BG_MAP_WIDTH + PAUSE_MENU_X + 2
    ld hl, PauseBackToTitleText
    ld c, PAUSE_MENU_TITLE
    jp Game_DrawPauseMenuItem

Game_DrawPauseFrame:
    ld hl, BG_MAP + PAUSE_MENU_Y * BG_MAP_WIDTH + PAUSE_MENU_X
    ld a, TILE_PAUSE_TOP_LEFT
    ld [hli], a
    ld b, PAUSE_MENU_WIDTH - 2
    ld a, TILE_PAUSE_HORIZONTAL
.topRow:
    ld [hli], a
    dec b
    jr nz, .topRow
    ld a, TILE_PAUSE_TOP_RIGHT
    ld [hl], a

    ld hl, BG_MAP + (PAUSE_MENU_Y + 1) * BG_MAP_WIDTH + PAUSE_MENU_X
    call Game_DrawPauseFrameMiddleRow
    ld hl, BG_MAP + (PAUSE_MENU_Y + 2) * BG_MAP_WIDTH + PAUSE_MENU_X
    call Game_DrawPauseFrameMiddleRow
    ld hl, BG_MAP + (PAUSE_MENU_Y + 3) * BG_MAP_WIDTH + PAUSE_MENU_X
    call Game_DrawPauseFrameMiddleRow
    ld hl, BG_MAP + (PAUSE_MENU_Y + 4) * BG_MAP_WIDTH + PAUSE_MENU_X
    call Game_DrawPauseFrameMiddleRow
    ld hl, BG_MAP + (PAUSE_MENU_Y + 5) * BG_MAP_WIDTH + PAUSE_MENU_X
    call Game_DrawPauseFrameMiddleRow

    ld hl, BG_MAP + (PAUSE_MENU_Y + PAUSE_MENU_HEIGHT - 1) * BG_MAP_WIDTH + PAUSE_MENU_X
    ld a, TILE_PAUSE_BOTTOM_LEFT
    ld [hli], a
    ld b, PAUSE_MENU_WIDTH - 2
    ld a, TILE_PAUSE_HORIZONTAL
.bottomRow:
    ld [hli], a
    dec b
    jr nz, .bottomRow
    ld a, TILE_PAUSE_BOTTOM_RIGHT
    ld [hl], a
    ret

Game_DrawPauseFrameMiddleRow:
    ld a, TILE_PAUSE_VERTICAL
    ld [hli], a
    ld b, PAUSE_MENU_WIDTH - 2
    ld a, TILE_BLANK
.middleFill:
    ld [hli], a
    dec b
    jr nz, .middleFill
    ld a, TILE_PAUSE_VERTICAL
    ld [hl], a
    ret

Game_DrawPauseMenuItem:
    ld a, [wGamePauseSelection]
    cp c
    ld a, TILE_BLANK
    jr nz, .storeMarker
    ld a, TILE_BLACK_RIGHT_TRIANGLE
.storeMarker:
    ld [de], a
    inc de
    ld a, TILE_BLANK
    ld [de], a
    inc de
.textLoop:
    ld a, [hli]
    cp $FF
    ret z
    ld [de], a
    inc de
    jr .textLoop

Game_UpdatePauseMenuCursor:
    ld a, [wGamePreviousPauseSelection]
    call Game_GetPauseMenuCursorAddress
    ld a, TILE_BLANK
    ld [hl], a

    ld a, [wGamePauseSelection]
    call Game_GetPauseMenuCursorAddress
    ld a, TILE_BLACK_RIGHT_TRIANGLE
    ld [hl], a
    ret

Game_GetPauseMenuCursorAddress:
    cp PAUSE_MENU_RESTART
    jr z, .restart
    cp PAUSE_MENU_TITLE
    jr z, .title
    ld hl, BG_MAP + (PAUSE_MENU_Y + 1) * BG_MAP_WIDTH + PAUSE_MENU_X + 2
    ret
.restart:
    ld hl, BG_MAP + (PAUSE_MENU_Y + 3) * BG_MAP_WIDTH + PAUSE_MENU_X + 2
    ret
.title:
    ld hl, BG_MAP + (PAUSE_MENU_Y + 5) * BG_MAP_WIDTH + PAUSE_MENU_X + 2
    ret

Game_UpdateDifficultySelectCursor:
    ld a, [wGamePreviousDifficultySelection]
    call Game_GetDifficultyCursorAddress
    ld a, TILE_BLANK
    ld [hl], a

    ld a, [wGameDifficultySelection]
    call Game_GetDifficultyCursorAddress
    ld a, TILE_BLACK_RIGHT_TRIANGLE
    ld [hl], a
    ret

Game_GetDifficultyCursorAddress:
    cp DIFFICULTY_NORMAL
    jr z, .normal
    cp DIFFICULTY_HARD
    jr z, .hard
    ld hl, BG_MAP + DIFFICULTY_EASY_Y * BG_MAP_WIDTH + DIFFICULTY_CURSOR_X
    ret
.normal:
    ld hl, BG_MAP + DIFFICULTY_NORMAL_Y * BG_MAP_WIDTH + DIFFICULTY_CURSOR_X
    ret
.hard:
    ld hl, BG_MAP + DIFFICULTY_HARD_Y * BG_MAP_WIDTH + DIFFICULTY_CURSOR_X
    ret

Game_ClearPauseMenu:
    ld hl, BG_MAP + PAUSE_MENU_Y * BG_MAP_WIDTH + PAUSE_MENU_X
    ld b, PAUSE_MENU_HEIGHT
.row:
    ld c, PAUSE_MENU_WIDTH
    ld a, TILE_BLANK
.column:
    ld [hli], a
    dec c
    jr nz, .column
    ld de, BG_MAP_WIDTH - PAUSE_MENU_WIDTH
    add hl, de
    dec b
    jr nz, .row
    ret

Game_RedrawPlayfieldAfterPause:
    call Graphics_DisableLCD
    call Game_ClearPauseMenu
    call Graphics_DrawStatusBar
    call Game_UpdateMineDisplay
    call Game_UpdateTimeDisplay
    call Game_DrawFullBoardDirect
    call Graphics_ClearOAM
    call Cursor_UpdateSprite
    jp Graphics_EnableLCD

Game_DrawFullBoardDirect:
    xor a
    ld [wGameDrawHead], a
    ld [wGameDrawTail], a
    ld [wGameWorkIndex], a
.loop:
    call Game_GetVisibleTileForWorkIndex
    ld [wGameWorkCell], a
    call Game_GetBGAddressForWorkIndex
    ld a, [wGameWorkCell]
    ld [hl], a
    ld a, [wGameWorkIndex]
    inc a
    ld [wGameWorkIndex], a
    ld b, a
    ld a, [wBoardCellCount]
    cp b
    ret z
    jr nc, .loop
    ret

Game_EnqueueFullBoardRedraw:
    xor a
    ld [wGameDrawHead], a
    ld [wGameDrawTail], a
    ld [wGameWorkIndex], a
.loop:
    call Game_GetVisibleTileForWorkIndex
    ld [wGameWorkCell], a
    call Game_EnqueueDrawWorkIndexWithTile
    ld a, [wGameWorkIndex]
    inc a
    ld [wGameWorkIndex], a
    ld b, a
    ld a, [wBoardCellCount]
    cp b
    ret z
    jr nc, .loop
    ret

Game_GetVisibleTileForWorkIndex:
    call Game_GetCellAddressForWorkIndex
    bit CELL_FLAG_BIT, [hl]
    jr nz, .flag
    bit CELL_OPENED_BIT, [hl]
    jr z, .closed
    bit CELL_MINE_BIT, [hl]
    jr nz, .mine
    ld a, [hl]
    and $0F
    add TILE_OPEN_0
    ret
.flag:
    ld a, TILE_FLAG
    ret
.closed:
    ld a, TILE_CLOSED
    ret
.mine:
    ld a, TILE_MINE
    ret

GameOverText:
    db TILE_LETTER_A + 'G' - 'A'
    db TILE_LETTER_A + 'A' - 'A'
    db TILE_LETTER_A + 'M' - 'A'
    db TILE_LETTER_A + 'E' - 'A'
    db TILE_BLANK
    db TILE_LETTER_A + 'O' - 'A'
    db TILE_LETTER_V
    db TILE_LETTER_A + 'E' - 'A'
    db TILE_LETTER_A + 'R' - 'A'

ClearText:
    db TILE_LETTER_A + 'C' - 'A'
    db TILE_LETTER_A + 'L' - 'A'
    db TILE_LETTER_A + 'E' - 'A'
    db TILE_LETTER_A + 'A' - 'A'
    db TILE_LETTER_A + 'R' - 'A'

PauseResumeText:
    db TILE_LETTER_A + 'R' - 'A', TILE_LETTER_A + 'E' - 'A'
    db TILE_LETTER_A + 'S' - 'A', TILE_LETTER_U
    db TILE_LETTER_A + 'M' - 'A', TILE_LETTER_A + 'E' - 'A', $FF

PauseRestartText:
    db TILE_LETTER_A + 'R' - 'A', TILE_LETTER_A + 'E' - 'A'
    db TILE_LETTER_A + 'S' - 'A', TILE_LETTER_A + 'T' - 'A'
    db TILE_LETTER_A + 'A' - 'A', TILE_LETTER_A + 'R' - 'A'
    db TILE_LETTER_A + 'T' - 'A', $FF

PauseBackToTitleText:
    db TILE_LETTER_A + 'B' - 'A', TILE_LETTER_A + 'A' - 'A'
    db TILE_LETTER_A + 'C' - 'A', TILE_LETTER_A + 'K' - 'A'
    db TILE_BLANK
    db TILE_LETTER_A + 'T' - 'A', TILE_LETTER_A + 'O' - 'A'
    db TILE_BLANK
    db TILE_LETTER_A + 'T' - 'A', TILE_LETTER_A + 'I' - 'A'
    db TILE_LETTER_A + 'T' - 'A', TILE_LETTER_A + 'L' - 'A'
    db TILE_LETTER_A + 'E' - 'A', $FF

Game_InitOpenQueue:
    xor a
    ld [wOpenQueueHead], a
    ld [wOpenQueueTail], a
    ret

Game_EnqueueOpenXY:
    ld a, [wOpenQueueTail]
    cp BOARD_QUEUE_CAPACITY
    ret nc
    ld c, a
    ld b, 0
    ld hl, wOpenQueueX
    add hl, bc
    ld [hl], e
    ld hl, wOpenQueueY
    add hl, bc
    ld [hl], d
    ld a, [wOpenQueueTail]
    inc a
    ld [wOpenQueueTail], a
    ret

Game_DequeueOpenXY:
    ld a, [wOpenQueueHead]
    ld c, a
    ld b, 0
    ld hl, wOpenQueueX
    add hl, bc
    ld a, [hl]
    ld [wGameCenterX], a
    ld hl, wOpenQueueY
    add hl, bc
    ld a, [hl]
    ld [wGameCenterY], a
    ld a, [wOpenQueueHead]
    inc a
    ld [wOpenQueueHead], a
    ret

Game_EnqueueDrawWorkIndexAuto:
    xor a
    ld [wGameDrawTileValue], a
    jr Game_EnqueueDrawWorkIndex

Game_EnqueueDrawWorkIndexWithTile:
    ld a, [wGameWorkCell]
    inc a
    ld [wGameDrawTileValue], a

Game_EnqueueDrawWorkIndex:
    ld a, [wGameDrawHead]
    ld b, a
    ld a, [wGameDrawTail]
    cp b
    jr nz, .enqueue
    xor a
    ld [wGameDrawHead], a
    ld [wGameDrawTail], a
.enqueue:
    ld a, [wGameDrawTail]
    cp BOARD_QUEUE_CAPACITY
    ret nc
    ld c, a
    ld b, 0
    ld hl, wGameDrawQueue
    add hl, bc
    ld a, [wGameWorkIndex]
    ld [hl], a
    ld hl, wGameDrawTileQueue
    add hl, bc
    ld a, [wGameDrawTileValue]
    ld [hl], a
    ld a, [wGameDrawTail]
    inc a
    ld [wGameDrawTail], a
    ret

Game_GetCellAddressForWorkIndex:
    ld a, [wGameWorkIndex]
    ld c, a
    ld b, 0
    ld hl, wBoard
    add hl, bc
    ret

Game_GetTileForWorkIndex:
    call Game_GetCellAddressForWorkIndex
    ld a, [hl]
    bit CELL_MINE_BIT, [hl]
    jr z, .numberTile
    ld a, TILE_MINE
    ret
.numberTile:
    and $0F
    add TILE_OPEN_0
    ret

Game_GetCursorIndex:
    ld a, [wCursorY]
    ld d, a
    ld a, [wCursorX]
    ld e, a
    jp Game_XYToIndex

Game_XYToIndex:
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
    ld a, e
    add h
    ret

Game_GetBGAddressForWorkIndex:
    ld a, [wGameWorkIndex]
    ld d, 0
.rowLoop:
    ld b, a
    ld a, [wBoardWidth]
    ld c, a
    ld a, b
    cp c
    jr c, .gotXY
    sub c
    inc d
    jr .rowLoop
.gotXY:
    ld e, a
    ld hl, BG_MAP
    ld a, [wBoardBgY]
    add d
    and a
    jr z, .addOriginX
.addRow:
    ld bc, BG_MAP_WIDTH
    add hl, bc
    dec a
    jr nz, .addRow
.addOriginX:
    ld a, [wBoardBgX]
    add e
    ld e, a
.addX:
    ld c, e
    ld b, 0
    add hl, bc
    ret
