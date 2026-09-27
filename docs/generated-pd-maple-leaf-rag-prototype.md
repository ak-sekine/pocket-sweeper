# Maple Leaf Rag prototype実装

対象: WBS-001-01692
調査・実装日: 2026-09-27

## Scope

`Mutopia MIDI → MusicXML → NormalizedScore → ArrangementPlan → JSON Version 2`の最小deterministic adapterを実装した。prototypeはMusicXMLを再読込してから正規化・編曲する。Mutopia sourceやgenerated MusicXMLはrepositoryへ追加しない。ROM生成とHuman試聴は01693以降で扱う。

## Tool and command

実装: `tools/maple_leaf_rag_prototype.py`。外部依存なしのPython標準ライブラリSMF parserとMusicXML writer/parserを使う。MuseScoreがなくても、許可されたMutopia MIDIから同じMusicXMLを生成できる明示的経路であり、MuseScoreへのsilent fallbackはしない。

```text
python3 tools/maple_leaf_rag_prototype.py <maple.mid> <output-dir>
python3 tools/json_to_uge.py <output-dir>/maple_leaf_rag.prototype.json <output-dir>/maple_leaf_rag.uge
python3 tools/json_to_huge_asm.py <output-dir>/maple_leaf_rag.prototype.json <output-dir>/maple_leaf_rag.asm
python3 tools/analyze_uge.py <output-dir>/maple_leaf_rag.uge
```

source SHA-256は01690の値と一致しない場合rejectする。

## Source and conversion provenance

- composition: Maple Leaf Rag / Scott Joplin
- provider: Mutopia Project
- identity: `Mutopia-2011/11/13-23`
- URL: `https://www.mutopiaproject.org/ftp/JoplinS/maple/maple.mid`
- format: Standard MIDI File, format 1, PPQ 384
- source SHA-256: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- license/provenance: Mutopia Public Domain contribution; details in 01690 document
- conversion tool: `maple_leaf_rag_prototype.py`, version `1`
- conversion settings: MIDI format/PPQ read from source; MusicXML 4.0; deterministic XML serialization
- generated MusicXML SHA-256 in validation run: `955fe1a837bc69c188efe76836e1f5b8fc3c9307a9bc4df29df6f6e2728beab4`
- parser: built-in SMF parser and `xml.etree.ElementTree`

The generated MusicXML is a MIDI-derived symbolic encoding, not the original Mutopia engraved notation. MIDI-to-MusicXML status is: voices `reconstructed`, staff `reconstructed`, spelling `reconstructed`, repeats `lost/unknown`, endings `lost/unknown`, articulation `lost/unknown`, dynamics `lost/unknown`, notation semantics `lost/unknown`. Tempo, meter, note timing and pitch events are preserved where present in the SMF.

## NormalizedScore

The parser output contains part ID, measure number, source event ID, start/duration in MusicXML divisions, pitch, meter and key. The source event ID is deterministic (`xml:Pn:mn:nn`) and does not use generation time. The prototype does not invent repeats, endings or articulation.

## ArrangementPlan

The explicit Maple configuration is:

|logical role|physical channel|policy|
|---|---|---|
|melody|pulse1|highest-average-pitch parsed part; deterministic source event ordering|
|harmony/accompaniment|pulse2|middle parsed part or upper events after bass split|
|bass/foundation|wave|lowest-average-pitch parsed part or low events|
|rhythm|noise|unused; piano pitch is not implicitly converted to noise|

This is a prototype configuration, not a production default. Parts are ranked from parsed content; MIDI track numbers are not hard-coded as roles.

Polyphony policy is deterministic one-event-per-quantized-start per role. Later notes at the same start are omitted and recorded with `polyphony_omitted`, source event ID and selected event. Pitch range transformation uses octave shifts only; rejected values receive a `range_reject` issue rather than silent clamping.

## Timing, range and loop

- source tempo: 500000 microseconds per quarter note (120 BPM)
- source meter: 2/4
- normalized timing: MusicXML divisions from source PPQ
- quantization grid: 30 source ticks
- JSON row: quantized event start divided by the grid
- JSON `tempo` / TicksPerRow: 6; it is not BPM
- prototype range: all parsed MIDI events are normalized; JSON emission uses one deterministic 64-row pattern window
- repeat policy: `do_not_infer`
- loop policy: `none`

The one-pattern output is an implementation boundary for 01692, not a claim that the full song is production-ready. The report retains source event range and issues for later extension.

## JSON Version 2 and existing pipeline

The generated JSON uses the existing Version 2 fields, current instrument contracts, four channels, one wave table and `loop.mode = none`. No JSON schema or existing converter was changed. `json_to_uge.build_uge` accepted the generated JSON; the existing CLI generated UGE and ASM, and `analyze_uge.py` parsed the UGE.

## Outputs and reports

Each run writes:

- `maple_leaf_rag.generated.musicxml`
- `maple_leaf_rag.prototype.json`
- `maple_leaf_rag.manifest.json`
- `maple_leaf_rag.report.json`

The manifest holds source/conversion/parser hashes, settings, mapping, source tempo, TicksPerRow, warnings, losses and transformation history. The report separates NormalizedScore summary and ArrangementPlan. Runtime JSON excludes provenance fields.

## Limitations and rights

No source file is committed by this implementation. The source license and commercial/GitHub conditions remain the conditional classifications recorded in `docs/generated-pd-prototype-rights-provenance-investigation.md`. Generated MusicXML is not asserted to have independent clearance beyond the documented conversion provenance. Lyrics and recordings are not included.

## Handoff to 01693

01693 can use a generated JSON/UGE/ASM artifact and perform the end-to-end generation checks. It must retain the manifest/report, avoid treating the one-pattern range as a complete production arrangement, and defer Human listening and production BGM judgment to the assigned later WBS.
