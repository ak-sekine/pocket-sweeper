# 生成曲のseed再現性契約

## 同一曲の定義

01590では、同一repository revision、同一`GENERATOR_VERSION`、同一master seed、同一caller-owned parameters/options、同一candidate ordering、同一pattern/rule definitions、同一resolution/allocation contextから、次の値が一致することを「同一」とする。

1. CompositionStructure
2. Melody、Accompaniment、Bass、Noiseのlogical layer
3. それらの決定的`as_dict()`表現

同じlogical inputから生成されるJSON Version 2、hUGEDriver ASM、確認用ROMも、各変換/build toolchainの契約範囲で再現可能である。seedだけで曲が決まること、異なるseedが必ず異なる曲になること、音楽品質が同じであることは保証しない。

## Master seedとstream

`generate_logical_composition(seed, plan)`がmaster seedを受け取り、1つの`GenerationContext`を次の固定順で共有する。

```text
structure → melody → accompaniment → bass → noise
```

現行01579のsingle shared streamを維持し、stage-specific sub-seedは導入しない。したがって、上流stageのrandom call変更は後続stageへ影響し得る。このcouplingは未解決の設計事項として記録し、`hash()`による暗黙派生や新しいseed treeは追加しない。

## 入力・metadata

`LogicalGenerationPlan`は全てのstructure/layer parametersとoptionsをcallerから受け取る。candidateは順序付きsequenceでなければならず、set等を使用しない。結果metadataにはmaster `seed` と `generator_version` を保持する。generator versionまたはアルゴリズムを変更した場合、同じseedの出力継続は保証しない。

## 検証範囲

複数seed、負数、大きな整数、global random状態変更に対して、全logical layerのdictが一致することを自動テストする。01587/01588/01589のJSON→ASM→ROM段階は既存の決定的converter/build contractを再利用して検証できるが、01590は新しいCLIを作らない。ROM byte equalityはtoolchainの実測なしに永続契約へ昇格しない。

## 境界と制限

pitch resolution、instrument、wave/noise mapping、allocation、timingなどcaller inputが異なれば同じseedでも結果は異なる。21曲UGEはseed derivation、weight、default、品質の根拠に使用しない。SameBoy、実機、試聴、SFX共存、音楽品質はこの契約の検証対象外であり、01591以降またはHuman evaluationへ残す。
