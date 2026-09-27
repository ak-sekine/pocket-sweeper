# Generated song UGE/ROM playback mismatch analysis

対象: candidate-01 / seed 1

## Human evidence

Humanが`build/generated-candidates/candidate_01/candidate_01.uge`をhUGETrackerで再生し、CH1のC-4→E-4が短い間隔で進行する一方、生成済みGB ROMではC-4相当が約4秒続き、再生内容が一致しないことを確認した。これは音楽品質評価とは別の変換/runtime不一致である。

## Trace before fix

- logical/profile: `generation_profile_candidates.py`はmelodyだけをCH1へ割り当てる。candidate-01のmelodyにはC4とE4の2有音eventがある。
- JSON: `tempo: 120`、CH1 patternはC4 length 2、rest、E4 length 2、rest。`ticks_per_row`はprofileで1だがJSON Version 2には別フィールドとして保存されない。
- UGE: Song Version 6、tempo raw 120、CH1 pattern/orderは1件で、C-4とE-4のcellを保持する。
- ASM: descriptorは`db 120`、CH1 `P0`にはC_4がrow 0、E_4がrow 16にあり、order1から到達可能。
- ROM builder: Version 2を検出して`hUGE_init_v2`を呼び、VBlank待ちごとに`hUGE_dosound`を1回呼ぶ。
- hUGEDriver: `hUGE_init_v2`から`hUGE_init`へ入り、descriptor先頭のtempo byteを`ticks_per_row`へ保存する。`tick_time`は呼び出し回数がその値に達した時だけrowを進める。

したがって、固定更新約60Hzではtempo byte 120は1row約2秒となる。C4のlength 2は約4秒、E4はrow 16のため約32秒後となる。これはHumanの約4秒観測と整合する。最初の証拠付き不一致は、JSON/UGEのtempo値をASM/hUGEDriverが同じ意味で使っていない候補profile契約にある。

## Minimal correction

JSON Version 2の`tempo`はSong Version 6のTicksPerRowであり、candidate profileの`tempo: 120`と`ticks_per_row: 1`は矛盾していた。candidate profileのtempoを1へ修正し、同じprofileからJSON→UGE→ASM→ROMを再生成した。修正後のJSON/ASMはtempo 1を使用し、UGE Song Version 6、order alignment一致、RGBDS ROM生成に成功した。

これはcandidate evaluation profileの時間契約修正であり、作曲rule変更ではない。修正ROMの聴感一致は未確認で、Humanによる再試聴が必要である。

## Follow-up timing comparison

その後のHuman比較では、`build/generated-candidates/candidate_01/candidate_01.uge`と前回修正後のROMが比較された。しかし前者は旧runのmanifestに記録された`tempo: 120`のUGE（SHA-256 `b95cb0e2a4abf6eb27ef4fcd1c5d7baec9e309772111e04776de50f6c11e1f4e`）であり、後者は`candidate_01_fixed` runの`tempo: 1`のROM（SHA-256 `22f08e9e3c3307a...`）である。同じrunのUGEとROMではない。

修正後の同一runは、`build/generated-candidates/candidate_01_fixed/candidate_01_fixed.uge`と`candidate_01_fixed.gb`である。前者はtempo raw 1、後者のASM descriptorも`db 1`で、CH1 pattern/orderは同じ生成結果から作られている。したがって旧UGEと修正ROMの約20秒/約0.5秒という比較から、hUGETrackerとhUGEDriverの倍率や新しいtempo補正値を導出してはならない。

Repository内にはhUGETrackerの再生実装そのものはなく、Humanの概算時間だけからtracker側の厳密な実時間式は確定できない。hUGEDriver側については、tempo raw 1、64 row、VBlank約60Hzなら理論上のfull-loopは約64/60秒である。固定更新が実機・エミュレータで同じであること、同一runのUGEをhUGETrackerで測ること、正確な測定方法は追加Human確認として残す。

## Final same-run human verification

Humanが同一runの次の2成果物を比較した。

- UGE: `build/generated-candidates/candidate_01_fixed/candidate_01_fixed.uge`
- GB ROM: `build/generated-candidates/candidate_01_fixed/candidate_01_fixed.gb`

Human listeningの結果、GB ROMでC-4 → E-4の2音が聞こえ、UGEとGB ROMは同じテンポで再生された。これにより、`tempo: 1` / `ticks_per_row: 1`へ修正したcandidate-01 fixed runでは、今回問題となったUGE/ROMの時間進行不一致が再現しないことを確認した。

この結果はcandidate-01 fixed runに限定する。全seed、全profile、実機、SFX共存、BGM品質、Pocket Sweeper用途適合性を証明しない。旧UGE（tempo 120）と修正ROM（tempo 1）の比較は異なるrunの過去観測として保持し、hUGETrackerとhUGEDriverがあらゆるUGEで完全一致する根拠にはしない。

## Not implicated by this trace

この証拠はnote数、4ch必須性、accompaniment/bass/noise必須性、SFX共存、音楽品質を判定しない。また、他candidateや全production profileへ自動一般化しない。
