# 一般音楽理論由来の作曲生成ルール

対象WBS: `WBS-001-01573`
調査基準日: 2026-09-26

## 1. 目的

01560で調査した一般音楽理論を、自動作曲器が扱える生成ルール候補、parameter、検証条件へ変換する。理論上定義できる関係と、Pocket Sweeperで採用する方針、Game-BGMの長時間loop向け技法、実際の試聴で評価すべき品質を分離する。

本書はscale、key、melody、motif、phrase、harmony、rhythm、cadence、bass、accompanimentの最終値や具体的な4ch割当を決めない。後続01575で根拠記録形式を正式化し、01576で層のデータ表現と制約管理を決める。

## 2. 根拠資料

### 2.1 一般音楽理論

|資料|追跡する内容|
|---|---|
|`docs/general-music-theory-for-rule-based-generation.md`（01560）|本書の最優先根拠。以下の一次・教育資料との対応、適用条件、未確定事項を再利用する。|
|Open Music Theory|interval、scale、melody、phrase、harmony、cadence、meter、syncopationの定義。<https://open-musictheory.github.io/>|
|Benward / Saker, *Music in Theory and Practice Vol. 1*|melody・harmony・rhythmの相互作用、phraseとcadence。01560の公開教材版リンクを参照する。|
|*Understanding Basic Music Theory*|motif、phrase、scale、key、meter、rhythmの入門的関係。<https://www.opentextbooks.org.hk/ditatopic/2180>|
|College Board AP Music Theory CED|cadence、authentic cadence、phrase、harmonic rhythm。PAC等はこの理論体系の条件として限定する。<https://apcentral.collegeboard.org/media/pdf/ap-music-theory-course-and-exam-description.pdf>|
|Berklee Harmony / Core Music Curriculum|melodic development、tonal harmony、counterpoint、およびcommon-practiceとcontemporary styleの区別。<https://college.berklee.edu/harmony>|

### 2.2 適用条件の根拠

|資料|本書での用途|
|---|---|
|`docs/game-boy-hardware-composition-rules.md`（01572）|4ch、1channel 1発音、note範囲、Wave/Noise等のhardware/tool境界。一般理論とは別分類で参照する。|
|`docs/game-bgm-composition-loop-research.md`|長時間loop、反復、variation、attention、closureのGame-BGM由来条件。|
|`docs/game-bgm-motif-variation-layer-research.md`|motif反復・変奏・layer変化のGame-BGM由来条件。|
|`docs/game-boy-pulse-accompaniment-harmony-research.md`|pulse伴奏・harmonyのGame Boy適用候補。CH割当を一般理論と混同しない。|
|`docs/game-boy-wave-bass-design-research.md`|bass layerとCH3の接続候補。`bass = CH3`を理論規則にしない。|
|`docs/game-boy-ch4-noise-rhythm-density-research.md`|rhythm/densityとCH4 Noiseの接続候補。drum役割を一般理論の必須事項にしない。|
|`docs/sound-spec.md` / `docs/json-format.md`|Pocket SweeperのBGM/SFX共存、JSONの時間・note表現、hUGE rowとの境界。|

## 3. 分類

- **Theory relationship**: scale degree、interval、chord tone、phrase、cadenceなど、理論上の関係。存在を表現できることと、必ず採用することを分ける。
- **Hard constraint**: 生成modeやparameterを明示的に選んだ場合、その内部整合性を守る条件。全音楽へ一般化しない。
- **Soft rule**: 候補の重み、優先順位、scoreへ使える傾向。違反してもinvalidではない。
- **Parameter**: Pocket Sweeper側で選択・調整する値。根拠資料にないdefaultは固定しない。
- **Human evaluation**: 理論資料や形式検査だけでは品質を確定できず、試聴が必要な項目。
- **Game-BGM relationship**: 長時間loopやゲーム中の注意との共存から生じる関係。一般理論とは別の根拠として記録する。

## 4. ルール一覧

|ID|分類|理論上の関係・ルール候補|生成時の状態/parameter|適用条件|機械検証|Game Boy / Game-BGM注意|Pocket Sweeperでの状態|
|---|---|---|---|---|---|---|---|
|MT-THEORY-001|Theory relationship|key/tonal center、scale、pitch class、octave、scale degreeを分離する|`key`、`scale`、`pitch_class`、`octave`、`scale_degree`|調性またはscaleを選ぶ生成|参照値とpitch classの整合|APUのnote範囲は01572で別検証|候補。major/minorは未選択|
|MT-HARD-001|Hard constraint|`scale_only=true`なら生成noteは選択scale内|`scale_only`、`scale_pitch_classes`|scale-only mode|各noteのpitch class membership|chromatic noteを許すmodeでは適用しない|候補。全曲共通にはしない|
|MT-SOFT-001|Soft rule|melodyのstep/leap、方向、range、contourを候補評価する|interval weight、方向、range、contour|melody候補生成|interval/rangeを計算可能|step必須・leap禁止にはしない|候補。重み未定|
|MT-THEORY-002|Theory relationship|motifはrelative pitch/scale degree、interval、rhythm、duration、rest、accentの関係で保持できる|motif referenceと相対関係|反復・変奏を使う場合|指定変換との差分を検査|具体schemaは01576|候補|
|MT-HARD-002|Hard constraint|exact-repeat modeでは指定区間が同一関係を保つ|`repeat_mode=exact`|exact repetitionを選択|pitch/rhythm/duration等を比較|4chへ展開する方法は別|候補|
|MT-SOFT-002|Soft rule|transposition、rhythmic/pitch/register/layer variationを変奏候補にする|variation type、amount、probability|variationを選択した場合|変奏量・参照元を記録|long-loop variationはGame-BGM由来|候補。値未定|
|MT-THEORY-003|Theory relationship|phraseはmelody・harmony・rhythmが相対的に完結する単位|phrase boundary、length、motif refs|phraseを表現する場合|boundaryと参照関係|4/8小節を必須にしない|候補|
|MT-SOFT-003|Soft rule|休符、長音、反復切れ目、和声変化、cadenceをphrase boundary候補にする|boundary weights|phrase segmentation|grid上のboundary整合|自然さは試聴|候補|
|MT-THEORY-004|Theory relationship|current chord、root、chord tones、inversion bass、bass noteを分離する|`current_chord`、`root`、`chord_tones`、`bass_note`|harmony layerを生成する場合|chord構成とinversionを検査|rootとbassを同一視しない|候補|
|MT-HARD-003|Hard constraint|`chord_tone_only`を選択したlayerはchord tone集合に属する|`chord_tone_only`|bass/melody等でmodeを選択|note membership|non-chord tone許可modeでは適用しない|候補|
|MT-SOFT-004|Soft rule|chord tone、common tone、nearest movement、functionを候補重みとする|relation weights、harmonic function|style/modeを選択した場合|関係値を計算可能|common-practiceを全曲に強制しない|候補|
|MT-THEORY-005|Theory relationship|progressionはchord sequence、harmonic rhythm、function、cadenceと関係する|chord sequence、change positions、function|progressionを扱う場合|参照chordと時間位置を検査|I-V-vi-IVをdefaultにしない|候補|
|MT-HARD-004|Hard constraint|`functional_harmony_mode`選択時のみ、指定function/cadence関係を検査する|`functional_harmony_mode`|functional harmonyを採用した場合|mode内のfunction参照整合|採用しない曲にも適用しない|候補|
|MT-SOFT-005|Soft rule|passing/neighbor/suspension等のnon-chord toneを位置・長さ・解決候補で評価する|non-chord type、resolution weight|non-chord tone許可mode|前後note/chordとの関係を検査|non-chord toneをinvalidにしない|候補。確率未定|
|MT-SOFT-006|Soft rule|voice leadingのcommon tone、nearest movement、stepwise connectionを優先候補にする|voice-leading weights|採用styleが指定された場合|voice間の移動量・crossingを計算|全Game Boy音楽のhard constraintにしない|候補|
|MT-THEORY-006|Theory relationship|beat、meter、measure、subdivision、onset、duration、rest、accent、syncopationを分離する|meter、tempo、subdivision、event timing|rhythmを生成する場合|time grid上のevent整合|4/4や四分音符を固定しない|候補|
|MT-HARD-005|Hard constraint|`fixed_meter`/`fixed_grid`選択時はeventが定義grid内|meter、grid、start/duration|fixed time mode|開始・長さ・小節境界を検査|hUGE row/pattern/orderとは別層|候補|
|MT-SOFT-007|Soft rule|rhythmic repetition、accent整合、syncopation、density、restを重みづける|rhythm pattern、density、accent、syncopation|rhythm候補生成|event count/positionを計算可能|具体値はGame-BGM/試聴へ|候補|
|MT-THEORY-007|Theory relationship|cadenceはphrase/harmonic/melodic closureの候補で、強さや種類を持つ|cadence type、closure strength|functionalまたはphrase closureを使う場合|指定終止の関係を検査|PAC等は理論体系限定|候補|
|MT-SOFT-008|Soft rule|authentic、half、deceptive等をphrase終止候補にする|cadence candidates|対応するharmony mode|chord/scale degree/境界を検査|全曲必須ではない|候補|
|MT-THEORY-008|Theory relationship|bassは抽象layerで、root、chord tone、passing、pedal、ostinato等を担える|bass relation、register、pattern|bass layerを生成する場合|chordとの関係を検査|`bass = CH3`ではない|候補|
|MT-SOFT-009|Soft rule|accompanimentはchord support、rhythmic support、arpeggio、broken chord、sustain、counter-lineの候補|accompaniment style、pattern、density|伴奏layerを生成する場合|参照harmony/時間gridを検査|`accompaniment = CH2`ではない|候補|
|MT-HUMAN-001|Human evaluation|melody、motif、phrase、harmony、rhythm、bass、伴奏の自然さ|試聴記録|生成結果評価|自動判定のみでは不可|hardware-validとは別|未実施|
|MT-GAME-001|Game-BGM relationship|exact repetition、modified repetition、layer variation、attention、long-loop fatigueを分ける|loop、variation、layer presence|ゲームBGMとして反復する場合|loop境界・参照関係は検査可|長時間の快適性は試聴|後続へ引継ぎ|

## 5. scale / key

`key`またはtonal center、`scale`、pitch class、octave、scale degreeを独立状態として扱う。scale degreeを介して移調と生成規則を分離し、absolute pitchとpitch classを混同しない。major/minorは代表的な選択肢だが、Pocket Sweeperの採用scaleやkeyは本WBSで決めない。

chromatic/non-scale noteを表現できるようにし、`scale_only`を選んだときだけscale membershipをHard constraintにする。scale外音を一般的にエラー扱いしない。Game Boyのnote表現可能範囲は01572、hUGE/JSONのC3〜B8はtool constraintとして別に検査する。

## 6. melody

melodyはpitch sequenceとrhythmic sequenceの関係として扱う。各noteについてpitch、scale degree、octave、start、duration、rest、accentを分け、隣接noteからstep/leap、direction、contour、rangeを計算できるようにする。

stepwise motionを優先する、leap後に反対方向のstepを候補にする、rangeを制限する、同一pitchやmotifを反復する、といったものはSoft ruleまたはParameter候補である。step必須、大きなleap禁止、特定range固定にはしない。最大interval、方向連続数、repetition probability、rest probability等の具体defaultは根拠不足のため決めない。

## 7. motif / phrase

motifを単なる絶対note列ではなく、relative pitchまたはscale degree、interval、rhythm、duration、rest、accent、layer関係の一部または組合せで参照できるものとして定義する。何を不変にして何を変えるかを記録すれば、exact repetition、transposition/sequence、rhythmic variation、pitch variation、register variation、accompaniment/layer variationを区別できる。

phraseはmotifより上位の時間単位で、melody、harmony、rhythmのまとまりとboundaryを持つ。boundary候補は休符、長音、反復切れ目、和声変化、cadence、accent変化である。phrase lengthをparameterとし、4小節・8小節を一般必須値にしない。具体的なmotif/phrase schemaは01576へ引き継ぐ。

## 8. repetition / variation

一般理論上のrepetitionは素材の再提示、sequenceは一定関係での移動、variationはpitch、rhythm、register、伴奏等の一部変更として扱う。Game-BGMでは、ゲーム滞在時間が不定でexact repetitionが露呈し得るため、modified repetition、layer variation、再配置を別のGame-BGM関係として記録する。

variationを増やすほど良いとも、exact repetitionを禁止するとも定義しない。motif identity、予測可能性、loop疲労、attentionのバランスは試聴対象である。

## 9. harmony / chord / progression

`chord`、`root`、`chord_tone`、`inversion`、`bass_note`、`harmonic_function`を分離する。chord rootとbass noteは一致する場合もあるが、inversionやpedalなどにより同一ではない。chord progressionはchord sequenceとharmonic rhythmを持ち、I-V-vi-IV等の特定進行をdefaultにしない。

tonic/predominant/dominantのfunctionは`functional_harmony_mode`を選んだときだけ利用する。採用しない曲にfunctionを強制しない。melody noteとcurrent chordの関係はchord tone、non-chord tone、passing、neighbor等の関係として保持する。

## 10. non-chord tone / voice leading

passing tone、neighbor、suspension等のnon-chord toneをinvalidにしない。`chord_tone_only`、`allow_non_chord_tone`、strong beat/weak beat、resolution candidate等のmode・parameterで扱う。どの種類を何％使うかは未確定とする。

voice leadingではcommon tone、nearest movement、stepwise connection、voice crossing、parallel motionを関係・評価候補として持つ。common-practiceの特定禁止規則を全Game Boy音楽のHard constraintにしない。4chや1channel 1発音は01572由来であり、voice-leading theoryとは別の制約である。

## 11. rhythm / meter / time grid

beat、meter、measure、subdivision、tempo、onset、duration、rest、accent、syncopationを別状態にする。4/4、一定BPM、四分音符中心、常時一定densityは固定しない。

音楽時間の抽象gridを`meter`、`tempo`、`ticks_per_beat`、`measure_index`、`beat_position`、`subdivision`、`start_tick`、`duration_ticks`で表現し、後でhUGE rowへ量子化できるようにする。musical beat/measure/subdivisionとhUGE row/pattern/orderは異なる層である。実際の量子化・channel同期schemaは01576へ渡す。

rhythm patternはonset、duration、rest、accent、syncopation、densityの組合せである。restを必ず一定割合入れる規則は作らない。note durationは発音時間だけでなくphrase boundary、密度、articulation候補として扱う。

## 12. cadence

cadenceはphraseまたはharmonic progressionの相対的なclosureであり、harmonic closureとmelodic closureが一致する必要はない。authentic cadence、half cadence、deceptive cadence、PACは候補として記録するが、PACの詳細条件は特定の調性理論体系に限定する。

cadence type、closure strength、phrase boundary、final scale degree、終止chord、長音、restを分離する。全曲に強いauthentic cadenceを要求せず、loop境界でのclosureや未完感はGame-BGM設計と試聴へ渡す。

## 13. bass / accompaniment

bassは抽象layerであり、root、chord tone、passing tone、pedal、ostinato、inversionのbass noteなどを候補にできる。`bass note = chord root`を常時必須にせず、`bass = CH3`も一般理論上の規則にしない。register、octave、rhythm、duration、rest、density、variationを独立parameter候補とする。

accompanimentはchord support、rhythmic support、arpeggiation、broken chord、sustained note、counter-line等の候補を持つ。CH2固定にはしない。同時和音を発音できないGame Boyでchordをarpeggiation、broken chord、note omission、layer reduction、channel sharingへ変換する必要性は01572/01576側で扱う。

## 14. melody / harmony / bass / accompanimentの関係

概念上は、`key/scale → harmony/chord → melody relation / bass relation / accompaniment relation`を追跡できるようにする。これは必ずこの生成順序にする指示ではなく、各層の参照関係を機械検証できるようにするモデルである。

最低限、current chord、root、chord tones、melody note relation、bass note relation、accompaniment relation、time positionを別に保持できる候補を用意する。具体的な依存方向、4ch割当、同時発音削減は01576へ渡す。

## 15. Hard constraint

一般理論由来のHard constraintは、modeが明示された場合の内部整合性に限定する。

- `scale_only=true`: noteのpitch classが選択scaleに属する。
- `chord_tone_only=true`: 対象layerのnoteがcurrent chordのchord toneに属する。
- `functional_harmony_mode=true`: 使用するfunction/cadence参照が選択した体系内で整合する。
- `fixed_meter=true`または`fixed_grid=true`: onset、duration、rest、measure boundaryが定義time grid内にある。
- `repeat_mode=exact`: 指定したmotif/phrase区間の指定された関係が一致する。
- motif/phrase/chord等の参照先が存在し、移調量・変奏種別・時間範囲が記録と一致する。

「すべてscale内」「大きなleap禁止」「不協和音禁止」「root bass必須」「V-I必須」「4/4必須」は一般Hard constraintにしない。

## 16. Soft rule

候補評価や確率に利用できるSoft ruleは以下とする。

- melodyのstep/leap比、intervalの重み、方向の連続、range、contour。
- chord tone、common tone、nearest movement、voice-leading、harmonic function。
- non-chord toneの位置、duration、strong/weak beat、resolution。
- motif reuse、exact/modified repetition、variation amount、phrase-level contour。
- rhythm repetition、meterとのaccent整合、syncopation、rest、density、harmonic rhythm。
- cadenceのclosure強度、bassのroot/chord tone/passing/pedal、伴奏のsupport/arpeggio/ostinato。
- Game-BGMにおけるloop反復、layer variation、attention、長時間疲労の抑制候補。

これらは破ってもデータinvalidとはせず、style、mode、曲目的、試聴結果によって重みを変更する。

## 17. Parameter

具体値を固定せず、次のparameter候補を定義する。

`key`、`scale`、`tonal_center`、`scale_only`、`mode`、`melody_range`、`interval_weighting`、`contour`、`motif_length`、`phrase_length`、`repetition_mode`、`variation_type`、`variation_amount`、`chord_vocabulary`、`progression_mode`、`harmonic_rhythm`、`functional_harmony_mode`、`cadence_type`、`non_chord_tone_mode`、`voice_leading_style`、`meter`、`tempo`、`subdivision`、`rhythm_pattern`、`rhythm_density`、`rest_density`、`accent`、`syncopation`、`bass_relation`、`bass_style`、`accompaniment_style`、`layer_presence`。

major/minor、key、tempo、meter、phrase/motif length、progression、cadence、bass style、accompaniment styleのdefaultは本WBSで決めない。

## 18. Game Boyへの適用条件

一般理論上のchordが3音同時で説明できても、Game Boyは1channel 1発音・4chである。したがって、理論上のchord/chord tone集合と、実際の発音イベント・channel割当を分離する。arpeggiation、broken chord、note omission、layer reduction、channel sharingは変換候補だが、具体的allocation algorithmは01576へ渡す。

CH1=melody、CH3=bass、CH2=accompaniment、CH4=drumという固定は01572のhardware factから導かない。`C3..B8`やhUGE row/64-row patternも、理論上のpitch/time概念とは別のtool constraintである。Wave、Noise、SFX共存の制約は01572と各実装仕様を参照する。

## 19. Game-BGMへの適用条件

一般理論のmotif/repetition/phrase/cadenceと、Game-BGM固有のlong loop、modified repetition、layer variation、attention、gameplayとの共存を分ける。exact repetitionが長時間で露呈する可能性、variation過多によるidentity・beat安定性の低下、loop境界のclosureはGame-BGM由来の評価対象である。

ゲーム中の思考や操作を妨げないdensity、強いaccent、Noise foreground化、layer欠落時の骨格維持は、理論だけでは確定しない。01561、01558、01564と人の試聴へ引き継ぐ。

## 20. Pocket Sweeperへの適用候補

直接利用候補は、pitch class/octave/scale degree分離、intervalによるmelody遷移、motif/phrase参照、current chordとchord tone集合、root/inversion/bass分離、抽象time grid、duration/rest、cadence候補である。

本WBSではkey、scale、tempo、meter、progression、phrase length、motif length、bass style、accompaniment styleを決定しない。一般理論とPocket Sweeper policy、Game Boy hardware/tool constraint、Game-BGM techniqueをルール表の分類で追跡する。

## 21. Human evaluation

次は資料・形式検査だけでは完了扱いにしない。

- melodyが自然で識別できるか、interval/rangeが適切か
- motifが認識可能で、repetitionが単調でないか
- variationが多過ぎず、loopで疲れないか
- harmony、non-chord tone、cadenceが不自然でないか
- bassがharmonyを支え、root以外のbassも成立するか
- accompanimentがmelodyを妨げず、chord supportを感じられるか
- rhythm、rest、accent、syncopation、densityが安定しているか
- Game Boy音色、4ch削減、SFXによるlayer欠損でも構造が伝わるか

本書作成時点で試聴、実機、エミュレータ確認は実施していない。

## 22. 未確定事項

- Pocket Sweeperのkey、major/minor、scale、tempo、meter。
- melody range、interval weighting、contour、motif/phrase length。
- chord vocabulary、progression、functional harmony採否、harmonic rhythm。
- non-chord toneの種類・確率・strong beat処理、voice-leading style。
- cadence type、loop境界のclosure、bass relation/style、accompaniment style。
- 4chへchord/layerを配置・削減するアルゴリズム。
- Game-BGMのvariation量、long-loop fatigue、attention、SFX欠損時の聴感。

## 23. 後続WBSへの引き継ぎ

- **01575**: 本書の暫定IDと、Theory / Hardware / Tool / Game-BGM / Pocket Sweeper / Human evaluationの根拠記録形式を正式化する。
- **01576**: melody、motif、rhythm、harmony、bass、noiseの状態・参照・依存・4ch制約・loop・SFX欠損を表現する方法を決める。
- **01561**: motif反復、variation、layer、long-loopのGame-BGM固有ルール。
- **01562/01563/01564**: pulse伴奏、wave bass、CH4 rhythm/densityのGame Boy適用。

## 24. 21曲UGEの扱い

既存21曲UGEの多数派、scale、chord progression、interval、channel役割、rhythm densityは品質根拠として使用していない。形式・解析・回帰用途に限定し、理論ルールやdefault parameterを統計から導出しない。
