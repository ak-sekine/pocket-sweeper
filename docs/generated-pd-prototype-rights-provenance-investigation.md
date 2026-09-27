# prototype用PD曲の権利・provenance調査

対象: WBS-001-01690　調査日: 2026-09-27

## Scope

01687でHumanが「いったんMusicXMLをベースに考えようと思います。」と判断したため、OpenScore Liederの具体的なscoreを候補にした。曲の選択、sourceのdownload、repositoryへの追加は行わない。`confirmed`は一次資料で確認できた事実、`conditionally allowed`は対象範囲と条件が限定された判定、`unclear / not confirmed`は判断しない事項である。

## Rights model

composition（原曲）、edition（版・校訂）、arrangement（編曲）、transcription（採譜）、symbolic encoding（`.mscx`/`.mxl`）、recording（録音）を別identityとして扱う。OpenScore READMEはcontributorsがscoresをtranscribeし、proofreadersがmoderateしたと記載するが、個別の全encoder名や歴史的editionを保証しない。CC0 score dataはrecording、lyrics/translation、第三者editionを自動的に包含しない。

日本文化庁の原則は著作者死後70年。以下のcomposition判定はこの通常則による暫定整理であり、戦時加算・共同著作・翻訳等の最終法律判断ではない。

## Investigation method

OpenScoreのREADME、LICENSE.txt、個別ファイルmetadataと、日本文化庁の著作権期間説明を開いて確認した。READMEのscore path/ID規則、`.mscx`から`.mxl`への`corpus_conversion.json`による公式変換手順、個別source metadataのcomposer/copyright/arranger/sourceを確認した。downloadせず、hashは取得していない。

## Candidate 1: Heidenröslein (D.257)

### Composition

Franz Schubert (1797–1828)、1815作曲としてsource identityが確認できる。日本の通常life+70分析ではcompositionは`confirmed`（歌詞・翻訳は別）。出版年と歴史的editionは今回未確認。

### Concrete MusicXML source

OpenScore/Lieder、`scores/Schubert,_Franz/Op.3/3_Heidenröslein,_D.257/lc30321236.mscx`。repository sourceはMuseScore XML `.mscx`、対応するcompressed MusicXML `.mxl` raw pathは`https://raw.githubusercontent.com/OpenScore/Lieder/main/scores/Schubert,_Franz/Op.3/3_Heidenr%C3%B6slein,_D.257/lc30321236.mxl`。READMEの公式変換経路も利用可能。retrieval date 2026-09-27、hash not obtained。arranger/transcriber/encoder個人名は未確認。

### Source license / Commercial ROM / GitHub publication

OpenScore READMEとLICENSE.txtはscoresをCC0 1.0と明記する。score dataの改変・再配布・商用ROM利用は`conditionally allowed`、OpenScoreはpublic-facing useでcredit/linkをrequestする。MusicXMLのGitHub公開もCC0対象に限り`conditionally allowed`だが、selected commit、変換bytes、歌詞/翻訳、edition、recordingは別途確認が必要。

### Provenance / Technical characteristics / Unresolved items

vocal+piano art-song scoreで、melodyとaccompanimentを持つ候補。exact parts/voices/polyphony/repeats/tempo/complexityは未downloadのため未確認。composition、source path、format、CC0、OpenScore corpus provenanceは確認済み。edition、hash、個人encoder、text rights、最終法的確認は未解決。

## Candidate 2: Wiegenlied (Op.49 No.4)

### Composition

Johannes Brahms (1833–1897)、`5 Lieder, Op.49/4 Wiegenlied`。日本の通常life+70分析でcompositionは`confirmed`。初版日、歴史的editionは未確認。

### Concrete MusicXML source

`https://github.com/OpenScore/Lieder/blob/main/scores/Brahms,_Johannes/5_Lieder,_Op.49/4_Wiegenlied/lc5701612.mscx`。file metadataはcomposer Brahms、work Op.49、`copyright OpenScore (CC0)`、`arranger: Transcribed from #81909`を示す。`.mxl`はREADMEの公式conversion manifestで生成可能だが、このpathのdirect `.mxl` URLは未確認。hash not obtained、retrieval 2026-09-27。

### Source license / Commercial ROM / GitHub publication

CC0 1.0。score dataについて改変、再配布、商用ROM、MusicXML公開は`conditionally allowed`。creditはCC0必須ではないがOpenScoreのrequestに従う。#81909のedition、lyrics、変換出力と第三者素材は未確認。

### Provenance / Technical characteristics / Unresolved items

metadata上のvocal/piano songで、melody+accompaniment候補。exact voices/polyphony/repeats/tempo/complexity、個人transcriber/encoder、edition #81909、hash、text rightsは未確認。

## Candidate 3: Das Wirtshaus (Winterreise D.911 No.21)

### Composition

Franz Schubert (1797–1828)、lyricist Wilhelm Müller (1794–1827)、`Winterreise D.911 No.21`。両名とも日本の通常life+70分析でcomposition/text originalは`confirmed`だが、translationは別。出版史は未確認。

### Concrete MusicXML source

`https://github.com/OpenScore/Lieder/blob/main/scores/Schubert,_Franz/Winterreise,_D.911/21_Das_Wirthshaus/lc5013945.mscx`。metadataはSchubert/Müller、`copyright Creative Commons copyright waiver (CC0 1.0 Universal)`、`Transcribed by pental from IMSLP #60822`を示す。`.mxl`は公式conversion経路、direct URL/hashは未確認。retrieval 2026-09-27。

### Source license / Commercial ROM / GitHub publication

CC0 1.0。score dataの改変・再配布・商用ROM・MusicXML公開は`conditionally allowed`。creditはrequest。IMSLP #60822のedition、詩/翻訳、recording、変換bytesは未確認。

### Provenance / Technical characteristics / Unresolved items

metadataからvoice+keyboard/piano、4/4、key、tempo/direction、articulationを確認できる。exact polyphony/repeats/complexityは未解析。edition #60822、text rights、hash、converter versionは未解決。

## Candidate 4: Fischerweise (D.881)

### Composition

Franz Schubert (1797–1828)、`4 Lieder Op.96/4 Fischerweise D.881`。日本の通常life+70分析でcompositionは`confirmed`、初版日・edition・lyricsは未確認。

### Concrete MusicXML source

`https://github.com/OpenScore/Lieder/blob/main/scores/Schubert,_Franz/4_Lieder,_Op.96/4_Fischerweise,_D.881/lc6487832.mscx`。file identityとSchubert/Op.96 metadata、OpenScore CC0を確認。`.mxl`は公式conversion manifestで生成する経路、direct `.mxl`、個人transcriber/encoder、hashは未確認。retrieval 2026-09-27。

### Source license / Commercial ROM / GitHub publication

CC0 1.0。対象score dataに限り改変・再配布・商用ROM・MusicXML公開は`conditionally allowed`、creditはrequest。edition、text、recording、converter outputは未確認。

### Provenance / Technical characteristics / Unresolved items

structured vocal/piano scoreでmelody+accompaniment候補。exact parts/voices/polyphony/repeats/tempo/complexity、edition、個人transcriber、hashは未解決。

## Candidate comparison

|候補|composer|composition PD|MusicXML source|source license|商用ROM|MusicXML repo公開|attribution|未確認事項|
|---|---|---|---|---|---|---|---|---|
|Heidenröslein D.257|Schubert, 1828死亡|confirmed: ordinary life+70|`lc30321236.mscx` + direct `.mxl` path|CC0 1.0|conditionally allowed|conditionally allowed with sidecar|CC0非必須、credit request|edition/hash/text/encoder|
|Wiegenlied Op.49/4|Brahms, 1897死亡|confirmed: ordinary life+70|`lc5701612.mscx` + official `.mxl` conversion|CC0 1.0|conditionally allowed|conditionally allowed with sidecar|same|#81909/hash/text/conversion|
|Das Wirtshaus D.911/21|Schubert/Müller, 1828/1827|confirmed: ordinary life+70|`lc5013945.mscx` + official `.mxl` conversion|CC0 1.0|conditionally allowed|conditionally allowed with sidecar|same|#60822/translation/hash|
|Fischerweise D.881|Schubert, 1828死亡|confirmed: ordinary life+70|`lc6487832.mscx` + official `.mxl` conversion|CC0 1.0|conditionally allowed|conditionally allowed with sidecar|same|edition/text/hash/encoder|

順位は付けない。全候補はHumanの比較対象であり、Codexは選択しない。

## Repository storage options

現在はURL/path/license/metadataのみを保存する。01691でHumanが選択後、MusicXML自体を保存する場合は、OpenScore commit、変換tool/version、hash、CC0/license、credit、edition/transcriber情報をsidecarに固定する。CC0対象のscore dataは`conditionally allowed`だが、exact converted file、lyrics/translation、edition、recordingを自動的に許可済みとは扱わない。

## Commercial-use and derived-artifact considerations

normalized data、ArrangementPlan、JSON Version 2、UGE、ASM、ROMは、CC0対象のscore dataから作る範囲では`conditionally allowed`と整理できる。しかし資料はPocket Sweeperの変換chainを個別承認していないため、独立した許諾と推測せず、Human選択後にsource範囲と第三者素材を確認する。prototype内部利用と有料ROM・GitHub再配布は分ける。

## Provenance fields

composition identity、composer/lyricist、source project/URL/path/score ID、format、license、edition/IMSLP ID、arranger、transcriber、encoder、OpenScore commit、conversion tool/version、retrieval date、source hash、normalization/arrangement設定、generated artifact hashesを記録する。本調査ではdownloadせずhash/selected commitは未取得。

## Unresolved items

Humanの曲・source・利用範囲選択、exact commitとhash、`.mxl` conversion output、edition、個人encoder、lyrics/translation、商用配布の最終法的確認、parts/voices/polyphony/repeats/tempo/complexityのparser実測が未解決。

## Human decision points for WBS-001-01691

Humanは候補、prototype-onlyかcommercial-releaseまでか、MusicXMLをrepoへcommitするか、normalized/JSON/UGE/ASM/ROMの公開範囲、credit、未確認事項の扱いを選択する。Codexは曲を決定しない。

## External evidence

|URL|title/provider|確認した事実|調査日|
|---|---|---|---|
|https://github.com/OpenScore/Lieder|OpenScore Lieder README/repository|score path/ID規則、`.mscx`、公式`.mxl`変換、CC0、transcription/proofreading方針|2026-09-27|
|https://github.com/OpenScore/Lieder/blob/main/LICENSE.txt|OpenScore CC0-1.0 LICENSE|repositoryがリンクするlicense本文|2026-09-27|
|https://github.com/OpenScore/Lieder/blob/main/scores/Schubert%2C_Franz%2FOp.3%2F3_Heidenr%C3%B6slein%2C_D.257%2Flc30321236.mscx|個別source|file identity、composer/work metadata、direct `.mxl` pathの手掛かり|2026-09-27|
|https://github.com/OpenScore/Lieder/blob/main/scores/Brahms%2C_Johannes%2F5_Lieder%2C_Op.49%2F4_Wiegenlied%2Flc5701612.mscx|個別source|Brahms/Op.49、OpenScore CC0、`Transcribed from #81909`|2026-09-27|
|https://github.com/OpenScore/Lieder/blob/main/scores/Schubert%2C_Franz%2FWinterreise%2C_D.911%2F21_Das_Wirthshaus%2Flc5013945.mscx|個別source|Schubert/Müller、CC0、`Transcribed by pental from IMSLP #60822`|2026-09-27|
|https://github.com/OpenScore/Lieder/blob/main/scores/Schubert%2C_Franz%2F4_Lieder%2C_Op.96%2F4_Fischerweise%2C_D.881%2Flc6487832.mscx|個別source|Schubert/Op.96、OpenScore CC0|2026-09-27|
|https://www.bunka.go.jp/english/policy/copyright/system/|Japan Agency for Cultural Affairs|著作者死後70年を原則とする保護期間と例外|2026-09-27|
