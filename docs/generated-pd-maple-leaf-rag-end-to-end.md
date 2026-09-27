# Maple Leaf Rag prototype end-to-end execution

## Scope

This is the WBS-001-01693 machine-validation record for the Human-approved
Mutopia MIDI. It does not assess musical quality or approve production BGM.
The MIDI is normalized in full, but JSON/UGE/ASM/ROM contain one 64-row
prototype window only; this is not the complete song.

## Source and conversion

- composition: Maple Leaf Rag, Scott Joplin
- provider/identity: Mutopia Project, `Mutopia-2011/11/13-23`
- URL: `https://www.mutopiaproject.org/ftp/JoplinS/maple/maple.mid`
- temporary source: `/tmp/pocket-sweeper-01693/maple.mid`
- source SHA-256: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- converter: `tools/maple_leaf_rag_prototype.py`, version 1
- settings: deterministic MusicXML 4.0 writer/parser, source MIDI format/PPQ retained
- generated MusicXML SHA-256: `955fe1a837bc69c188efe76836e1f5b8fc3c9307a9bc4df29df6f6e2728beab4`

The prior 01692 MusicXML value was malformed by transcription (not a 64-digit
SHA-256). The source document and WBS were corrected to the measured value.

## Commands and artifacts

Two runs used identical source/configuration. The first-run output directory
was `/tmp/pocket-sweeper-01693/run1` and the second was `run2`:

```text
python3 tools/maple_leaf_rag_prototype.py /tmp/pocket-sweeper-01693/maple.mid <run>
python3 tools/json_to_uge.py <run>/maple_leaf_rag.prototype.json <run>/maple_leaf_rag.uge
python3 tools/json_to_huge_asm.py <run>/maple_leaf_rag.prototype.json <run>/maple_leaf_rag.asm
python3 tools/analyze_uge.py <run>/maple_leaf_rag.uge
python3 tools/build_sound_test_rom.py <run>/maple_leaf_rag.asm <run>/maple_leaf_rag.gb
```

| artifact | first-run path | SHA-256 |
|---|---|---|
| source MIDI | `/tmp/pocket-sweeper-01693/maple.mid` | `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66` |
| MusicXML | `run1/maple_leaf_rag.generated.musicxml` | `955fe1a837bc69c188efe76836e1f5b8fc3c9307a9bc4df29df6f6e2728beab4` |
| JSON V2 | `run1/maple_leaf_rag.prototype.json` | `7c114e3e6007bf89a132e1f68166d5eb4f3a2d713737310a8fb9fec6fff0ec69` |
| manifest | `run1/maple_leaf_rag.manifest.json` | `c99879285403f96e1ef154c5b5f5d6d9c260fae0a24f4b8d3ca730a4230ff2f2` |
| report | `run1/maple_leaf_rag.report.json` | `c062320833bbd52d85264870a61d9b07ec0c4293d5ad38af42ee79a3dc953bdf` |
| UGE | `run1/maple_leaf_rag.uge` | `59f19eb95c3b692ebb8c5c428f29510b26393611ff568fce249f7d82bfbc2c3a` |
| ASM | `run1/maple_leaf_rag.asm` | `202a94de2e0b0c42685bc1c3610a94e4fa3c63a2dc304412e8ca60a1536d13b0` |
| ROM | `run1/maple_leaf_rag.gb` | `4c54ee6df7386816d452165656b2394e3f7a9d5f6217412e83fa19981955923c` |

Run2 hashes were identical for every listed artifact, including manifest and
report. Generated artifacts remain outside the repository.

## Validation

`analyze_uge.py` parsed UGE Version 6, song `Maple Leaf Rag Prototype`,
tempo raw 6, four patterns, and four aligned channels. The generated ASM has
the Version 2 descriptor, tempo `6`, order/instrument data, and
`maple_leaf_rag_loop_metadata: db 2,0,63`; mode 2 is the explicit `none`
mode used by the sound-test builder. The UGE analyzer reports an implicit
full-order cycle when no jump is present; that structural observation is not
treated as the intended JSON loop. `build_sound_test_rom.py` selected its
non-loop completion path and RGBDS successfully ran:

- `rgbasm v1.0.1-157-gdecc5f71`
- `rgblink v1.0.1-157-gdecc5f71`
- `rgbfix v1.0.1-157-gdecc5f71`

Source tempo is 120 BPM (`500000` microseconds per quarter); runtime
TicksPerRow is 6. They are separate fields and are not interchangeable.

## Provenance, losses, and limitations

The manifest/report retain source hash, conversion settings, parser, mapping,
warnings/losses, transformation history, prototype range, and JSON hash.
MIDI-derived voices, staff, spelling, repeats/endings, articulation, dynamics,
and notation semantics retain the statuses recorded by 01692; no repeat was
inferred. The CH4 policy is unused rather than implicit piano-to-noise conversion.

The ROM build proves machine-level pipeline compatibility only. Human listening,
musical quality, natural ending, and production BGM adoption are not evaluated.
Those decisions are handed to WBS-001-01694. Source/license conditions remain
those recorded in the rights/provenance investigation; no source or generated
MusicXML was committed here.
