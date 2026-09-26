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

## Not implicated by this trace

この証拠はnote数、4ch必須性、accompaniment/bass/noise必須性、SFX共存、音楽品質を判定しない。また、他candidateや全production profileへ自動一般化しない。
