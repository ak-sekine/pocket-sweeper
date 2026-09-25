# ゲームBGMの構成・loop技法調査

対象WBS: `WBS-001-01558`
調査日: 2026-09-25

## 調査範囲と結論

ゲームBGMは、固定尺の映像に一度だけ同期して終わる音楽ではない。プレイヤーが場面に留まる時間、失敗して再試行する回数、行動の順序は事前に一意に決まらないため、音楽は再生継続・再開始・遷移を含む運用を前提に設計する必要がある。したがって、曲の「鑑賞用の完結した時間構造」だけでなく、任意の時点で再び成立するloop境界、長時間反復への耐性、ゲームプレイを邪魔しない注意量を評価対象にする。

これは「必ず長い曲にする」「必ず短いloopにする」という数値規則を意味しない。loop長、セクション数、variationの量はゲームの滞在時間、実装方式、聴感評価に依存し、本調査だけでは確定できない。

## 資料と採用した根拠

### 1. Oxford Handbook of Interactive Audio 第7章

- 資料名: “How Can Interactive Music be Used in Virtual Worlds Like World of Warcraft?”
- 著者: Jon Inge Lomeland
- 種別: Oxford University Press刊行の専門書の章（2014）
- URL: <https://academic.oup.com/edited-volume/37182/chapter-abstract/324106701>
- 参照内容: MMORPGのように音楽が長期間・反復的に聴かれる場面、repetitive musicとlistener fatigue、反復を避ける作曲上の技法、変化させ過ぎることがゲーム体験を損なう問題を扱う。
- 採用根拠: 長時間再生では「変化を増やせば常に良い」のではなく、反復疲労と曲の記憶・役割の両方を扱う必要がある、という一般原則の根拠とする。個別ゲームの具体的なloop秒数はこの資料から導かない。

### 2. A Survey of Variation Techniques for Repetitive Games Music

- 資料名: “A Survey of Variation Techniques for Repetitive Games Music”
- 著者: Axel Berndt, Raimund Dachselt, Rainer Groh（TU Dresden Media Design Chair等）
- 種別: 学術的なゲーム音楽技法サーベイ
- URL: <https://paperzz.com/doc/9366478/a-survey-of-variation-techniques-for-repetitive-games-music>
- 参照内容: インタラクティブな場面でプレイヤーの滞在時間を予測できないこと、音楽を連続loopさせる方式の反復性への危険、反復を変化させる複数の技法を論じる。
- 採用根拠: 可変滞在時間とloopの必要性はゲーム固有の問題であり、短い素材の単純反復だけでは反復が露呈しやすい、という整理に用いる。掲載先は原著者の所属を確認できる学術資料への追跡入口として記録し、細部の実装仕様を断定しない。

### 3. Going With the Flow: Can Sound Design Keep Players Immersed in Video Games

- 資料名: “Going With the Flow: Can Sound Design Keep Players Immersed in Video Games”
- 組織: Georgia Tech Center for Computing and Media Technology / Computational and Cognitive Musicology Lab
- 種別: 大学研究プロジェクトの実験報告
- URL: <https://ccml.gtcmt.gatech.edu/projects/McNamara_Flow_2022.html>
- 参照内容: 約15秒と約2分30秒のloop長、曲間のseamless crossfadeと短い無音を比較し、20分のプレイ後にflow等を調べた。統計的に有意な結果は多くなかったが、短いloopではプレイヤーのコメントから楽しさが低く感じられた可能性、長いloopでは経過時間を短く見積もる傾向を報告している。
- 採用根拠: loop長や遷移方式には聴感・プレイヤー体験上の影響があり得るが、単一実験から普遍的な秒数や方式を決められない、という限定付きの根拠とする。Pocket Sweeperでは人による試聴を別途必要とする。

### 4. Scoring for Games: Composing Music for Interactive Media

- 資料名: “Scoring for Games: Composing Music for Interactive Media”
- 著者・組織: Berklee Online
- 種別: ゲーム音楽作曲の専門教育資料
- URL: <https://online.berklee.edu/takenote/scoring-for-games-top-techniques-for-composing-music-for-interactive-media/>
- 参照内容: loopingを、loop点を聴かせずcueを反復できることと説明し、プレイヤーが想定より長くlevelやareaに留まる場合に音楽を延長できるとする。また、crossfade、次のdownbeatやmusical phraseまで待つ遷移、transition cue、horizontal re-sequencingを説明する。
- 採用根拠: loop boundaryは単なるファイル末尾ではなく、拍・フレーズ・和声の接続点として設計すること、終止や遷移がゲームイベントの時刻と一致しない問題には音楽的な接続方法が必要だという根拠とする。

## ゲームBGM固有の原則

### 可変滞在時間と長時間再生

固定尺の映像では映像編集が音楽の開始・展開・終止を決められる。一方、マインスイーパーでは、プレイヤーの思考、盤面、ミス、再試行により1ゲームの滞在時間をBGM側から正確に決められない。通常は、曲が終了するまで待たせるのではなく、場面が続く限り音楽が成立するloopまたは再生継続を用意する。このため、想定初回再生だけでなく、2回以上の反復と長時間のBGM単独再生を設計・試聴対象にする。

### loop開始点・終了点とseamless boundary

- 開始点と終了点は、波形がつながるだけでなく、拍、フレーズ、和声、音色の状態が再開時に不自然にならない位置に置く。
- ループ末尾だけに強い終止、長い余韻、派手なfill、完結を示す休止を集めると、直後の開始点への戻りが「曲の終了後に冒頭へ巻き戻った」ように聞こえやすい。
- 逆に、常に未解決で弱い区切りにする必要もない。ループ内で局所的な区切りを作りつつ、境界では次の開始へ接続する十分な推進力を残す。
- 実装上のloop位置と音楽上のphrase boundaryを一致させ、境界を各チャンネルのうち一つの派手な効果だけに依存させない。これはGame Boyのチャンネル分担そのものを決める結論ではなく、境界設計の一般原則である。

### 反復疲労、variation、長さ

短いloopは構造を早く把握できる反面、同じ音型・リズム・音色が短い周期で再出現し、反復を意識させやすい。長いloopは反復を遅らせられるが、長さだけで単調さや注意の問題を解決するとは限らない。反復の中で、モチーフの再提示、リズム・密度・音色・伴奏の変化、休符、複数セクションの対比を検討する。ただし、variationを増やし過ぎて曲の役割や識別性を失わせない。

### 注意、展開、終止感

BGMはゲームプレイを支えるが、プレイヤーの盤面認知や思考を常に競争してはならない。高密度な反復、頻繁な高域アクセント、強いクライマックス、急な展開は、ゲーム上の重要な出来事でなくても注意を引く可能性がある。特に思考時間が長くなり得るゲームでは、強い展開を一定時刻に固定してもプレイヤーの行動タイミングと一致しない。

したがって、強い展開はloopの毎回同じ位置で必ず最大化するのではなく、長時間再生で許容できる密度・音量・変化として検討する。強い終止感は、非ループ曲の終了には適していても、直後に冒頭へ戻るloopでは衝突し得る。loop版では完全終止を境界の唯一の意味にせず、接続句、開放的な和声、リズム上の受け渡しなどを候補にする。具体的な和声・音域・チャンネル実装は01560〜01565の対象である。

## Pocket Sweeperへの適用

資料から適用できる事項:

- BGMは可変のプレイ時間を許容するloop前提で設計する。非ループ曲を採用するか、loopと併設するかはゲーム仕様と実装で決める。
- 初回再生だけでなく、少なくとも複数回のloopと、プレイヤーが長く考え続けるケースを試聴対象にする。
- loop境界は拍・フレーズ・和声・音色の接続を確認し、境界でクリック、無音の穴、急な音量差、強い終止からの不自然な冒頭回帰を避ける。
- 反復する核を保ちながら、セクション、休符、密度、補助要素などに変化を置く。ただしvariationの具体方式は01561以降に分離する。
- 盤面を読む・考える時間を妨げないよう、強いアクセントや展開を常時最大化しない。BGMとSFXのチャンネル共存・ミュート方針は既存の`docs/sound-spec.md`を維持し、本調査では変更しない。

仮説・人による確認が必要な事項:

- 現行仕様の6 order、`range` loop、tempo、約25.6秒のloop区間が、Pocket Sweeperの長時間再生に適するかは、資料だけでは判定できない。
- どの長さ・密度・variationが「邪魔になりにくい」か、強い終止感が許容できるか、loop境界をプレイヤーが意識するかは、実機または同等環境での人による試聴が必要である。今回その試聴は実施していない。
- 盤面の難易度、平均思考時間、再試行時間をBGMの尺から逆算して固定しない。

後続WBSへ引き継ぐ事項:

- 01559: Game Boy 4chの同時発音・音源制約。
- 01560: melody、harmony、rhythm、cadence等の一般音楽理論。
- 01561: motifの反復・variationとlayer設計。
- 01562〜01564: pulse/harmony、wave/bass、noise rhythmの具体設計。
- 01565: hUGETracker/hUGEDriver/UGEの表現可能範囲。

## 21曲のUGE素材の扱い

既存の約21曲は品質評価・作曲ルールの根拠に使用していない。本調査では、UGEのorder/pattern/loop値の多数派も一般原則の根拠にしていない。必要になった場合の形式確認・parser/analyzerの回帰試験用データという、01557で定義された役割に限定する。

## 仕様との整合性

`docs/sound-spec.md`のBGM loop方針（Version 2の`full`/`range`/`none`、`range`のloop区間、BGMとSFXのチャンネル共存）は、本調査の一般原則と矛盾しない。特に既存仕様がloop境界、CH2/CH4の一時ミュート耐性、運用確認用BGMの試聴を扱っている点は整合する。ただし、本調査から既存の秒数、order数、チャンネル役割、SFX制御を変更する提案は行わない。

## 限界

上記資料は、loopと可変滞在時間、反復疲労、遷移の考え方を支持するが、Pocket Sweeperの最適な秒数、order数、pattern数、テンポ、音域、Game Boy固有の実装可否を決めるものではない。また、Georgia Techの報告は実験結果に有意差が少ないことを明記しているため、loop長の優劣を断定する根拠にはしない。
