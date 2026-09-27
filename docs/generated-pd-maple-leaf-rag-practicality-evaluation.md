# PD曲自動編曲方式の実用性評価

## Scope

WBS-001-01692〜01694の証跡を統合し、MutopiaのMaple Leaf Rag MIDIを
Game Boy向けprototypeへ変換する方式の成立範囲と残課題を評価する。
本書は現在のprototypeの評価であり、方式全体の不可能性や曲の廃止を
決定するものではない。

## Evidence sources

- `wbs/tasks/WBS-001-01692.md`: prototype implementation and provenance
- `wbs/tasks/WBS-001-01693.md`: end-to-end machine validation
- `wbs/tasks/WBS-001-01694.md`: Human SameBoy evaluation
- `docs/generated-pd-maple-leaf-rag-prototype.md`
- `docs/generated-pd-maple-leaf-rag-end-to-end.md`
- `docs/generated-pd-maple-leaf-rag-human-evaluation.md`
- `tools/maple_leaf_rag_prototype.py` and existing JSON/UGE/ASM/ROM tools

## Machine evidence

The approved Mutopia MIDI was hash-validated, then processed through:

```text
MIDI → generated MusicXML → NormalizedScore → ArrangementPlan
     → JSON Version 2 → UGE → ASM → RGBDS → ROM
```

The process used deterministic parsing and generated MusicXML. JSON Version 2
validation, UGE analysis, ASM generation, and `rgbasm`/`rgblink`/`rgbfix`
build all succeeded. Source BPM (120; 500000 microseconds per quarter) and
runtime TicksPerRow (6) remained separate. Loop policy was `none`. Source,
MusicXML, JSON, manifest, report, UGE, ASM, and ROM hashes matched across two
runs. This establishes a machine-verifiable source-to-ROM pipeline, not musical
success.

The output was a 64-row prototype window. MIDI events were normalized across
the source, but the ROM was not the complete song and no section name is
inferred from the available evidence.

## Human evidence

Human listened to the generated ROM in SameBoy and supplied these unchanged
statements:

> Maple Leaf Ragとは全く違う曲になっていました。

> 曲としても成立していませんが、自動作曲よりは進歩しているように感じます。

Therefore the Human evidence establishes that the result was not recognized as
Maple Leaf Rag, was judged not to constitute a song, and was felt to be an
improvement over the previous automatic-composition method. It does not establish
production suitability.

## Established capabilities

| area | assessment |
|---|---|
| technical pipeline | confirmed for this source and 64-row prototype |
| artifact/provenance tracking | confirmed for the recorded run metadata and hashes |
| 4ch transformation execution | mechanically executed with explicit mapping and loss reports |
| JSON/UGE/ASM integration | confirmed by validation/build |
| rights/provenance | source conditions remain those classified in the rights investigation; generated MusicXML clearance and derived-artifact scope are not universally confirmed |
| musical preservation | not confirmed; Human did not recognize the result as Maple Leaf Rag |
| musical quality | not achieved according to the Human statement |
| production readiness | not established; no Human approval for production BGM |

## Known lossy transformations

These transformations are confirmed to exist in the implementation, but none is
confirmed as the cause of the Human result:

- MIDI-derived voices, staff, and spelling are reconstructed.
- repeats, endings, articulation, dynamics, and notation semantics are lost or unknown.
- logical roles are extracted by parsed-part/average-pitch ranking.
- polyphony is reduced deterministically; same quantized-row notes can be omitted.
- range changes use octave shifts and can reject out-of-range events.
- source timing is quantized on a 30-tick grid.
- output is limited to one 64-row JSON pattern window.
- CH4 is unused; piano pitch is not silently converted to noise.

## Unknown cause / diagnostic boundaries

| boundary | machine validation | musical equivalence | known loss / Human check |
|---|---|---|---|
| Mutopia MIDI | hash/source validated | not separately evaluated | Human/source comparison needed |
| MIDI parser | deterministic execution | not confirmed | event interpretation diagnostic needed |
| MIDI → MusicXML | deterministic output/hash | not confirmed | reconstructed notation; compare events |
| MusicXML → NormalizedScore | executed | not confirmed | parser/event preservation diagnostic |
| role extraction/melody | JSON generated | not confirmed | average-pitch and selection effects unknown |
| harmony/accompaniment/bass | JSON generated | not confirmed | reduction effects unknown |
| polyphony reduction | reports omissions | not confirmed | omitted-event comparison needed |
| pitch/octave transformation | explicit output | not confirmed | transformed contour/range comparison needed |
| quantization | grid recorded | not confirmed | onset/duration comparison needed |
| 64-row window | machine range recorded | not confirmed | window contribution unknown |
| JSON V2 emission | validator accepted | not confirmed | runtime musical equivalence unknown |
| JSON → UGE/ASM | tools/build accepted | not confirmed | playback equivalence not isolated |
| runtime playback | ROM built and heard | Human found result unlike source | playback/runtime contribution unknown |

The table separates confirmed causes from candidates. No cause is confirmed by
the current evidence.

## Rights and provenance state

The Mutopia source identity and source hash are recorded. The composition/source
rights classifications from the rights investigation remain in force. This
evaluation does not convert any `conditionally allowed` or `unclear` status into
permission. The source and generated MusicXML were not committed to the
repository.

## Production readiness

The current prototype is not established as production BGM. In particular,
Human approval for Pocket Sweeper production use was not obtained. This is not a
decision to reject the method, Maple Leaf Rag, MIDI-to-MusicXML, or 4ch output.

## Remaining Human decisions

Any continued use requires a Human decision about whether to pursue Maple Leaf
Rag, another source/conversion path, improved reduction, or diagnostic work.
The individual unassessed melody, bass/accompaniment/rhythm, tempo, loop, and
Game Boy BGM observations remain open.

## Recommended next investigation

Before parameter tuning, propose a follow-up diagnostic task that compares each
boundary using note pitch, onset, duration, melody contour, bass contour,
simultaneous-note count, event count, omissions, and transformations:

```text
Mutopia MIDI → MIDI events → MusicXML → NormalizedScore → ArrangementPlan
             → JSON → UGE/ROM
```

The diagnostic should retain source event IDs and report differences at each
stage. It is a proposal only; no large diagnostic implementation was started in
WBS-001-01695.

## Explicit non-conclusions

This evidence does not prove that PD automatic arrangement is impossible, that
MIDI-to-MusicXML failed as a method, that Maple Leaf Rag is unsuitable for Game
Boy, that 4ch arrangement is impossible, or that the previous method was made
practical. It also does not approve production BGM.

## Existing test issue

The full test suite still contains the known `tests/test_validate_wbs.py` fixed
count issue (expected 679 versus current WBS count 696). It is unrelated to the
music evaluation and was not changed in this WBS.
