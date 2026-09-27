# Generated song evaluation profile requirements

対象: WBS-001-01673

## 目的とscope

現在の`generation_profile_candidates.py`は、logical generationの4 layerを持つが、変換対象はmelodyのみ、allocationはmelody-001→CH1である。これはJSON→UGE→ASM→ROM pipelineの最小fixtureとしては有用だが、2有音eventのcandidate-01だけではHumanが自動作曲方式の音楽品質を十分に観察できない。

本書は、01674で作成する評価用profileの要件を定義する。production composition rule、pipeline fixture、evaluation profileを分離し、具体的な音楽品質defaultは決めない。

## Requirement classification

|対象|classification|evidence / applicability|allowed use|prohibited inference|status|
|---|---|---|---|---|---|
|既存fixtureのseed再現、JSON/UGE/ASM/ROM生成|pipeline fixture requirement|01591〜01593のimplementation・automated/format validation。pipeline確認範囲|format validation、parser regression、documentation|曲としての品質、layerの十分性|confirmed, fixture scope|
|複数section/phraseとloop境界を観察できる構造|evaluation profile requirement|generated structure仕様、Game-BGMのloop評価方針。評価profileに限定|human_review、structural_comparison、documentation|production曲の最低section数・loop長|provisional, profile scope|
|melodyのmotif repetition/variationを観察できる入力|evaluation profile requirement|01581 melody model、01597 gate、Human評価項目。具体的な回数・note数は未確定|human_review、documentation|最低note数、rest率上限、自然さの保証|provisional|
|accompaniment/bass/noiseを評価対象へ含める候補|evaluation profile requirement|generatorが4 logical layerを生成可能、sound-specの役割分離。logical coverageの要件|structural_comparison、human_review、documentation|4 layer必須、特定channel role、音楽品質保証|provisional|
|logical layerからphysical channelへの明示allocation|pipeline fixture / evaluation profile requirement|01585 allocation model、logical≠physical。profileの入力整合性|format_validation、human_review、documentation|melody=CH1等をGame Boy一般ruleやproduction defaultにすること|conditional, caller-supplied|
|tempo / ticks_per_row契約の整合|pipeline fixture / evaluation profile requirement|JSON Version 2、hUGEDriver実装、同一run Human確認。tempoはSong Version 6 TicksPerRow|format_validation、parser_regression、human_review|BPM相当値の推測、`tempo=1`の一般default化|confirmed, explicit contract|
|SFX共存|evaluation profile requirementの観察対象|sound-specと01585。profileがSFXを実装・保証する条件ではない|human_review、documentation|SFX聴感のmachine保証|conditional, later review|

## Evaluation profile requirements for 01674

01674のprofileは、次を明示入力として持てること。

- melody、accompaniment、bass、noiseの各logical layerを、評価対象として含めるか個別に確認できること。
- 含めるlayerごとにcaller-supplied allocationを持ち、logical objectへphysical channelを固定書き戻さないこと。
- section、phrase、motif、repetition/variation、loopの構造をHumanが観察できること。ただし具体的な最低数・長さは未確定とする。
- absolute pitch、instrument、noise mapping、tempo/TicksPerRow、resolution contextを明示し、silent fallbackしないこと。
- 同一profile・seedからJSON、UGE、ASM、ROMを再生成できること。
- pipeline fixtureの最小候補とは別profileであることをmetadataと文書で示すこと。

「評価対象にlayerを含める」はcoverage requirementであり、「完成BGMは必ず全layerを使う」というcomposition ruleではない。評価profileの構造は、Humanに観察材料を渡すためのものに限定する。

## Machine-checkable requirements

01674/01675では、既存API・pipelineで次を検証する。

- generation input、candidate ordering、seedの再現性。
- logical layer referenceと明示allocationの整合、physical capability、exclusive allocation。
- event、phrase、pattern、pitch/noise mapping、instrumentのreference整合。
- JSON Version 2のtempo、order、pattern、note length、loop、4 channel構造。
- UGE Song Version 6、order alignment、pattern/order参照、既存analyzerの構造検証。
- JSON→ASM変換成功、ASM descriptorのtempo、pattern/order、loop metadata。
- RGBDSによる確認ROM build成功。
- 同一runのJSON/UGE/ASM/ROM pathとhashの対応。

これらは構造・変換・toolchainの成立条件であり、Humanが「良い曲」と判断する証拠ではない。

## Human-only evaluation

01677へ残す項目は次のとおり。

- 曲として成立しているか。
- melody、伴奏、bass、noiseの役割が聴感上確認できるか。
- Pocket Sweeperのプレイ中BGMとして適切か。
- loopの自然さ、長時間再生時の品質。
- 必要な場合のSFX共存、欠損、復帰の聴感。

自動検証成功やlayer数から、これらを判定しない。

## Unresolved parameters

以下は01674で明示選択が必要になり得るが、01673では値を決めない。

- minimum note/event count、rest density、melody range、motif length。
- phrase/section数、loop length、repetition/variation amount。
- key、scale、harmony progression、accompaniment realization、bass relation。
- layer presence、allocation、register、instrument、wave/noise mapping。
- tempo/TicksPerRowの候補値。BPMからの自動推測はしない。
- SFX occupancy、degradation policy、Human評価時間。

21曲UGEはこれらのdefaultや品質基準の根拠に使用しない。許可用途はformat、parser、regression、structural comparisonに限定する。

## Handoff to WBS-001-01674

01674はこの文書を入力として、既存fixtureを変更せず、評価用profileを別ファイルまたは明示的profileとして実装する。profileの目的を「Humanが観察可能な候補を作る」と記録し、production composition ruleと区別する。値を追加する場合は01575/01577のsource、evidence、applicability、allowed use、prohibited inference、statusを記録し、根拠不足の値はcaller-owned parameterまたは未確定として残す。
