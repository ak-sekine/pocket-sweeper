# Maple Leaf Rag MIDI → MusicXML → NormalizedScore preservation

## Scope

WBS-001-01698のmachine diagnostic。対象はsource MIDI、parsed MIDI、generated
MusicXML、NormalizedScoreのfull normalized sourceである。ArrangementPlan、
4ch reduction、JSON/UGE/ASM/ROM、Human試聴、64-row windowは対象外。

## Source / provenance

- identity: Mutopia Project `Mutopia-2011/11/13-23`
- URL: `https://www.mutopiaproject.org/ftp/JoplinS/maple/maple.mid`
- source SHA-256: `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- SMF format 1, PPQ 384, 3 tracks
- tool: `tools/analyze_pd_source_preservation.py`, version 1

Source hashは承認済み値と一致した。既存のSMF parser/writer/parserを再利用し、
`midi:tN:eM`のsource_event_idをsidecarへ保持した。MusicXMLへIDは埋め込まず、
track/part内の決定的なnote順序でmappingした。

## Tick conversion / rounding rule

`xml_divisions_to_source_tick_v1`を使用した。

```text
exact = Fraction(xml_value * PPQ, divisions)
```

整数ならexact、それ以外はdeterministic half-up roundingとし、元の有理数、
丸め値、deltaをevent recordへ保存する。今回のPPQ=divisions=384ではnote
onset/durationの丸めは0件だった。MusicXMLのmeasure-local cursorにはwriterの
measure offsetを加えてabsolute source tickへ戻した。

## MIDI source statistics

| field | result |
|---|---:|
| SMF format | 1 |
| PPQ | 384 |
| tracks | 3 |
| parsed note events | 2566 |
| tempo | 500000 microseconds/quarter = 120 BPM |
| meter | 2/4 at tick 0 |

note countは既存parser由来であり、独立した第二MIDI parserによる検証ではない。

## MIDI → MusicXML comparison

| metric | result |
|---|---:|
| source / MusicXML note events | 2566 / 2566 |
| source-to-XML mapping | 2566 (1→1) |
| unmapped / 1→0 / 1→N / N→1 | 0 / 0 / 0 / 0 |
| pitch exact / mismatch / unknown | 2566 / 0 / 0 |
| onset exact / rounded / mismatch | 981 / 0 / 1585 |
| onset max absolute delta | 1152 ticks |
| duration exact / rounded / mismatch | 2566 / 0 / 0 |
| duration max absolute delta | 0 ticks |

PitchはMIDI整数値として一致したが、C#/Db等のnotation spelling保存は主張しない。
voices、staff、spellingは`RECONSTRUCTED`である。

Onset mismatchは実測差分として残した。現在のwriterはsource restを明示的な
MusicXML timing eventとして出力せず、parserはmeasure-local cursorを使うため、
diagnosticはmissing restを推測せず1585件を可視化している。これはHuman評価の
原因とは断定しない。

## MusicXML → NormalizedScore comparison

NormalizedScoreは既存`parse_musicxml`の出力であり、独立parserではない。
generated MusicXMLとの比較は以下の通りだった。

- event count: 2566 → 2566
- pitch exact: 2566
- absolute onset exact: 2566
- duration exact: 2566

これはMusicXMLと既存NormalizedScore表現の内部整合性を示すもので、MIDIから
MusicXMLへのonset mismatchを取り消すものではない。

## Tempo / meter / metadata

- source tempo: 500000 microseconds/quarter、120 BPM
- MusicXML tempo: generated metronome metadata、`RECONSTRUCTED`
- source meter: 2/4
- MusicXML meter: 2/4、source notation preservationではなくmetadata再構成
- NormalizedScore: generated MusicXML metadataを参照
- repeats/endings/articulation/dynamics/notation semantics: source MIDI note
  semanticsには存在しない、またはこの比較対象外。保存を主張しない

## Diagnostic artifacts and determinism

一時出力: `/tmp/pocket-sweeper-01698/run1` と `run2`

| artifact | SHA-256 |
|---|---|
| source MIDI | `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66` |
| generated MusicXML | `955fe1a837bc69c188efe76836e1f5b8fc3c9307a9bc4df29df6f6e2728beab4` |
| diagnostic JSON | `a25edd84e5d83dcf25bbe92d32cce4486cd999581d5e799caa73c756d816c087` |
| diagnostic Markdown | `b35668a4d5d55acfa503e88c4447fcec926ba264bb91e60cf3acf9e13d8d2d52` |

run1/run2の全artifactでhashが一致した。schemaは`maple-pd-diagnostic/v1`。
reportにはsource identity/hash、tool/version、configuration、stage mappings、
summary metrics、metadata、diagnostic hashを記録した。

## Classification and machine conclusion

数値的に一致したnoteは`PRESERVED`、数値差分は`TRANSFORMED`、notationの再生成は
`RECONSTRUCTED`、比較不能な意味論は`UNKNOWN`または`NOT_APPLICABLE`とした。
今回note eventのomitted/rejectedはない。pitch/duration/event countはsourceから
MusicXMLへ一致したが、onsetは部分一致である。MusicXMLとNormalizedScoreは内部的
には一致した。

これはmachine note/timing evidenceのみであり、Maple Leaf Ragらしさ、曲としての
成立、Human評価の原因、音楽品質、production BGM suitabilityは判定しない。

## Handoff to 01699

01699ではこのsidecarのsource_event_idを使い、NormalizedScoreからArrangementPlan
へのmelody/bass/accompaniment role selectionとevent coverageを検証する。今回の
onset差分を原因確定として扱わない。
