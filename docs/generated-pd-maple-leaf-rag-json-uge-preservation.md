# Maple Leaf Rag ArrangementPlan → JSON Version 2 → UGE preservation

## Scope

WBS-001-01701のformat-level diagnostic。01700で選択された31 ArrangementPlan
eventsを基準にJSON Version 2とUGEを比較した。runtime playback、ASM/ROM、
SameBoy、Human musical evaluationは対象外である。

## Source / upstream

- source: Mutopia `Maple Leaf Rag (Mutopia-2011/11/13-23)`
- source SHA-256: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- 01698 diagnostic: `a25edd84e5d83dcf25bbe92d32cce4486cd999581d5e799caa73c756d816c087`
- 01699 role diagnostic: `032256e6735d00c2eec5f9276048dc5de41a9600a99c701e4ffe24cdd91391fd`
- 01700 reduction diagnostic: `7ed9939805ac2fa9550888d7a08db53839c0033008c2652e96b33a7abed547b6`

## Actual pipeline

The current implementation performs ArrangementPlan selection and transformation,
then `make_json` creates one pattern per physical channel. It emits rests until
the event row, emits a note with a length/instrument, and fills the remaining
pattern to 64 rows. Events reached after `row >= 64` are not emitted. The JSON
is then passed unchanged to `json_to_uge.py`, which validates the four-channel
order matrix and packs each 64-row pattern into UGE cells.

## ArrangementPlan baseline / window

| role/channel | ArrangementPlan events | JSON encoded | window omitted | mismatch |
|---|---:|---:|---:|---:|
| melody / CH1 pulse1 | 18 | 13 | 5 | pitch/row comparisons recorded |
| harmony / CH2 pulse2 | 0 | 0 | 0 | 0 |
| bass / CH3 wave | 13 | 13 | 0 | pitch/row comparisons recorded |
| rhythm / CH4 noise | 0 | 0 | 0 | 0 |

Total: 31 input, 26 JSON note cells, 5 `prototype_window_overflow`. The
window is applied during JSON pattern emission, with nominal rows 0–63. All 31
ArrangementPlan rows were within the nominal range, but five were not reached
because preceding emitted note lengths advanced the pattern cursor to the
64-row boundary. This downstream omission is distinct from 01700's 2535
polyphony omissions.

The mapping sidecar retains all 31 source_event_id values and classifies each as
mapped or `prototype_window`. JSON does not contain source IDs; the diagnostic
maps encoded notes by deterministic per-channel selected-event order.

## ArrangementPlan → JSON

| metric | result |
|---|---:|
| input events | 31 |
| JSON encoded | 26 |
| window omitted | 5 |
| unmapped other | 0 |
| pitch exact | 6 |
| row exact | 3 |

The pitch/row comparison is against the JSON cell associated by deterministic
per-channel order. A JSON pattern is a sequential note/rest token stream, not a
source-event-indexed array; the association and its limitations are retained in
the sidecar. Note tokens are decoded to absolute MIDI pitch for comparison.

Duration is represented by JSON `length` tokens and implicit cursor advancement,
not by a separate absolute onset field. Therefore duration is classified as a
representation change rather than asserted to be one-to-one preserved. The
cursor behavior accounts for row mismatches; no converter change was made.

## JSON structure

Each of pulse1, pulse2, wave, and noise has one named pattern and one order
entry. Each pattern totals 64 rows:

| JSON channel | patterns | note cells | rest cells | order |
|---|---:|---:|---:|---|
| pulse1 | 1 | 13 | 0 | maple_pulse1 |
| pulse2 | 1 | 0 | 1 | maple_pulse2 |
| wave | 1 | 13 | 0 | maple_wave |
| noise | 1 | 0 | 1 | maple_noise |

CH2 and CH4 are rest-only patterns with default instruments. Four-channel format
does not mean all four channels contain source-derived notes.

## JSON → UGE

`tools/analyze_uge.py` parsed UGE Song Version 6. The UGE mapping was:

| channel | JSON notes | UGE notes | exact | transformed | omitted | mismatch |
|---|---:|---:|---:|---:|---:|---:|
| CH1 | 13 | 13 | 13 | 0 | 0 | 0 |
| CH2 | 0 | 0 | 0 | 0 | 0 | 0 |
| CH3 | 13 | 13 | 13 | 0 | 0 | 0 |
| CH4 | 0 | 0 | 0 | 0 | 0 | 0 |

UGE note values were compared using the converter's C3-relative note numbering;
instrument IDs also matched. Pattern/order references matched structurally.
The UGE analyzer can report encoded cells, instruments, patterns, order, and
tempo fields, but not source_event_id or audible timing.

## Tempo / TicksPerRow

- source: 500000 microseconds/quarter = 120 BPM
- JSON `tempo`: 6, meaning runtime TicksPerRow
- UGE `tempo_raw`: 6

The source BPM and runtime timing parameter are distinct and are not compared as
the same quantity.

## Loop metadata

- intended ArrangementPlan/config: `none`
- JSON: `{"mode":"none"}`
- UGE analyzer: `implicit_full_order_cycle` because there is no B position jump

The analyzer result describes format control flow, not the intended semantic
loop setting. Real hUGEDriver runtime termination/loop behavior remains unknown.

## Determinism / hashes

Two complete runs produced identical hashes:

- source: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- JSON: `7c114e3e6007bf89a132e1f68166d5eb4f3a2d713737310a8fb9fec6fff0ec69`
- UGE: `59f19eb95c3b692ebb8c5c428f29510b26393611ff568fce249f7d82bfbc2c3a`
- diagnostic JSON: `a879a5963a684aed8098b2fca18a6731296ffa8c85e316f29c97a55087c7c64e`
- diagnostic Markdown: `9e82c532592a9b8958688e2e233fdee3d746f2801c1ff3ee4305a7d7235a6f10`

## Runtime boundary and non-conclusions

Format-level evidence confirms JSON/UGE encoded note cells, instruments, rows,
patterns, orders, timing parameter, and loop metadata as described. It does not
prove hUGEDriver real-time timing, APU writes, audible duration, SameBoy output,
Human recognition, musical quality, or production BGM suitability. It does not
identify the cause of the Human evaluation or conclude that any upstream
omission/onset mismatch is causal.

## Handoff to 01702

01702 can combine 01698–01701 evidence. It should preserve the distinction
between upstream onset loss, 01700 reduction, JSON window overflow, and UGE
format encoding.
