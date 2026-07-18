[PROJECT.mdへ戻る](../PROJECT.md)

# 楽曲定義JSON仕様

### 楽曲定義JSON仕様

- 楽曲定義JSONは `assets/` 直下に配置する。
- ファイル名は用途が分かる名前にする。
  - 例: `assets/bgm_title.json`
  - 例: `assets/bgm_game.json`
  - 例: `assets/se_cursor.json`
- JSONから生成した `.uge` も `assets/` 直下に配置する。
- `.uge` はhUGETrackerで再生確認・微調整するための生成物として扱う。
- `.uge` はひとまずGit管理対象とする。hUGETrackerで手修正した結果も確認・比較しやすくするためである。
- JSONは人間とChatGPTが読み書きしやすいことを優先する。
- 初版では高度な編集機能を目指さず、短いBGM・効果音の下書き生成を目的とする。
- hUGETrackerの全機能をJSONで表現する必要はない。
- `.uge` の詳細仕様が不明な箇所は、既存の `.uge` ファイルやhUGETracker出力を確認してから実装する。
- 不明点は推測で確定せず、TODOまたはWBSに残す。
- `.uge` 変換時に必要なら、JSON仕様を後から拡張してよい。

初版で扱うJSON項目:

- `version`: JSON仕様バージョン。
- `title`: 曲名または効果音名。
- `type`: `bgm` または `sfx`。
- `priority`: `type = "sfx"` の本番SFX用優先度。値が大きいほど高優先度とする。
- `tempo`: Song Version 6の `TicksPerRow` として保存する。
- `instruments`: 音色定義。音色番号、名前、種別、およびPulse/Noise向けの最小Instrument詳細を扱う。
- `order`: 再生するパターン順。
- `patterns`: パターン定義。
- `channels`: `pulse1`、`pulse2`、`wave`、`noise` の4チャンネル。
- 各ノート情報:
  - `note`: 音名。休符は `rest` とする。
  - `length`: 音の長さ。初版ではpattern row数として扱い、音符セルと空行へ展開する。
  - `instrument`: 使用する音色番号。
  - `volume`: note単位の音量指定。Version 2で追加する任意項目。
  - `effect`: 効果指定。未使用時は `null` とする。
  - `effect_param`: 効果パラメータ。未使用時は `null` とする。

### Version 2のnote共通項目

Version 2では、CH1 / Pulse1、CH2 / Pulse2、CH3 / Wave、CH4 / Noiseのすべてのnoteで、次の共通項目を使用できる。`volume` は任意項目であり、Version 1では使用不可とする。

| JSON項目 | 型・許容値 | 未指定時の動作 | 使用可能チャンネル | 意味 |
| --- | --- | --- | --- | --- |
| `volume` | 整数、0～15。`null`も許可する場合は項目省略と同じ扱い | volume commandを出力せず、Instrumentまたは直前の音量状態に従う | CH1 / CH2 / CH3 / CH4 | pattern cell単位の音量指定 |

- `volume` はVersion 2で追加し、Version 1のJSONでは指定できない。Version 1入力に存在する場合はバリデーションエラーとする。
- `volume` を省略した場合はvolume commandを出力せず、Instrumentまたは直前の音量状態に従う。
- `volume: null` を許可する実装では、項目省略と同じくvolume commandなしとして扱う。指定不要の場合は、`null` を書くより項目自体を省略することを原則として推奨する。
- `volume: 0` は項目省略とは異なり、明示的な音量0として扱う。`volume: 1`～`15`は指定音量への変更として扱う。
- 範囲外、整数以外、未対応Versionでの指定はバリデーションエラーとする。
- CH4 / Noiseの`note: "rest"`では`volume`を指定禁止とする。`volume: null`を含め、`volume`キーが存在する場合はVersion 2の入力バリデーションエラーとする。CH1～CH3のrestについては、このCH4固有の決定を推測で共通規則にしない。

`instruments[].initial_volume` とnote側の `volume` は別の役割を持つ。`initial_volume` はInstrumentの基本音量であり、PulseまたはNoiseの音量エンベロープ開始値を表す。一方、note側の `volume` はpattern cell単位の音量指定であり、特定の音符のアクセント、音量変化、フェード、将来のMIDI velocity反映などに使用する。note側の `length` とInstrument側の `length` が別項目であるのと同様に、`initial_volume` とnote側の `volume` も別項目として扱う。

JSON上では「volume指定なし」と `volume: 0` を明確に区別する。hUGETracker Song Version 6の通常patternでは `TCellV2.Volume` をnote volumeの保存先として使用せず、UGEのpattern cellに`EffectCode = $C`、`EffectParams.Value = xy`を設定してCxy（Set volume）として表現する。volume省略または`volume: null`ではeffectを出力しない。`volume: 0`はチャンネルにより異なり、CH1 / CH2 / CH3では必ず`C00`、CH4ではNoise Instrumentの`envelope_direction`と`envelope_sweep`から生成した上位nibble `x`を含む`Cx0`を出力する。CH4で上位nibble `x`も`0`の場合に限り、出力は`C00`となる。hUGEDriver用ASMでも同じCxyを`$Cxy`として出力する。

#### `length`展開で生成する空行とenvelope

- noteの`length`展開では、先頭の発音行だけがnote、Instrument、必要なvolume commandを持つ。2行目以降は空行とし、volume commandを出力せず、Instrument由来のenvelopeを再適用しない。
- 空行では、直前のenvelope状態を初期化、上書き、補完しない。CH4ではCxyを出力せず、NR42を書き換えず、noteを再triggerしない。
- 空行を通過している間も、Game Boy APU上ですでに開始されているhardware envelopeは自然に進行する。「envelope状態を変更しない」とは、変換データやhUGEDriverから新たな変更命令を出さないことであり、hardware envelopeの時間経過を停止することではない。
- 次の有効note行では、そのnoteのInstrumentとvolume指定に従って必要なenvelopeを生成する。
- patternを64行へ補完する空行も、note、Instrument、volume commandを持たず、envelope状態を変更せず、再triggerしない。同じ空セルとして扱うため、`length`展開による空行とpattern末尾補完による空行の間で再生上の規則は変わらない。
- この規則はVersion 2のnote volume変換に適用し、Version 1の既存変換動作は変更しない。

例えば、次のnoteは1行目だけで発音とvolume指定を行い、2～4行目ではvolume command、Instrument再適用、再triggerを行わない。

```json
{
  "note": "C4",
  "length": 4,
  "instrument": 1,
  "volume": 10
}
```

### Version 2のorder / pattern構造

Version 2では、トップレベルの `order` と `patterns` をチャンネル別オブジェクトとして定義する。使用可能なチャンネル名は `pulse1`、`pulse2`、`wave`、`noise` の4つだけであり、Version 1の共通 `order` 配列や `patterns.<pattern名>.channels` 構造とは混在させない。

#### `order`

- `order` はオブジェクトとする。
- `order.pulse1`、`order.pulse2`、`order.wave`、`order.noise` の各値は、同じチャンネルのpattern名を並べた文字列配列とする。
- 各order要素は空でない文字列とし、同じチャンネルの `patterns` 配下にあるpattern名を参照する。存在しないpattern名の参照はエラーとする。
- チャンネルごとに異なるpattern列を指定できる。同じpattern名を異なるチャンネルで使用してもよく、参照先はorder側の所属チャンネルによって一意に決まる。
- 使用する全チャンネルのorder配列長は同一とする。チャンネルごとにorder配列長を変えることは禁止し、最初に定義されたチャンネル（`pulse1`、`pulse2`、`wave`、`noise`の順）を基準値として検証する。不一致時は各対象チャンネル名とorder数を含む入力エラーとする。
- 各order位置は、4チャンネルが同時に再生する1つの64行区間に対応する。将来のループ位置を全チャンネル共通のorderインデックスで指定できるよう、この配列長をそろえる。
- 使用チャンネルのorder配列は空配列にできない。少なくとも1チャンネルを使用する必要があり、全4チャンネルが省略されたJSONは無効とする。
- 未知のチャンネル名は無視せずエラーとする。

hUGETracker / `.uge` の4チャンネル別OrderMatrixには、次のように対応させる。具体的な内部pattern番号への変換方法は、変換ツール対応時に決定する。

| Version 2 JSON | hUGETracker OrderMatrix |
| --- | --- |
| `order.pulse1` | CH1 OrderMatrix |
| `order.pulse2` | CH2 OrderMatrix |
| `order.wave` | CH3 OrderMatrix |
| `order.noise` | CH4 OrderMatrix |

#### `patterns`

- `patterns` はオブジェクトとする。
- 使用可能なキーは `pulse1`、`pulse2`、`wave`、`noise` だけとする。
- `patterns.<channel>` は、そのチャンネル専用patternのオブジェクトとする。
- `patterns.<channel>.<pattern名>` は、そのチャンネル1つ分のnote配列とする。Version 1のように、1つのpattern内へ `channels` オブジェクトを持たせない。
- pattern名は同一チャンネル内で一意とする。異なるチャンネル間では同じpattern名を使用してよい。例えば `patterns.pulse1.intro` と `patterns.pulse2.intro` は別のpatternとして扱う。
- orderから参照されないpattern定義も許可する。未参照patternを警告対象とするかどうかは、変換ツール実装時に決定する。
- 未知のチャンネル名や不正なpattern構造はエラーとする。

#### patternの行数

- 各patternは、noteの `length` をrowへ展開した結果で最大64行とする。
- 64行を超えた場合はエラーとする。
- 64行未満の場合は、変換ツールが残りを空行で補完して64行にする。
- 同じorder位置で、各チャンネルの実データ行数が異なっていてもよい。ただし、最終的には各patternを64行へ補完し、同じ区間長として扱う。
- 64行を超える曲は、複数patternへ分割する。

#### 未使用チャンネル

Version 2では未使用チャンネルを省略できる。未使用チャンネルは `order` と `patterns` の両方を省略する。例えばCH4を使わない場合、 `order.noise` と `patterns.noise` をともに省略できる。

- `order` と `patterns` の両方でチャンネルが省略されている場合は、未使用チャンネルとして扱い、変換ツールが他の使用チャンネルと同じorder数だけ空pattern参照を補完する。
- `order` に存在しないチャンネルは未使用チャンネルとする。`patterns` のみ存在するチャンネルは未参照pattern定義を許可する従来仕様を維持し、orderは補完対象として扱う。
- 未使用チャンネルに `order.<channel>: []` を明示した場合は、使用チャンネルとして扱い、空orderエラーとする。`patterns.<channel>: {}` のみ、または両方の省略は未使用として扱う。
- `order.<channel>` だけ存在して `patterns.<channel>` が存在しない場合はエラーとする。
- `patterns.<channel>` だけ存在して `order.<channel>` が存在しない場合は、未参照pattern定義として許可する。
- orderから同じチャンネル内に存在しないpatternを参照している場合はエラーとする。
- 省略されたチャンネルを含め、最終的に変換する4チャンネルのorderは同じ長さとして扱う。補完orderはチャンネルごとの内部pattern keyを参照し、各keyのpatternは64行すべて空セルとする。空patternはチャンネル別に持ち、ユーザー定義pattern keyと衝突しない予約内部keyを使用する。

#### Version 2のバリデーション

Version 2では、少なくとも次をバリデーションする。

- `order` と `patterns` はオブジェクトである。
- チャンネル名は `pulse1`、`pulse2`、`wave`、`noise` だけである。
- 少なくとも1チャンネルを使用する。
- 使用チャンネルのorder配列は空ではない。
- 使用する全チャンネルのorder配列長が一致する。
- order要素は空でない文字列である。
- orderの参照先patternが同じチャンネル内に存在する。
- patternはnote配列である。
- patternのnote展開後に64行を超えない。
- `order` だけ存在するチャンネルはエラーである。
- 未知のキー、不正なpattern構造、Version 1 / Version 2構造の混在はエラーである。
- 未使用チャンネルは `order` と `patterns` の両方を省略する。
- `order` が存在するチャンネルを使用チャンネルとし、使用チャンネルが1つ以上必要である。未使用チャンネルの内部orderは、基準チャンネルのorder数だけ予約空patternを参照する。

pattern名について、既存仕様では専用の正規表現を定義していない。そのためVersion 2でも新しい命名規則は追加せず、空文字列の禁止と同一チャンネル内の一意性までを確定する。

#### Version 1との互換性

Version 1の既存仕様は変更しない。Version 1では引き続き `order` を文字列配列とし、 `patterns.<pattern名>.channels.<channel>` にnote配列を持つ。既存JSONの意味、デフォルト値、バリデーション規則は維持し、既存JSONをVersion 2へ自動移行しない。

Version別の構造は次のとおりとする。

| Version | `order` | `patterns` |
| --- | --- | --- |
| Version 1 | 文字列配列 | `patterns.<pattern名>.channels.<channel>` にnote配列を持つ |
| Version 2 | チャンネル別オブジェクト | `patterns.<channel>.<pattern名>` がnote配列を持つ |

Version 1とVersion 2の構造を混在させた場合は、無視や自動変換を行わずバリデーションエラーとする。Version 2ではVersion 1形式の共通orderや `patterns.<pattern名>.channels` は使用不可である。

#### ループ仕様との関係

order / pattern構造と同じ共通orderインデックスを、Version 2のloop指定で使用する。ループ前後を含むtempoの扱いは前述の単一tempo仕様に従い、loopの具体的なmodeと範囲は後述の「Version 2のloop仕様」で定義する。

### Version 2のtempo仕様

Version 2では、曲全体で単一のtempoを使用する。`tempo` はトップレベルに1つだけ置き、全チャンネル共通の値として扱う。Version 1で使用しているトップレベルの `tempo` の基本的な意味は変更しない。

- `tempo` はhUGETracker Song Version 6の `TicksPerRow` に対応する。
- 曲の開始から終了まで同じ `tempo` を使用する。
- チャンネルごとの個別tempoは持たない。
- order単位、pattern単位、row単位、note単位のtempo指定は持たない。
- 曲中のtempo変更イベント配列は追加しない。
- `patterns`、note、`effect`、`effect_param`などへtempo変更専用項目を追加しない。
- 現行の変換ツールで確認できる既存規則として、`tempo` は必須の正整数とする。今回、上限、デフォルト値、その他の新しい許容範囲は推測で追加しない。

単一tempoを採用する理由は、対象とするhUGETracker Song Version 6の `TicksPerRow` が曲全体で共通の単一値だからである。Version 2のチャンネル別order / pattern構造でも、全チャンネルは同じ64行区間を同期して再生するため、チャンネル別または曲中可変tempoを導入すると、チャンネル同期、order位置、ループ位置、patternの時間長の解釈が複雑になる。本プロジェクトの目的は短いゲームボーイ用BGM・効果音を安定して生成することであり、曲中tempo変更は必須ではない。

JSONのnote `length` はpattern row数を表し、`tempo` は1rowあたりのtick数を表す。同じnote `length` でも `tempo` の値によって実際の再生時間は変わる。hUGEDriverの既存コメントと処理では、`TicksPerRow = 1` は1回の更新で1行進み、値が大きいほど1行に必要なtick数が増えるため、固定更新頻度では値が大きいほど再生は遅くなる。tempoを曲の途中で変更しないため、同じ曲内ではrowの時間基準が一定になり、4チャンネルすべてが同じtempoを使用する。

#### MIDIの複数tempoを単一tempoへ正規化する方針

MIDIなどの入力素材に複数のtempoが含まれる場合は、楽曲定義JSONへ変換する段階で単一tempoへ正規化する。MIDIのtempo changeイベントは解析対象とするが、tempo changeイベント自体はVersion 2 JSONへ出力しない。

- MIDI上の各イベントの絶対時刻または実時間上の位置を算出する。
- 選定した単一tempoのrow位置へ、各イベントを再量子化する。
- tempo変更前後の音符位置や長さは、可能な範囲で単一tempo上のrowへ変換する。
- 変換後のrow位置と長さは整数へ量子化する。
- 量子化によって元のタイミングを完全には保持できない場合がある。
- 量子化誤差が大きい場合は、警告または変換レポートで通知する。
- 正規化後のJSONにはトップレベルの `tempo` を1つだけ出力する。

単一tempoの具体的な自動選択アルゴリズムは今回確定しない。先頭tempo、最頻tempo、主要区間のtempo、手動指定などを候補として、後続のMIDI変換WBSで決定する。元MIDIのtempo change情報をメタデータとして保持するかどうかも、後続のMIDI変換運用設計で決める。今回決めるのは、複数tempoをVersion 2 JSONへそのまま保持せず、選定した1つのtempoへ時間位置を再量子化する方針だけである。

#### effectとの関係

Version 2では、tempo変更をnoteの `effect` / `effect_param` で表現することを正式対応しない。hUGETracker / hUGEDriverには `Fxy Set speed`（ticks per rowを変更するeffect）が存在することを既存コード・資料で確認できるが、現行JSONでは非null effect全般が未対応であるため、今回そのeffect番号や動作をVersion 2の正式対応仕様として確定しない。

tempo変更に相当するeffectを含む入力は、現行の未対応effect規則に従い、無視して再生を続けず、エラーまたは未対応として扱う。effect codeやeffect parameterの仕様は今回変更しない。tempo変更effectの具体的な対応は、将来のeffect仕様拡張WBSで扱う。

#### Song Version 7との関係

既存調査では、hUGETracker Song Version 7がチャンネル別 `TicksPerRow` を持つ可能性を確認している。ただし、本プロジェクトの対象は現在Song Version 6である。Version 2 JSONはSong Version 6への安定した変換を優先し、チャンネル別tempoを採用しない。

将来Song Version 7へ対応する場合も、Version 2 JSONの単一tempoを全チャンネルへ適用することで変換可能とする。将来チャンネル別tempoが必要になった場合は、既存の `tempo` の型を曖昧に変更せず、JSON仕様のバージョン更新として検討する。Song Version 7対応自体は今回の実装対象やWBSへ追加しない。

#### Version 1との互換性

- Version 1の既存 `tempo` の意味を変更しない。
- Version 1の既存JSONを書き換えない。
- Version 2でもトップレベルの単一 `tempo` を継続して使用する。
- Version 2へチャンネル別tempoやtempo change配列を追加しない。
- 未知のtempo関連項目は無視せず、既存の未知項目に対するバリデーション方針に従ってエラーとする。

例えば `tempo` をチャンネル別オブジェクトにしたり、`tempo_changes` 配列を追加したりする構造はVersion 2では使用不可である。これらの項目名を特別な予約語として扱うのではなく、Version 2で定義されていない未知の構造として扱う。

#### ループ仕様との関係

ループ前後を含め、曲全体で同じtempoを使用する。ループ開始・終了位置でtempoを切り替える機能は持たない。単一tempoのため、orderインデックスおよびrow位置の時間基準は曲全体で一定になる。Version 2の具体的なループ構造は、後述の「Version 2のloop仕様」で定義する。

### Version 2のloop仕様

Version 2では、曲全体の繰り返し、イントロ再生後の部分ループ、繰り返さない再生を、トップレベルの `loop` オブジェクトで明示する。`loop` はVersion 2の必須項目とし、Version 2で省略した場合はバリデーションエラーとする。Version 1の既存構造に包括的な未指定項目の動作を追加するものではなく、Version 2の再生意図を曖昧にしないための必須化である。

#### 共通仕様

- `loop` はVersion 2で追加するトップレベルオブジェクトとする。
- `loop.mode` は必須で、使用できる値は `"full"`、`"range"`、`"none"` の3つだけとする。
- ループ範囲は全チャンネル共通とする。チャンネル別のloop指定は持たない。
- ループ位置は共通orderインデックスで指定し、インデックスは0始まりとする。
- pattern内、note内、effect内にloop専用項目を追加しない。
- row単位およびpattern途中のループは扱わず、ループ境界はorder境界だけとする。
- 曲中の `tempo` は単一であり、ループ前後でも同じtempoを使用する。
- `loop` とループ相当のeffectを同時に指定する構造は認めない。非null effect全般が未対応のため、ループ相当effectを含む入力は現行の未対応effect規則に従いエラーまたは未対応として扱う。

Version 2の使用チャンネルはorder配列長を同一とし、各order位置を全チャンネル共通の64行区間として扱う。また、4チャンネルは単一tempoで同期して再生する。このためチャンネル別ループを許可すると、チャンネル間のorder位置と時間軸がずれる。CH2やCH4が効果音で一時的にミュートされる場合でも、BGM自体の再生位置は全チャンネル共通で維持する必要がある。共通orderインデックスへ集約することで、JSON、UGE、ASM、将来のMIDI変換を単純化する。

#### `mode: "full"`

`mode` が `"full"` の場合は全order範囲 `[0, N)` を繰り返す。`N` は使用チャンネルの共通order数である。再生はorderインデックス0から開始し、最終order再生後にorderインデックス0へ戻る。`start_order` と `end_order` は指定禁止とし、指定された場合は無視せずバリデーションエラーとする。

#### `mode: "range"`

`mode` が `"range"` の場合は `start_order` と `end_order` を必須とし、ループ範囲を半開区間 `[start_order, end_order)` として扱う。`start_order` はループの先頭を含み、`end_order` は終端を含まない。

- `start_order` と `end_order` はbooleanではない整数とする。
- どちらも0始まりのorderインデックスとして扱う。
- 曲の再生自体は常にorderインデックス0から開始する。
- `start_order` より前のorderはイントロとして1回だけ再生する。
- `end_order` に到達したら `start_order` へ戻る。
- `end_order` より後ろのorderは通常再生で到達しないため、Version 2では禁止する。
- したがって `end_order` は共通order数 `N` と同じ値でなければならず、部分ループは「先頭に非ループのイントロを持ち、曲の末尾までを繰り返す」形式に限定する。

`start_order = 0` かつ `end_order = N` は意味上 `"full"` と同じであり、`"full"` の使用を推奨する。入力自体は同じ意味のrangeとして許可し、変換ツールで警告するかどうかは実装時に決定する。中間範囲だけを無限ループしてその後ろへ抜ける構造は、通常再生されない末尾データを生じるため採用しない。

`range` の最低限のバリデーションは次のとおりとする。

- `0 <= start_order < N`
- `1 <= end_order <= N`
- `start_order < end_order`
- `end_order == N`
- `start_order` または `end_order` の小数、文字列、boolean、`null` はエラー
- `start_order` または `end_order` の省略はエラー

#### `mode: "none"`

`mode` が `"none"` の場合はorderインデックス0から最終orderまでを1回だけ再生し、最終order再生後は先頭へ戻らない。`start_order` と `end_order` は指定禁止とし、指定された場合はバリデーションエラーとする。ここで確定するのは「繰り返さない」という再生意図までであり、実際に再生を停止するのか、無音状態を維持するのか、呼び出し元へ終了を通知するのかは、再生処理とhUGEDriverの仕様確認後に決定する。ROM側の停止処理や終了通知は今回実装しない。

#### order境界に限定する理由

Version 2のループ境界はorder境界だけとする。pattern途中のrowをループ開始・終了位置にせず、row単位のループも許可しない。row単位のループを許可すると、4チャンネルすべてのpattern内位置を同期させる必要があり、patternの再利用、OrderMatrix、hUGETracker Export ASMとの対応が複雑になる。必要な場合はpatternを分割し、ループ境界をorder境界へ合わせる。将来row単位のループが必要になった場合は、JSON仕様バージョン更新として別途検討する。

#### hUGETracker・hUGEDriver・UGE・ASMとの対応

Song Version 6の保存構造は、ヘッダ、15個ずつの3種のInstrument、16個のWave bank、tempo関連値、pattern数と64行のpattern cell、4本のOrderMatrix、16本のroutineで構成される。OrderMatrixは各チャンネルについて、`uint32` の保存要素数、pattern番号列、末尾の `uint32` filler を持つ。仕様資料の「Order length + 1 (Off by one bug)」は、保存要素数が実際のorder数より1大きいことを示す。したがって、現在の `channel_orders + [0]` の末尾 `0` は終端マーカーでもloop先指定でもなく、UGE形式のoff-by-one fillerである。実際に再生されるorderは先頭からそのfiller直前までである。

専用のloop start/end、非ループ、停止フィールドはVersion 6の構造資料、既存UGE、現在のhUGEDriver実装で確認できない。hUGEDriverはOrderMatrixの実order数を読み、最終order後に `current_order` を0へ戻すため、通常のOrderMatrixだけで `full`（分類2: OrderMatrixの構造／値で表現可能）が実現する。末尾fillerの値自体はloop動作に関与しない。Version 1の既存出力も同じ保存規則と通常の全体ループを維持する。

`range` は分類3: pattern cellへ変換ツールがeffectを生成すれば表現可能とする。ループ範囲は仕様で `end_order == N` に限定するため、最終orderの最終row（またはそのorder境界へ確実に到達するcell）にglobal effect `Bxx`（Position jump、`xx = start_order`）を変換ツールが内部生成すれば、introを1回だけ再生して指定位置へ戻せる。B effectはglobal effectなので、全4チャンネルへ同じeffectを複製する必要はないが、無音補完チャンネルを含めて同期・編集結果を明確にする実装配置は後続WBSで決める。B effectはUGEの通常pattern cellのeffect code／parameterとして保存できる。UGE形式上は通常effectとして保持可能な構造である。ただし、今回の調査ではhUGETracker GUIで読み込み、編集・再保存した実ファイルについて、B effectが保持されることまでは確認していない。

`none` は分類4: UGEだけでは表現できず、hUGEDriver／ROM側の追加対応が必要とする。OrderMatrixは最終order後に先頭へ戻る規則を変えず、B/D effectにも停止命令はない。hUGETrackerの停止ボタンはエディタの再生を止める操作であり、UGEへ「最後まで再生したら停止」というデータを保存する機能ではない。したがって、hUGETracker上のプレビュー停止と、hUGEDriverを組み込んだROMでの再生停止・無音維持・終了通知は別問題であり、後者は再生処理側で実装する。

なお、`loop` の意図をJSON利用者にeffectとして直接指定させる方式は採用しない。上記のB effect生成は変換ツール内部の候補であり、今回実装しない。UGE出力で保持できるのは通常のorder列、pattern cell、通常effectまでで、loop modeのメタデータと停止意図は後続のhUGEDriver用ASM／ROM再生処理へ渡す境界とする。

#### Version 1との互換性

- Version 1には新しい `loop` 構造を追加しない。
- Version 1で `loop` を指定した場合はバリデーションエラーとする。
- Version 1の既存JSONは書き換えない。
- Version 1のループ動作は、現在の変換ツールとhUGEDriverの既存動作を維持する。確認できたBGM用の既存経路では、OrderMatrix末尾からorder 0へ戻るため、曲全体ループが暗黙の動作である。
- Version 2では `loop.mode` によって再生意図を明示する。
- Version 1とVersion 2のloop表現を混在させない。

#### effectとの関係

ループの再生意図はトップレベルの `loop` に集約する。利用者がnoteの `effect` にposition jumpなどを直接記述してループを構築する方式は正式仕様にしない。ループ用effectの具体的な番号やparameterをJSON公開仕様へ追加せず、非null effect全般の正式対応は別WBSで扱う。

#### MIDI変換との関係

将来のMIDI変換では、MIDIからループ情報を取得できる場合はVersion 2のトップレベル `loop` へ変換する。MIDIにループ情報がない場合のデフォルトmodeは、後続のMIDI変換運用設計で決める。

- MIDIのループ位置がpattern途中にある場合は、patternを分割してorder境界へ合わせる。
- MIDIの時間位置は、単一tempoへ正規化・量子化した後のrow位置を基準にpattern分割する。
- MIDI由来のループ開始・終了位置をどのマーカーやメタデータから取得するかは今回決定しない。
- 自動検出できない場合に手動指定を許可するかは後続WBSで決める。

#### SFXとの関係

Version 2の `type: "sfx"` では `loop.mode` を `"none"` に限定する。効果音は1回再生して終了するものとして扱い、`"full"` または `"range"` を指定した場合はバリデーションエラーとする。`type: "bgm"` では `"full"`、`"range"`、`"none"` を使用できる。将来、持続音や環境音などのループSFXが必要になった場合は、別途仕様を拡張する。

Pulse Instrument詳細項目:

- `duty`: Pulse duty設定。0～3を指定する。未指定時はInstrument IDに応じた従来のデフォルト値を使う。
- `initial_volume`: 初期音量。0～15を指定する。未指定時は15を使う。
- `envelope_direction`: 音量エンベロープ方向。`"up"` または `"down"` を指定する。未指定時は `"down"` を使う。
- `envelope_sweep`: 音量エンベロープのsweep値。0～7を指定する。未指定時はInstrument IDに応じた従来のデフォルト値を使う。
- これらのInstrument詳細項目は、初版では `pulse1` / `pulse2` 用Instrumentのみ対応する。
- 不正な範囲や未対応チャンネルでの指定は、変換ツールでバリデーションエラーにする。

### Version 2のPulse Instrument共通項目

Version 2では、CH1 / Pulse1とCH2 / Pulse2が同じPulse Instrument共通項目を使用する。Version 1で扱っている項目の意味は変更せず、`length` と `length_enable` はVersion 2で追加する項目として扱う。Version 1入力時にはVersion 2専用項目を参照しない。

| JSON項目 | 型・許容値 | 未指定時のデフォルト | 使用可能チャンネル | 意味 |
| --- | --- | --- | --- | --- |
| `duty` | 整数、0～3 | Version 1のInstrument IDに応じた既存デフォルト | `pulse1` / `pulse2` | Pulse波形のduty設定。Version 1の意味を変更しない。 |
| `length` | 整数、0～63 | `0` | `pulse1` / `pulse2` | ハードウェアのsound length設定。 |
| `length_enable` | boolean | `false` | `pulse1` / `pulse2` | length counterを有効にするかどうか。 |
| `initial_volume` | 整数、0～15 | `15` | `pulse1` / `pulse2` | 音量エンベロープの初期音量。Version 1の意味を変更しない。 |
| `envelope_direction` | `"up"` または `"down"` | `"down"` | `pulse1` / `pulse2` | 音量エンベロープの方向。Version 1の意味を変更しない。 |
| `envelope_sweep` | 整数、0～7 | Version 1のInstrument IDに応じた既存デフォルト | `pulse1` / `pulse2` | 音量エンベロープの周期設定。Version 1の意味を変更しない。 |

Instrument側の `length` はGame Boyハードウェアのsound length設定であり、pattern内のnote側にある `length` とは別の項目である。note側の `length` はpattern row数を表し、Instrument側の `length` はハードウェアのsound length registerへ反映する値を表す。

hUGETrackerの初期Duty Instrumentは `SweepIncDec = stDown` であり、Version 2 JSONの `sweep_direction` 未指定時は対応する `"down"` とする。hUGETrackerの `stDown`、JSONの `"down"`、NR10 bit 3の1（周波数減算）は同じ方向を表す。

Pulse InstrumentのJSON項目を未指定にした場合は、可能な限りhUGETrackerの初期値を採用する。これはhUGETrackerで新規作成したInstrumentとJSONの初期状態を一致させ、JSONからUGEを経由してhUGETrackerで扱う場合の不要な差分を抑えるためである。Version 1から引き継ぐ `duty` と `envelope_sweep` のInstrument ID別デフォルトなど、既存JSONの意味に関わる値はVersion 1互換性方針を優先して維持する。`length = 0`、`length_enable = false`、`initial_volume = 15`、`envelope_direction = "down"` は、今回のVersion 2共通項目で採用する未指定時の値であり、length counterを無効、その他を標準的な初期状態として扱うためである。

JSONのデフォルト値は、hUGETrackerの初期値との互換性を優先して決定する。将来、hUGETrackerの初期値と異なるデフォルト値を採用する場合は、その理由をこの仕様書に明記する。

### CH1 / Pulse1専用項目

CH1 / Pulse1だけがハードウェアの周波数Sweep機能を持つため、次の項目は`channel = "pulse1"`でのみ使用可能とする。

| JSON項目 | 型・許容値 | 未指定時のデフォルト | 意味 |
| --- | --- | --- | --- |
| `sweep_time` | 整数、0～7 | `0` | CH1周波数スイープの周期設定。 |
| `sweep_direction` | `"up"` または `"down"` | `"down"` | CH1周波数スイープの方向。 |
| `sweep_shift` | 整数、0～7 | `0` | CH1周波数スイープのshift設定。 |

`sweep_direction` のJSON上の意味は、ハードウェアの周波数変化方向として定義する。`"up"` は周波数加算でNR10のbit 3を0、`"down"` は周波数減算でNR10のbit 3を1とする。既存のhUGETracker / hUGEDriver側では、hUGETrackerの `SweepIncDec` および変換ツールの `ST_UP = 0` / `ST_DOWN = 1` に対応する。hUGEDriverはInstrumentのSweep値をNR10へ書き込む。

### CH2 / Pulse2用Instrument

CH2 / Pulse2はPulse Instrument共通項目だけを使用する。`channel` は必ず `"pulse2"` とし、使用可能な項目は `duty`、`length`、`length_enable`、`initial_volume`、`envelope_direction`、`envelope_sweep` の6項目とする。CH2固有の新しいInstrument項目は追加しない。

CH2にはハードウェア上の周波数Sweep機能がないため、`sweep_time`、`sweep_direction`、`sweep_shift` は指定禁止とする。`channel = "pulse2"` のInstrumentでこれらが指定された場合は、無視せずバリデーションエラーとする。

FrequencyとTriggerはInstrument JSONの項目にしない。実際の周波数はpattern内の `note` から生成し、再生開始時のTriggerはASMまたはUGE生成側で設定する。

Version 2のPulse Instrumentでは、次の共通バリデーションを行う。

- `channel` は対象チャンネルに応じた値とし、CH2 / Pulse2用Instrumentでは `"pulse2"` とする。
- `duty` は整数で0～3の範囲とする。
- `length` は整数で0～63の範囲とする。
- `length_enable` はbooleanとする。
- `initial_volume` は整数で0～15の範囲とする。
- `envelope_direction` は `"up"` または `"down"` とする。
- `envelope_sweep` は整数で0～7の範囲とする。
- `sweep_time`、`sweep_direction`、`sweep_shift` は `channel = "pulse1"` でのみ指定可能とする。CH2 / Pulse2での指定は禁止する。
- 未対応チャンネルで指定された項目は無視せずエラーとする。
- 型が不正な場合はエラーとする。
- 未指定時は、上記で定めた項目ごとのデフォルト値を使用する。

Version 1の既存JSONでは、既存の項目の意味、デフォルト値、バリデーション規則を変更しない。今回整理した `length`、`length_enable`、`sweep_time`、`sweep_direction`、`sweep_shift` はVersion 2向けの項目として扱い、Version 1入力時には参照しない。

### Version 2のCH3 / Wave用Instrument

CH3 / Wave用Instrumentは、hUGETracker Song Version 6の `TInstrumentV3` におけるWave固有の役割をJSONで表現する。使用可能な項目は `waveform`、`output_level`、`length`、`length_enable` の4項目とする。Wave Instrument本体とWave tableの32サンプルデータは分離し、InstrumentにはWave tableへの参照だけを持たせる。

| JSON項目 | 型・許容値 | 未指定時のデフォルト | 意味 |
| --- | --- | --- | --- |
| `waveform` | 文字列。空文字列は禁止 | デフォルトなし。必須 | Wave table定義の一意な名前を参照する。 |
| `output_level` | `"mute"`、`"100%"`、`"50%"`、`"25%"` | `"100%"` | CH3のNR32出力レベル。 |
| `length` | 整数、0～255 | `0` | CH3のハードウェアsound length設定。 |
| `length_enable` | boolean | `false` | CH3のlength counterを有効にするかどうか。 |

`waveform` は配列位置や数値IDをJSONに直接記録せず、Wave table定義側の名前を参照する。hUGETrackerの `TInstrumentV3.Waveform` および既存のVersion 6生成処理では内部的に0始まりの数値を使用するため、変換時には名前をWave table側で定義された数値へ解決する。名前から数値への対応、数値IDの範囲、Wave tableの最大定義数は本節で確定する。

`waveform` はInstrument IDから暗黙に補完しない。hUGETrackerの新規Wave InstrumentにはWave bankの位置に応じた数値初期値があるが、JSONで名前参照を採用する以上、対応するWave table名が確定していない状態で推測した名前をデフォルトにしないためである。したがって、Version 2のWave Instrumentでは `waveform` を必須とする。

`output_level` は人間が読み書きしやすい文字列表現を採用する。hUGETrackerの `OutputLevel` は数値で保存されるが、JSONから内部数値へ単純に変換でき、次の値に対応する。

| JSON値 | hUGETracker / 内部値 | NR32値 | 意味 |
| --- | ---: | ---: | --- |
| `"mute"` | `0` | `$00` | 無音。DAC自体の有効・無効とは別である。 |
| `"100%"` | `1` | `$20` | 100%出力。 |
| `"50%"` | `2` | `$40` | 50%出力。 |
| `"25%"` | `3` | `$60` | 25%出力。 |

hUGETrackerのWave bank初期値は、`Length = 0`、`LengthEnabled = false`、`OutputLevel = 1` であるため、JSONの `output_level`、`length`、`length_enable` のデフォルトはそれぞれ `"100%"`、`0`、`false` とする。CH3のsound lengthはGame Boyハードウェアの8-bit設定であるため、Pulseの0～63とは異なり0～255を許容する。

Instrument側の `length` はCH3ハードウェアのsound length設定であり、pattern内のnote側にある `length` とは別の項目である。note側の `length` はpattern row数を表し、Instrument側の `length` はCH3のsound length registerへ反映する値を表す。

Frequency、Trigger、DAC enableはWave Instrument JSONの項目にしない。周波数はpattern内の `note` から生成し、TriggerはASMまたはUGE生成側で設定する。DAC enableはCH3再生時に再生処理側が管理する。hUGEDriverではWave tableをWave RAMへコピーする際にCH3を一時停止し、コピー後に有効化するため、これを人が調整する音色項目として公開しない。

hUGEDriverにはeffect 9によって再生中のWave tableを変更する処理があるが、これはInstrument本体の項目ではない。今回のWave Instrument仕様ではInstrumentの `waveform` を初期参照として扱い、pattern effectによる途中変更のJSON表現・バリデーションは別途effect仕様で扱う。現行JSONのeffectは未使用であるため、今回その機能を確定しない。

CH3 / Wave用Instrumentでは、次の項目を指定禁止とする。

- Pulse専用項目: `duty`、`initial_volume`、`envelope_direction`、`envelope_sweep`、`sweep_time`、`sweep_direction`、`sweep_shift`
- Noise専用項目: `noise_length`、`clock_shift`、`width_mode`、`divisor_code`
- `trigger`、`frequency`、Wave tableの32サンプルデータ

Version 2のCH3 / Wave用Instrumentでは、次のバリデーションを行う。

- `channel` は必ず `"wave"` とする。
- `waveform` は空でない文字列とし、Wave table定義に存在する名前を指定する。Wave tableの名前・数値対応表が未確定の間は、完全な存在確認の実装条件を後続WBSで確定する。
- `output_level` は `"mute"`、`"100%"`、`"50%"`、`"25%"` のいずれかとする。
- `length` は整数で0～255の範囲とする。
- `length_enable` はbooleanとする。
- Pulse専用項目、Noise専用項目、その他の未対応項目は無視せずエラーとする。
- 型不正はエラーとする。
- 未指定時は、`waveform`を除き上記のデフォルト値を使用する。`waveform`未指定はエラーとする。

Version 1の既存JSONでは、既存の項目の意味、デフォルト値、バリデーション規則を変更しない。今回の `waveform`、`output_level`、CH3用の `length`、`length_enable` はVersion 2向けの項目として扱い、Version 1入力時には参照しない。既存のVersion 1 JSONは書き換えない。

### Version 2のCH3 / Wave table定義

Version 2では、Wave tableをトップレベルの `wave_tables` 配列で定義する。Wave tableはWave Instrument本体から分離し、Wave Instrumentの `waveform` がこの配列内の `name` を参照する。Wave tableを使用しないJSONでは `wave_tables` を省略するか、空配列にできる。Version 1入力時には `wave_tables` を参照しない。

```json
{
  "version": 2,
  "title": "Wave Example",
  "type": "bgm",
  "wave_tables": [
    {
      "name": "bass_wave",
      "samples": [
        0, 1, 2, 3, 4, 5, 6, 7,
        8, 9, 10, 11, 12, 13, 14, 15,
        15, 14, 13, 12, 11, 10, 9, 8,
        7, 6, 5, 4, 3, 2, 1, 0
      ]
    }
  ],
  "instruments": [
    {
      "id": 3,
      "name": "Wave Bass",
      "channel": "wave",
      "waveform": "bass_wave",
      "output_level": "50%",
      "length": 0,
      "length_enable": false
    }
  ]
}
```

#### `wave_tables` と `name`

- `wave_tables` は配列とする。
- 配列要素はWave tableオブジェクトとする。
- Wave tableの `name` は必須の文字列とし、空文字列を禁止する。
- `name` はJSON内で一意とする。大文字・小文字を区別する。
- `name` の前後に空白を許可しない。
- 命名規則は `^[a-z][a-z0-9_]*$` とする。先頭は英小文字、2文字目以降は英小文字・数字・アンダースコアを使用する。
- Wave Instrumentの `waveform` は `name` を参照する。数値IDや配列位置をJSONに明示しない。
- Wave tableを定義したがInstrumentから参照していない場合もエラーにしない。配列順どおり出力し、必要に応じた未参照警告は変換ツール実装時に決める。

#### `samples`

- `samples` は必須の配列とする。
- 要素数は必ず32とする。
- 各要素はbooleanではない整数で、0～15の範囲とする。
- 小数、文字列、boolean、null、負数、16以上はエラーとする。
- 配列の順序はWave RAM上の再生順と一致させる。
- JSONでは4bitサンプルを可読な整数配列で表現し、圧縮済み16byte配列、16進文字列、Base64、外部PCMファイル参照は使用しない。

Game BoyのWave RAMは16バイトで32個の4bitサンプルを保持し、各バイトの上位nibbleが先のサンプル、下位nibbleが後のサンプルになる。したがって、JSONの `[1, 2, 10, 15]` は内部のWave RAM形式では `0x12, 0xAF` となる。hUGETracker Version 6の`.uge`では各Wave tableを32個の `uint8` nibble値として保存し、hUGEDriver用ASM・実行時データでは隣接する2サンプルを1バイトへパックして出力する。

#### 内部Waveform番号と最大定義数

- `wave_tables` の配列順を内部Waveform番号へ対応させる。
- 配列先頭を内部番号0とし、以降を1ずつ増加させる。
- 使用可能な内部番号は0～15、最大定義数は16とする。
- 変換ツールがInstrumentの `waveform` 名を検索して内部番号へ解決する。JSON利用者は内部番号を直接指定しない。
- 配列順を変更すると内部番号は変わるが、Instrumentは名前参照のため、同じ名前と内容を維持する限りJSON上の参照意味は維持される。
- 同名Wave tableの重複を許可しないため、名前解決は一意になる。

これはhUGETracker Version 6のWave table固定数16、Wave index 0～15、およびhUGEDriverがWave indexから16バイト単位でWave RAMデータを選択する構造に合わせたものである。

#### 未使用Wave bankの補完

- JSON利用者は未使用Wave bankを明示的に記述しない。
- `.uge`の固定構造に必要な16個のWave bankは変換ツールが補完する。
- `wave_tables`に記述されたWave tableを配列先頭から内部index 0以降へ割り当て、利用者定義済みのindexはその内容を優先する。補完対象は利用者が定義していない残りのindexだけとし、利用者定義済みindexを標準Waveや全サンプル0で上書きしない。
- 未定義のindex 0～10は同じindexのhUGETracker初期値相当の標準Waveで補完し、未定義のindex 11～15は全サンプル0で補完する。
- 16個すべてを利用者定義した場合は、補完を行わない。
- 補完Wave bankはJSON上のInstrumentから参照されない。
- JSONに定義したWave tableと変換ツールが補完したWave bankは、`.uge`上では同じ固定配列に保存される。将来JSONへ逆変換する場合に補完値を自動的に利用者定義と区別する仕組みは、今回追加しない。

例えば3個を定義した場合は、index 0～2を利用者定義、index 3～10を同じindexの標準Wave、index 11～15を全サンプル0で補完する。

#### CH3 Instrumentとの参照整合性

- `channel = "wave"` のInstrumentは `waveform` を必須とする。
- `waveform` は `wave_tables` 内の一意な `name` を参照する。
- 参照先が存在しない場合、空文字列の場合、名前が重複している場合はエラーとする。
- `channel != "wave"` のInstrumentで `waveform` を指定した場合は、無視せずエラーとする。
- Wave tableの途中変更を表すpattern effectはInstrument参照とは別の仕様であり、今回のWave table定義では扱わない。

#### Wave tableのバリデーション

- `wave_tables` は省略可能だが、存在する場合は配列とする。
- 配列要素はオブジェクトとする。
- 要素数は0～16の範囲とする。空配列はWave table未使用として許可する。
- `name` は必須の文字列、空文字禁止、命名規則一致、前後空白禁止、重複禁止とする。
- `samples` は必須の配列で、要素数32、各要素はbooleanではない整数0～15とする。
- 要素不足、要素超過、型不正、範囲外はエラーとする。
- Wave tableオブジェクトの未知の項目は無視せずエラーとする。
- Wave Instrumentの `waveform` 参照先が存在しない場合はエラーとする。
- `channel != "wave"` のInstrumentにある `waveform` はエラーとする。
- Version 2でWave Instrumentを使用する場合、`wave_tables` を省略または空配列にはできない。

#### JSONで扱わない項目

Wave table定義には、出力レベル、sound length、length enable、Instrument ID、note、Frequency、Trigger、DAC enable、pattern effectによる途中Wave変更、手動内部番号、圧縮済みデータ、外部音声ファイル参照を含めない。これらはWave Instrument、pattern、変換処理、または将来のeffect仕様の責務とする。

Version 1のJSONでは `wave_tables` を参照せず、既存の未使用Wave bank出力方針を変更しない。今回のWave table定義はVersion 2専用であり、既存のVersion 1 JSONは書き換えない。

Noise Instrument詳細項目:

- `noise_length`: NR41のsound length。0～63を指定する。未指定時は0を使う。
- `initial_volume`: NR42の初期音量。Pulseと同じく0～15を指定する。未指定時は15を使う。
- `envelope_direction`: NR42の音量エンベロープ方向。Pulseと同じく `"up"` または `"down"` を指定する。未指定時は `"down"` を使う。
- `envelope_sweep`: NR42の音量エンベロープsweep値。Pulseと同じく0～7を指定する。未指定時は0を使う。
- `clock_shift`: NR43のclock shift。0～15を指定する。未指定時は4を使う。
- `width_mode`: NR43のLFSR幅。`"15bit"` または `"7bit"` を指定する。未指定時は `"15bit"` を使う。
- `divisor_code`: NR43のdivisor code。0～7を指定する。未指定時は0を使う。
- `length_enable`: NR44のlength enable。booleanを指定する。未指定時は `false` を使う。
- `trigger` はJSON項目にしない。SFX step出力時にNR44のtrigger bitを常に立てる。
- これらのNoise Instrument詳細項目は、初版では `noise` 用Instrumentのみ対応する。
- 不正な範囲、未対応文字列、未対応チャンネルでの指定は、`json_to_sfx_asm.py` 実装時にバリデーションエラーとする。

### Version 2のCH4 / Noise用Instrument

Version 2では、CH4 / NoiseをBGMのリズム音源として使用する。Noise Instrumentは音色の性格、音量エンベロープ、ハードウェアsound length、LFSR幅を保持し、Noiseの音高に相当するNR43の値はpattern側のNoise noteから生成する。CH4でも他チャンネルと同じnote文字列形式を使用し、`C3`～`B8`は平均律の正確な音高ではなく、hUGETracker / hUGEDriverのNoise note番号を人間が扱いやすく表記したNoise pitch indexとする。

| JSON項目 | 型・許容値 | 未指定時のデフォルト | 意味 |
| --- | --- | --- | --- |
| `length` | 整数、0～63 | `0` | CH4のハードウェアsound length設定。Version 1の`noise_length`に対応する。 |
| `length_enable` | boolean | `false` | length counterを有効にするかどうか。 |
| `initial_volume` | 整数、0～15 | `15` | NR42の初期音量。 |
| `envelope_direction` | `"up"` または `"down"` | `"down"` | NR42の音量エンベロープ方向。 |
| `envelope_sweep` | 整数、0～7 | `0` | NR42の音量エンベロープ周期。 |
| `width_mode` | `"15bit"` または `"7bit"` | `"15bit"` | NR43のLFSR幅。15bitは長周期、7bitは短周期で金属的・周期的な音色。 |

hUGETracker Version 6のNoise Instrumentは、`Length`、`LengthEnabled`、音量エンベロープ、`CounterStep`をInstrument recordに保持する。`CounterStep`はhUGEDriverのNoise Instrument entryへ渡され、7bit/15bitの幅を決める。一方、hUGEDriverの`get_note_poly`はNoise noteからNR43のclock shiftとdivisor codeを計算し、Instrumentのwidth bitと合成してNR43を生成する。したがって、同じNoise Instrumentで異なるNoise noteを演奏できる。

CH4用の責務分担は次のとおりとする。

- Instrument側: `length`、`length_enable`、`initial_volume`、`envelope_direction`、`envelope_sweep`、`width_mode`
- Noise note側: hUGETrackerのNoise note番号へ変換される音名文字列、note側の`length`、`instrument`、必要に応じた共通`volume`、`effect`、`effect_param`
- 再生・変換側: note文字列からnote番号への変換、note番号からclock shift / divisor codeへの変換、`width_mode`との合成、NR43の完成値、Trigger、DAC enable、NR41～NR44への最終書き込み

`clock_shift`と`divisor_code`は同じInstrumentでNoiseの質感やNoise pitch indexを変えられる必要があり、hUGEDriverでもnote処理側で生成されるため、Version 2のNoise Instrument項目にもnote項目にも直接指定しない。Version 2のInstrumentでこれらを指定した場合はエラーとする。`width_mode`はhUGETrackerの`CounterStep`に対応するInstrument固定値であり、note側へ移さない。

Instrument側の `length` はCH4ハードウェアのsound length設定であり、pattern内のnote側にある `length` とは別の項目である。note側の `length` はpattern row数を表し、Instrument側の `length` はNR41へ反映する値を表す。

Version 1では`noise_length`を使用し、Version 2では`length`を使用する。Version 1入力時は従来どおり`noise_length`を解釈し、Version 2入力時に`noise_length`を指定した場合はエラーとする。同一Version内で`noise_length`と`length`を併用しない。既存のVersion 1 SFX用Noise JSONの意味、デフォルト値、バリデーション規則は変更しない。

Version 2のCH4 / Noise用Instrumentでは、次のバリデーションを行う。

- `channel` は必ず `"noise"` とする。
- `length` は整数で0～63の範囲とする。
- `length_enable` はbooleanとする。
- `initial_volume` は整数で0～15の範囲とする。
- `envelope_direction` は `"up"` または `"down"` とする。
- `envelope_sweep` は整数で0～7の範囲とする。
- `width_mode` は `"15bit"` または `"7bit"` とする。
- `noise_length`、`clock_shift`、`divisor_code`はVersion 2のInstrumentで指定禁止とする。
- Pulse専用項目（`duty`、`sweep_time`、`sweep_direction`、`sweep_shift`）は指定禁止とする。
- Wave専用項目（`waveform`、`output_level`）は指定禁止とする。
- `trigger`、`frequency`、DAC enable、NR43完成済みbyte値はJSON項目にしない。
- 型不正、範囲外、未対応項目は無視せずエラーとする。
- 未指定時は上記のVersion 2デフォルト値を使用する。

Frequencyに相当するレジスタ値、Trigger、DAC enable、完成済みNR43 byte、pattern noteそのもの、音符ごとのeffect・volume、効果音再生手順はNoise Instrument JSONでは扱わない。音符ごとの `volume` はVersion 2のnote共通項目として扱い、Noise Instrumentの項目にはしない。Noise noteの音名は`C3`～`B8`または`rest`とし、`clock_shift`、`divisor_code`、数値note番号、NR43生値をJSON利用者へ直接指定させない。

Version 1入力時にはVersion 2の`length`やその他のVersion 2 Noise Instrument解釈を参照しない。Version 2入力時にはVersion 1専用の`noise_length`を参照しない。既存Version 1 JSONは書き換えない。

### Version 2のBGM用Noise note

#### JSON利用者向け仕様

Version 2の`patterns.noise`でも、`note`にはPulse / Waveと同じ音名文字列を使用する。使用可能な音名は既存のnote共通規則に従う`C3`～`B8`とし、休符は`rest`とする。`C3`、`C#3`、`D3`などの大文字・シャープ・オクターブ表記を使用し、`C-4`、`C_4`などの既存JSONで不採用の表記はCH4でも使用しない。

CH4の音名は、Pulse / Waveのような旋律上の正確な音程を保証しない。hUGETrackerのnote番号を通してNR43のclock shiftとdivisor codeへ変換される、抽象的なNoise pitch indexである。同じ音名とInstrumentの組み合わせは、同じ変換規則では同じ結果になる。`width_mode`はNoise Instrument側に保持し、note文字列には含めない。

例えば、Noise patternは次のように記述する。`C4`をキック、`G4`をスネアとするような固定の打楽器対応は定義しない。

```json
"patterns": {
  "noise": {
    "drums_a": [
      { "note": "C4", "length": 4, "instrument": 1 },
      { "note": "G4", "length": 4, "instrument": 2 },
      { "note": "C4", "length": 2, "instrument": 1 },
      { "note": "rest", "length": 2, "instrument": 1 }
    ]
  }
}
```

`rest`を含むnote要素の`instrument`は、CH4専用の別規則を設けず、既存のnote共通仕様に従う。現行のJSON変換ツールではnote要素の`instrument`自体を必須の1～15整数として検証し、`rest`の場合だけ出力cellのInstrumentを0へ変換する。したがって、CH4の`rest`入力で`instrument: 0`を許可する変更は今回行わない。

`kick`、`snare`、`hat`などの打楽器名はnote値として使用しない。同じ打楽器名でもNoise InstrumentとNoise noteの組み合わせで音が変わり、Game Boy CH4にはPCMドラム音源の固定セットがなく、打楽器の役割とNoise pitchを一対一に固定できないためである。将来の制作支援ツールやMIDI変換側で打楽器候補をNoise Instrumentと音名候補へマッピングすることは許可するが、そのマッピングはVersion 2 JSONの正式なnote値ではない。

#### hUGETracker / hUGEDriverの確認済み変換

hUGETracker Song Version 6のpattern cellはCH1～CH4で共通のnote番号フィールドを持つ。`include/hUGE.inc`では`C3`～`B8`が0～71、`___` / `NO_NOTE`が90であり、hUGEDriverは`LAST_NOTE = 72`以上を有効noteとして扱わない。したがって、Version 2のCH4 noteもnote番号0～71へ変換し、`rest`は90へ変換する。

hUGEDriverの`get_note_poly`について、note番号`n`から内部値`x`を次のように作ることを確認した。

```text
x = bitwise_not((n + 192) modulo 256)
```

その後、`x < 7`の場合は`x`をそのまま返し、`x >= 7`の場合は次でNoise polyを生成する。

```text
clock_shift  = (x - 4) div 4
divisor_code = (x modulo 4) + 4
noise_poly   = (clock_shift << 4) | divisor_code
```

上記の式はhUGEDriverの実装上の確認済み規則である。`n = 57`～`63`では`x < 7`の特殊分岐に入り、0～6の値が返る。その他の範囲ではclock shiftとdivisor codeの組み合わせが生成される。対応範囲外のnote番号72～89は有効noteとして扱わず、90は`NO_NOTE`である。`n = 0`～`71`の範囲ではこの変換により同じnote番号から同じNoise polyが得られるが、note番号が上がるほど聞こえるNoiseが単純に高くなる、低くなるという旋律的な関係は仕様として保証しない。

Noise Instrumentの`width_mode`は、hUGEDriverでInstrument entryから得たwidth bitをnote由来のNoise polyへORしてNR43を生成する。`"15bit"`はwidth bitなし、`"7bit"`はbit 3を設定する。Noise Instrumentの音量・lengthはNR42・NR41へ、生成したNoise polyはNR43へ、Instrumentのlength enableとnote発音時のhighmaskはNR44へ反映される。具体的な`.uge`内部値やExport ASMの出力表現は変換ツール対応時に確認する。

JSON利用者はNR43値、clock shift、divisor codeを直接指定しない。次のようなNoise専用noteオブジェクト、`noise_note`項目、数値note、`clock_shift` / `divisor_code`項目は採用しない。

```json
{ "note": { "clock_shift": 4, "divisor_code": 3 } }
{ "noise_note": 27 }
```

既存の4チャンネル共通note構造、hUGETrackerの共通note番号、既存の音名→note番号変換を再利用でき、人間・ChatGPTが編集しやすく、MIDI noteから音名へ変換しやすい。また、JSON利用者をNR43のハードウェア表現から分離できる。CH4だけ異なるJSON構造にすると、pattern生成・検証・自然言語による調整が複雑になるため、Noise専用構造は採用しない。

#### `rest`、`length`、再trigger

- `rest`は新しいNoise発音を開始しない行を表す。
- `rest`は直前のNoise音を明示的に停止する操作ではない。明示的な停止は将来のnote cut、note off、effectなどの別機能として検討する。
- hUGEDriverでは`NO_NOTE`を有効noteとして処理せず、CH4のnote polyやtriggerを更新しないことを確認した。Noiseの自然な減衰・停止はInstrumentのenvelope、hardware length、再生処理に従う。
- note側の`length`はpattern row数であり、Noise Instrument側の`length`はNR41のhardware sound lengthである。両者は別項目である。
- note側の`length`は既存仕様どおり音符行と後続の空行へ展開し、後続の空行でNoiseを再triggerしない。
- 同じNoise音を連打する場合は、note要素を複数記述して各発音位置でtriggerする。現行hUGEDriverでは有効なCH4 note行の処理でNR43とNR44のtriggerが更新される。

例えば、次は1回発音して後続rowを空行とする。

```json
{ "note": "C4", "length": 4, "instrument": 1 }
```

次は2回発音して各note位置で再triggerする。

```json
[
  { "note": "C4", "length": 2, "instrument": 1 },
  { "note": "C4", "length": 2, "instrument": 1 }
]
```

#### note `volume`

CH4でもVersion 2の有効noteではnote共通`volume`を使用できる。`volume`はpattern cell単位の音量指定であり、Noise Instrumentの`initial_volume`とは別の役割を持つ。省略または`null`ではeffectを出力せず、`volume: 0`ではNoise Instrumentのenvelope情報を上位nibbleへ含めた`Cx0`を出力する。上位nibbleが`0`の場合だけ`C00`となる。非null effectは現時点で未対応である。

ただし、CH4の`note: "rest"`では`volume`を指定禁止とする。`volume: null`を含め、restを持つnote要素に`volume`キーが存在する場合はVersion 2の入力バリデーションエラーとする。restは新しいNoise発音を開始せず、直前の音を明示的に停止する操作でもないが、CH4のnoteなし行にvolumeをCxyとして出力すると、hUGEDriverの`fx_set_volume`が`NR42`を書き換えた後に`play_ch4_note`を呼び、保持中の`channel_period4`と`highmask4`で現在音をretriggerするためである。曲の先頭など有効な現在noteがない場合は保持値に依存し、UGE生成と直接ASM生成の意味を入力だけから安定して保証できない。直前のNoise音の音量だけを変更する用途はrestへ暗黙に持たせず、将来のnote off、note cut、volume effectなど、再triggerと状態境界を明示できる機能で扱う。

この禁止規則は、restの意味とCxy動作を確認したVersion 2のCH4だけに適用する。CH1～CH3のrestとvolumeの組み合わせは今回の決定対象外であり、各チャンネルの必要性と再生動作を確認せずに全チャンネル共通規則へ拡張しない。

#### Version 2 Noise noteのバリデーション

- `note`は既存の音名形式または`rest`とする。
- 音名範囲は`C3`～`B8`に限定する。
- 大文字・小文字、シャープ表記、オクターブ表記は既存のnote共通規則に従う。既存規則では音名は大文字、シャープは`#`、音域はC3～B8である。
- `C-4`、`C_4`、`kick`、`snare`、`hat`などはnote値として禁止する。
- 数値のnote番号、NR43生値、`clock_shift`、`divisor_code`の直接指定は禁止する。
- CH4 noteが参照する`instrument`はNoise bankのInstrumentでなければならない。PulseまたはWave用Instrumentを参照した場合はエラーとする。
- `rest`の`instrument`は既存note共通仕様に従い、CH4専用の0許可規則は設けない。
- `note`が`rest`である要素に`volume`キーが存在する場合は、値が`null`でもVersion 2の入力バリデーションエラーとする。
- 未知のnote項目は無視せずエラーとする。
- Version 1とVersion 2の規則を混在させない。

#### Version 1およびSFXとの互換性

今回決定するBGM用Noise noteはVersion 2専用とする。Version 1のCH4 / Noise BGM note対応範囲が未対応である場合は未対応のままとし、Version 1の既存JSON、既存SFX形式、`noise_length`の意味、既存変換動作を変更しない。Version 1入力へVersion 2のNoise BGM note規則を暗黙適用しない。

Version 2ではNoise Instrumentの`length`を使用し、Version 1の`noise_length`は使用しない。Version 2で`noise_length`、Instrument側の`clock_shift`、Instrument側の`divisor_code`を指定した場合は既存の決定どおりエラーとする。既存のSFXがNR43の`clock_shift`や`divisor_code`をstep単位で直接指定する方式を持つ場合、その仕様は変更しない。BGM用JSONとSFX用JSONで内部表現が異なっていても、既存SFXの後方互換性を優先し、将来SFX側も音名方式へ統一するかは今回決めない。

#### MIDIドラム変換との関係

MIDIチャンネル10のドラムnote番号を、そのままVersion 2 JSONのCH4 note番号として使用しない。MIDIドラムnoteは打楽器の種類を表す一方、hUGETrackerのNoise noteはNR43生成用のNoise pitch indexを表すため、意味が異なる。

- MIDIドラムイベントは、Noise InstrumentとNoise noteの組み合わせへ変換する。
- kick、snare、hi-hatなどを異なるInstrumentと音名候補へマッピングすることを候補とする。
- MIDIドラム番号とCH4用Instrument / noteの対応表は、後続のMIDI変換運用設計で決める。
- 自動変換後に、人またはChatGPTが試聴結果をもとにInstrumentとnoteを調整できる構造とする。
- MIDI velocityは既存方針に従い、note `volume`へ変換する候補とする。
- 同時刻の複数ドラムをCH4の単音へ削減する優先順位は、後続WBSで決める。

SFX priority:

- `priority` は `type = "sfx"` のJSONで使用する。
- `priority` は整数値とし、初版では1～5を使う。
- 値が大きいほど高優先度とする。
- `priority = 5`: 地雷爆発、ゲームオーバー。
- `priority = 4`: クリア。
- `priority = 3`: マス開封、旗設置、旗解除。
- `priority = 2`: 決定、キャンセル。
- `priority = 1`: カーソル移動。
- `type = "sfx"` で `priority` が未指定の場合、初版の本番SFX ASM生成ではバリデーションエラーとする。
- `type = "bgm"` では `priority` は使用しない。

JSON側の設計例:

```json
{
  "version": 1,
  "title": "Game Draft",
  "type": "bgm",
  "tempo": 6,
  "instruments": [
    { "id": 1, "name": "lead", "channel": "pulse1" },
    { "id": 2, "name": "bass", "channel": "pulse2" }
  ],
  "order": ["intro"],
  "patterns": {
    "intro": {
      "channels": {
        "pulse1": [
          { "note": "C4", "length": 4, "instrument": 1, "effect": null, "effect_param": null },
          { "note": "E4", "length": 4, "instrument": 1, "effect": null, "effect_param": null },
          { "note": "G4", "length": 4, "instrument": 1, "effect": null, "effect_param": null },
          { "note": "C5", "length": 4, "instrument": 1, "effect": null, "effect_param": null }
        ],
        "pulse2": [
          { "note": "C3", "length": 8, "instrument": 2, "effect": null, "effect_param": null },
          { "note": "G3", "length": 8, "instrument": 2, "effect": null, "effect_param": null }
        ],
        "wave": [],
        "noise": []
      }
    }
  }
}
```

Version 2の4チャンネルBGM構造、チャンネル別order / pattern、Wave table、Noise Instrument、共通note `volume` の確認用サンプルは [4チャンネルBGM JSONサンプル](json_examples/bgm_4ch_sample.json) を参照する。これは決定済み仕様を具体化した確認用データであり、新しいJSON項目や変換規則を追加するものではない。

### 4チャンネル対応へ向けた不足項目（調査結果）

必須
- CH3 Wave Instrument定義
- CH3 Wave table定義
- CH4をBGM利用するためのNoiseノート表現
- Instrument種別(type/channel)の整理

推奨
- CH1周波数スイープ
- Pulse length / length enable
- Version 2のnoteごとのvolume
- チャンネル別order
- ループ範囲指定
- Instrument使用可能チャンネルのバリデーション

将来対応
- 非null effect
- note cut / gate
- Instrument subpattern
- 曲中テンポ変更
- Routine
- Version 7対応

### .uge形式調査結果

調査対象:

- `/home/akihiro/gbdev/hello/assets/twinkle.uge`
- `/home/akihiro/gbdev/hello/src/music/bgm_twinkle.asm`
- hUGETracker公式ソース `src/song.pas`
- hUGETracker公式ソース `src/hugedatatypes.pas`

確認できたこと:

- `.uge` はテキスト形式ではなくバイナリ形式である。
- ローカルの `twinkle.uge` は先頭4バイトが `06 00 00 00` で、hUGETrackerのSong Version 6として読める構造である。
- hUGETracker公式ソースでは、現行の `TSong` はSong Version 7として定義され、Version 1～7を読み込んで現行形式へUpgradeする処理がある。
- `.uge` は曲全体をFreePascalのrecord構造に近い形で保存している。
- Song Version 7の主な構成要素は、`Version`、`Name`、`Artist`、`Comment`、`Instruments`、`Waves`、`TicksPerRow`、`TimerEnabled`、`TimerDivider`、`Patterns`、`OrderMatrix`、`Routines` である。
- `Patterns` はパターン番号と64行分のセルデータを持つ。セルには `Note`、`Instrument`、`Volume`、`EffectCode`、`EffectParams` が含まれる。
- `OrderMatrix` は4チャンネル分の配列で、各チャンネルが再生するパターン番号の並びを保持する。
- `Routines` は16個の文字列として保存される。
- ローカルの `twinkle.uge` には、音色名やデフォルト波形名がASCII文字列として含まれているが、ファイル全体はバイナリである。
- ローカルの `twinkle.uge` には `0x5A` が多数含まれており、後続のnote番号調査で、hUGETracker / hUGEDriver側の `NO_NOTE = 90` と対応することを確認した。

#### Version 6 pattern cellのVolume調査結果

hUGETracker v1.0.11のRelease commit `0623f3f`にある公式ソース `src/hugedatatypes.pas`、`src/song.pas`、`src/trackergrid.pas`、`src/codegen.pas`と、同一セルのVolumeだけを変更したVersion 6 `.uge` のバイナリ比較から、次を確認した。

- `TCellV2`は`packed record`で、`Note: Integer`、`Instrument: Integer`、`Volume: Integer`、`EffectCode: Integer`、`EffectParams: TEffectParams`の順に保存される。
- FreePascalの`Integer`は対象ファイルでは4バイトであり、実ファイルではlittle-endianで保存される。`EffectParams`は1バイトなので、1セルは合計17バイトである。
- セル先頭からのoffsetは、`Note = +0`、`Instrument = +4`、`Volume = +8`、`EffectCode = +12`、`EffectParams = +16`である。
- `WriteSongToStream` / `ReadSongFromStreamV6`は64個の`TCellV2`を含む`TPattern`をrecordのまま読み書きするため、CH1 / CH2 / CH3 / CH4で保存形式は共通である。チャンネルはOrderMatrixが参照するpattern番号によって決まり、セルrecord自体にチャンネル別形式はない。
- 空セルは`Default(TCell)`を基に作られるため`Volume = 0`である。通常patternのGUIはVolume列を常に`...`と描画し、`TTrackerGrid.InputVolume`も空実装であるため、通常patternでは0、1、15を含むVolume値をGUIから明示入力できない。
- 通常patternでVolume欄が空の状態と、内部値として明示的に`Volume = 0`を設定した状態は、どちらも`00 00 00 00`となり、`.uge`上で区別できない。
- バイナリ上で`Volume = 1`は`01 00 00 00`、`Volume = 15`は`0F 00 00 00`となる。ただし、これは型と保存形式の確認用にセル値を直接変更した結果であり、通常patternのGUIで作成した音量指定ではない。
- `Volume`の型は範囲付き型ではなく`Integer`であり、通常pattern向けの0～15バリデーションは公式ソースに存在しない。範囲外のIntegerも読み書き上は保存可能だが、通常patternのGUIから入力できず、音量値としての有効範囲は定義されていない。
- `TTrackerGrid.RenderCell`は通常patternの`Volume`値を表示せず、`RenderCell`によるRGBDS / GBDK Exportも`Volume`を参照しない。このためnoteの有無にかかわらず、通常patternの`Volume`を音量指定として利用できない。
- 通常patternの`Volume`値が次のnoteへ状態として引き継がれる処理は確認できない。公式Export処理が同フィールドを無視するため、`.uge`形式だけから音量状態の継続動作を定義しない。
- 同じ`TCell.Volume`はInstrument subpatternでは音量ではなく、`Jxx`で表示されるsubpatternのジャンプ先行番号として使用される。通常patternのnote volumeと混同しない。

比較に使用した先頭patternの先頭cellでは、セル先頭offsetが`0xF88A`、Volume offsetが`0xF892`だった。条件をVolumeだけに限定した17バイトの比較結果は次のとおりである。offsetは比較用ファイルの固定構成に依存するため、一般仕様として固定しない。

| 状態 | offset `0xF88A`からの17バイト |
| --- | --- |
| Volume欄が空 | `0C 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00` |
| 内部値`Volume = 0` | `0C 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00` |
| 内部値`Volume = 1` | `0C 00 00 00 01 00 00 00 01 00 00 00 00 00 00 00 00` |
| 内部値`Volume = 15` | `0C 00 00 00 01 00 00 00 0F 00 00 00 00 00 00 00 00 00` |

以上から、JSONのnote `volume`は`TCellV2.Volume`ではなくCxy effectとして保存する。volume省略または`null`はeffectなし、CH1 / CH2 / CH3の`volume: 0`は`C00`、CH4の`volume: 0`はNoise Instrumentのenvelope情報を含む`Cx0`（上位nibbleが0の場合のみ`C00`）となるため、両者を区別できる。

Song Versionの決定:

- 本プロジェクト初版では、hUGETracker 1.0.11の安定版で扱えるSong Version 6を対象とする。
- 初版 `tools/json_to_uge.py` が書き出す `.uge` は、Song Version 6を採用する。
- Version 7はGitHub公式リポジトリの最新ブランチ上では現行 `TSong` として確認できるが、現在使用中のhUGETracker v1.0.11配布バイナリには含まれていないため、初版採用は見送る。
- 使用中のhUGETracker実行版は `/mnt/c/Users/akihiro/OneDrive/tools/hUGETracker-1.0.11-windows/hUGETracker.exe` で、実行ファイル内の表示文字列からv1.0.11であることを確認した。
- GitHub Releasesでは、hUGETracker 1.0.11が最新Releaseで、Release commitは `0623f3f` と確認した。
- `0623f3f` 時点の公式ソースでは `UGE_FORMAT_VERSION = 6`、`TSong = TSongV6`、読み込み対応はVersion 1～6までである。
- GitHub最新ブランチ先頭は `aa259a4936b9b539131abf51cdc8486829d2bab4` で、`UGE_FORMAT_VERSION = 7`、`TSong = TSongV7`、Version 6をVersion 7へUpgradeする処理が追加されている。
- v1.0.11実行ファイル内の文字列には `TSongV1`、`TSongV2`、`TSongV3`、`TSongV4`、`TSongV6` が確認できる一方、`TSongV7` は確認できなかった。
- v1.0.11配布物の `Sample Songs` にはVersion 1～6の `.uge` が含まれ、Version 7のサンプルは確認できなかった。
- ローカルの `twinkle.uge` もVersion 6であり、Windows版hUGETrackerで作成・再生確認・RGBDS ASM Exportまで行った実績がある。
- 公式ソースではVersion 6を読み込んでVersion 7へUpgradeする処理があるため、Version 6は新しいhUGETracker系でも読み込み対象である。
- Release Notes、Issue、Pull Request上でVersion 7を正式Release済み仕様として説明している情報は確認できなかった。
- 以上から、Version 7は次期Release向けの開発ブランチ上の保存形式と判断し、現行の安定運用対象はVersion 6とする。

Version 6/7の比較:

| 項目 | Version 6 | Version 7 |
| --- | --- | --- |
| `TicksPerRow` | `Integer` 1つ | 4チャンネル分の `Integer` 配列 |
| チャンネル別tempo | 直接は持たない | 持てる |
| `TimerEnabled` / `TimerDivider` | 持つ | 持つ |
| `Patterns` | `TCellV2` 64行pattern | Version 6と同系統 |
| `OrderMatrix` | 4チャンネル分のorder配列 | Version 6と同系統 |
| 公式ソース上の扱い | 読み込み後Version 7へUpgrade | 現行 `TSong` として読み書き |
| 使用中のv1.0.11実行版 | 配布サンプルと運用実績あり | 対応未確認 |
| v1.0.11 Release source | `TSong = TSongV6` | 存在しない |
| 最新ブランチ source | 読み込み互換対象 | `TSong = TSongV7` |
| 初版ツール実装難度 | 低い | `TicksPerRow` 配列対応が必要 |

Version 6採用理由:

- 初版目的は短いBGM・効果音の下書き生成であり、チャンネル別tempoは不要である。
- `tempo` を単一の `TicksPerRow` に対応させられるため、JSON仕様と実装が単純になる。
- 使用中のhUGETracker v1.0.11配布物にVersion 6サンプルが含まれ、ローカルでもVersion 6の `twinkle.uge` を運用済みである。
- 使用中のv1.0.11実行版でVersion 7を読める根拠が確認できず、Version 7を書き出すと「新しいhUGETrackerで作成された曲」として開けない可能性がある。
- 公式ソースでVersion 6読み込みとVersion 7へのUpgrade経路が確認できるため、将来のhUGETrackerへ移行してもVersion 6資産は読み込める可能性が高い。
- Version 7は最新ブランチ上では確認できるが、現行安定Releaseには含まれていないため、本プロジェクト初版では対象外とする。
- 将来Version 7対応版を使う場合は、`.uge` 形式やJSONから `.uge` への変換処理の見直しが必要になる可能性がある。

`json_to_uge.py` 実装時の注意:

- 先頭のSong Versionはlittle-endianの4バイト整数として `6` を書き出す。
- Version 6の `TicksPerRow` は単一整数として書き出し、JSONの `tempo` を対応させる。
- Version 7形式の `TicksPerRow[0..3]` は初版では書き出さない。
- hUGETrackerで保存し直すと、保存したhUGETracker実行版の対応Song Versionへ更新される可能性があるため、生成直後の `.uge` とhUGETracker保存後の `.uge` は差分が出る前提で扱う。
- Version 7は初版スコープ外とし、WBS上の未完了タスクとしては管理しない。
- 将来Version 7へ移行する場合は、JSONの `tempo` を単一値のまま全チャンネルへ複製するか、チャンネル別tempoを表現できるようJSON仕様を拡張する。

JSON項目と `.uge` 側の対応:

| JSON項目 | `.uge`側の対応 | 備考 |
| --- | --- | --- |
| `version` | JSON仕様バージョン | `.uge` のSong Versionとは別物として扱う。 |
| `title` | `Name` | 曲名・効果音名として保存する。 |
| `type` | 直接対応なし | `bgm` / `sfx` は制作・出力運用上の区分として扱う。 |
| `tempo` | `TicksPerRow` | Version 6では単一値、Version 7では4チャンネル分の配列。初版では全チャンネル同値にする。 |
| `instruments` | `Instruments` | 初版ではsquare/pulse用の最低限の音色定義を中心に扱う。 |
| Version 1の`order` | `OrderMatrix` | 共通のパターン順を4チャンネル分のorder配列へ展開する。 |
| Version 1の`patterns` | `Patterns` | パターン名と`channels`内の各チャンネルを内部pattern番号へ割り当てる。 |
| Version 2の`order.pulse1` | `OrderMatrix[0]` / CH1 pattern cells | Version 2のCH1 OrderMatrixへ変換する。内部pattern番号の割り当ては実装時に決定する。 |
| Version 2の`order.pulse2` | `OrderMatrix[1]` / CH2 pattern cells | Version 2のCH2 OrderMatrixへ変換する。内部pattern番号の割り当ては実装時に決定する。 |
| Version 2の`order.wave` | `OrderMatrix[2]` / CH3 pattern cells | Version 2のCH3 OrderMatrixへ変換する。内部pattern番号の割り当ては実装時に決定する。 |
| Version 2の`order.noise` | `OrderMatrix[3]` / CH4 pattern cells | Version 2のCH4 OrderMatrixへ変換する。内部pattern番号の割り当ては実装時に決定する。 |
| `note` | `TCell.Note` | 音名をhUGETrackerのnote番号へ変換する。休符はNo Note値へ変換する。 |
| `length` | 直接対応なし | 1セルに長さは無い。音符行と休符行へ展開して表現する。 |
| `instrument` | `TCell.Instrument` | 1～15の音色番号として扱う。 |
| `volume` | 単純対応不可 | `TCellV2.Volume`は通常patternの音量指定としてGUI・ASM Exportで使用されず、0は空欄と同じ値になる。Instrumentまたはeffectなど別の表現を後続WBSで検討する。 |
| `effect` | `TCell.EffectCode` | 初版では未指定または基本effectのみ扱う。 |
| `effect_param` | `TCell.EffectParams` | 1バイト値として扱う。nibble分割が必要なeffectは実装時に確認する。 |

note番号・休符値:

- hUGETracker v1.0.11の公式ソース `src/constants.pas` では、`LOWEST_NOTE = 0`、`C_3 = 0`、`HIGHEST_NOTE = 71`、`B_8 = 71`、`NO_NOTE = 90` と定義されている。
- `include/hUGE.inc` でも `C_3 = 0` から `B_8 = 71` まで同じ番号で定義され、`___ = 90`、`NO_NOTE = ___` と定義されている。
- hUGETracker上の音名表記は `C-3`、`C#3`、`D-3` のように、ナチュラル音では音名とオクターブの間に `-` を入れる。
- RGBDS Export ASMでは `C_3`、`C#3`、`D_3` のように、ナチュラル音は `_`、シャープ音は `#` を使う。
- ローカルの `twinkle.uge` とExport ASM `bgm_twinkle.asm` を照合し、ASM上の `C_4`、`G_4`、`A_4`、`___` が `.uge` 内でそれぞれ `12`、`19`、`21`、`90` として現れることを確認した。
- JSON側では、ChatGPTと人間が読み書きしやすい表記として、ナチュラル音は `C3`、`D3`、シャープ音は `C#3`、`D#3`、休符は `rest` を採用する。
- JSON側では `C-3` や `C_3` は採用しない。これらはhUGETracker UIまたはExport ASM側の表記として扱う。

note番号対応:

| JSON音名 | `.uge` `TCell.Note` |
| --- | --- |
| `C3`～`B3` | 0～11 |
| `C4`～`B4` | 12～23 |
| `C5`～`B5` | 24～35 |
| `C6`～`B6` | 36～47 |
| `C7`～`B7` | 48～59 |
| `C8`～`B8` | 60～71 |
| `rest` | 90 |

各オクターブ内の半音順:

| 音名 | オクターブ内オフセット |
| --- | --- |
| `C` | 0 |
| `C#` | 1 |
| `D` | 2 |
| `D#` | 3 |
| `E` | 4 |
| `F` | 5 |
| `F#` | 6 |
| `G` | 7 |
| `G#` | 8 |
| `A` | 9 |
| `A#` | 10 |
| `B` | 11 |

JSON音名から `.uge` note番号への変換方針:

- `rest` は `NO_NOTE = 90` へ変換する。
- 音名は `C3`～`B8` の範囲に限定する。
- シャープは `#` で表記する。フラット表記は初版では扱わない。
- 変換式は `note_number = (octave - 3) * 12 + semitone_offset` とする。
- 例: `C3 = 0`、`C#3 = 1`、`D3 = 2`、`C4 = 12`、`C5 = 24`、`B8 = 71`。
- 範囲外の音名、未対応表記、空文字はバリデーションエラーとする。
- JSONから行展開するとき、音を伸ばすために追加する空行は `rest` と同じ `NO_NOTE = 90` を使う。

note変換実装時の注意:

- hUGETracker UI表記の `C-4` とJSON表記の `C4` は同じ音として扱うが、JSON入力では `C4` に統一する。
- Export ASM表記の `C_4` とJSON表記の `C4` は同じ音として扱うが、JSON入力では `C4` に統一する。
- `C#3` のようなシャープ表記はJSON文字列として問題なく扱えるため、`Cs3` 形式は採用しない。
- `NO_NOTE = 90` はhUGETracker公式ソースとhUGEDriver用 `hUGE.inc` の双方で確認済みのため、休符値として使用する。
- ノイズチャンネルでは音名がノイズ周波数選択として扱われるため、BGM音程と同じ意味で鳴るとは限らない。初版では同じnote番号変換を使い、音色・聴こえ方はhUGETracker上で確認する。

effect code・effect parameter:

- hUGETracker v1.0.11の公式ソース `src/hugedatatypes.pas` では、`TCellV2` が `EffectCode: Integer` と `EffectParams: TEffectParams` を持つ。
- `TEffectParams` は `Value: Byte` としても、`Param1` / `Param2` の2つの4bit nibbleとしても扱える `bitpacked record` である。
- `.uge` Version 6では、pattern内の各セルに `TCellV2.EffectCode` と `TCellV2.EffectParams` が保存される。
- hUGEDriverのpattern rowは `NNNNNNNN, IIIIEEEE, XXXXYYYY` の3バイトで、`E` がeffect code、`X` / `Y` がeffect parameterの上位/下位nibbleである。
- RGBDS Export ASMでは `dn note,instrument,$EPP` の形で出力される。`E` はeffect code、`PP` は `EffectParams.Value` である。
- `include/hUGE.inc` の `dn` macroは、`$EPP` の上位nibbleをeffect code、下位1バイトをeffect parameterとしてdriver用3バイトへpackする。
- hUGEDriver上のeffect未使用は `000`、つまり `EffectCode = 0` かつ `EffectParams.Value = 0` である。
- `EffectCode = 0` でも `EffectParams.Value` が0以外の場合は `0xy` Arpeggioとして扱われるため、未使用effectとは区別する。

effect未使用時の値:

- effect未使用とは、`EffectCode = 0` かつ `EffectParam = 0` の場合である。
- `EffectCode = 0` でも `EffectParam` が0以外の場合は、Arpeggio `0xy` として扱われる。
- そのため、effect未使用判定は `EffectCode` だけでは判定できない。
- 初版 `tools/json_to_uge.py` では、JSONの `effect = null`、`effect_param = null` の場合のみ `EffectCode = 0`、`EffectParam = 0` を出力する。
- 初版では `effect` が `null` 以外の場合は未対応とし、バリデーションエラーとする方針を維持する。

effect code対応:

| code | hUGEDriver表記 | JSON側の予約表記 | 初版対応 |
| --- | --- | --- | --- |
| `0` | `0xy` Arpeggio | `arpeggio` | 未対応 |
| `1` | `1xy` Slide up | `slide_up` | 未対応 |
| `2` | `2xy` Slide down | `slide_down` | 未対応 |
| `3` | `3xy` Toneporta | `tone_portamento` | 未対応 |
| `4` | `4xy` Vibrato | `vibrato` | 未対応 |
| `5` | `5xy` Set master volume | `set_master_volume` | 未対応 |
| `6` | `6xy` Call routine | `call_routine` | 未対応 |
| `7` | `7xy` Note delay | `note_delay` | 未対応 |
| `8` | `8xy` Set panning | `set_panning` | 未対応 |
| `9` | `9xy` Set duty cycle | `set_duty_cycle` | 未対応 |
| `A` | `Axy` Volslide | `volume_slide` | 未対応 |
| `B` | `Bxy` Position jump | `position_jump` | 未対応 |
| `C` | `Cxy` Set volume | `set_volume` | 未対応 |
| `D` | `Dxy` Pattern break | `pattern_break` | 未対応 |
| `E` | `Exy` Note cut | `note_cut` | 未対応 |
| `F` | `Fxy` Set speed | `set_speed` | 未対応 |

effect parameterの扱い:

- `EffectParams.Value` は1バイト値 `0x00`～`0xFF` として扱う。
- hUGETracker / hUGEDriver上ではeffectによって `Param1` / `Param2` のnibble単位で意味を持つものと、1バイト値として意味を持つものがある。
- `0xy` Arpeggio、`5xy` Set master volume、`Axy` Volslide、`Cxy` Set volumeなどはnibble単位の意味があることを公式ソース `src/utils.pas` の説明文字列で確認した。
- `1xy` Slide up、`2xy` Slide down、`3xy` Toneporta、`6xy` Call routine、`7xy` Note delay、`Bxy` Position jump、`Dxy` Pattern break、`Exy` Note cut、`Fxy` Set speedなどは `EffectParams.Value` の1バイト値として扱うことを確認した。
- `4xy` Vibrato、`8xy` Set panning、`9xy` Set duty cycleはdriver-formatおよびhUGEDriverのjump table上に存在するが、パラメータの詳細説明は `src/utils.pas` の `EffectToExplanation` では確認できなかった。

#### hUGEDriver用ASMのnote volume表現

hUGETracker v1.0.11 Release commit `0623f3f`の公式ソース `src/codegen.pas`、`src/utils.pas`、`src/effecteditor.pas`、`src/effecteditor.lfm`と、本リポジトリの`include/hUGE.inc`、`src/hUGEDriver.asm`を照合し、通常patternのcell単位音量変更には`Cxy Set volume`を使用できることを確認した。

通常pattern cellは3バイトで、`dn note,instrument,$EPP`により次の順で格納する。

| byte | bit | 内容 |
| --- | --- | --- |
| 0 | bit 0～6 | note番号 |
| 0 | bit 7 | Instrument番号のbit 4 |
| 1 | bit 7～4 | Instrument番号のbit 3～0 |
| 1 | bit 3～0 | effect code `E` |
| 2 | bit 7～0 | effect parameter `PP` |

例えば`C_4 = 12`、Instrument 1では、effectなしの`dn C_4,1,$000`が`0C 10 00`、音量0の`dn C_4,1,$C00`が`0C 1C 00`、音量1の`dn C_4,1,$C01`が`0C 1C 01`、音量15の`dn C_4,1,$C0F`が`0C 1C 0F`となる。effectなしと明示的な音量0は別のバイト列であり、hUGEDriverでも`000`はeffectなし、`C00`はSet volumeとして別処理になる。

`Cxy`の下位nibble `y`は初期音量0～15、上位nibble `x`はenvelope指定である。hUGETrackerのEffect Editorでは`C - Set Volume`として2つの0～15 TrackBarから入力でき、patternには`Cxy`、RGBDS ASM Exportには`$Cxy`として出力される。公式UIの説明は次のとおりである。

| `x` | 公式UI上の意味 |
| --- | --- |
| `0` | 現在のenvelopeを維持 |
| `1`～`7` | envelope down、周期`x / 64 Hz` |
| `8` | envelope off |
| `9`～`F` | envelope up、周期`(x - 8) / 64 Hz` |

hUGEDriverの`fx_set_volume`はparameterを`swap c`して、`y`をAPU音量の上位nibbleへ、`x`をenvelope側の下位nibbleへ配置し、tick 0だけで処理する。代表値の実際の解釈は次のとおりである。

| parameter | swap後 | CH1 / CH2 | CH3 | CH4 |
| --- | --- | --- | --- | --- |
| `$00` | `$00` | 音量0、現在のenvelopeを維持 | mute | `NR42 = $00` |
| `$01` | `$10` | 音量1、現在のenvelopeを維持 | 25% | `NR42 = $10` |
| `$0F` | `$F0` | 音量15、現在のenvelopeを維持 | 100% | `NR42 = $F0` |
| `$10` | `$01` | 音量0、現在のenvelope下位nibbleと`1`をOR | 25% | `NR42 = $01` |
| `$F0` | `$0F` | 音量0、現在のenvelope下位nibbleと`F`をOR | 25% | `NR42 = $0F` |
| `$FF` | `$FF` | 音量15、現在のenvelope下位nibbleと`F`をOR | 100% | `NR42 = $FF` |

CH1 / CH2では、現在の`NR12` / `NR22`を読み、下位nibbleを残してswap後のparameterをORし、書き戻してnoteをretriggerする。このため`C0y`はInstrumentまたは直前状態のenvelopeを維持し、音量だけを0～15へ変更できる。`x`が0以外の場合、実装は現在の下位nibbleを置換せずORするため、既に立っているenvelope bitをクリアできない。CH1とCH2の差は対象レジスタとretrigger処理だけであり、CH1の周波数sweep設定は変更しない。

CH3では、swap後の値を量子化して`NR32`へ書き、retriggerは行わない。JSON volumeを`C0y`へ対応させる場合のhUGEDriver実装上の対応は、`0 = mute`、`1～4 = 25%`、`5～9 = 50%`、`10～15 = 100%`である。Game BoyのCH3出力レベルがmute / 100% / 50% / 25%の4段階だけであるため、JSONの0～15を15段階のまま表現することはできない。この量子化はhUGEDriver本体に実装済みなのでASM向け変換規則として採用可能だが、異なるJSON値が同じ出力レベルになる。

CH4では、swap後のparameter全体を`NR42`へ直接書いてnoteをretriggerする。従って`y`で音量0～15を指定できるが、CH1 / CH2と異なり`x = 0`でも現在のenvelopeを保持せず、envelope下位nibbleを0へ置き換える。Instrumentのenvelopeを維持するには、同じ行のInstrumentまたは追跡中の状態から`x`を求めて`Cxy`へ含める変換規則が必要である。

tick 0の通常行処理では、valid noteとInstrumentがある場合にInstrumentの`initial_volume`とenvelopeを`NR12` / `NR22` / `NR32` / `NR42`へ先に書き、その後で同じcellのCxyを処理する。このため同じ行のCxyがInstrument値より優先される。noteなしの行でもCxyは処理され、CH1 / CH2 / CH4では現在のnoteをretriggerし、CH3では`NR32`だけを変更する。再生開始直後など有効な現在noteがない状態の聴感は保証しない。

Cxy適用後は専用のソフトウェア音量状態ではなくAPUレジスタ値が維持される。effectなしのrest / 空行、pattern境界、order境界では変更されず、曲ループでも自動リセットされない。次にInstrument番号付きnoteを処理すると、そのInstrumentの音量とenvelopeで先に上書きされる。同じInstrument番号を再指定したnoteでも再ロードされる。Instrument 0のnoteはInstrumentを再ロードしないため現在状態を維持する。ループ後はループ先のInstrumentまたはCxyが再度処理された時点でその値へ変わる。`hUGE_init`を呼び直した場合はdriver内部状態が初期化されるため、曲中の境界とは別に扱う。

以上から、現在のJSON仕様はhUGEDriver用ASMに対して次のように評価する。

| チャンネル | 対応可否 |
| --- | --- |
| CH1 / Pulse1 | `volume`省略時はeffectなし、0～15は`C0y`とすれば、そのまま実現可能。Instrument envelopeは維持される。 |
| CH2 / Pulse2 | CH1と同じ方法で、そのまま実現可能。 |
| CH3 / Wave | `C0y`へ変換可能だが4段階へ量子化されるため、0～15を完全には実現できない。hUGEDriver既定の境界を変換規則として使用する。 |
| CH4 / Noise | 0～15の音量自体は表現できるが、Instrumentまたは直前のenvelopeを維持するには`x`を補完する状態追跡規則が必要。 |

UGE出力では通常patternの`TCellV2.Volume`を使用せず、`EffectCode = $C`と`EffectParams.Value = xy`を設定してCxyとして出力する。JSONのvolume省略または`null`はeffectを追加せず、`volume: 0`はCH1 / CH2 / CH3では`C00`、CH4ではNoise Instrumentのenvelope nibbleを含む`Cx0`へ変換する。`volume: 1`～`15`も同様に下位nibble `y`へ変換する。

#### Version 2 CH4でInstrumentとvolumeを同時指定する場合

Version 2のCH4 / Noise noteでInstrumentと`volume`を同じnoteに指定した場合は、対象Noise Instrumentのenvelopeを維持するため、`Cxy`の`x`をInstrumentの`envelope_direction`と`envelope_sweep`から生成し、`y`をnoteの`volume`とする。変換式は`x = envelope_sweep`（`down`）または`x = $8 | envelope_sweep`（`up`）であり、NR42生成式`(initial_volume << 4) | (direction_bit << 3) | envelope_sweep`の下位nibbleと一致する。`width_mode`、`length`、`length_enable`は`x`へ含めない。これによりInstrumentの`initial_volume`だけをnoteの`volume`で上書きし、envelope方向と周期は維持する。

| `envelope_direction` | `envelope_sweep` | `x` |
| --- | ---: | ---: |
| `down` | 0～7 | `$0`～`$7` |
| `up` | 0～7 | `$8`～`$F` |

従って、down / sweep 0、1、7はそれぞれ`x = 0`、`1`、`7`、up / sweep 0、1、7はそれぞれ`x = 8`、`9`、`F`となる。down / sweep 0とup / sweep 0のNR42下位nibbleはそれぞれ`$0`と`$8`であり、どちらもsweep paceが0なので通常のenvelope変化は無効となる。ただし、対象InstrumentのNR42ビット列を忠実に反映するため、sweep 0でもdirection bitを維持し、両者を同じバイト値へ正規化しない。`x = 8`はhUGETracker Effect Editorの「envelope off」という説明とハードウェア動作が整合する。一方、`x = 0`の「現在のenvelopeを維持」という説明は、現在のenvelope下位nibbleを残すCH1 / CH2のdriver処理には当てはまるが、swap後の値全体でNR42を書き換えるCH4には当てはまらない。

具体例:

- down / sweep 0 / volume 5 → `C05`
- down / sweep 2 / volume 5 → `C25`
- up / sweep 0 / volume 5 → `C85`
- up / sweep 2 / volume 5 → `CA5`
- down / sweep 2 / volume 0 → `C20`
- up / sweep 2 / volume 15 → `CAF`

同じ条件で`volume`を省略した場合はCxyを生成せず、従来どおりInstrumentの`initial_volume`とenvelopeを使用する。この規則はVersion 2のCH4 noteでInstrumentと`volume`を同時指定した場合だけに適用し、Version 1のNoise変換には適用しない。`length`展開で生成される後続空行およびpattern末尾の補完行にもCxyは出力しない。

#### Version 2 CH4 note volumeのpattern / order / loop境界

hUGEDriverの確認済み動作として、通常のpattern切替とorder遷移はpattern pointer、`current_order`、`row`を更新するだけであり、`NR42`またはCH4のenvelope状態を初期化しない。order末尾からorder 0へ戻る全体ループでも同様である。このため、APU上の状態を曲全体で連続して追跡する方式では、ループ後に初回と同じ開始状態になる保証がなく、同じpatternを複数のorder位置から参照した場合も進入元によって開始時の状態が異なり得る。

Pocket SweeperのVersion 2 CH4 note volumeでは、この継続状態を変換時の入力として使用しない。`volume`を持つ各有効noteについて、同じnoteで必須指定される1～15のNoise Instrumentからenvelope nibble `x`を必ず生成し、noteの`volume`を`y`として`Cxy`を出力する。曲頭、pattern先頭、order先頭、loop先頭へ専用のreset cellやCxyは追加せず、order位置ごとの状態計算も行わない。従って、同一patternはどのorder位置から参照されても同じcell列へ変換し、loopによる再進入でもvolume指定noteへ到達した時点の`NR42`は初回と同じ値へ設定される。volume指定noteより前にあるvolume未指定行のAPU状態や聴感まで初回と同一にする仕様ではない。

この方式は、各noteのInstrumentが必須でInstrument 0を禁止する現行仕様、およびInstrument指定時に対象InstrumentのenvelopeをCxyへ反映する確定済み方針を利用する。`.uge`では通常pattern cellの`EffectCode = $C`と`EffectParams.Value = xy`、hUGEDriver用ASM直接出力では同じcellの`$Cxy`として表現し、両出力で同一のpattern cell列と意味を維持する。境界専用データを出力形式ごとに追加しない。

なお、コード上のレジスタ書き込み順と状態非初期化は確認済みだが、実機またはエミュレータでpattern再利用とloop再進入を含む聴感比較は未実施である。また、Version 2の`loop.mode = "range"` / `"none"`自体のUGE・ASM実現方式は別の後続WBSで未確定であり、ここで確定するのは、どのorder境界へ遷移する場合もCH4 note volumeの変換規則を進入元に依存させないことまでとする。

#### JSON noteにおけるInstrument 0とinstrument省略

Version 1 / Version 2とも、JSONのnoteでは`instrument`を必須とし、Instrument IDは従来どおり1～15とする。Instrument 0の明示指定および`instrument`の省略は許可しない。現在のゲームでInstrumentなしnoteをJSONから生成する明確な利用目的はなく、Version 2 CH4のnote volumeは同じnoteで指定するNoise InstrumentからCxyのenvelope nibbleを生成することで表現できるためである。Instrument 0を許可すると、直前のInstrumentまたはNR42状態をpattern / order / loop境界をまたいで追跡し、UGEと直接生成ASMで一致させる必要があり、変換結果が再生経路へ依存する。将来のMIDI変換でInstrument再指定を省略できる可能性や小さなROM削減だけを理由に、この状態依存を導入しない。

従って、Version 2 CH4 noteで`volume`を指定する場合は、必ず同じnoteのNoise InstrumentからCxyの`x`を生成し、直前のenvelope状態は取得・追跡しない。Instrument 0用のenvelope定義やデフォルト値も設けない。この決定によるVersion 1のJSON仕様、バリデーション、Noise変換への変更はない。

JSONの`rest`もnote共通仕様に従って`instrument`に1～15を必須とするが、変換後のrest cellではInstrument 0を使用してInstrumentを再ロードしない。また、noteの`length`展開で生成される後続の空cellおよび64行までの補完空cellでも、内部表現としてInstrument 0を使用できる。これらは変換処理が生成する「Instrumentなし」の内部値であり、JSON入力でInstrument 0または`instrument`省略を許可することを意味しない。

JSON側で採用するeffect表記:

- effect未使用は `effect: null`、`effect_param: null` とする。
- 初版 `tools/json_to_uge.py` では、`effect: null`、`effect_param: null` のみを対応対象とする。
- 初版で `effect` に非null値が指定された場合は、将来の実装ではバリデーションエラーにする方針とする。
- 非null effectを将来対応する場合は、上記のJSON側予約表記を使う。
- 非null effect対応時の `effect_param` は、まず `0`～`255` の整数として扱う方針とする。nibble単位の指定が必要になった場合はJSON仕様を拡張する。

初版 `tools/json_to_uge.py` で対応するeffect:

- effect未使用のみ対応する。
- `effect: null`、`effect_param: null` を `.uge` の `EffectCode = 0`、`EffectParams.Value = 0` へ変換する。
- Export ASM上では `$000` として出力される状態を目標にする。

初版 `tools/json_to_uge.py` では対応しないeffect:

- `arpeggio`
- `slide_up`
- `slide_down`
- `tone_portamento`
- `vibrato`
- `set_master_volume`
- `call_routine`
- `note_delay`
- `set_panning`
- `set_duty_cycle`
- `volume_slide`
- `position_jump`
- `set_volume`
- `pattern_break`
- `note_cut`
- `set_speed`

effect変換実装時の注意:

- `EffectCode = 0`、`EffectParams.Value = 0` はeffect未使用だが、`EffectCode = 0`、`EffectParams.Value != 0` はArpeggioである。
- 未使用判定を `EffectCode == 0` のみで実装してはいけない。必ず `EffectCode == 0` かつ `EffectParams.Value == 0` で判定する。
- `effect_param` を扱う場合は、`TEffectParams.Param1` / `Param2` のbitpacked上の並びと、hUGEDriver document上の `X` / `Y` の対応をeffectごとに確認する。
- `5xy`、`8xy`、`Bxy`、`Dxy`、`Fxy` はhUGEDriver上でglobal effectとして扱われるため、BGM全体への影響を確認してから対応する。
- `6xy` Call routineはroutine定義と組み合わせる必要があるため、初版では扱わない。
- `9xy` Set duty cycleはチャンネルやinstrument状態との関係を確認してから対応する。
- 非null effectを追加する場合は、hUGETrackerで読み込み、再生、保存、ASM Exportした結果を必ず確認する。

Instrument構造:

- hUGETracker v1.0.11の公式ソース `src/hugedatatypes.pas` では、Version 6の `TInstrument` は `TInstrumentV3` である。
- `TInstrumentV3` はInstrument種別にかかわらず同じrecord構造を持ち、`Type_` によってSquare/Duty、Wave、Noiseとして扱う。
- `TInstrumentType` は `itSquare = 0`、`itWave = 1`、`itNoise = 2` である。
- `TInstrumentCollectionV3` は `Duty`、`Wave`、`Noise` の3 bankを持ち、各bankは `1..15` の15個である。`All[1..45]` としても参照できる。
- Instrument番号 `0` はhUGEDriver上で「Instrumentなし」として扱われるため、JSONで指定できるInstrument IDは `1`～`15` とする。

`TInstrumentV3` の主なメンバー:

| メンバー | 用途 |
| --- | --- |
| `Type_` | `itSquare` / `itWave` / `itNoise` の種別。 |
| `Name` | hUGETracker上のInstrument名。 |
| `Length` | 各チャンネルのlength registerへ反映される値。 |
| `LengthEnabled` | length counterを使うかどうか。 |
| `InitialVolume` | Square/Noiseの初期音量。 |
| `VolSweepDirection` | Square/Noiseのvolume envelope方向。 |
| `VolSweepAmount` | Square/Noiseのvolume envelope量。 |
| `SweepTime` | SquareのNR10 sweep time。 |
| `SweepIncDec` | SquareのNR10 sweep方向。 |
| `SweepShift` | SquareのNR10 sweep shift。 |
| `Duty` | Squareのduty比。 |
| `OutputLevel` | Waveの出力レベル。 |
| `Waveform` | Waveが参照する波形番号。 |
| `CounterStep` | Noiseの7bit/15bit counter設定。 |
| `SubpatternEnabled` | Instrument subpatternを使うかどうか。 |
| `Subpattern` | Instrument subpattern。64行の `TPattern`。 |

Version 6でのInstrument保存形式:

- `TSongV6` は固定長record部分に `Instruments: TInstrumentCollection` を含む。
- `WriteSongToStream` は `TSong` から `TPatternMap`、`TOrderMatrix`、`TRoutineBank` を除いた固定長部分を先に書き出すため、Instrumentは曲名、作者、コメントの後、Wave bankやtempoより前に保存される。
- 保存されるInstrumentはDuty 15個、Wave 15個、Noise 15個の合計45個である。
- `.uge` 内では `TInstrumentV3` recordとして保存される。ASM Export時のdriver用Instrumentは `.uge` 内のrecordそのものではなく、`InstrumentToBytes` でhUGEDriver用のバイト列へ変換される。
- hUGEDriver用ASMでは、Square/Wave/Noiseの各Instrument entryは実質6バイト単位で出力される。Square/Waveは4バイトのregister系値とsubpattern pointer、Noiseはenvelope、subpattern pointer、highmask/length相当、paddingで構成される。
- `src/song.pas` は保存時に `SizeOf(TSong)` や `SizeOf(TInstrumentV3)` を使う。Pythonで実装する場合は手計算したサイズだけに依存せず、hUGETrackerが保存した `.uge` と照合する。
- この環境ではFreePascalコンパイラが無く、`SizeOf(TInstrumentV3)` の数値を実行確認できなかった。実装時は実ファイルとの照合で確定する。

hUGETracker新規作成時のInstrument初期値:

- `InitializeSong` は全Instrumentを `Default(TInstrument)` で初期化し、全Instrumentの `Subpattern` を `BlankPattern` で空パターン化する。
- Duty bankは全15個に `Type_ = itSquare`、`Length = 0`、`LengthEnabled = False`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`SweepTime = 0`、`SweepIncDec = stDown`、`SweepShift = 0`、`Duty = 2`、`OutputLevel = 1` を設定する。
- Wave bankは全15個に `Type_ = itWave`、`Length = 0`、`LengthEnabled = False`、`OutputLevel = 1`、`Waveform = I - 1` を設定する。
- Noise bankは全15個に `Type_ = itNoise`、`Length = 0`、`LengthEnabled = False`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`CounterStep = swFifteen` を設定する。
- `LoadDefaultInstruments` はDuty 1～8に名前とduty比を設定し、Duty 5～8には `VolSweepAmount = 1` を設定する。
- `LoadDefaultInstruments` はWave 1～11にデフォルト波形名を設定し、`DefaultWaves` を `Waves[0..10]` へ設定する。
- ローカルの `twinkle.uge` には `Lead 12.5%`、`Base 25%`、`Coin 50%`、`Laser75%`、`Duty 25% plink`、`Square wave 12.5%` などのInstrument名文字列が含まれることを確認した。

Instrumentの最小構成:

- 再生に必要な最小構成は、使用するbankのInstrument `Type_`、鳴る音量設定、長さ設定、subpattern無効状態、空のsubpatternである。
- Square/Dutyを鳴らすには、少なくとも `Type_ = itSquare`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`Duty`、`Length = 0`、`LengthEnabled = False`、`SubpatternEnabled = False` を設定する。
- Waveを鳴らすには、`Type_ = itWave`、`OutputLevel = 1`、`Waveform`、`Length = 0`、`LengthEnabled = False`、`SubpatternEnabled = False` を設定する。`OutputLevel = 0` は無音になるため避ける。
- Noiseを鳴らすには、`Type_ = itNoise`、`InitialVolume = 15`、`VolSweepDirection = stDown`、`VolSweepAmount = 0`、`CounterStep = swFifteen`、`Length = 0`、`LengthEnabled = False`、`SubpatternEnabled = False` を設定する。
- `Default(TInstrument)` のままではSquare/Noiseの `InitialVolume` が0になり、無音になるため、0初期化だけでInstrumentを生成してはいけない。
- `Subpattern` は未使用でもrecord上は存在するため、`BlankPattern` 相当で全セルを `NO_NOTE` にした空パターンとして保存する。
- Wave/Noiseを初版で未使用にする場合でも、`.uge` Version 6の固定record構造として15個ずつ保存する必要がある。

JSON項目とInstrumentの対応:

| JSON項目 | `.uge`側の対応 | 初版方針 |
| --- | --- | --- |
| `id` | bank内のInstrument番号 `1..15` | 1～15のみ許可する。 |
| `name` | `TInstrument.Name` | 指定された名前を保存する。未指定ならデフォルト名を使う。 |
| `channel` | `Duty` / `Wave` / `Noise` bank選択 | `pulse1` / `pulse2` はDuty、`wave` はWave、`noise` はNoiseへ割り当てる。 |
| 詳細音色パラメータ | `Duty`、`InitialVolume`、`VolSweepDirection`、`VolSweepAmount` など | Pulse向けに `duty`、`initial_volume`、`envelope_direction`、`envelope_sweep` を扱う。 |

- 初版では、JSONの `id`、`name`、`channel` と、任意のPulse Instrument詳細からInstrumentを生成する。
- `pulse1` と `pulse2` はどちらも同じDuty bankのInstrument番号を参照する。
- JSONの `channel` は主にどのbankへInstrumentを配置するかを決めるための情報であり、pattern cell側では `TCell.Instrument` に `id` を入れる。
- 同じ `id` を異なるbankで使うことは可能だが、同じbank内で重複した `id` はバリデーションエラーとする。
- Pulse Instrument詳細が未指定の場合は、従来どおりhUGETracker初期値またはデフォルトInstrument相当を使う。

初版 `tools/json_to_uge.py` のInstrument方針:

- Pulse向けInstrumentを主対象とし、`pulse1` / `pulse2` はDuty bankへ出力する。
- Duty bank、Wave bank、Noise bankは常に15個ずつ生成する。
- 使用されていないInstrumentもhUGETrackerの初期値相当で出力する。
- Duty 1～8は `LoadDefaultInstruments` 相当の名前、duty比、volume envelopeを使う。JSONでPulse Instrument詳細が指定されたInstrumentは、その値で上書きする。
- Wave/Noiseは初版では詳細編集を行わず、hUGETracker初期値相当の固定値で生成する。
- `SubpatternEnabled` は全Instrumentで `False` とし、`Subpattern` は空パターンにする。
- `tools/json_to_huge_asm.py` はPulse Instrument詳細をhUGEDriver ASMのduty instrument entryへ反映する。
- `tools/json_to_uge.py` はPulse Instrument詳細をSong Version 6のDuty bank Instrumentへ反映する。

Instrument実装時の注意:

- Instrument ID `0` は「Instrumentなし」なのでJSONでは禁止する。
- `InitialVolume = 0` のSquare/Noise、`OutputLevel = 0` のWaveは無音になるため、デフォルト値を必ず設定する。
- Instrumentのrecordサイズ、`ShortString`、enum、Boolean、subrange型の保存サイズはFreePascalのバイナリ表現に合わせる必要がある。
- Python実装時は、公式ソースのfield順に従って書き出し、hUGETrackerで保存した `.uge` との比較でoffsetとサイズを確認する。
- `.uge` 内のInstrument recordと、ASM Export後のhUGEDriver用Instrumentバイト列は同一ではない。`.uge` 生成では `TInstrumentV3` を書き、ASM出力はhUGETrackerに任せる。
- Wave bankを使わない場合でも、`Waves` とWave InstrumentはVersion 6の固定構造として保存する。

wave/noise未使用時の扱い:

- 初版では、`wave` / `noise` チャンネルを省略するのではなく、空patternを再生する未使用チャンネルとして扱う。
- hUGETracker v1.0.11の `InitializeSong` は4チャンネルすべての `OrderMatrix` を長さ2に初期化し、各チャンネルの先頭にpattern番号を設定する。
- hUGETrackerのExport処理は `OrderMatrix[I]` の `High(...)-1` までを有効orderとして扱う実装になっているため、空配列ではなく、少なくとも長さ2のOrderMatrixを持たせる方針にする。
- `WriteSongToStream` はOrderMatrixの長さを書いた後、`OrderMatrix[i][0]` から内容を書き出すため、長さ0のOrderMatrixは避ける。
- `wave` / `noise` を未使用にする場合も、pulse側と同じorder数にそろえ、各orderで空patternを参照させる。
- 空patternは `BlankPattern` 相当とし、64行すべて `Note = NO_NOTE`、`Instrument = 0`、`Volume = 0`、`EffectCode = 0`、`EffectParams.Value = 0` にする。
- `Instrument = 0` はhUGEDriverで「Instrumentなし」として扱われるため、空pattern内ではWave/Noise Instrumentを参照しない。

確認できたこと:

- hUGETracker公式ソース `src/utils.pas` の `BlankPattern` は、全セルを `Default(TCell)` にした上で `Note = NO_NOTE` を設定する。
- hUGETracker公式ソース `src/hugedatatypes.pas` の `TPatternMap.GetOrCreateNew` は、存在しないpattern番号を参照した場合に `BlankPattern` で空patternを作成する。
- hUGETracker公式ソース `src/codegen.pas` の `FindUsedStuff` は、Wave/Noise channelのpattern内で `Instrument = 0` のセルをInstrument未使用として扱い、Wave/Noise Instrumentの使用数を増やさない。
- hUGETracker公式ソース `src/codegen.pas` の `RenderInstruments` は、使用上限が `-1` のbankではInstrument entryを出力しない。
- ローカルの `bgm_twinkle.uge` はhUGETracker v1.0.11で作成・保存・RGBDS ASM Export済みのVersion 6ファイルであり、Export ASM `bgm_twinkle.asm` ではCH3に対応する `bgm_twinkle_P2` が64行すべて `dn ___,0,$000` の空patternとして出力されている。
- 現在の `src/bgm_test.asm` では、CH3/CH4に対応する `TestBgmPattern3` / `TestBgmPattern4` を64行すべて `dn ___, 0, $000` とし、`TestBgmWaveInstruments` / `TestBgmNoiseInstruments` は空sectionとして扱っている。

OrderMatrixの扱い:

- 初版 `tools/json_to_uge.py` では、4チャンネルすべてにOrderMatrixを出力する。
- `wave` / `noise` が未使用の場合でも、OrderMatrix自体は省略しない。
- `wave` / `noise` の各orderは、空pattern番号を参照させる。
- hUGETrackerの初期化・Export処理に合わせ、OrderMatrixは長さ0にしない。
- pulse側に複数orderがある場合、`wave` / `noise` も同じorder数分だけ空patternを並べる。

Patternの扱い:

- 空patternは64行固定で出力する。
- 各行は `NO_NOTE = 90`、`Instrument = 0`、`Volume = 0`、`EffectCode = 0`、`EffectParams.Value = 0` とする。
- Export ASM上では `dn ___,0,$000` が64行並ぶpatternとして見える。
- hUGETrackerの `OptimizeSong` は同一内容のpatternをまとめるため、Wave/Noise用の空patternがExport時に1つへ統合される可能性がある。

Instrumentの扱い:

- `wave` / `noise` が未使用でも、`.uge` Version 6の固定構造としてWave bank 15個、Noise bank 15個は保存する。
- 未使用channelのpattern cellでは `Instrument = 0` とするため、Wave/Noise Instrumentは参照されない。
- Wave/Noise InstrumentはhUGETracker初期値相当の固定値で出力する。
- Export ASMでは、Wave/Noise Instrumentが参照されていない場合、`wave_instruments:` / `noise_instruments:` ラベルは出るが、その配下にInstrument entryは出力されない。

Export ASM上の見え方:

- order tableには `order3` / `order4` も出力される。
- `wave` / `noise` 未使用channelのorderは空patternを参照する。
- 空patternは `dn ___,0,$000` のみで構成される。
- Wave/Noise Instrumentが参照されない場合、`wave_instruments:` / `noise_instruments:` は空になる。

初版 `tools/json_to_uge.py` でのwave/noise出力方針:

- JSONの `channels.wave` または `channels.noise` が空配列、または未指定相当の場合は、そのチャンネルを未使用として扱う。
- 未使用channelには空OrderMatrixではなく、空pattern参照を持つ最小構成のOrderMatrixを書き出す。
- 空patternは全セル `NO_NOTE` / `Instrument = 0` / effect未使用で書き出す。
- Wave/Noise Instrument bankは常に15個ずつhUGETracker初期値相当で書き出す。
- Wave bank用の `Waves` もVersion 6の固定構造として保存する。
- 初版ではWave/Noiseの詳細編集は行わず、未使用または空patternのみを基本とする。

wave/noise未使用実装時の注意:

- OrderMatrixを長さ0にしない。
- Wave/Noise用のpattern番号が `Patterns` に存在するようにする。
- 空patternには `Instrument = 0` を使い、未使用Instrument番号を誤って参照しない。
- Wave/Noiseを未使用にしても、`.uge` の固定record領域からWave/Noise InstrumentやWave bankを削らない。
- hUGETrackerの直接GUI操作による最小 `.uge` の新規作成・再保存は今回実施していない。生成 `.uge` の読み込み・保存・ASM Export確認は、後続WBS「生成した `.uge` をhUGETrackerで読み込み・保存・ASM Exportできることを確認する」で実施する。

初版 `tools/json_to_uge.py` で対応する範囲:

- `.uge` バイナリを書き出す。
- Song VersionはVersion 6を書き出す。
- `title` を曲名として保存する。
- `tempo` を全チャンネル共通のticks-per-rowとして保存する。
- 最大64行の短いパターンを生成する。
- `pulse1` / `pulse2` を中心に、note、instrument、effect、effect_paramをセルへ変換する。
- Version 2のnote `volume`はJSON上で省略または`null`と`volume: 0`を区別し、UGEの通常pattern cellへCxy（`EffectCode = $C`、`EffectParams.Value = xy`）として出力する。CH1 / CH2 / CH3では省略または`null`はeffectなし、`volume: 0`は`C00`となる。CH4では省略または`null`はeffectなし、`volume: 0`はNoise Instrumentのenvelope direction / sweepを上位nibbleへ含めた`Cx0`となり、上位nibbleが0の場合のみ`C00`となる。
- `wave` / `noise` は空パターンまたは限定対応から始める。
- `length` は音符セルと休符セルへ展開する。
- 未使用のinstrument、wave、routineはhUGETrackerの初期値または空値に近い状態で出力する。

初版 `tools/json_to_uge.py` では対応しない範囲:

- hUGETrackerの全effect対応。
- instrument subpattern、routine、wave tableの詳細編集。
- チャンネルごとに異なるtempo。
- 高度なpattern再利用最適化。
- hUGETracker上の全GUI設定の再現。
- 既存 `.uge` の読み込み・差分マージ。

実装時の注意点:

- `.uge` はバイナリ形式のため、文字列連結ではなく `struct` などで明示的にバイト列を書き出す。
- FreePascalの `Integer` サイズ、booleanサイズ、`ShortString` の保存形式、packed recordのアラインメントを公式ソースと実ファイルで照合する。
- 初版対象はSong Version 6に固定し、`TicksPerRow` は単一整数として実装する。
- hUGETrackerが読む順序は、固定長領域、pattern数、pattern keyとpattern本体、4チャンネル分のorder配列、routine文字列の順である。
- pattern cellは64行固定として扱う。
- `length` は `.uge` に直接保存されないため、行展開後に64行を超えないようバリデーションする。
- 出力した `.uge` はhUGETrackerで開けることを必ず確認する。

未確定事項・TODO:

- 非null effectを実装対象に追加する場合、各effectのチャンネル制約、tick上の挙動、parameterの意味を個別に確認する。
- noteの `volume` はUGEの通常pattern cellへCxyとして変換する。CH1 / CH2 / CH3は`C0y`、CH4は各volume指定noteのNoise Instrumentからenvelope nibbleを生成する。
- noteの `volume` はhUGEDriver用ASMでも同じCxyへ変換する。volume省略または`null`ではeffectを出力せず、`volume: 0`では明示的なCxyを出力する。

### JSON仕様のバージョン更新方針

- 楽曲定義JSONの `version` は、JSON仕様の世代を表す整数とする。
- 現行仕様は `version: 1` とする。
- バージョン番号は `1`、`2`、`3` のように1ずつ増加させる。
- 小数やセマンティックバージョニング形式は使用しない。
- JSONの構造、必須項目、項目の型、項目の意味など、変換ツールの解釈に影響する変更を行う場合はバージョンを更新する。
- 既存JSONを同じ意味で解釈できなくなる変更は、必ず新しいバージョンとして扱う。
- 誤字修正、説明の整理、実装内部の変更など、JSONの解釈結果に影響しない変更ではバージョンを更新しない。
- 変換ツールは、対応していないバージョンを推測で処理せず、分かりやすいエラーを出す。
- バージョンを更新する場合は、JSON仕様書、サンプルJSON、関連する変換ツールを同じ作業単位で更新する。
- 新しい任意項目の追加を同一バージョン内の拡張として扱うか、新しいバージョンとして扱うかは、既存JSONとの後方互換性方針と合わせて決定する。

### 既存JSONとの後方互換性方針

- 既存の楽曲定義JSONとの後方互換性を維持する。
- 現行JSON仕様は引き続き `version: 1` として扱う。
- 4チャンネル対応など、今後拡張するJSON仕様は `version: 2` とする。Version 2の具体的なJSON構造は別途確定する。
- 関連するJSON変換ツールは、当面 `version: 1` と `version: 2` の両方を明示的に処理する。
- `version: 1` のJSONは、現在と同じ項目の意味、デフォルト値、バリデーション規則を維持する。
- Version 2対応のために、Version 1の項目の意味を変更しない。
- Version 1に存在しないVersion 2項目は、Version 1入力時には参照しない。
- Version 1からVersion 2への自動変換機能は現時点では必須としない。
- Version 2からVersion 1へのダウングレード機能は作成しない。
- 既存のVersion 1 JSONを一括してVersion 2へ書き換えることは必須としない。
- Version 2仕様確定後に新規作成するJSONは、原則としてVersion 2を使用する。
- 未対応のversionは推測で読み込まず、分かりやすいエラーとする。
- 将来Version 1対応を廃止する場合は、別途WBSを追加して判断する。

後方互換性は、Version 2対応後の変換ツールへ既存のVersion 1 JSONを入力した場合に、以下を満たすことと定義する。

- Version 1 JSONがエラーにならず読み込める。
- 各項目が従来と同じ意味で解釈される。
- Instrument、音符、テンポ、パターン順、効果音priorityなどが従来と同じ意味になる。
- 生成されるASMまたはUGEの再生結果が実質的に同等になる。
- ラベル順、コメント、未使用データの配置など、再生に影響しない差分は許容する。
- バイト単位またはテキスト単位での完全一致は必須としない。

### Version 2 note volume追加時のVersion 1 Noise互換性方針

Version 2のCH4 note `volume`を実装しても、Version 1のNoise変換結果と動作を変更しない。互換性の境界はJSONの`version`値で明示し、note `volume`の検証、内部表現、Cxy生成、およびそれに伴う空行補完はVersion 2の処理経路だけで行う。共通処理を変更する場合は、Version 1入力では従来と同じ値を渡す分岐または専用の互換経路を設け、Version 1の出力を固定する。

Version 1で維持する出力は次のとおりとする。

- Version 1のnoteに`volume`キーを追加しない。キーが存在する場合はVersion 1入力のバリデーションエラーとする。
- UGEでは、従来のpattern cellのnote、Instrument、Volume、EffectCode、EffectParams.Value、および`length`展開後の空行を変更しない。Noise Instrument bankは15個の固定領域を維持し、Version 1のNoise Instrumentは名前を除き、`length=0`、`length_enable=false`、`initial_volume=15`、音量sweep下降、sweep量0、`counter_step=15bit`相当の既定値を維持する。未定義のNoise Instrumentも同じ既定値とする。
- hUGEDriver用通常ASMでは、Version 1のpattern cellを従来どおり`dn <note>,<instrument>,$000`で出力し、effectは`$000`のままとする。`noise_instruments:`は従来どおり空のbankラベルとし、Version 2 Noise Instrument entryやCxyを追加しない。未使用channelの空patternも従来どおり`dn ___,0,$000`とする。
- Version 1のNoise Instrumentを、Version 2のnote `volume`用のenvelope補完やInstrument 0解決の入力として扱わない。Version 2で必要な状態はVersion 2専用の内部表現で保持する。

実装時は、まず入力Versionを取得し、Version 1では従来のnote変換、Instrument packing、pattern cell生成、空行補完、Noise bank生成をそのまま選択する。Version 2でのみ`volume`を検証し、UGEで表現できない場合の扱いを含めた方式と、hUGEDriver ASMのCxy生成を適用する。CxyはVersion 1のeffect出力へ遡及して追加しない。

この方針の回帰確認では、既存のVersion 1 Noiseを含むJSON（`assets/se_cursor.json`およびNoiseを含む既存サンプル）から変更前後のUGEをバイト単位で比較し、通常ASMをテキスト単位で比較する。差分が出た場合は、再生に影響しない差分として許容する前に原因を特定する。さらに、Version 1 Noise BGM/SFXをテストROMまたはSameBoy等で再生し、note、音量envelope、7bit/15bit、length、再trigger、空行の挙動に変化がないことを確認する。これらの自動比較・再生確認は、note volume変換実装および検証の後続WBSで回帰テストとして追加する。


## 関連仕様

サウンド全体の再生・実装方針は [サウンド仕様](sound-spec.md) を参照する。
