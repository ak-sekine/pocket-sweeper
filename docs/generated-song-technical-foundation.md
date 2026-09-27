# 自動作曲方式に依存しない技術基盤の整理

対象: WBS-001-01680

## Scope

旧ルールベース方式の検証で確認できた、作曲方式を変更しても契約を満たせば再利用できる技術基盤と、方式選択後に再評価が必要な部分を分離する。新方式の調査・比較・選択・実装は行わない。

過去のHuman評価「全部、音を並べただけで曲になっていません。」は作曲品質の証拠であり、JSON→UGE→ASM→ROMの技術基盤が利用不能という意味ではない。逆に、pipeline成功は新方式で良い曲が作れる証拠でもない。

## Confirmed reusable foundation

### JSON Version 2の後段入力契約

JSON Version 2は、version、title/type、tempo、4 channel別のorder/pattern、instrument、loop、wave table等を表す楽曲データ契約である。旧generatorのmotif・section・logical layer生成ロジックそのものとは分離されている。新方式がこの契約を満たすJSONを生成できれば、後段converterの入力候補にできる。

### JSON→UGE

`tools/json_to_uge.py`はJSON Version 2を検証・正規化し、Song Version 6 UGEへ変換する。channel-local order/pattern、instrument、tempo、Version 2 loop、wave/noise、note length等の契約を満たす入力に対して再利用可能である。これは旧generatorの乱数・motif・logical modelを参照しない。

### JSON→hUGEDriver ASM

`tools/json_to_huge_asm.py`は同じJSON Version 2からhUGEDriver descriptor、order/pattern、instrument、wave data、loop metadata、tempo byteを生成する。新方式の作曲ロジックとは独立しており、JSON契約を満たす限り再利用候補である。

### ASM→確認用ROM

`tools/build_sound_test_rom.py`は生成ASMを入力に、Version 2なら`hUGE_init_v2`、VBlank待ち、`hUGE_dosound`、`hUGE_bgm_finished`を含む確認ROMをRGBDSで構築する。test ROMは作曲品質を判定せず、ASMの再生確認用であるため、入力ASM契約を満たす新方式でも再利用候補である。

### hUGEDriver runtime契約

`src/hUGEDriver.asm`には4 channel、descriptor tempoを`ticks_per_row`へ格納する処理、tick/row進行、Version 2 loop metadata、BGM終了状態、channel mute等が実装されている。これらのruntime実装は作曲方式とは独立した既存基盤として再利用候補である。SFX共存の聴感品質はHuman未確認であり、runtime APIの存在とは分離する。

### 構造・artifact validation

既存pipelineで、JSON validation、UGE Song Version確認、order alignment、pattern/order参照、ASM生成、RGBDS build、manifest SHA-256、同一run対応を確認できる。これらはファイル・変換・toolchainの成立条件であり、音楽として良いことは判定しない。

## Conditionally reusable foundation

### 4 channel / physical mapping

新方式がGame BoyのCH1〜CH4 capabilityに適合するphysical allocationを明示し、JSONのpulse1/pulse2/wave/noise表現へ変換できる場合に再利用できる。旧quality profileのmelody→CH1等はevaluation-only allocationであり、新方式のproduction defaultではない。

### Instrument、wave、noise

既存converterが要求するpulse、wave table、noise instrument、note mappingを新方式が明示的に提供できる場合に再利用できる。instrument設計、wave/noise parameterの決定は作曲方式またはresolution contextに依存する。

### tempo / TicksPerRow / loop

JSONのtempoはVersion 2/Song Version 6とhUGEDriverのTicksPerRow契約として扱われる。新方式が同じ意味のtempoと`full`/`range`/`none` loopを提供できれば後段を再利用できる。ただし新方式のlogical time、BPM、quantization、loop意図からの換算契約は方式選択後に確認する。

### UGE structural analyzer

`tools/analyze_uge.py`はSong Version 6、order alignment、pattern参照、event等の構造を確認できる。新方式がUGEへ変換可能なら再利用できるが、analyzerは音楽品質・自然さ・Human聴感を判定しない。

### artifact and reproducibility evidence

同一inputから同一JSON/UGE/ASM/ROMを比較するartifact/hash検証は方式を問わず適用候補である。ただし新方式がseedを使うとは限らず、seed値・metadata・再現入力・toolchainの契約は新方式に合わせて再定義する必要がある。

## Method-dependent parts requiring reevaluation

- composition generator、motif、section、phrase、harmony、pitch resolution、rhythm、layer relation
- logical layer modelと、logical layerから4 physical channelへのallocation policy
- production composition rule、品質基準、Human評価条件
- tempo/BPM・time grid・quantization・loop意図の生成側モデル
- instrument、wave、noise mappingをどの段階で決定するか
- seedの有無、random stream、candidate ordering、再現性metadata
- MIDI等を使うか、別の中間表現を使うか、JSONへ直接変換するか
- 著作権・ライセンス・source provenance

これらは旧generatorの契約を新方式へそのまま移植できるとは確認していない。

## Technical contracts

新方式候補が再利用を検討できる最小境界は、明示的で検証可能なJSON Version 2を生成し、既存JSON validationを通過させることである。その後は、JSON→UGE、JSON→ASM、ASM→RGBDS ROM、hUGEDriver runtime、manifest/hash・structural analyzerの順に既存契約を適用できる。

この境界は「変換・再生可能」を意味するだけで、曲として成立すること、Pocket Sweeperに適すること、SFX共存、Human品質評価を保証しない。

## Known limitations

- 旧quality profileのHuman評価は3候補すべてが曲として成立しないという結果であり、作曲方式の原因を特定していない。
- hUGETracker/GBの聴感一致は同一runの技術確認に限定される。
- SFX共存、長時間loop品質、production composition ruleは未確定または未評価である。
- seed再現性は旧方式ではsingle shared stream契約だが、新方式の必須条件ではない。
- 既存JSONの表現力を超える新方式の要件、ライセンス、source provenanceは未評価である。

## Handoff to WBS-001-01681

01681では、作曲方式・logical model・時間表現・source/provenance・seedの有無を自由な候補として調査できる。一方、候補が既存JSON Version 2を出力できる場合は、JSON validation、JSON→UGE、JSON→ASM、ASM→ROM、hUGEDriver runtime、artifact validationを再利用候補として扱える。方式候補を採用・比較・実装すること、また品質を保証することは01680の範囲外である。
