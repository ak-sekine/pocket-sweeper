# 一般音楽理論に基づく自動作曲向け基礎

対象WBS: `WBS-001-01560`
調査日: 2026-09-25

## 範囲と資料

本資料は、ルールベース生成の前提となる一般音楽理論を整理する。西洋調性理論で体系化された概念を中心に扱うが、各概念を「全音楽に必須の規則」や特定ジャンルの慣習へ拡張しない。Game Boy APU、hUGETracker、ゲームBGMの反復設計は本資料の対象外であり、01559、01561〜01565へ引き継ぐ。

### 参照資料

1. **Open Music Theory**, V. K. Agmonほか編、VIVA/Open Music Theory。<https://open-musictheory.github.io/>。interval、scale、melody、phrase、harmony、cadence、meter等を大学レベルの章立てで参照した。定義と、特定の調性・声部書法に依存する説明を分離できる体系的資料として採用した。
2. **Music in Theory and Practice, Vol. 1**, Bruce Benward / Marilyn Saker、McGraw-Hill。公開教材版: <https://www.hchsmusic.com/uploads/2/0/4/7/20479636/music_theory_and_practice_textbook.pdf>。phraseがmelody・harmony・rhythmの相互作用で形成され、cadenceがphrase/sectionを閉じるという説明を参照した。教科書として用語間の関係を確認する根拠とした。
3. **Understanding Basic Music Theory**, Robert M. Coganほか、Open Textbooks for Hong Kong。<https://www.opentextbooks.org.hk/ditatopic/2180>。motif、phrase、scale、key、meter、rhythmの入門的定義を参照した。短いmotifとphraseの階層関係を確認する根拠とした。
4. **AP Music Theory Course and Exam Description**, College Board。<https://apcentral.collegeboard.org/media/pdf/ap-music-theory-course-and-exam-description.pdf>。cadence、authentic cadence、phrase、harmonic rhythmの教育上の定義を参照した。perfect authentic cadenceの条件はこの理論体系に限定して採用した。
5. **Harmony Core / Core Music Curriculum**, Berklee College of Music。<https://college.berklee.edu/harmony>、<https://college.berklee.edu/core-music-curriculum>。melodic development、tonal harmony、counterpointと、common-practiceとcontemporary styleを区別する教育方針を確認した。ジャンル慣習を一般理論と同一視しない根拠とした。

## 一般理論の整理

### scale / key / pitch / interval

- **pitch**は音の高さ、**pitch class**はオクターブを区別しない音名クラス、**octave**は周波数比2:1の周期的関係として扱える。生成データでは、絶対pitch（MIDI等の番号に相当）とpitch classを分離する。
- **semitone**は隣接する半音、**whole tone**は半音2つ分の距離である。**interval**は2音間の音程で、melodic interval（時間順）とharmonic interval（同時）を区別する。音程は半音数またはscale degree差で保存できる。
- **scale**は一定の音高集合を順序づけたもの。major/minor scaleは西洋調性理論の代表例だが、Pocket Sweeperがどのscaleを使うかは別のparameterである。
- **key / tonal center**は、音楽がある中心音とその周辺の音階・和声を基準に組織される枠組み。**scale degree**（tonicを1とする度数）で表すと、移調と生成規則を分離できる。
- consonance/dissonanceは音程・和音の安定/不安定の分類に使われるが、基準は文脈、理論体系、様式、聴取によって変わる。機械生成で「不協和音を禁止」と一般化しない。

機械表現の候補は、`key`、`scale_pitch_classes`、`pitch_class`、`octave`、`scale_degree`、`interval_semitones`、`interval_scale_steps`である。これは発音可能性を保証する抽象表現であり、APUで発音できることとは別である。

### melody / contour / motif / phrase

- **melody**は時間順に組織された音高とリズムのまとまり。**contour**は上行・下行・反復などの音高の輪郭、**range**は最低音から最高音までの幅である。
- stepwise motion（隣接するscale degree中心の進行）とleap（より大きい音程）は、melodyを記述する関係であって、常にどちらかを選ぶ規則ではない。前noteから次noteへは、scale内候補、interval上限、方向、range、休符後かどうかを条件・重みとして表せる。
- **motif**は短い認識可能な音楽的アイデアで、通常phraseより小さい。**phrase**はmelody・harmony・rhythmがまとまった、相対的に完結した単位である。phrase boundaryは休止、長い音、反復の切れ目、和声変化、cadenceなど複数の手掛かりで生じ得る。
- repetitionは同一またはほぼ同一素材の再提示、sequenceは音高等を一定の関係で移動した反復、variationは一部の音高・リズム・音域・伴奏等を変えた再提示として扱う。何回反復するか、loop中のvariation数、layerの増減はゲームBGM設計（01561）で決める。
- note durationとrestはmelodyの輪郭だけでなく、句読点、呼吸、期待、密度を作る。休符の価値は長さ・位置・周囲のリズムと文脈で決まり、休符を必ず入れる/避けるという一般規則はない。

### harmony / chord / progression

- **harmony**は同時的な音の関係と、時間に沿う和声の組織を指す。**chord**は同時に知覚される音の集合で、**triad**はroot・third・fifthを積んだ三音和音として説明される。major/minor triadはthirdの種類で区別される。
- **root**は和音の基礎音、**chord tone**は和音を構成する音。**inversion**はroot以外の構成音を最低音に置く配置で、和音名とbass noteを分離して表現できる。
- key/scaleからstackingして得る**diatonic chord**は、そのscaleの音だけで構成する和音というモデルである。**chord progression**は和音の時間的な列で、同じscaleでも複数の進行が可能であり、I–V–vi–IV等を必須とする根拠はない。
- 機能和声ではtonic（安定・中心）、predominant（dominantへ向かう準備）、dominant（tonicへの緊張）という機能を区別する。ただし、すべての音楽・ジャンル・進行がこの機能体系に従うわけではない。
- **voice leading**は各声部を次の和音へ接続する動き。共通音、近い移動、交差や特定の平行進行の回避などは、採用する声部書法ではsoft ruleになり得るが、一般音楽全体のhard constraintではない。
- **non-chord tone**はその時点の和音集合に含まれない旋律音で、passing tone、neighbor、suspension等として説明できる。非和声音を全て誤りとせず、位置、長さ、前後の解決、様式を記録する。

生成では、`current_chord`、`chord_tone_pitch_classes`、`root`、`inversion_bass`、`scale_degree`、`harmonic_function`、`melody_chord_relation`（chord tone / non-chord tone等）を分けて持てる。これは機械的な関係の表現であり、響きの良否の判定ではない。

### rhythm / beat / meter

- **beat**は時間の規則的な脈、**meter**はbeatを強弱・階層で組織する枠組み、**measure**はmeterの単位、**tempo**はbeatの速さである。4/4、特定tempo、一定note densityは理論上の必須値ではない。
- **note duration**は音の持続、**rest**は発音しない時間、**subdivision**はbeatをより小さい単位へ分割したもの。**rhythmic pattern**は開始位置・長さ・休符・アクセントの組合せである。
- **accent**は相対的な強調で、meter上の強勢、音価、音域、音量、音色など複数の要因で生じる。**syncopation**は通常のmetric accentと異なる位置を強調する関係であり、誤りではない。

最小の時間表現は、`meter_numerator`、`meter_denominator`、`tempo`、`ticks_per_beat`、`measure_index`、`beat_position`、`start_tick`、`duration_ticks`、`is_rest`、`accent`である。音符の音高と同じく、時間grid上で成立することと、音楽的に自然であることを分離する。

### cadence / closure

**cadence**はphraseまたはharmonic progressionの終止・相対的な休止点で、harmonic closureとmelodic closureが一致する場合も、ずれる場合もある。Open Music Theory/AP資料の調性体系では、authentic cadenceはV–I系、perfect authentic cadence（PAC）はroot-positionのV–I、sopranoがscale degree 1など、より強い条件を持つ。half cadenceはdominant側で止まり未完、deceptive cadenceは期待されたtonic以外へ進む終止として説明される。資料・流派により用語条件は異なるため、採用体系と条件をデータに記録する。

closureを作る候補は、終止和声、tonal centerへの到達、melodic final tone、長いduration、休符、アクセント低下、phrase boundaryである。強いclosureが常に望ましいわけではなく、loop境界でどのcadenceを採用するかは01558のloop調査および後続の試聴・設計へ残す。

### bass / accompaniment

**bass**は最低域の声部・線で、root、chord tone、inversionの最低音、経過音などを担い得る。rootを常にbassに置くことは一般理論上の定義ではない。**accompaniment**はmelodyを支える和声的・リズム的な素材で、block chord、arpeggio、ostinato、反復pattern等は作曲上の手法である。harmonic supportとrhythmic supportは独立にも組み合わせてもよい。

したがって、`bass = CH3`、`accompaniment = CH2`、bassはrootのみ、という割当は本資料から導けない。Game Boy channelへの割当と具体的patternは01562・01563・01565へ引き継ぐ。

## 自動生成への利用候補

### Hard constraint候補（抽象データ上の成立判定）

- pitchが選択したscale/許可pitch集合に含まれる（chromatic/non-diatonicを許す設定なら別集合として扱う）。
- noteの`start_tick`、`duration_ticks`、restが時間grid・measure境界の表現範囲内にある。
- chordのroot/quality/inversionとchord tone集合が整合する。
- phrase/motif参照が存在し、sequenceの移動量などが記録された変換と一致する。
- range、同時発音数、データ型など、別レイヤーで明示した機械仕様を満たす。

これらは「理論的に良い音楽」のhard constraintではなく、内部表現の矛盾を検出する候補である。

### Soft rule候補

- melodyの隣接interval、step/leapの比率、方向の連続、range逸脱の少なさ。
- 強拍でのchord tone、弱拍や短いdurationでのnon-chord tone、解決の有無。
- voice leadingの共通音・近接、harmonic functionの流れ、cadenceのclosure強度。
- rhythmic patternの反復、accentとmeterの整合、syncopation量、休符による密度調整。
- motifのrecognizabilityとvariation量。

上記は重み・確率・scoreの候補であり、様式・目的・聴感によって変更できる。資料は具体的な重みや絶対閾値を与えていない。

### Parameter候補

`key`、`scale`、`tonal_center`、`meter`、`tempo`、`phrase_length`、`melody_range`、`note_density`、`allowed_intervals`、`chord_progression`、`harmonic_rhythm`、`rest_density`、`cadence_type`、`variation_amount`、`accompaniment_pattern`。

### Human evaluation

自然さ、覚えやすさ、motifの識別性、緊張と解決、loop境界の違和感、注意を奪い過ぎない密度、bass/accompanimentの聞き分けやすさ、実際の音色との相性は、資料と数式だけでは確定できない。人の試聴をしていない本調査では確認済みとしない。

## Pocket Sweeperへの適用

### 直接利用候補

scale degree表現、pitch classとoctaveの分離、intervalによるmelody遷移、melodic contour/range、motif/phraseの構造、chord tone集合、root/inversionの分離、rhythm grid・note開始位置・duration・rest、meter上の位置、cadenceの強弱概念は、将来の中間表現や候補評価へ直接利用できる。

### 未確定事項

key、major/minor、scale、tempo、meter、phrase length、melody range、note density、chord progression、harmonic rhythm、accompaniment pattern、cadence選択、具体的なinterval重みは決めない。4小節/8小節、I–V–vi–IV、chord tone開始、root bass、4/4も一般理論上の必須条件として採用しない。

## 後続WBSとの役割分担

- 01561: ゲームBGM固有のmotif反復回数、variation、layer設計。
- 01562: Game Boy pulseを用いる伴奏/harmonyの具体設計。
- 01563: wave channelとbassの具体設計。
- 01564: CH4 noise rhythmと密度。
- 01565: hUGETracker/hUGEDriver/UGEでのInstrument/effect表現範囲。

01558のloop、長時間再生、終止感の衝突は前提として参照したが、loop向けcadenceを決定していない。01559のAPU制約は再調査せず、一般理論とhardware-validを混同していない。

## 21曲UGE素材

既存約21曲のUGE素材は、理論の品質根拠、scale/chord progression/intervalの多数派根拠として使用していない。形式・解析機能の確認用途に限定する01557の扱いを維持する。

## 限界

本資料は西洋調性理論を中心とした教育資料の整理であり、非西洋音楽、現代音楽、各ジャンルの作曲慣習を網羅するものではない。用語の定義と適用条件は資料の理論体系に依存する。Pocket Sweeperの具体的なルール、Game Boy上の発音可否、聴感品質は後続WBSで決定・確認する。
