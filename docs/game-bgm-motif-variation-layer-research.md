# ゲームBGMにおけるmotif反復・変奏とlayer設計

対象WBS: `WBS-001-01561`
調査日: 2026-09-25

## 範囲と結論

本調査は、一般音楽理論の用語定義（01560）やloop一般の問題設定（01558）を再掲するものではなく、ゲームBGMでmotif、repetition、variation、layerを運用する際の根拠を整理するものである。

資料から支持できる中心結論は、ゲーム中の滞在時間を予測できないため、反復を前提にしつつ、反復が機械的に露呈することを避ける複数の変化手段を設計候補にする、ということである。ただし、変化を増やすほど良い、特定の回数・確率・秒数が最適、またはlayer欠落時にも必ず成立する、とは資料から確定できない。

## 情報源と採用根拠

### 1. A Survey of Variation Techniques for Repetitive Games Music

- 資料名: “A Survey of Variation Techniques for Repetitive Games Music”
- 著者: Axel Berndt, Raimund Dachselt, Rainer Groh
- 書誌情報: *Proceedings of the 7th Audio Mostly Conference*, ACM SIGCHI, 2012, pp. 61–67, DOI [10.1145/2371456.2371466](https://doi.org/10.1145/2371456.2371466)
- 参照先: [TU Dresden掲載PDF](https://mt.inf.tu-dresden.de/cnt/uploads/2012/12/2012-AM-SurveyOfVariationTechniquesForRepetitiveGamesMusic.pdf)、[Paderborn書誌情報](https://ris.uni-paderborn.de/record/47380)
- 参照内容: ゲーム内滞在時間が予測困難で連続loopが必要になること、反復が露呈する危険、反復を隠す／変える作曲、編曲、演奏、生成の技法をサーベイしている。
- 採用根拠: 可変滞在時間、exact repetitionとmodified repetitionの区別、variationを複数の音楽要素へ適用する候補を、ゲーム音楽固有の資料から得るために採用した。

### 2. Wwise 2012 Interactive Music: Re-sequencing / Re-orchestration

- 資料名: Wwise 2012 Interactive Music course, “Lesson 1: Re-sequencing – Creating Variation Using a Sequential Approach” / “Lesson 2: Re-orchestration – Using a Layered Approach”
- 組織: Audiokinetic
- URL: [Looping a Music Segment using a Playlist Container](https://www.audiokinetic.com/courses/wwise201/?id=looping_music_segment_using_playlist_container&source=wwise201)
- 参照内容: sequentialなセグメント選択によるvariationと、layered approachによるre-orchestrationを別の設計手段として扱い、Music Playlist Containerでセグメント反復を構成する。
- 採用根拠: 「時間方向に別セクションを選ぶ」方法と「同じ時間軸でlayerを加減する」方法を分離する根拠とした。Pocket SweeperへWwiseの機能を導入する根拠ではない。

### 3. Wwise公式 Interactive Music overview

- 資料名: “Creating interactive music” / “The Wwise Project: Adventures in Music”
- 組織: Audiokinetic
- URL: [Creating interactive music](https://www.audiokinetic.com/en/public-library/2024.1.8_8893/?id=creating_interactive_music&source=Help)、[Adventures in Music PDF](https://www.audiokinetic.com/download/documents/WwiseProjectAdventure_en.pdf)
- 参照内容: Music Segment、Music Track、Playlist、Switch、time-synced layers、horizontal（時間同期したlayerの変化）とvertical（loop区間内の多様化）を説明している。
- 採用根拠: layerをmelody等の固定channel名ではなく、同期した音楽部品の追加・削減・切替として捉える根拠とした。高度なinteractive systemは参考技法にとどめる。

### 4. Oxford Handbook of Interactive Audio 第7章

- 資料名: “How Can Interactive Music be Used in Virtual Worlds Like World of Warcraft?”
- 著者: Jon Inge Lomeland
- 書誌情報: *The Oxford Handbook of Interactive Audio*, Oxford University Press, 2014。 [書誌ページ](https://academic.oup.com/edited-volume/37182/chapter-abstract/324106701)
- 参照内容: 長時間・反復的に聴かれるゲーム音楽、listener fatigue、変化とゲーム体験の一貫性の両立を論じる資料として01558で確認した。
- 採用根拠: 反復疲労を避ける変化が、ゲームの記憶性・役割・一貫性を損なう可能性もある、という制約付きの判断に用いる。

### 5. FMOD公式 Core API overview

- 資料名: “Core API Key Concepts”
- 組織: Firelight Technologies / FMOD
- URL: [FMOD Core API Key Concepts](https://www.fmod.com/docs/2.03/api/core-api-concepts.html)
- 参照内容: FMODをadaptive game audioの実行基盤として位置づけ、ゲーム条件に応じて音楽・音響を扱う考え方を説明している。
- 採用根拠: adaptive／interactive musicが一般的な技法であることの補助資料とする。ただし、Pocket SweeperがFMODの機能や高度なadaptive musicを採用する根拠にはしない。

## Motif identity

motifのidentityは、単一の音高列だけでなく、複数の手掛かりの組合せで認識される。01560の一般理論整理とBerndtらのゲーム音楽サーベイを踏まえ、生成上は次を別属性として扱うのが妥当な候補である。

- **保持しやすい核:** pitch contour（上行・下行・反復の輪郭）、主要intervalの関係、rhythmic cell、phrase内の位置、反復時の開始・終端の機能。
- **変化候補:** 絶対pitchやoctave/register、note duration、articulation、細部の音高、伴奏、音色・instrumentation、音数・density、layerの有無。
- **注意:** 資料は「どの要素を必ず保持すればmotifを認識できるか」を普遍的に決めていない。contourを保ってrhythmを変える場合、rhythmを保ってpitchを変える場合などは、変奏タイプごとに人が識別性を評価する必要がある。

従って、motif preservationは「全音符を一致させる」hard constraintではなく、保持属性と変化属性を明示する設計項目・評価項目とする。

## RepetitionとVariation

### Repetition

ゲームではプレイヤーの滞在時間が不定で、同じ場面の音楽をloopし続ける必要がある。exact repetitionはmotif・場面・ゲームのidentityを覚えやすくする一方、短い周期で同じ音型・音色・密度が戻ると反復が露呈し、疲労や単調感につながり得る。modified repetitionは、核を残して一部を変えるため、記憶性と長時間耐性の両方を検討できる。

### Variationの候補

BerndtらのサーベイおよびWwiseのre-sequencing／re-orchestrationの区別から、候補を次のように分類する。ただし、資料は全候補の併用や最適な量を要求していない。

| 分類 | 変化候補 | ゲームBGMでの意味 |
| --- | --- | --- |
| melody/rhythm | rhythmic variation、pitch/melodic variation、interval、adding/removing notes | motifの核を一部保持したmodified repetition |
| timing/発音 | octave/register、duration、articulation | 同じ素材の聴感を変える |
| harmony/accompaniment | reharmonization、伴奏pattern、bass/和声の変化 | melodyを維持し背景を変える |
| orchestration | instrumentation/timbre、音域、texture | 同じ時間構造を別のlayerで響かせる |
| density | layerの追加・削減、音数、rhythmic density | 長時間の厚みや注意量を変える |
| sequence | 別segmentの順序、re-sequencing | 水平方向の反復を遅らせる |

「variation probability」「variation amount」「repetition count」などは将来のparameter候補であり、既定値はこの調査では設定しない。variation頻度と量は、初回、2回目、多数回loop、長時間再生で、motif identityと疲労の両方を人が確認する。

## Layer設計とlayer削減

layerは、melody、accompaniment、bass、rhythmic/percussive material、texture等の機能的な音楽部品として記述できる。Wwise資料が示すlayered re-orchestrationは、同じ時間軸の音楽へlayerを追加・削減する考え方の実例である。これはGame Boyの物理channel割当とは異なる抽象レベルである。

Pocket Sweeperでは、layerを少なくとも次の観点で記録する候補とする。

- **essential information:** motif、調性・進行、拍・phrase境界など、曲の骨格を支える情報。
- **optional information:** doubling、装飾、対旋律、厚み、補助rhythm、textureなど、欠落しても骨格が残ることを目指せる情報。
- **shared support:** motif identityをmelodyだけへ集中させず、rhythm、register、伴奏の同期など複数手掛かりで支える可能性。

ただし、外部資料から「melodyは必須」「bassは任意」などの普遍的なlayer階層や、欠落しても必ず自然に聞こえる冗長化則は確認できない。したがって、**graceful degradation**は、SFXで一部BGMが一時欠落するPocket Sweeper固有の設計仮説である。確認候補は、通常、補助layer欠落、複数layer欠落、途中復帰の状態で、motif、調性、拍、phrase進行、loop境界が保たれるかである。これは聴感評価を伴い、未確認のまま成立済みとはしない。

具体的なCH1〜CH4の役割、どのlayerをSFXで失うか、channel数やSFX専用channelは本資料では決めない。

## Attentionと長時間再生

01558の資料が示す可変滞在時間・反復疲労の問題に加え、layerの密度、強いaccent、急なdramatic change、予期しないeventは、音楽のforeground性を高め、盤面を読む注意と競合する可能性がある。一方、familiar repetitionは予測可能性を与え、常に注意を奪うとは限らない。資料は「このBPM」「このnote density」なら安全という値を与えていない。

設計上は、motifを保ちながら、強い変化を頻発させない、layer密度を固定値ではなく候補parameterとして扱う、というsoft rule候補にする。初回だけでなく複数loop・長時間再生で、注意を奪うaccent、急な密度変化、飽き、motifの埋没をHuman evaluationする。

## Adaptive / interactive musicとの区別

Wwiseのvertical layering、horizontal resequencing、playlist、switch、transitionは、layer追加・削減を理解するための一般的なゲームオーディオ技法である。Pocket Sweeperの現仕様はhUGEDriver、共通order、loop metadataを用いるため、今回これらの高度なruntime systemを必須仕様にはしない。

今回採用候補は、静的な曲データ内でmotif、variation、layerの関係を記録し、欠落状態を試聴するという考え方に限る。adaptiveな状態遷移、stinger、vertical remixing、horizontal resequencingの実装は後続で別途決定する。

## 自動生成への利用候補

### Hard constraint候補

- 参照するmotif/layerが存在し、時間位置・loop範囲・データ構造が整合する。
- Layer欠落時にも再生データが不正な時間軸やchannel数にならない、という機械的成立条件。

motifを完全一致させること、特定layerを必須にすることは、資料だけではhard constraintにしない。

### Soft rule候補

- motif identityの一部の手掛かりを保持してmodified repetitionを作る。
- 同一素材のexact repetitionだけを長時間連続させない候補を持つ。
- variation量・頻度を制御し、identity喪失と反復疲労の両方を避ける。
- layer密度やforeground性の急変を頻発させない。
- optional layerが欠落してもessential informationが追える構造を候補にする。

### Parameter候補

`repetition_count`、`variation_type`、`variation_amount`、`variation_probability`、`motif_preservation_features`、`layer_density`、`optional_layer_probability`、`section_density`、`layer_presence`、`foreground_strength`。

数値のdefault、variation率、回数、section長、motif長、layer数は資料根拠なしに決めない。

### Human evaluation

motifを同じものとして認識できるか、exact/modified repetitionの差、飽き・疲労、変化過多、注意の奪われ方、初回・2回目・多数回loopでの印象、layer欠落・復帰時の自然さ、長時間の不快感を試聴で評価する。今回この評価は実施していない。

## Pocket Sweeperへの適用

採用候補:

- motif identityを複数属性で表し、保持・変更する要素を明示する。
- exact repetitionとcontrolled variationを別候補として生成・比較する。
- melody、accompaniment、bass、rhythm、textureを抽象layerとして扱い、密度とpresenceを設計項目にする。
- SFXによる一部layer欠落を、通常再生・欠落・復帰の試聴条件に含める。
- 初回だけでなく複数loopと長時間再生でmotif、疲労、注意、loop境界を評価する。

未確定:

- motif長、反復回数、variation確率・回数・種類の既定値。
- motif identityを担う具体的なpitch/rhythm/registerの優先順位。
- essential/optional layerの具体的分類、channel割当、SFX占有方式。
- adaptive music、vertical remixing、horizontal resequencingの採用。
- 「邪魔にならない」密度・BPM・音域の具体値。

## 21曲のUGE素材

既存約21曲のUGE素材は、motifの多数派、variation方法、layer構成の品質根拠として使用していない。parser/analyzer、format variation、regression用途に限定する01557の扱いを維持する。

## 後続WBSへの引き継ぎ

- **01562:** pulseを用いるaccompaniment / harmonyの具体設計。抽象layerの伴奏をpulse上でどう表現するか。
- **01563:** wave / bassの具体設計。bassをessentialまたはoptionalとする判断はここで分離して検討する。
- **01564:** CH4 noise rhythm / density。rhythmic layerの密度、注意、欠落時の評価を扱う。
- **01565:** hUGETracker / hUGEDriver / Instrument / effect。抽象layerとmotif variationを実装可能な表現へ落とす範囲を確認する。

01561では、CH1〜CH4の固定役割、具体的なpulse/wave/noise実装、Instrument/effect仕様を確定しない。

## 限界

資料は、ゲーム音楽の反復・変奏・layer構造を設計候補として支持するが、Pocket Sweeperに最適な数値、4chでの冗長化、layer欠落時の聴感品質を証明しない。特にgraceful degradation、注意を奪わないこと、長時間の快適さ、motifの識別性はHuman evaluationを必要とする。
