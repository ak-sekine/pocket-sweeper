PROJECT := pocket-sweeper

SRC_DIR := src
INCLUDE_DIR := include
OBJ_DIR := obj
BUILD_DIR := build

SOURCES := $(wildcard $(SRC_DIR)/*.asm)
SFX_ASM := $(OBJ_DIR)/se_cursor_sfx.asm
SFX_OBJECTS := $(patsubst $(OBJ_DIR)/%.asm,$(OBJ_DIR)/%.o,$(SFX_ASM))
BGM_ASM := $(OBJ_DIR)/bgm_title.asm $(OBJ_DIR)/bgm_game.asm $(OBJ_DIR)/bgm_clear.asm
BGM_OBJECTS := $(patsubst $(OBJ_DIR)/%.asm,$(OBJ_DIR)/%.o,$(BGM_ASM))
OBJECTS := $(patsubst $(SRC_DIR)/%.asm,$(OBJ_DIR)/%.o,$(SOURCES)) $(SFX_OBJECTS) $(BGM_OBJECTS)

ROM := $(BUILD_DIR)/$(PROJECT).gb
MAP := $(OBJ_DIR)/$(PROJECT).map
SYM := $(OBJ_DIR)/$(PROJECT).sym

GRAPHICS := $(OBJ_DIR)/tiles.2bpp $(OBJ_DIR)/cursor.2bpp $(OBJ_DIR)/font.2bpp
TITLE_TILES_PNG := $(OBJ_DIR)/title_tiles.png
TITLE_MAP := $(OBJ_DIR)/title_map.bin
TITLE_CONVERT_STAMP := $(OBJ_DIR)/title.stamp

RGBASM ?= rgbasm
RGBLINK ?= rgblink
RGBFIX ?= rgbfix
RGBGFX ?= rgbgfx
PYTHON ?= .venv/bin/python
EMULATOR ?= sameboy

RGBASMFLAGS ?= -I $(INCLUDE_DIR)/
RGBLINKFLAGS ?= -m $(MAP) -n $(SYM)
RGBFIXFLAGS ?= -v -p 0xFF -t "POCKET SWEEPER" -m ROM -r 0x00
RGBGFX_BG_COLORS := \#E0F8D0,\#88C070,\#346856,\#081820
RGBGFX_CURSOR_COLORS := \#88C070,\#E0F8D0,\#346856,\#081820

.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SECONDARY: $(SFX_ASM) $(BGM_ASM)

.PHONY: all clean run

all: $(ROM)

$(ROM): $(OBJECTS) | $(BUILD_DIR) $(OBJ_DIR)
	$(RGBLINK) $(RGBLINKFLAGS) -o $@ $(OBJECTS)
	$(RGBFIX) $(RGBFIXFLAGS) $@

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.asm | $(OBJ_DIR)
	$(RGBASM) $(RGBASMFLAGS) -o $@ $<

$(OBJ_DIR)/%.o: $(OBJ_DIR)/%.asm | $(OBJ_DIR)
	$(RGBASM) $(RGBASMFLAGS) -o $@ $<

$(SFX_ASM): assets/se_cursor.json tools/json_to_sfx_asm.py tools/json_to_uge.py | $(OBJ_DIR)
	$(PYTHON) tools/json_to_sfx_asm.py $< $@

$(OBJ_DIR)/bgm_%.asm: assets/bgm_%.json tools/json_to_huge_asm.py tools/json_to_uge.py | $(OBJ_DIR)
	$(PYTHON) tools/json_to_huge_asm.py $< $@

$(BGM_OBJECTS): $(INCLUDE_DIR)/hUGE.inc

$(OBJ_DIR)/graphics.o: $(GRAPHICS) $(OBJ_DIR)/title_tiles.2bpp $(TITLE_MAP) $(INCLUDE_DIR)/graphics.inc $(INCLUDE_DIR)/hardware.inc
$(OBJ_DIR)/input.o: $(INCLUDE_DIR)/input.inc $(INCLUDE_DIR)/hardware.inc
$(OBJ_DIR)/main.o: $(INCLUDE_DIR)/hardware.inc
$(OBJ_DIR)/sound.o: $(INCLUDE_DIR)/hardware.inc
$(OBJ_DIR)/hUGEDriver.o: $(INCLUDE_DIR)/hardware.inc $(INCLUDE_DIR)/hUGE.inc $(INCLUDE_DIR)/hUGE_note_table.inc
$(OBJ_DIR)/bgm_test.o: $(INCLUDE_DIR)/hUGE.inc
$(OBJ_DIR)/cursor.o: $(INCLUDE_DIR)/graphics.inc $(INCLUDE_DIR)/input.inc $(INCLUDE_DIR)/hardware.inc
$(OBJ_DIR)/board.o: $(INCLUDE_DIR)/graphics.inc $(INCLUDE_DIR)/input.inc
$(OBJ_DIR)/game.o: $(INCLUDE_DIR)/graphics.inc $(INCLUDE_DIR)/input.inc

$(OBJ_DIR)/font.2bpp: assets/font.png | $(OBJ_DIR)
	$(RGBGFX) -c "$(RGBGFX_BG_COLORS)" -L 0,0:16,3 -o $@ $<

$(OBJ_DIR)/tiles.2bpp: assets/tiles.png | $(OBJ_DIR)
	$(RGBGFX) -c "$(RGBGFX_BG_COLORS)" -o $@ $<

$(OBJ_DIR)/cursor.2bpp: assets/cursor.png | $(OBJ_DIR)
	$(RGBGFX) -c "$(RGBGFX_CURSOR_COLORS)" -o $@ $<

$(TITLE_TILES_PNG) $(TITLE_MAP): $(TITLE_CONVERT_STAMP)

$(TITLE_CONVERT_STAMP): assets/title.png tools/convert_bg_image.py | $(OBJ_DIR)
	$(PYTHON) tools/convert_bg_image.py $< $(TITLE_TILES_PNG) $(TITLE_MAP)
	touch $@

$(OBJ_DIR)/title_tiles.2bpp: $(TITLE_TILES_PNG) | $(OBJ_DIR)
	$(RGBGFX) -c "$(RGBGFX_BG_COLORS)" -o $@ $<

$(OBJ_DIR) $(BUILD_DIR):
	mkdir -p $@

run: $(ROM)
	"$(EMULATOR)" "$(ROM)"

clean:
	rm -rf $(OBJ_DIR) $(BUILD_DIR)
