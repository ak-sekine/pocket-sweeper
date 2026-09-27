# Maple Leaf Rag full-song ROM layout design (01756)

## Scope and decision boundary

This is a machine-evidence design record for WBS-001-01756. It does not
approve a production cartridge architecture or claim Human listening success.
The measured input is `/tmp/pocket-sweeper-01747/dedup/full-song.asm` and its
matching `full-song.json`, generated from the structure-aware full-song plan.

## Measured section layout

The generated ASM declares `SECTION "full_song Song Data", ROMX`. Counting the
actual `db`, `dw`, and `dn` operands gives `0x84D9` after RGBDS section
alignment. The byte accounting is:

| component | machine calculation | bytes |
| --- | ---: | ---: |
| pattern definitions | 173 definitions × 64 rows × 3 bytes (`dn`) | `0x81C0` (33216) |
| order tables | 4 tables × 58 entries × 2 bytes, including the 1 repeated order reference in pulse2/pulse1 sequence | `0x1D1` (465) |
| descriptor, order count, instruments, routines, loop metadata | generated `db`/`dw` records | `0x38` (56) |
| wave table | 16 waves × 16 bytes | `0x100` (256) |
| section alignment/padding | RGBDS section placement | `0x10` (16) |
| **total** | | **`0x84D9` (34009)** |

The order-table count is 465 rather than a guessed 464 because the generated
ASM has a one-byte order-count record adjacent to the order data; the complete
directive count is preserved in the 56-byte descriptor/metadata bucket. The
important capacity result is unchanged: the 173 fixed patterns alone consume
`0x81C0`, leaving only `0xE40` bytes in a `0x4000` section before all other
data, while the complete section is short by `0x44D9` (17625) bytes.

The generated routine labels contain no emitted routine bytes in this case;
they are included in the descriptor/metadata accounting only where an actual
directive is present. The UGE container size (`317990` bytes) is not a ROM
section size and is not used for this calculation.

## Pattern utilization evidence

For each JSON pattern, note lengths were expanded to rows and counted only at
note-start rows. The generated ASM still emits all 64 rows, including empty
rows, as required by `PATTERN_LENGTH EQU 64` in `src/hUGEDriver.asm`.

| channel | definitions | note events | non-empty rows | occupancy | min / max / median | patterns ≤4 rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pulse1 | 58 | 758 | 3111 / 3712 | 83.81% | 18 / 62 / 57 | 0 |
| pulse2 | 57 | 524 | 3218 / 3648 | 88.21% | 6 / 62 / 60 | 0 |
| wave | 57 | 559 | 3321 / 3648 | 91.04% | 36 / 62 / 60 | 0 |
| noise | 1 | 0 | 0 / 64 | 0% | 0 / 0 / 0 | 1 |

The all-empty noise pattern is already shared. The three musical channels are
not sparse: fixed 64-row encoding is overhead, but trimming trailing rows
cannot preserve the current hUGEDriver contract. The evidence does not support
an ordinary sparse/trailing-row optimization as a safe one-bank solution.

## One-bank reduction audit

The known deduplication reduced the section from `0xB119` to `0x84D9`, a saving
of `0x2C40` (11328) bytes. The remaining deficit is `0x44D9`; it is larger than
all non-pattern metadata combined. Empty-pattern reuse is already present,
and the ASM/order graph has 173 reachable definitions across the 58-order
timeline. No evidence permits deleting musical orders, unused notes, or
instrument/wave records without changing the song. Consequently, retaining
the current hUGEDriver format and fitting this full song into one 16KB bank is
**not established and is practically implausible**.

## Cartridge and address evidence

Game Boy ROM0 is `$0000-$3FFF`; ROMX is `$4000-$7FFF` and selects a bank. The
current sound-test builder links the song as ROMX but invokes
`rgbfix -m ROM -r 0x00`, and no MBC register write exists. A multi-bank song
therefore cannot be selected by the current ROM-only runtime.

`src/hUGEDriver.asm` places the driver in ROM0. `hUGE_init` copies descriptor
pointers to WRAM, `load_patterns` reads 16-bit order pointers, and
`hUGE_dosound` dereferences the cached 16-bit pattern pointers on every tick.
There is no bank byte, bank save/restore, or bank switch in that path. A
pattern split across banks would require a bank-aware pointer and switching
before every pattern read, with driver code remaining in ROM0. Changing the
bank while executing hUGEDriver in ROMX would be unsafe; a design must keep
the switch routine and all interrupt/driver code in ROM0.

`0x84D9` requires three 16KB ROMX banks if represented as one continuous data
blob (`ceil(34009 / 16384) = 3`). A practical MBC1 prototype header would be
ROM size `64 KiB` / 4 banks (`-r 0x01`) and cartridge type `MBC1` (`-m MBC1`),
with one ROM0 bank and three addressable ROMX banks. This is a prototype
calculation, not approval of MBC1 for Pocket Sweeper production.

## Candidate comparison

| method | capacity | runtime change | MBC | production impact | judgment |
| --- | --- | --- | --- | --- | --- |
| A. Current format, reduction into one bank | Not shown; deficit `0x44D9` | none | no | low if possible | **not established** |
| B. Prototype bank-aware hUGEDriver | Yes, at least 3 data banks | descriptor, banked pointers, load/read path, bank save/restore and interrupt safety | yes | isolateable but high risk | **conditionally成立** |
| C. Independent hUGE songs per bank | Potentially yes | transition controller and re-init | yes | changes musical continuity and state semantics | **conditionally成立; Human musical decision** |
| D. Bank only pattern access | Yes in principle | every pattern/order read needs bank metadata and safe switching | yes | high driver coupling | **conditionally成立; large change** |
| E. Prototype-only alternate representation/player | Yes in principle | new player and converter | optional | isolateable, but no longer hUGEDriver validation | **conditionally成立; scope choice** |
| F. More aggressive musical/data reduction | Unknown | converter and musical content changes | maybe no | changes source preservation | **not allowed without Human approval** |

### Song splitting specifically

The existing 58-order timeline provides candidate boundaries, but no machine
evidence here proves that a boundary is musically seamless, preserves tempo and
instrument state, or avoids an audible gap. `hUGE_bgm_finished` can signal a
non-looping song end, but it cannot by itself preserve a continuous song while
reinitializing the next descriptor. Reinitialization resets driver state and
would need an explicitly designed handoff. Therefore C cannot be selected from
the current evidence alone.

### Pattern-bank-aware specifics

A safe D/B implementation would need a bank byte alongside each order/pattern
pointer (or banked descriptors), bank-aware `load_patterns`, bank-aware row
fetch/effect/routine/wave access, a ROM0 switch helper, saved current bank, and
an interrupt-safe protocol. Switching only at song transitions is insufficient
for a pattern layout spanning banks unless each active pattern set remains in
one mapped bank. This is materially more than a linker or header change.

## 01756 outcome

The machine evidence safely rejects “just add more ROM banks” with the current
runtime and safely establishes that fixed-format deduplication is not enough.
It does **not** uniquely choose B, C, D, or E: B/D change the production-like
runtime contract, C changes musical continuity/state behavior, and E changes
the playback representation. A Human must choose whether the goal is
hUGEDriver-compatible prototype playback, a split-song approximation, or a
prototype-only player. Therefore 01756 stops before 01757; no production bank
architecture is approved and no WBS status is advanced.

