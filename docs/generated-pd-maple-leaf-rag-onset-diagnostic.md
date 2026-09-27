# Maple Leaf Rag MIDI→MusicXML onset diagnostic

## Scope

WBS-001-01704のmachine diagnosticとして、承認済みMutopia Maple Leaf Rag MIDIからgenerated MusicXML、MusicXML parser、NormalizedScore、01698 diagnosticのabsolute onset復元までを比較した。編曲、JSON、UGE、ROM、Human音楽評価は対象外である。sourceとgenerated artifactはrepositoryへ追加せず、一時領域で生成した。

## Source and execution

- source: Mutopia Project `Mutopia-2011/11/13-23`, Maple Leaf Rag, `maple.mid`
- source SHA-256: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- SMF: format 1, 3 tracks, PPQ 384, source meter event 2/4
- tool: `tools/analyze_pd_onset_diagnostic.py`, version 1
- command: `python3 tools/analyze_pd_onset_diagnostic.py /tmp/pocket-sweeper-01704/maple.mid /tmp/pocket-sweeper-01704/run1`
- second command: same command with output `/tmp/pocket-sweeper-01704/run2`
- generated MusicXML SHA-256: `955fe1a837bc69c188efe76836e1f5b8fc3c9307a9bc4df29df6f6e2728beab4`
- diagnostic JSON SHA-256: `eccf8b4bcff80b8a1cf3bdf102a6d97d0022f59a0b1e943feb097160acc9a0c6`
- diagnostic Markdown SHA-256: `2444854928d15a39fccfd3a45be5eb3e27185b1f191ac0216670deeee63839c1`

The generated MusicXML hash is a 64-character SHA-256 value. It is the same value previously recorded as the generated artifact; the earlier concern about an invalid length was a transcription/inspection concern, not an invalid measured digest.

## Stage contract

Each event is recorded in the machine-readable diagnostic JSON produced in `/tmp/pocket-sweeper-01704/run1/maple_leaf_rag.onset-diagnostic.json` with `source_event_id`, track/part, source onset, writer input onset, MusicXML measure-local onset, parser onset, NormalizedScore onset, diagnostic absolute onset, deltas, PPQ/divisions, chord status, and first mismatch stage.

The comparison stages are:

1. source MIDI note
2. existing deterministic MIDI parser
3. writer input (the parsed MIDI note)
4. actual MusicXML implicit cursor representation
5. existing MusicXML parser result
6. NormalizedScore (the existing parser output)
7. diagnostic absolute-onset reconstruction

The MIDI parser and writer input are the same implementation boundary, so their equality is parser-derived rather than an independent parser proof.

## Measured onset result

| metric | count |
|---|---:|
| total note events | 2566 |
| final exact onset | 981 |
| final mismatch | 1585 |
| maximum absolute final delta | 1152 source ticks |
| first mismatch: generated MusicXML representation | 931 |
| first mismatch: MusicXML parser | 866 |
| first mismatch: diagnostic-only reconstruction | 0 |
| no mismatch | 769 |

The first-mismatch categories are mutually exclusive. The final 1585 mismatches therefore comprise 931 events whose actual MusicXML implicit representation already differs from the source and 866 events whose representation is source-aligned at that event but whose existing parser result differs. Some events have both effects, so the two counts must not be added as independent final-mismatch counts.

## What the implementation does

The writer uses `measure_ticks = ppq * 4` (1536 source ticks) as its measure boundary while writing source metadata as 2/4. It writes note durations and uses `<chord/>` for notes sharing a source onset, but it does not write rests or `<forward>` elements for gaps. Therefore a gap before a note is not an explicit MusicXML timing token; the implicit cursor starts at the current measure cursor instead.

The existing parser resets a cursor at each measure, treats a chord note as if the cursor were unchanged before the note but advances the cursor after every note, and does not implement `<backup>`/`<forward>` timing. In this generated file there are no rest, forward, or backup elements. Consequently a chord note can be read at the prior note's post-duration cursor rather than the preceding note's onset.

The diagnostic restores an absolute onset as:

`(musicxml_measure - 1) * (PPQ * 4) + measure_local_cursor`

with exact integer arithmetic. Since PPQ equals MusicXML divisions (384), no fractional rounding occurs. The diagnostic did not create a separate mismatch category in this run.

## Representative events

| source_event_id | source / writer input | XML semantic local | parser / NormalizedScore | final delta | first mismatch |
|---|---:|---:|---:|---:|---|
| `midi:t1:e0` | 288 | 0 | 0 | -288 | generated MusicXML representation |
| `midi:t1:e1` | 384 | 96 | 192 | -192 | generated MusicXML representation; parser adds a chord-related delta |
| `midi:t2:e0` | 0 | 0 | 192 | +192 | MusicXML parser |

These examples show distinct mechanisms: omitted gap representation and chord cursor handling. They do not by themselves establish which mechanism affects Human perception.

## Delta regularity

The final delta distribution was:

| delta (source ticks) | events |
|---:|---:|
| -1152 | 3 |
| -1056 | 9 |
| -576 | 3 |
| -480 | 12 |
| -384 | 6 |
| -288 | 81 |
| -192 | 124 |
| -96 | 371 |
| 0 | 981 |
| 96 | 140 |
| 192 | 790 |
| 288 | 36 |
| 384 | 8 |
| 480 | 2 |

The deltas are multiples of 96 source ticks in this source. They vary by track and measure; the evidence does not support reducing the result to a single monotonic measure-offset rule. The machine JSON retains full per-measure and per-track distributions.

## 2566 → 31 relationship

This diagnostic does not run ArrangementPlan reduction. It therefore does not prove a causal relationship between onset mismatch and the later 2566 → 31 reduction. It preserves the upstream evidence boundary: 01700 reported 31 preexisting same-onset collision groups in NormalizedScore, but this task did not independently remeasure those groups against the source MIDI.

## Determinism

The generated MusicXML, diagnostic JSON, and Markdown report hashes matched between run1 and run2. Canonical outputs contain no timestamp. The event-level JSON is reproducible from source bytes, tool version, and configuration.

## Conclusions

Confirmed:

- the MIDI parser and writer input preserve the parsed source onset in this implementation;
- 931 events first differ when the actual MusicXML implicit cursor is compared with source onset;
- 866 events first differ at the existing MusicXML parser boundary after source-aligned XML semantics for that event;
- no event first differed only in the diagnostic absolute reconstruction;
- the existing generated MusicXML omits explicit gap timing and the parser does not implement chord-correct cursor semantics for this file;
- the observed final result is 981 exact and 1585 mismatch, maximum delta 1152 ticks.

Not concluded:

- that the writer is definitively defective rather than using an insufficient representation for this diagnostic;
- that the parser behavior is the sole cause of any musical result;
- that onset mismatch caused the Human trial failure;
- that a correction will improve the music, production readiness, or Maple Leaf Rag recognition.

## Handoff

Any correction or A/B listening comparison should be a separate WBS. Candidate follow-up work includes explicitly encoding gaps with rests/forward, implementing chord/backup/forward-aware parser semantics, and comparing absolute-onset reconstruction against the source. This report does not select among those changes.
