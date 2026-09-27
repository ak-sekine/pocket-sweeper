# Maple Leaf Rag prototype リズム診断

## 結論（先に）

source MIDI と NormalizedScore までは、2566音の開始時刻と長さが一致した。一方、現行prototypeはNormalizedScoreの「小節内の位置」だけを30 tick単位で行へ変換しているため、別小節の音も同じrole・rowへ集約される。結果として2566音から16音だけが選択され、2550音が省略された。選択後はJSONが64行のnote/rest列へ詰め直すため、sourceの音符間隔・休符間隔はそのままではない。JSONからUGEへの追加のnote/rhythm差分は、今回のformat-level比較では確認されなかった。

これは機械的な変換事実であり、Humanが「リズムが違う」と感じた原因の確定ではない。

## Scope / inputs

- source: Mutopia `Mutopia-2011/11/13-23`, SHA-256 `3dd712a85fabd267f5a2cee5cb23af4683408c2f29b8814721844498f1ee4f66`
- artifact: 01708 timing-fixed artifact (`/tmp/pocket-sweeper-01705/artifacts`)
- full source/NormalizedScore scope: 2566 note events
- diagnostic tool: `tools/analyze_pd_rhythm_diagnostic.py`
- comparison is machine structural evidence only; no musical-quality score is assigned.

## Source rhythm

| metric | value |
|---|---:|
| note events | 2566 |
| unique absolute onsets | 1005 |
| simultaneous onset groups | 698 |
| simultaneous group sizes | 1:307, 2:280, 3:130, 4:171, 5:79, 6:36, 7:2 |
| duration (ticks) | 96:678, 192:1802, 288:60, 384:12, 480:14 |
| source IOI (ticks) | 96:864, 192:134, 288:6 |

NormalizedScoreはsourceとのonset 2566/2566、duration 2566/2566で一致した。従ってこの診断では、source→NormalizedScore間のrhythm lossは確認されていない。

## Collision and omission

現行実装の実際のkeyは `(role, round(measure_local_start / 30))` である。absolute source onsetやmeasure番号をkeyに含めない。collisionは16 groups、全て複数event、最大389 eventで、selected 16 / omitted 2550となった。

| classification | groups |
|---|---:|
| sourceで同時 (`PREEXISTING_SIMULTANEOUS`) | 0 |
| quantizationだけで新規衝突 | 0 |
| 別measureのlocal cursor集約 (`CROSS_MEASURE_LOCAL_CURSOR_AGGREGATION`) | 16 |

従って2550件は、source MIDI上で同時だったためだけに省略されたものではない。今回のmachine evidenceでは、別measureのeventが同じmeasure-local rowへ集約された後、`polyphony_omitted`になった。これは現行処理の説明であり、望ましさやHuman原因の判断ではない。

## Quantization

- grid: 30 source ticks
- local onset: exact 629, changed 1937, maximum absolute delta 12 ticks
- duration: exact 14, changed 2552, maximum absolute delta 12 ticks
- quantization-induced collision: 0 groups

onsetの1937件のlocal quantization変化と、2550件のomissionは別の集計である。今回のcollision群はNormalizedScoreのabsolute onset上で同時だった群ではなく、cross-measure local cursor aggregationとして分類された。

## Selected events and interval effect

selected eventはsource timeline全体に散在する。最初のselected onsetは `midi:t2:e210`、17088 ticks (22.25 sec)、最後は `midi:t2:e1372`、110400 ticks (143.75 sec) である。したがって16音は冒頭だけの抜粋ではないが、sourceの音符間隔を保持した16音列でもない。

代表例は、全selected eventをsource onset順に並べたうえで、最初・最後・隣接する最初のbass pairを選んだ。

| source_event_id | source onset | source duration | JSON channel/row/length |
|---|---:|---:|---|
| `midi:t2:e210` | 17088 ticks (22.25s) | 192 ticks | wave / row 0 / length 6 |
| `midi:t2:e211` | 17184 ticks (22.375s) | 192 ticks | wave / row 9 / length 6 |
| `midi:t2:e1372` | 110400 ticks (143.75s) | 192 ticks | wave / row 27 / length 6 |

隣接するsource音のIOI 96 ticks (0.125 sec) が、JSONではtoken cursor上の9 rows (0.9 sec)になる例がある。またsource上で121.5秒以上離れた最初と最後のselected eventが、prototypeの同じ64-row pattern内に再配置される。これはsource timelineの圧縮・再配置を示すが、Human聴感の因果は未確定である。

## JSON token / channel / UGE

JSONはsource event indexed列ではなく、note/rest tokenとlengthでcursorを進める列である。selected 16 notesは pulse1 8、wave 8、pulse2 0、noise 0。pulse1/waveのtoken列は各channelで終端cursor 64、patternは4個、各patternは64 rows、orderは1件。sourceの長いgapは同じsource時間のrestとして保存されず、64-row列へ再配置された後のrest/cursorとして表現される。

JSON→UGEでは、JSON 16 notesとUGE 16 notesのrow/token/instrument/pattern対応に追加のomissionまたはrhythm mismatchは確認されなかった。これはformat-levelの結果であり、hUGEDriverの実時間・APU出力・Human聴感を証明しない。

## Timing-fix前後

canonical evidenceでは、timing修正前は2566→31、修正後は2566→16。今回の診断は修正後の16群を、cross-measure local cursor aggregationとして説明する。修正前31群との全event単位の差分artifactはこの診断入力に含めていないため、31→16の全原因を本書だけで確定しない。

## Machine conclusions / non-conclusions

確認できたのは、source→NormalizedScoreのonset/duration保存、現行row collision key、16 groups、2550 omission、JSON token再配置、UGEへの追加lossなしである。確認できないのは、これらのどれがHuman評価の原因か、またどの改善が有効かである。01714で音程・メロディを別途診断する。

## Reproducibility

実行:

```text
python3 tools/analyze_pd_rhythm_diagnostic.py /tmp/pocket-sweeper-01705/maple.mid /tmp/pocket-sweeper-01705/artifacts /tmp/pocket-sweeper-01713/run1
python3 tools/analyze_pd_rhythm_diagnostic.py /tmp/pocket-sweeper-01705/maple.mid /tmp/pocket-sweeper-01705/artifacts /tmp/pocket-sweeper-01713/run2
```

canonical diagnostic hash (run1/run2): JSON `3532e59ed96f040302c9a7abbbe13d8272aa2b61c35fd3ff1859d8eccaa9ca87`、Markdown `24c8c1944d9e2592137b1485c67edb9f75bac7f35c15fdbbe38b54462d207b3e`。

## Handoff

WBS-001-01714ではsource pitch、role選択、octave変換、JSON/UGE pitchを同じsource_event_idで比較する。
