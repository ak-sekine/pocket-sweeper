[サウンド仕様へ戻る](sound-spec.md) / [PROJECT.mdへ戻る](../PROJECT.md)

# Game Boy楽曲解析元候補の曲数・偏り調査

## 調査範囲と結論

確認日：2026-08-01。対象は、hUGETrackerのUGEまたはhUGEDriver ASMとして論理構造を解析できる可能性があるGame Boy向け楽曲配布元である。配布ページ上の説明とライセンス表示に加え、今回Yogi #1/#2の取得済みZIPを展開せずに検査し、Git追跡対象外の作業領域へ展開してファイル一覧・ハッシュ・README/LICENSE候補を確認した。ページ記載曲数と実ファイル確認数を混同しない。

配布ページ上で収録曲数を確認できた候補は29曲である。個別曲名まで確認できたのはYogi #1/#2の18曲で、lillstrumpa vol.1〜3の11曲はパック単位の曲数だけを確認した。前回の暫定31曲に含まれていた lillstrumpa vol.4（6曲）とvol.5（4曲）は、作者ページで商品の存在と方向性は確認できるが、個別ページ本文で収録曲数を確認できなかったため、29曲の合計には含めない。

この29曲のうち、今回実ファイル名を確認できたのはYogi #1/#2の18曲で、UGEは18曲、ASMは0曲である。現時点の「商用ゲーム向けルールの根拠として利用可能な曲数」「元データをGitHubで管理できる曲数」は、ライセンス適用範囲や詳細解析が未確認のため0曲のままである。これは配布元が利用を禁止しているという意味ではなく、取得内容・対象ファイル・ライセンス適用範囲を確認できていないため、Pocket SweeperのA〜D受入判定を確定していないという意味である。

## 配布元の確認記録

| 配布元・作者 | 配布ページ上の曲数 | ページで確認できた形式 | ページ上のライセンス | 実ファイル確認 | 受入判定 | 用途・曲調の根拠と未確認事項 |
|---|---:|---|---|---:|---|---|
| lillstrumpa（Pia / Lil’Sock）vol.1 | 4 | UGE、WAV | CC BY 4.0 | UGE 0、ASM 0 | 未判定（A候補） | calm、playful、mysterious、warm/happy。ZIP内部、曲名、UGE個数、同梱条件は未確認 |
| lillstrumpa vol.2 | 3 | UGE、WAV | CC BY 4.0 | UGE 0、ASM 0 | 未判定（A候補） | 3 original loops。個別曲の用途・曲調、ZIP内部、同梱条件は未確認 |
| lillstrumpa vol.3 | 4 | UGE、WAV | CC BY 4.0 | UGE 0、ASM 0 | 未判定（A候補） | 4 loops、calm/background向けの説明。個別曲の用途・曲調、ZIP内部は未確認 |
| lillstrumpa vol.4 | 6（作者ページの暫定表示。個別本文未確認） | UGEを含む旨の作者説明 | CC BY 4.0の個別適用未確認 | UGE 0、ASM 0 | 未判定 | 商品の存在、Soft chiptune loops for GB Studio and GameBoyは作者ページで確認。曲数・個別ライセンス・ZIP内部は未確認 |
| lillstrumpa vol.5 | 4（作者ページの暫定表示。個別本文未確認） | UGEを含む旨の作者説明 | CC BY 4.0の個別適用未確認 | UGE 0、ASM 0 | 未判定 | 商品の存在、Cute loops in uge-formatは作者ページで確認。曲数・個別ライセンス・ZIP内部は未確認 |
| Yogi（Tronimal）Game Boy Music Pack #1 | 8 | UGE | CC BY表示（READMEはCC-BY 2025表記） | UGE 8、ASM 0 | 曲単位で判定 | remix、tribute、influence等が混在。原曲権利者・編曲許諾・UGE再配布条件は未確認 |
| Yogi（Tronimal）Game Boy Music Pack #2 | 10 | UGE | 配布ページ表示はCC BY 4.0、同梱記載なし | UGE 10、ASM 0 | 未判定（A候補） | ZIP実体で10曲のUGEを確認。個別曲の権利関係・UGE再配布条件は未確認 |

### 一次情報

- [lillstrumpa Game Boy Music Pack vol.1](https://lillstrumpa.itch.io/game-boy-music-pack-cozy-playful-loops-for-gb-studio)：4 original loops、UGE/WAV、作者、CC BY 4.0を確認。購入が必要なZIP名もページに表示されるが、内部は未取得。
- [lillstrumpa Game Boy Music Pack vol.2](https://lillstrumpa.itch.io/game-boy-music-pack-vol-2)：3 original loops、UGE/WAV、作者、CC BY 4.0を確認。ZIP内部は未取得。
- [lillstrumpa Game Boy Music for GB Studio vol.3](https://lillstrumpa.itch.io/music-pack-for-gb-studio-vol3)：4 loops、UGE/WAV、作者、CC BY 4.0を確認。ZIP内部は未取得。
- [lillstrumpa作者ページ](https://lillstrumpa.itch.io/)：vol.4、vol.5の存在、作者の制作方針、UGEを含むパックであることを確認。ただし個別ページの曲数・適用ライセンスは未確認。
- [Yogi Game Boy Music Pack #1](https://yogi-tronimal.itch.io/game-boy-music-pack)：8曲、各曲名、UGE、CC BY 4.0、remix/tribute/influenceの記載を確認。作者コメントの「commercial games」許可も確認したが、原曲権利者の許諾を代替しない。
- [Yogi Game Boy Music Pack #2](https://yogi-tronimal.itch.io/game-boy-music-pack-2)：10曲、各曲名、UGE、CC BY 4.0を確認。取得ZIP内でも10個のUGEを確認した。

ライセンス本文の一般条件は、既存の [`docs/sound-spec.md`](sound-spec.md) に記録したCreative Commons公式情報を参照する。今回の候補調査では、Pack #1 README内の「Tronimal - CC-BY 2025」と第三者作品由来の記載、Pack #2の同梱ファイル不在を確認した。これは個別UGEへのライセンス適用範囲や原曲権利者の許諾を最終確定するものではない。

## 取得済みZIPの実ファイル確認（2026-08-01）

元素材のZIPと展開後ファイルは `.gitignore` の `local/music-source-candidates/` 配下に置き、Git管理へ追加しない。ZIPは暗号化されておらず、`unzip -t` は両方とも `No errors detected` となった。ZIP内部のパスに絶対パスまたは `..` はなく、展開は `unzip -n` で既存ファイルを上書きせず実施した。単純な拡張子集計であり、UGEの曲名・構造・ライセンス適用範囲の詳細解析は後続WBSで行う。

### Pack #1（Yogi Game Boy Music Pack #1）

- ZIP：`local/music-source-candidates/yogi-pack1/original/Free Game Boy Music Pack.zip`
- サイズ：25,082 bytes
- SHA-256：`3ad5fd2ad0e081e10427722bcd873dbd650634fd6a6db2cd40d4ff8a2d13a581`
- ZIPテスト・形式：ZIP、非暗号化、`unzip -t` 成功
- 内部件数：ファイル9、ディレクトリ1（配布ページ記載8曲と一致）
- 拡張子別：UGE 8、ASM 0、INC 0、WAV 0、MP3 0、OGG 0、TXT 1、MD 0、その他0
- UGE一覧：`free_01_hypergolic_blast_off.uge`、`free_02_blue_ocean_remix.uge`、`free_03_darkstone_remix.uge`、`free_04_neurotic_robonaut.uge`、`free_05_hideout.uge`、`free_06_delight.uge`、`free_07_observing_jupiter.uge`、`free_08_terminate.uge`
- README候補：`Free Game Boy Music Pack/readme.txt`
- LICENSE候補：なし
- その他の記載候補：README内に `Tronimal - CC-BY 2025`、`based on` 3曲、`tribute` 1曲、`influenced by` 1曲の記載。第三者原曲の権利・許諾は未確認
- 展開先：`local/music-source-candidates/yogi-pack1/extracted/`
- Git：ZIP・展開後代表ファイルとも除外確認済み
- 未確認：UGE詳細、曲名対応の確定、個別ライセンス適用範囲、原曲権利・編曲許諾、試聴・用途・曲調、A〜D確定

### Pack #2（Yogi Game Boy Music Pack #2）

- ZIP：`local/music-source-candidates/yogi-pack2/original/Game Boy Music Pack.zip`
- サイズ：25,351 bytes
- SHA-256：`8ecc7cac7f21de233f0532023002fd2b48ef17d71c0a75f6917c4eb2b4cd16fc`
- ZIPテスト・形式：ZIP、非暗号化、`unzip -t` 成功
- 内部件数：ファイル10、ディレクトリ1（配布ページ記載10曲と一致）
- 拡張子別：UGE 10、ASM 0、INC 0、WAV 0、MP3 0、OGG 0、TXT 0、MD 0、その他0
- UGE一覧：`01_decampment.uge`、`02_only_hope.uge`、`03_walking_outdoors.uge`、`04_absent.uge`、`05_roam_the_world.uge`、`06_whirlwind.uge`、`07_tech.uge`、`08_gone_missing.uge`、`09_that_morning.uge`、`10_closing.uge`
- README候補：なし
- LICENSE候補：なし
- その他の記載候補：なし（安全にテキストとして読める記載ファイルなし）
- 展開先：`local/music-source-candidates/yogi-pack2/extracted/`
- Git：ZIP・展開後代表ファイルとも除外確認済み
- 未確認：README相当の配布条件、個別ライセンス適用範囲、各曲の作者・権利関係、UGE詳細、曲名対応の確定、試聴・用途・曲調、A〜D確定

### Yogi Game Boy Music Pack #1の曲単位判定

### Yogi #1/#2 実ファイルと曲名の対応

UGE内部曲名は、リポジトリ内に既存のUGE読み取りツールがなく、hUGETrackerも実行環境にないため、未確認とした。バイナリからUTF-16LEらしい可読文字列は得られるが、それだけでは内部Song Nameの確定根拠としない。以下の対応判定は、配布ページ、Pack #1 README、曲順、ファイル名を照合した結果である。Pack #2にはREADMEがない。今回の確認では配布ZIPにASM/INCはなく、UGEからのASM exportも実施していない。

#### Pack #1

| 曲順 | 配布ページ曲名 | README曲名 | UGEファイル名 | UGE内部曲名 | 対応判定 | 判定根拠 | 備考 |
|---:|---|---|---|---|---|---|---|
| 1 | Hypergolic Blast Off | Hypergolic Blast Off | `free_01_hypergolic_blast_off.uge` | 未確認 | 確定 | 曲順、番号、ファイル名、READMEが一致 | README原文は `Hypergolic Blast  Off`。`based on Creepy Organ` の権利事項は後続 |
| 2 | Blue Ocean Remix | Blue Ocean Remix | `free_02_blue_ocean_remix.uge` | 未確認 | 確定 | 曲順、番号、ファイル名、READMEが一致 | README原文は `Blue Ocean Remix`。`based on Blue Ocean` の権利事項は後続 |
| 3 | Darkstone Remix | Darkstone Remix | `free_03_darkstone_remix.uge` | 未確認 | 確定 | 曲順、番号、ファイル名、READMEが一致 | README原文は `Darkstone  Remix`。`based on Darkstone` の権利事項は後続 |
| 4 | Neurotic Robonaut | Neurotic Robonaut | `free_04_neurotic_robonaut.uge` | 未確認 | 確定 | 曲順、番号、ファイル名、READMEが一致 | README原文は `Neurotic  Robonaut`、内部文字列候補は根拠に不使用 |
| 5 | Hideout | Hideout | `free_05_hideout.uge` | 未確認 | 確定 | 曲順、番号、ファイル名、READMEが一致 | README記載のPatreon由来事項は後続 |
| 6 | Delight | Delight | `free_06_delight.uge` | 未確認 | 確定 | 曲順、番号、ファイル名、READMEが一致 | README記載のbased on事項は後続 |
| 7 | Observing Jupiter | Observing Jupiter | `free_07_observing_jupiter.uge` | 未確認 | 確定 | 曲順、番号、ファイル名、READMEが一致 | README記載のtribute事項は後続 |
| 8 | Terminate | Terminate | `free_08_terminate.uge` | 未確認 | 確定 | 曲順、番号、ファイル名、READMEが一致 | README原文は `Terminate`。influenced by事項は後続 |

#### Pack #2

| 曲順 | 配布ページ曲名 | README曲名 | UGEファイル名 | UGE内部曲名 | 対応判定 | 判定根拠 | 備考 |
|---:|---|---|---|---|---|---|---|
| 1 | Decampment | なし | `01_decampment.uge` | 未確認 | 確定 | 曲順、番号、ファイル名が一致 | |
| 2 | Only Hope | なし | `02_only_hope.uge` | 未確認 | 確定 | 曲順、番号、ファイル名が一致 | |
| 3 | Walking Outdoors | なし | `03_walking_outdoors.uge` | 未確認 | 確定 | 曲順、番号、ファイル名が一致 | |
| 4 | Absent | なし | `04_absent.uge` | 未確認 | 確定 | 曲順、番号、ファイル名が一致 | |
| 5 | Roam The World | なし | `05_roam_the_world.uge` | 未確認 | 確定 | 曲順、番号、ファイル名が一致 | |
| 6 | Whirlwind | なし | `06_whirlwind.uge` | 未確認 | 確定 | 曲順、番号、ファイル名が一致 | |
| 7 | Tech | なし | `07_tech.uge` | 未確認 | 確定 | 曲順、番号、ファイル名が一致 | |
| 8 | Gone Missing | なし | `08_gone_missing.uge` | 未確認 | 確定 | 曲順、番号、ファイル名が一致 | |
| 9 | That Morning | なし | `09_that_morning.uge` | 未確認 | 確定 | 曲順、番号、ファイル名が一致 | |
| 10 | Closing | なし | `10_closing.uge` | 未確認 | 確定 | 曲順、番号、ファイル名が一致 | |

対応集計は、確定18曲、暫定0曲、不一致0曲、確認不能0曲である。実ファイルはPack #1 UGE 8件、Pack #2 UGE 10件の計18件、ASM 0件、INC 0件で、空ファイル・同一内容ファイル・ファイル名重複は確認されなかった。配布ページ記載曲数（8曲、10曲）とも一致する。UGE内部曲名の確認、Song Version・CH1〜CH4・CH4/Noise・loop構造、ライセンス適用範囲、試聴は後続WBSで扱う。

配布ページの説明をそのまま分類根拠とし、`inspired by` や `influence` を `remix` と同一視しない。これは法的な最終判断ではなく、実ファイル・原曲権利・許諾を確認するまでの保守的なプロジェクト判定である。

| 曲名 | 配布ページの記述 | 暫定区分 | 判定理由 |
|---|---|---|---|
| Hypergolic Blast Off | based on Creepy Organ by Beatscribe | D（第三者権利確認待ち） | 他作者曲を基にしたと明記。原曲権利者・編曲許諾を確認できていない |
| Blue Ocean Remix | based on Blue Ocean by Coffee Bat | D（第三者権利確認待ち） | Remixかつ他作者名を明記。原曲権利者・編曲許諾を確認できていない |
| Darkstone Remix | based on Darkstone by DeerTears | D（第三者権利確認待ち） | Remixかつ他作者名を明記。原曲権利者・編曲許諾を確認できていない |
| Neurotic Robonaut | a port of my own Virtual Boy music | 未判定（A候補） | 作者自身の曲のportと記載。ただし元UGE、再配布、詳細解析結果の条件は未確認 |
| Hideout | original song from my discontinued Patreon project | 未判定（A候補） | 作者自身のoriginal songと記載。ただしPatreon由来の権利・再配布条件は未確認 |
| Delight | based on the most popular western chord progression | 未判定 | 他作品・他作者の特定記載はなく、originalとも明記されない |
| Observing Jupiter | tribute to the Game Boy Camera OST | D（第三者権利確認待ち） | tributeと明記。原曲権利者・許諾を確認できていない |
| Terminate | influenced by the Terminator 2 OST | 未判定 | influenceとの記載のみ。remix・cover・原曲利用とは断定しないが、権利関係は未確認 |

Yogi #1の集計はD 4曲、未判定（A候補）2曲、未判定2曲で合計8曲である。個別UGEを取得するまで、どの曲も商用ルール根拠またはGitHub管理可能とは確定しない。

## 利用可能曲数の定義と集計

分母を明記する。ページ確認曲数の分母は29曲、実ファイル確認曲数の分母は0曲である。「未判定」はA〜Dのいずれにも確定していない候補であり、D（権利確認待ち）と同一視しない。

| 指標 | 曲数 | 分母・意味 |
|---|---:|---|
| 配布ページ上で曲名・曲数を確認 | 29 | vol.1〜3、Yogi #1/#2のページ記載分。vol.4/#5暫定表示は除外 |
| 配布ページ上で存在だけ確認した追加候補 | 10 | lillstrumpa vol.4/#5の暫定曲数。内訳・個別ページ未確認 |
| 配布ページ上で個別曲名を確認 | 18 | Yogi #1/#2。lillstrumpa vol.1〜3の11曲は曲名未確認 |
| 実ファイル名確認済み | 18 | Yogi #1/#2のZIPを取得してファイル一覧を確認できた曲 |
| 実ファイル確認済みUGE | 18 | Yogi #1/#2のZIP内UGEファイル（曲名対応まで確認、詳細内容は未解析） |
| 実ファイル確認済みASM | 0 | ASMを取得して内容を確認できた曲 |
| 曲名対応確定 | 18 | Pack #1 8曲、Pack #2 10曲。配布ページ・README/ファイル名・曲順を照合 |
| 曲名対応暫定 | 0 | 該当なし |
| 曲名対応不一致 | 0 | 該当なし |
| 曲名対応確認不能 | 0 | 該当なし |
| ライセンス適用範囲まで確認済み | 0 | 個別UGE/ASMまたは同梱条件まで照合できた曲 |
| A（公開・商用利用可）確定 | 0 | 実ファイルと対象範囲の確認後に確定する区分 |
| B（解析・ローカル限定）確定 | 0 | 解析・変換・非公開保管の条件まで確認できた曲 |
| C（一般化結果のみ）確定 | 0 | 元を再現しない結果の利用条件まで確認できた曲 |
| D（採用しない／作者確認待ち） | 4 | Yogi #1のbased on/remix/tribute 4曲 |
| A〜D未判定 | 25 | Yogi #1の未判定4曲、lillstrumpa vol.1〜3 11曲、Yogi #2 10曲 |
| 商用ゲーム向けルール根拠として利用可能 | 0 | 実ファイル・権利条件確認済みの曲 |
| 元データをGitHub管理可能 | 0 | 元UGE/ASM再配布条件まで確認済みの曲 |
| ローカル解析のみ可能 | 0 | 非公開解析条件まで確認済みの曲 |
| 権利確認待ち | 4以上 | Yogi #1のD 4曲。未判定25曲にも確認待ち事項がある |

集計の検算は `11 + 8 + 10 = 29`、`個別曲名 18 + 曲数のみ 11 = 29`、および `A 0 + B 0 + C 0 + D 4 + 未判定 25 = 29` である。Yogi #1の検算は `D 4 + 未判定（A候補）2 + 未判定 2 = 8`。vol.4/#5の暫定10曲は別母数なので、この計算に加えていない。

### 作者別・配布元別・ライセンス別・形式別

| 分類 | 内訳（ページ確認29曲を分母） |
|---|---|
| 作者 | lillstrumpa 11曲（37.9%）、Yogi 18曲（62.1%） |
| 配布元 | lillstrumpa vol.1〜3 11曲（37.9%）、Yogi #1 8曲（27.6%）、Yogi #2 10曲（34.5%） |
| ライセンス表示 | CC BY 4.0表示あり 29曲（100%）。ただし個別ファイルへの適用確認済みは0曲 |
| 形式表示 | UGE表示あり 29曲（100%）、WAV併記 11曲（37.9%）、ASM表示 0曲（0%） |

作者ページのvol.4/#5を含めると、作者・配布元の暫定母数は39曲となるが、曲数と個別ライセンスの確認不足があるため、分布集計には使用しない。

### 用途別・曲調別

曲単位で試聴またはREADMEの個別説明を確認できていないため、用途別・曲調別の確定集計は未実施である。ページのパック説明と曲名から安全に言える範囲だけを「配布元説明による暫定タグ」として記録する。

| 暫定タグ | 曲数 | 分母 | 根拠・注意 |
|---|---:|---:|---|
| calm / gentle / cozy / background | 11以上 | 29 | lillstrumpa vol.1〜3のパック説明。個別曲への割当ではない |
| playful / happy / warm / cute | 4以上 | 29 | vol.1の4 mood説明、vol.2/#3のパック説明。重複あり |
| mysterious / slightly tense | 1 | 29 | vol.1の説明にあるmood。個別曲名は未確認 |
| based on / remix / tribute / influence | 5 | 29 | Yogi #1の曲説明。D 4曲と未判定1曲（Terminate）。法的分類は未確定 |
| タイトル、メニュー、通常プレイ等の用途 | 0確定 | 29 | 個別曲の用途説明・試聴未確認 |
| 戦闘、ボス、勝利、ゲームオーバー、短いジングル | 0確定 | 29 | 不足と断定せず、未確認として扱う |
| 曲調不明 | 29 | 29 | 個別曲単位の試聴・説明確認がないため、上記タグと両立する |

したがって、配布元説明から「穏やか・日常・背景向けに偏る可能性」は示せるが、29曲中21曲などの個別曲調割合はまだ算出できない。曲名だけから用途や曲調を確定しない。

## 偏りの評価と追加収集目標

- 20曲程度を選べるページ上の候補母数があり、実ファイル名確認済みは18曲ある。ただしライセンス適用範囲・詳細構造・試聴が未確認なので、解析コーパスとして利用可能と確定した母数はまだ0曲である。
- 作者は確認済み母数では2名、lillstrumpaとYogiへ偏っている。特定作者の作風を一般化しないため、後続選定では少なくとも4〜5名を目標にする。
- 配布元説明はcalm、cozy、cute、background寄りで、戦闘・高速アクション・不穏・恐怖・勝利・短いジングルの実数は未確認である。
- UGEは配布ページ上で29曲すべてに表示されるが、ASM候補は0曲である。実ファイル取得後も、UGEからのASM exportだけでなく、最初からASMで配布される候補を少なくとも3曲探す。
- 4チャンネル全体の比較、CH4/Noiseの役割比較、loop・pattern・orderの多様性は、実ファイルと試聴を確認するまで評価できない。

これは統計的代表性を保証する目標ではなく、設計パターンの種類を増やすためのプロジェクト上の収集目標である。次の不足カテゴリを、権利条件と実ファイル確認を満たす候補で補う。

| 不足カテゴリ | 追加目標 | 選定理由 |
|---|---:|---|
| 戦闘・ボス・高速アクション | 3〜5曲 | 現在の配布元説明から確認できない |
| 不穏・緊張・恐怖 | 3曲 | calm/cozy系との対比を作る |
| 勝利・クリア・ファンファーレ | 2〜3曲 | 短い構成・終止のルールを補う |
| Noise主体・強いリズム | 3曲以上 | CH4の設計比較に必要 |
| ASMを主形式とする候補 | 3曲 | UGE依存を避け、export差異を比較する |
| 作者 | 追加で2〜3名 | 作者偏りを緩和する |

20曲程度の選定は、ページ上の曲数だけなら可能だが、実ファイル・ライセンス・用途分類が未確認のため、現時点では解析対象として確定できない。まず少なくとも20曲について、ZIP内部のUGE、ライセンス適用範囲、著作権者、用途・曲調、CH1〜CH4の構造を確認してから選定する。

## 後続WBSの候補選定方針

1. 配布ページの曲数ではなく、実ファイルのUGE/ASM一覧を取得して曲単位のレコードを作る。
2. `docs/sound-spec.md` の候補記録様式に、作者、取得日、対象ファイル、ライセンス版、適用根拠、A〜D区分、未確認事項を記録する。
3. ライセンス表示が同じでも、remix、cover、tribute、他作者作品は原曲権利者と編曲許諾を別に確認する。
4. 元データをGitHubに登録できる曲、ローカル解析だけの曲、一般化結果だけ使える曲を分ける。詳細なorder、pattern、loop、音符列を公開できるとは推測しない。
5. Aまたは、商用利用と一般化結果の公開条件を確認したCだけを商用ゲーム向けルールの根拠に使う。Dと未判定は採用候補から除外する。
6. 用途・曲調は、配布元説明、曲名、README、試聴の根拠を別欄に記録し、曲名だけの分類は暫定タグにする。
7. 20曲を選ぶ場合も、作者・配布元・用途・曲調・形式の最大偏りを避け、特定パックだけで埋めない。

## 未確認事項

- 各UGEのSong Version、OrderMatrix、pattern、Instrument、Wave/Noise、loop表現、内部Song Nameの安全な読み取り。
- Pack #1/#2の実ファイルにはASM/INCが同梱されていない。UGEからのASM exportは未実施であり、ASMが必要な後続解析では別途exportまたは別配布元調査が必要。
- hUGEDriver ASMが同梱されるか、またはUGEから再ExportしたASMを解析対象としてよいか。
- 個別UGEに作者・著作権・ライセンス情報が埋め込まれているか。
- lillstrumpa vol.4/#5の個別曲数、曲名、個別ページのライセンス表示。
- Yogi #1のremix・tribute対象の原曲権利者、編曲許諾、詳細解析結果の公開条件。
- Yogi #2の各曲の作者・権利関係、元データ再配布条件。
- 試聴に基づく用途・曲調、CH4/Noise使用傾向、4チャンネルの多様性。
- Doug T、Beatscribe、TipTopTomCat等の追加候補は、今回の調査では一次情報とファイル内容を十分確認できなかったため、候補一覧の集計に含めていない。

以上の未確認事項が解消されるまで、このWBSは完了にしない。

## 実ファイルの取得・保管・確認手順

### 取得対象の優先順位

候補は次の順で確認する。

1. 認証不要かつ無料で直接取得できる公開ファイル
2. itch.io等で無料ダウンロード可能だが、画面上のDownload操作が必要な素材
3. 任意価格または支払いが必要な素材
4. 有料素材
5. 作者への問い合わせが必要な素材

購入、ログイン、メール入力、決済、利用規約への同意、Cookie同意、アクセス制御の回避、配布元が意図しないURLの推測は行わない。Codexが自動取得できない候補は、ユーザーによる取得が必要として記録する。任意価格・有料素材を今回購入するとは決めず、必要ならユーザー判断とする。

### ローカル保管場所とGit管理

元素材はリポジトリルート配下のGit追跡対象外ディレクトリ `local/music-source-candidates/` に保存する。このディレクトリは今回 `.gitignore` に追加し、次の構成を使う。

```text
local/music-source-candidates/<candidate-id>/original/   # 元ZIP、元UGE、元ASM
local/music-source-candidates/<candidate-id>/reference/  # README、LICENSE、出典保存
local/music-source-candidates/<candidate-id>/preview/    # 試聴用WAV/MP3
local/music-source-candidates/<candidate-id>/notes/      # 非公開の作業メモ
```

Git管理するのは本調査文書と、必要になった場合の小規模な機械可読一覧だけとする。Git管理する一覧には配布元URL、取得日、ZIP名、ファイル一覧、SHA-256、ライセンス記載箇所、判定結果、元素材がGit非管理であることを記録する。元ZIP、UGE、ASM、WAV、MP3、README、LICENSE、試聴用変換物、詳細解析結果は、ライセンス判定と公開許可の確認が終わるまでGitへ追加しない。

元データをGit管理へ移せる条件は、対象ファイルへのライセンス適用、再配布、GitHub公開、変換・fixture・詳細解析結果の公開範囲、表示義務、第三者権利を候補・曲単位で確認し、Aまたは明示的に公開可能な区分と判定した場合だけとする。確認できない場合はローカル保管に留める。調査終了後は、公開許可がない元素材と作業用変換物を削除するか、権利条件に従う非公開保管へ移し、削除・保管日を調査メモへ記録する。ライセンス証拠を削除する場合は、Git管理文書にURL、取得日、版、ハッシュ、確認した記載箇所を残す。

### ファイル確認とSHA-256

取得したZIP、UGE、ASM、README、LICENSEは、ファイル名を変更せず、`sha256sum`等でSHA-256を記録する。ハッシュは候補レコードまたは小規模な機械可読一覧へ記録し、文書本文へ長大な一覧を直接埋め込まない。確認項目はファイル名、拡張子、サイズ、SHA-256、README/LICENSEの有無、ファイル内著作権表示、配布ページとの一致、Song Version、CH1〜CH4、CH4/Noise、loop、試聴可否、用途、曲調、分類根拠、未確認事項である。hUGETracker GUI確認や試聴は、人が実際に行った場合だけ完了扱いにする。

### ユーザーによる手動取得手順

自動取得できない候補は、次の手順で取得する。

1. 表の公式配布ページから、無料・有料の表示とライセンスを確認する。
2. ZIPを展開せず、指定のローカルディレクトリへファイルを置く。
3. ファイル名を変更せず、Gitへ追加しない。
4. 取得日、ZIP名、配布ページURLを記録する。パスワード、メールアドレス、決済情報は記録しない。
5. Codexへ再確認を依頼する。

| 候補 | 取得ページ | 料金・取得操作 | 必要ファイル | 配置先 | Codexが次回確認する内容 |
|---|---|---|---|---|---|
| lillstrumpa vol.1 | [公式ページ](https://lillstrumpa.itch.io/game-boy-music-pack-cozy-playful-loops-for-gb-studio) | $1以上の購入表示、Download操作が必要 | `LillstrumpaChiptuneMusicPack.zip` | `local/music-source-candidates/lillstrumpa-vol1/original/` | ZIP一覧、UGE/WAV数、README/LICENSE、ハッシュ、曲単位構造 |
| lillstrumpa vol.2 | [公式ページ](https://lillstrumpa.itch.io/game-boy-music-pack-vol-2) | $1以上の購入表示、Download操作が必要 | `GameBoy_MusicPack_vol2.zip` | `local/music-source-candidates/lillstrumpa-vol2/original/` | 同上 |
| lillstrumpa vol.3 | [公式ページ](https://lillstrumpa.itch.io/music-pack-for-gb-studio-vol3) | $1以上の購入表示、Download操作が必要 | `LillstrumpaChiptuneMusicPack3.zip` | `local/music-source-candidates/lillstrumpa-vol3/original/` | 同上 |
| lillstrumpa vol.4/#5 | [作者ページ](https://lillstrumpa.itch.io/) | 個別ページ・料金・Download操作をユーザー確認 | 個別ページ表示のZIP | `local/music-source-candidates/lillstrumpa-vol4/` または `vol5/` | 個別ページ、曲数、ライセンス、ZIP一覧 |
| Yogi #1 | [公式ページ](https://yogi-tronimal.itch.io/game-boy-music-pack) | Name your own price、Download操作が必要 | `Free Game Boy Music Pack.zip` | `local/music-source-candidates/yogi-pack1/original/` | 8曲のファイル対応、UGE、README/LICENSE、第三者権利、ハッシュ |
| Yogi #2 | [公式ページ](https://yogi-tronimal.itch.io/game-boy-music-pack-2) | Name your own price、Download操作が必要 | `Game Boy Music Pack.zip` | `local/music-source-candidates/yogi-pack2/original/` | 10曲のファイル対応、UGE、README/LICENSE、権利、ハッシュ |

この手順で、ユーザーに購入・ログイン・連絡先入力を要求するものではない。無料候補でもDownload操作やitch.ioの状態により自動取得できない場合があるため、取得できない候補は未確認のまま残す。
