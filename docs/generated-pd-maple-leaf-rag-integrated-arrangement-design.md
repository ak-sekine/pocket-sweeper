# Maple Leaf Rag 統合編曲方式設計

## 目的

01715のHuman判断に従い、長さ・テンポ・リズム・音程/メロディを個別のparameter tuningではなく、source構造を追跡可能なGame Boy向け縮約として扱う。

## Canonical event contract

各eventは `source_event_id`、track/part、measure、`absolute_onset_tick`、`measure_local_tick`、duration、pitch、logical role、physical channel、selection status、reasonを持つ。collision identityは `(role, physical_channel, quantized_absolute_row)` とし、measure-local tick単独は使用しない。

保持・変換・lossを分離する。

| field | rule |
|---|---|
| absolute onset / measure / event order | 必ずsidecarで保持 |
| duration / pitch / role/channel | outputで変換してもsource値と理由を保持 |
| rest/gap | output tokenのcursorとして明示し、source gapとの差を記録 |
| simultaneous notes | 同一absolute onsetとquantized collisionを別分類 |
| melody continuity | selected source_event_id/measure/onset/interval列で検証 |
| quantization | timing transformとして独立記録 |
| polyphony reduction | collision単位、selection rule、omission reasonを記録 |
| timeline scaling | source秒とruntime row秒を別fieldで記録 |
| tempo conversion | source BPMとTicksPerRowを混同しない |
| repeat/ending | sourceにない意味を推測しない |
| loop | intended metadataとruntime control flowを分離 |

Game Boy 4chへの割当はlogical roleとphysical channelを分離する。既存のP2/P3平均pitch rankingは明示的な暫定ruleとして記録し、主旋律の音楽的正しさとは扱わない。harmony/noiseがない場合は0件をloss reportへ記録する。

JSON V2は変更せず、source provenanceはmanifest/diagnostic sidecarで保持する。64-row patternはprototype windowであり、window外eventはpolyphony omissionと分類しない。

## Completion contract

machine contractは、cross-measure false collisionが0、source_event_idが全入力eventのselected/omitted/window外のいずれかで説明可能、JSON/UGEのencoded pitch/rowがsidecarと一致、source BPM/TicksPerRowの意味が分離されることとする。Humanの原曲認識・曲としての成立・production採用は後続Human taskで判断する。
