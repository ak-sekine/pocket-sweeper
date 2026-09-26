# Game Boy BGM allocation / SFX制約

対象WBS: `WBS-001-01585`

## Scopeと層分離

01581〜01584のlogical layerを、caller-suppliedな`LayerAllocation`でphysical channel候補へ接続し、hardware capability、排他的channel、SFX preemptionを機械検証する。allocationはlogical objectへ書き戻さず、別representationとして保持する。生成結果を「良い編曲」と判定するものではなく、logical pitchのfrequency化、Instrument、Wave/Noise parameter、UGE/order、ROM生成は01586以降へ委譲する。

## Channel capability

| channel | capability | この文書での意味 |
|---|---|---|
| CH1 | pulse, sweep | sweepを要求するallocation候補を受けられる |
| CH2 | pulse | sweep capabilityを要求するallocationを受けられない |
| CH3 | wave | Wave channel候補。bass固定ではない |
| CH4 | noise | Noise channel候補。Noise layer固定の逆推論はしない |

capabilityはallocation policyではない。melody→CH1、accompaniment→CH2、bass→CH3、noise→CH4はPocket Sweeper profileでcallerが明示する候補であり、Game Boy一般のHard ruleではない。

## Allocation / degradation

`LayerAllocation`はlogical layer、physical channel、required capabilities、`required` / `temporarily_degradable` / `optional` policy、structural roleを保持する。同一channelへの排他的な複数allocation、未知layer/channel、4 channel超過、capability不一致はmachine violationとする。degradation priorityやlayerの重要度をhard-codeしない。

SFX占有中にrequired layerがpreemptされる場合はmachine violationとする。degradable/optional layerはmachine-validにできるが、聴感についてHuman review itemを残す。

## Current implementation facts

`src/sound.asm`と`src/hUGEDriver.asm`の確認結果:

- Pulse1 SFXはCH1、Noise/Cursor SFXはCH4を使う。
- SFX開始時に対象channelを`hUGE_mute_channel`でmuteする。
- `hUGE_dosound`は毎フレームSFX更新前に呼ばれ、mute channelはdriverから更新されない。
- SFX処理は対象APU registerを直接更新し、終了時に対象channelをunmuteする。
- BGM timelineはSFX中も進み、復帰時は現在位置から続く。失われたnoteを遅延再生する扱いではない。
- Pulse2 SFXは現行SFX generatorの対象外であり、CH2 occupancyはfuture/unimplementedとして扱う。
- 現行コード上、CH3 SFX occupancyは確認していない。将来不変の禁止規則にはしない。

## CH1 / CH4 conflict

既存BGM policyにはCH1を主旋律候補、CH3をfoundation候補、CH2をauxiliary、CH4をrhythm/noise候補とする記述がある。一方、現行Pulse1 SFXはCH1を占有する。このためCH1 melody allocationとPulse1 SFXが無条件に共存すると確認済みとはせず、requiredならmachine conflict、degradableならHuman reviewとして記録する。CH1欠損時に骨格が保たれることは今回保証しない。

CH4 Noise allocationとCursor/Noise SFXは、Noise layerをoptional/degradableと明示した場合にmachine-validとできる。ただし「聴感上問題ない」「復帰が自然」は自動検証しない。

## Existing human evidence

`docs/sound-spec.md`に記録されたSameBoy確認は、CH2/CH4同時mute、CH1/CH3 skeleton、BGM位置の進行と復帰に関する既存evidenceとして参照できる。ただしCH1 Pulse1 SFXでmelodyを欠損させた場合の聴感を証明するものではない。新規試聴は本WBSで行っていない。

## 3ch / 4ch policyと未確定事項

常時3ch運用か、4ch＋SFX時のtemporary lossかは決定しない。machine-checkable範囲はallocation、capability、occupancy、timeline継続、required layer lossの検出までである。melodyの認識、調性、拍、空白、復帰の自然さはHuman evaluation対象である。

未確定事項は、CH1 conflictのPocket Sweeper方針、CH2 SFX future support、CH3 future occupancy、degradation priority、tonality/beat skeleton、pitch/instrument/UGE mapping、CH1欠損とSFX復帰の聴感である。21曲UGEからallocationやdegradation policyを導出していない。

01586では、logical allocationをJSON/UGE/ASMへ変換し確認用ROMへ接続する。ここではその変換を実装しない。
