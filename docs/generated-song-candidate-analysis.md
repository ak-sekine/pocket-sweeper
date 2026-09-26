# 生成BGM候補の再生問題分析

## Human symptom

01594のHuman SameBoy確認では、candidate-01/seed 1、candidate-02/seed 5、candidate-03/seed 7のすべてについて「1音しかならず曲になっていません」と報告された。これはHuman evidenceであり、以下の構造解析とは分けて扱う。

## Pipeline trace

|段階|確認結果|
|---|---|
|logical generation|4 logical layerを生成。各candidateのmelodyは6 event（有音2、rest 4）。|
|profile/allocation|`logical_layers: (result.melody,)`、`melody-001 → CH1`のみ。accompaniment/bass/noiseは生成されるが変換入力へ渡らない。|
|JSON Version 2|`order`/`patterns`は`pulse1`のみ。`full` loop。各candidateの有音noteは2つ。|
|UGE|Song Version 6、order alignment 一致、CH1 order `[0]`、CH2〜CH4はunused。CH1 event_countは6（noteとrestの構造cellを含む）。|
|ASM|CH1 patternに有音`dn`が2つ。candidate-01はC4→E4、candidate-02はE4→D4、candidate-03はD4→C4。|
|ROM|各artifactはRGBDSで生成済み。Humanの「1音」観測は確認できるが、ROM再生経路の原因はこの分析だけでは確定しない。|

## Candidate comparison

|candidate|seed|phrase-001|phrase-002|有音event|
|---|---:|---|---|---:|
|candidate-01|1|motif-a: absolute pitch 0 (C4)|motif-c: absolute pitch 2 (E4)|2|
|candidate-02|5|motif-c: absolute pitch 2 (E4)|motif-b: absolute pitch 1 (D4)|2|
|candidate-03|7|motif-b: absolute pitch 1 (D4)|motif-a: absolute pitch 0 (C4)|2|

各motifはduration 2 tickの有音stepとduration 2 tickのrestを持ち、phrase残り12 tickはrestで補完される。logical dataには有音eventが1個しかないわけではないが、構造は小さい。この事実はHuman観測の原因そのものとは断定しない。

### JSON / UGE / ASM対応

|candidate|JSON pulse1|UGE|ASM|
|---|---|---|---|
|candidate-01|C4 length 2、E4 length 2|CH1 order `[0]`、6 structural cells|`dn C_4,1,$000`、`dn E_4,1,$000`|
|candidate-02|E4 length 2、D4 length 2|CH1 order `[0]`、6 structural cells|`dn E_4,1,$000`、`dn D_4,1,$000`|
|candidate-03|D4 length 2、C4 length 2|CH1 order `[0]`、6 structural cells|`dn D_4,1,$000`、`dn C_4,1,$000`|

有音noteが変換段階でゼロになった、またはCH1以外へ誤割当されたことは確認できない。`event_count`は品質scoreではなく構造観測値である。

## Cause classification

### Confirmed cause

今回の証拠だけでは、Humanが聞いた「1音」の再生原因をconfirmed causeとして特定できない。

### Contributing factors

- 評価profileは4 logical layerを生成するが、ROM変換対象はmelodyだけである。
- allocationはmelody-001をCH1へ割り当てる1系統のみである。
- 各candidateのmelodyは有音2 eventと多数のrestだけで、profileの構造自体が小さい。
- 既存自動テストはartifact生成、形式、hash、UGE構造、RGBDS buildを確認するが、SameBoyのruntime発音列や音楽品質をassertしていない。

### Not confirmed / not investigated

generator、profile選択、logical layer、allocation、JSON/UGE/ASM conversion、ROM builder、hUGEDriver playback、note length、pitch mapping、loop、instrument/APU、SameBoy固有要因のいずれも原因とは確定していない。SFX共存も今回の症状と結び付けていない。

01597以降で、bug fix、evaluation profile変更、composition rule/evidence確認のどれに該当するかを判断する。今回この文書では実装、profile、rule、candidateを変更していない。21曲UGEの多数派や品質比較も行っていない。
