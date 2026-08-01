[サウンド仕様へ戻る](sound-spec.md) / [PROJECT.mdへ戻る](../PROJECT.md)

# Game Boy楽曲解析元候補の曲数・偏り調査

## 調査範囲と結論

確認日：2026-08-01。対象は、hUGETrackerのUGEまたはhUGEDriver ASMとして論理構造を解析できる可能性があるGame Boy向け楽曲配布元である。配布ページ上の説明とライセンス表示に加え、今回Yogi #1/#2の取得済みZIPを展開せずに検査し、Git追跡対象外の作業領域へ展開してファイル一覧・ハッシュ・README/LICENSE候補を確認した。ページ記載曲数と実ファイル確認数を混同しない。

配布ページ上で収録曲数を確認できた候補は36曲である。内訳はYogi #1/#2の18曲、lillstrumpa vol.1〜3の11曲、objetdiscretの追加7曲である。個別曲名まで確認できたのはYogi #1/#2の18曲とobjetdiscretの7曲で、lillstrumpa vol.1〜3の11曲はパック単位の曲数だけを確認した。前回の暫定31曲に含まれていた lillstrumpa vol.4（6曲）とvol.5（4曲）は、作者ページで商品の存在と方向性は確認できるが、個別ページ本文で収録曲数を確認できなかったため、36曲の合計には含めない。

この36曲のうち、実ファイル名を確認できたのはYogi #1/#2の18曲で、UGEは18曲、ASMは0曲である。objetdiscretの7曲はページ上でUGEファイル名まで確認したが、実ファイルは取得待ちである。公開一次情報による既存Aは14曲で、今回の追加選定候補は7曲、合計のページ選定候補は21曲となる。ただし、実ファイル確認済みの利用可能曲数は既存14曲のままである。

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
- [Fabulous Classical Chiptunes](https://objetdiscret.itch.io/fab-class-tunes)：objetdiscret作。公式ページで7曲、7個の個別UGEファイル名、GB Studio/hUGETracker対応、UGEへのCC BY 4.0適用を確認。原曲は公開ページ記載のパブリックドメイン作曲家の作品。ダウンロードはitch.ioのName your own price操作が必要で、実ファイルは未取得。

ライセンス本文の一般条件は、既存の [`docs/sound-spec.md`](sound-spec.md) に記録したCreative Commons公式情報を参照する。今回の候補調査では、Pack #1 README内の「Tronimal - CC-BY 2025」と第三者作品由来の記載、Pack #2の同梱ファイル不在を確認した。これは個別UGEへのライセンス適用範囲や原曲権利者の許諾を最終確定するものではない。

## 追加選定候補（2026-08-01）

### 選定基準と状態

公開一次情報だけで、公式配布ページ、作者、UGE形式、曲数、ライセンス、商用利用・改変・再配布の判断材料、帰属条件、第三者由来の記載を確認した候補を選定した。実ファイル未取得の候補は「選定候補・取得待ち」とし、実ファイル確認済みの利用可能曲数には加えない。購入・ログイン・ダウンロード操作は行わない。

### objetdiscret / Fabulous Classical Chiptunes

公式ページは[こちら](https://objetdiscret.itch.io/fab-class-tunes)。作者は `objetdiscret`。ページ本文は、GBゲーム用に作成した7曲のアルバムで、`.uge` はGB Studio/hUGETracker互換、`.flac` と `.uge` にCC BY 4.0が適用されると明記している。曲はBach、Liszt、Beethoven、Chopin、Donaldson、Satie、Mozartの公開ページ記載作品を編曲したものとして説明されており、第三者の現行楽曲をbased on/remixした記載ではない。CC BY 4.0の帰属は `objetdiscret`、ライセンスURLは <https://creativecommons.org/licenses/by/4.0/> とする。

| 配布元 | パック名 | 公式URL | ページ記載曲数 | 個別曲名 | UGE | ASM | ライセンス | 商用利用 | 改変 | 元UGE公開 | 派生ASM公開 | 帰属 | 第三者由来 | 取得方法 | 状態 | 根拠・残課題 |
|---|---|---|---:|---|---:|---:|---|---|---|---|---|---|---|---|---|---|
| objetdiscret | Fabulous Classical Chiptunes | [itch.io](https://objetdiscret.itch.io/fab-class-tunes) | 7 | Title-Prelude; Overworld-Liebestraum; Gallery-Pathetique; Underwater-Tristesse; Indoors-Heaven; Dream-Gymnopedie; Ending-Rondo | 7（ページ記載） | 0（ページ記載なし） | CC BY 4.0 | 可 | 可 | 条件付きで可 | 条件付きで可 | 作者名、曲名、公式URL、CC BY 4.0、ライセンスURL、改変表示 | なし（公開ページ上。原曲は公開ページ記載のパブリックドメイン作品） | 人手（itch.ioのName your own price、最低価格表示あり） | 選定候補・取得待ち | ページ本文、個別UGEファイル名、ライセンス記載を確認。ZIP内部、UGEハッシュ、内部曲名、ASM有無は未確認 |

#### 曲単位の追加候補

| 曲名 | UGEファイル名 | 原曲（公式ページ記載） | 形式 | ライセンス適用 | 状態 |
|---|---|---|---|---|---|
| Title-Prelude | `01-Title-Prelude.uge` | Prelude in C major — Johann Sebastian Bach | UGE | CC BY 4.0 | 選定候補・取得待ち |
| Overworld-Liebestraum | `02-Overworld-Liebestraum.uge` | Liebestraum No. 3 — Franz Liszt | UGE | CC BY 4.0 | 選定候補・取得待ち |
| Gallery-Pathetique | `03-Gallery-Pathetique.uge` | Piano Sonata No. 8 — Ludwig van Beethoven | UGE | CC BY 4.0 | 選定候補・取得待ち |
| Underwater-Tristesse | `04-Underwater-Tristesse.uge` | Etude Op. 10, No. 3 — Frédéric Chopin | UGE | CC BY 4.0 | 選定候補・取得待ち |
| Indoors-Heaven | `05-Indoors-Heaven.uge` | My Blue Heaven — Walter Donaldson | UGE | CC BY 4.0 | 選定候補・取得待ち |
| Dream-Gymnopedie | `06-Dream-Gymnopedie.uge` | Gymnopédie No. 1 — Erik Satie | UGE | CC BY 4.0 | 選定候補・取得待ち |
| Ending-Rondo | `07-Ending-Rondo.uge` | Piano Sonata No. 11 / Rondo alla Turca — Wolfgang Amadeus Mozart | UGE | CC BY 4.0 | 選定候補・取得待ち |

この7曲はページ上の追加選定候補としては6曲以上の条件を満たすが、実ファイル取得前なので「利用可能確定20曲」とは扱わない。公開ページには音声プレビューとゲーム用途の説明があるが、試聴による最終的な用途・曲調評価は後続の人作業とする。

### 既存候補の再評価と代表的な除外

確認日：2026-08-01。lillstrumpa vol.1（4曲）、vol.2（3曲）、vol.3（4曲）は公式ページで作者、UGE形式、CC BY 4.0、GB Studio用途、original chiptune loopsの説明を再確認した。ただし各ページは最低価格購入が必要で、ZIP内部のUGEファイル名・ハッシュ・個別ライセンス適用は未確認のため、11曲は取得待ち候補ではなく既存の未判定候補として扱う。vol.4/vol.5は個別ページ・曲数・対象UGEを確認できないため保留のままとする。

| 候補 | 公開情報で確認した形式・条件 | 状態 | 除外/保留理由 |
|---|---|---|---|
| Not Jam / NJ Mix #01 | WAVのみ、CC0、7曲 | 除外 | UGE/ASMではなく、今回の追加選定形式に該当しない |
| SuperDisk / hUGEDriver `rgbds_example/sample_song.asm` | ASM 1件、リポジトリはpublic domain | 保留（追加選定数外） | 公式リポジトリとASMは確認できるが、単一サンプル曲で6曲の追加候補にならず、曲名・作者・用途の曲単位情報が不足 |
| potatoTeto / fur2uge demo songs | 変換ツール、demo曲はCC BY-NC 4.0 | 除外 | 商用利用不可のため受入基準外 |
| OpenGameArtの音声トラック候補 | WAV/OGG等、CC0/CC BYを含む | 除外 | UGE/ASM実ファイルではない |

主要検索語は `Game Boy UGE CC0`、`Game Boy UGE CC BY 4.0`、`hUGETracker music pack license UGE`、`hUGEDriver music ASM license`、`UGE format CC0`、`site:github.com .uge Game Boy music license`。itch.io公式ページ、GitHub公式リポジトリ、Creative Commons公式条件を優先し、検索結果スニペットだけでは採用しなかった。

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

## 18曲の曲単位ライセンス判定（更新）

確認日：2026-08-01。以下は法的保証ではなく、公開一次情報だけで採否を決めるPocket Sweeperの運用上の受入判定である。公式配布ページのAsset licenseがCC BY 4.0で、パックとUGEが一意に対応し、第三者楽曲由来を明記していない曲はAとする。第三者権利が絶対に存在しないこと、作者の追加保証、契約不存在の証明は要求しない。CC BY 4.0は商用利用・改変・再配布を許すが、帰属と変更表示が必要である（[CC BY 4.0公式](https://creativecommons.org/licenses/by/4.0/)）。

Pack #1 READMEの `Tronimal - CC-BY 2025` は正式な版表記としては扱わず、公式ページのCC BY 4.0表示を通常の利用根拠とする。Pack #2はREADME/LICENSEがないが、公式ページのAsset license、10曲の掲載、ZIP内の10 UGEとファイル名対応を根拠にする。第三者由来の記載がないことを確認したのであり、第三者権利の不存在を証明したわけではない。問い合わせは行わず、採用できない曲は別素材で置き換える。

### 由来・権利・区分

| Pack | 曲名 | UGEファイル | 配布ページライセンス | 同梱ライセンス | 曲の由来 | 第三者権利 | 商用利用 | 改変 | 元UGE公開 | ASM公開 | 一般化結果公開 | 帰属 | A〜D | 根拠・残課題 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| #1 | Hypergolic Blast Off | `free_01_hypergolic_blast_off.uge` | CC BY 4.0 | `Tronimal - CC-BY 2025` | based on Creepy Organ by Beatscribe | 明記あり | 不可 | 不可 | 行わない | 行わない | 不可 | 必要 | D（採用しない） | Pack #1本文・README。第三者曲由来が明記され、問い合わせなしで除外 |
| #1 | Blue Ocean Remix | `free_02_blue_ocean_remix.uge` | CC BY 4.0 | 同上 | based on Blue Ocean by Coffee Bat | 明記あり | 不可 | 不可 | 行わない | 行わない | 不可 | 必要 | D（採用しない） | Pack #1本文・README。第三者曲由来が明記され、問い合わせなしで除外 |
| #1 | Darkstone Remix | `free_03_darkstone_remix.uge` | CC BY 4.0 | 同上 | based on Darkstone by DeerTears | 明記あり | 不可 | 不可 | 行わない | 行わない | 不可 | 必要 | D（採用しない） | Pack #1本文・README。第三者曲由来が明記され、問い合わせなしで除外 |
| #1 | Neurotic Robonaut | `free_04_neurotic_robonaut.uge` | CC BY 4.0 | 同上 | port of my own Virtual Boy music | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #1本文・README。作者自身の作品由来、第三者由来の明記なし |
| #1 | Hideout | `free_05_hideout.uge` | CC BY 4.0 | 同上 | original song from discontinued Patreon project | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #1本文・README。originalの明記を採用根拠とする |
| #1 | Delight | `free_06_delight.uge` | CC BY 4.0 | 同上 | based on the most popular western chord progression | なし（特定曲の記載なし） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #1本文・README。一般的コード進行を第三者曲由来とは扱わない |
| #1 | Observing Jupiter | `free_07_observing_jupiter.uge` | CC BY 4.0 | 同上 | tribute to the Game Boy Camera OST | 明記あり | 不可 | 不可 | 行わない | 行わない | 不可 | 必要 | D（採用しない） | Pack #1本文・README。第三者作品との直接的関係が明記 |
| #1 | Terminate | `free_08_terminate.uge` | CC BY 4.0 | 同上 | influenced by Terminator 2 OST | なし（influenceのみ） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #1本文・README。influenceをremix/cover/based onと同一視しない |
| #2 | Decampment | `01_decampment.uge` | CC BY 4.0 | なし | 個別由来記載なし | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #2本文・ZIP。公式Asset licenseと一意なUGE対応 |
| #2 | Only Hope | `02_only_hope.uge` | CC BY 4.0 | なし | 個別由来記載なし | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #2本文・ZIP。README不在だけで除外しない |
| #2 | Walking Outdoors | `03_walking_outdoors.uge` | CC BY 4.0 | なし | 個別由来記載なし | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #2本文・ZIP |
| #2 | Absent | `04_absent.uge` | CC BY 4.0 | なし | 個別由来記載なし | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #2本文・ZIP |
| #2 | Roam The World | `05_roam_the_world.uge` | CC BY 4.0 | なし | 個別由来記載なし | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #2本文・ZIP |
| #2 | Whirlwind | `06_whirlwind.uge` | CC BY 4.0 | なし | 個別由来記載なし | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #2本文・ZIP |
| #2 | Tech | `07_tech.uge` | CC BY 4.0 | なし | 個別由来記載なし | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #2本文・ZIP |
| #2 | Gone Missing | `08_gone_missing.uge` | CC BY 4.0 | なし | 個別由来記載なし | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #2本文・ZIP |
| #2 | That Morning | `09_that_morning.uge` | CC BY 4.0 | なし | 個別由来記載なし | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #2本文・ZIP |
| #2 | Closing | `10_closing.uge` | CC BY 4.0 | なし | 個別由来記載なし | なし（公開記載上） | 可 | 可 | 条件付きで可 | 条件付きで可 | 可 | 必要 | A | Pack #2本文・ZIP |

 A曲の元UGE公開と派生ASM公開は、CC BY 4.0の帰属・変更表示・ライセンスURLを付ける条件付き可であり、ROM組込みとは別の判定である。D曲は採用、解析、ルール抽出、元UGE/ASM公開を行わず、問い合わせもしない。一般化結果はA曲について元曲を再現しない設計結果として可とするが、無条件の自由利用とは扱わない。

### 帰属表示案

 A曲の表示案は、`"<曲名>" by Yogi (Tronimal) / Source: <Pack公式URL> / Licensed under CC BY 4.0 / https://creativecommons.org/licenses/by/4.0/` とする。改変時は `Modified for Pocket Sweeper` を追加する。表示場所候補はゲーム内クレジット、配布README、itch.io配布ページ、GitHubのクレジット文書である。今回は正式なクレジットファイルを作成しない。

### A曲の利用形態別判定

| 利用形態 | A曲14曲 | 条件 |
|---|---|---|
| ローカル保管 | 可 | 作業領域で管理 |
| ローカル解析 | 可 | D曲は解析しない |
| ルール抽出の根拠 | 可 | 元曲を再現しない一般化として利用 |
| 商用ゲームへ使用 | 可 | CC BY 4.0の帰属条件を満たす |
| 改変 | 可 | 改変表示を付ける |
| 元UGEをGitHub公開 | 条件付きで可 | 帰属、変更表示、ライセンスURLを付ける |
| 派生ASMをGitHub公開 | 条件付きで可 | 改変物として同じ条件を満たす |
| 一般化結果公開 | 可 | 元曲の代替物・再現物にしない |
| 帰属表示 | 必要 | 作者、曲名、公式URL、CC BY 4.0、ライセンスURL |
| 変更表示 | 改変時に必要 | 変更内容を示す |

D 4曲はPocket Sweeperへの採用、商用利用、元UGE/ASM公開、ルール抽出、問い合わせを行わない。

### 問い合わせを行わない運用

今回の判定では作者・原曲権利者への問い合わせ、購入、ログイン、規約同意を行わない。公開一次情報で第三者楽曲由来が明記された4曲はD（採用しない）とし、残り14曲は公式Asset licenseを通常の利用根拠としてAとする。不足分は別の明確な公開ライセンス素材で補う。

## 利用可能曲数の定義と集計

分母を明記する。ページ確認曲数の分母は36曲、実ファイル確認曲数の分母は18曲である。今回の既存18曲はA〜Dを確定し、objetdiscretの追加7曲は選定候補・取得待ち、lillstrumpa vol.1〜3の11曲は個別ファイル未確認のため未判定である。

| 指標 | 曲数 | 分母・意味 |
|---|---:|---|
| 配布ページ上で曲名・曲数を確認 | 36 | vol.1〜3、Yogi #1/#2、objetdiscretのページ記載分。vol.4/#5暫定表示は除外 |
| 配布ページ上で存在だけ確認した追加候補 | 10 | lillstrumpa vol.4/#5の暫定曲数。内訳・個別ページ未確認 |
| 配布ページ上で個別曲名を確認 | 25 | Yogi #1/#2の18曲、objetdiscretの7曲。lillstrumpa vol.1〜3の11曲は曲名未確認 |
| 実ファイル名確認済み | 18 | Yogi #1/#2のZIPを取得してファイル一覧を確認できた曲 |
| 実ファイル確認済みUGE | 18 | Yogi #1/#2のZIP内UGEファイル（曲名対応まで確認、詳細内容は未解析） |
| 実ファイル確認済みASM | 0 | ASMを取得して内容を確認できた曲 |
| ページ上の追加選定候補 | 7 | objetdiscretの7 UGE。実ファイル取得待ちで、利用可能確定数には未算入 |
| 追加候補の取得待ち | 7 | itch.ioのName your own price操作・最低価格表示が必要 |
| 曲名対応確定 | 18 | Pack #1 8曲、Pack #2 10曲。配布ページ・README/ファイル名・曲順を照合 |
| 曲名対応暫定 | 0 | 該当なし |
| 曲名対応不一致 | 0 | 該当なし |
| 曲名対応確認不能 | 0 | 該当なし |
| ライセンス適用範囲まで確認済み | 14 | 今回のA曲。公式Asset license、対象パック、UGE対応を確認 |
| A（公開・商用利用可）確定 | 14 | Yogi #1の4曲、#2の10曲。公開一次情報上の受入判定 |
| B（解析・ローカル限定）確定 | 0 | 解析・変換・非公開保管の条件まで確認できた曲 |
| C（一般化結果のみ）確定 | 0 | 元を再現しない結果の利用条件まで確認できた曲 |
| D（採用しない） | 4 | Pack #1のbased on/remix 3曲とtribute 1曲。問い合わせは行わない |
| A〜D未判定 | 11 | lillstrumpa vol.1〜3の個別曲（今回対象外） |
| 商用ゲーム向けルール根拠として利用可能 | 14 | A曲。CC BY 4.0条件と帰属を適用 |
| 元データをGitHub管理可能 | 14 | CC BY 4.0の帰属・変更表示・URL付きで条件付き可 |
| 派生ASMをGitHub公開可能 | 14 | 改変物として変更表示・帰属・URL付きで条件付き可 |
| ローカル解析のみ可能 | 0 | A曲は公開根拠として利用し、D曲は解析しない |
| 作者問い合わせ待ち | 0 | 問い合わせを行わない運用 |
| 原曲権利者問い合わせ待ち | 0 | D曲は問い合わせせず採用しない |

ページ確認母数の検算は `11 + 8 + 10 + 7 = 36`。既存対象18曲の判定検算は `A 14 + B 0 + C 0 + D 4 + 未確定 0 = 18`。追加候補は `7曲・UGE 7・ASM 0・取得待ち7` である。実ファイル確認済み曲数は18曲で、そのうち利用可能なA確定曲は14曲である。ページ確認36曲全体では、既存A14、既存D4、追加取得待ち7、既存未判定11である。

### 作者別・配布元別・ライセンス別・形式別

| 分類 | 内訳（ページ確認36曲を分母） |
|---|---|
| 作者 | lillstrumpa 11曲（30.6%）、Yogi 18曲（50.0%）、objetdiscret 7曲（19.4%） |
| 配布元 | lillstrumpa vol.1〜3 11曲、Yogi #1/#2 18曲、objetdiscret 7曲 |
| ライセンス表示 | CC BY 4.0表示あり 36曲（100%）。実ファイル適用確認済みは既存A14曲 |
| 形式表示 | UGE表示あり 36曲（100%）、WAV/FLAC併記あり、ASM表示 0曲（0%） |

作者ページのvol.4/#5を含めると、作者・配布元の暫定母数は39曲となるが、曲数と個別ライセンスの確認不足があるため、分布集計には使用しない。

### 用途別・曲調別

曲単位で試聴またはREADMEの個別説明を確認できていないため、用途別・曲調別の確定集計は未実施である。ページのパック説明と曲名から安全に言える範囲だけを「配布元説明による暫定タグ」として記録する。

| 暫定タグ | 曲数 | 分母 | 根拠・注意 |
|---|---:|---:|---|
| calm / gentle / cozy / background | 11以上 | 29 | lillstrumpa vol.1〜3のパック説明。個別曲への割当ではない |
| playful / happy / warm / cute | 4以上 | 29 | vol.1の4 mood説明、vol.2/#3のパック説明。重複あり |
| mysterious / slightly tense | 1 | 29 | vol.1の説明にあるmood。個別曲名は未確認 |
| based on / remix / tribute / influence | 5 | 29 | Yogi #1の曲説明。Dはbased on/remix 3曲とtribute 1曲、influenced by 1曲はA |
| タイトル、メニュー、通常プレイ等の用途 | 0確定 | 29 | 個別曲の用途説明・試聴未確認 |
| 戦闘、ボス、勝利、ゲームオーバー、短いジングル | 0確定 | 29 | 不足と断定せず、未確認として扱う |
| 曲調不明 | 29 | 29 | 個別曲単位の試聴・説明確認がないため、上記タグと両立する |

したがって、配布元説明から「穏やか・日常・背景向けに偏る可能性」は示せるが、29曲中21曲などの個別曲調割合はまだ算出できない。曲名だけから用途や曲調を確定しない。

## 偏りの評価と追加収集目標

- 20曲程度を選べるページ上の候補母数があり、実ファイル名確認済みは18曲ある。既存Yogi 18曲のうち、ライセンス適用範囲まで確認して解析コーパスとして利用可能と確定した母数は14曲である。objetdiscret追加7曲は実ファイル取得待ちである。
- 作者は確認済みページ母数では3名、lillstrumpa、Yogi、objetdiscretへ偏っている。特定作者の作風を一般化しないため、後続選定では少なくとも4〜5名を目標にする。
- 配布元説明はcalm、cozy、cute、background寄りで、戦闘・高速アクション・不穏・恐怖・勝利・短いジングルの実数は未確認である。
- UGEは配布ページ上で36曲すべてに表示されるが、ASM候補は0曲である。実ファイル取得後も、UGEからのASM exportだけでなく、最初からASMで配布される候補を少なくとも3曲探す。
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

現時点で公開一次情報に基づき採用できるのは14曲で、約20曲の目標には6曲以上不足する。後続WBSでは問い合わせで救済せず、公式配布ページと明確な公開ライセンスが確認できるUGE/ASM素材を追加選定する。用途・曲調と構造は後続の解析・試聴WBSで確認する。

## 後続WBSの候補選定方針

1. 配布ページの曲数ではなく、実ファイルのUGE/ASM一覧を取得して曲単位のレコードを作る。
2. `docs/sound-spec.md` の候補記録様式に、作者、取得日、対象ファイル、ライセンス版、適用根拠、A〜D区分、未確認事項を記録する。
3. remix、cover、based on、tributeなど第三者作品との関係が明記された候補は問い合わせず採用対象外にする。influenced byだけは同一視しない。
4. A曲の元データGitHub公開、派生ASM公開、ROM組込み、一般化結果公開を分け、CC BY 4.0の帰属・変更表示・URL条件を付ける。
5. Aだけを商用ゲーム向けルールの根拠に使い、Dは採用・解析しない。未判定候補は別途公開ライセンスを確認する。
6. 用途・曲調は、配布元説明、曲名、README、試聴の根拠を別欄に記録し、曲名だけの分類は暫定タグにする。
7. 20曲を選ぶ場合も、作者・配布元・用途・曲調・形式の最大偏りを避け、特定パックだけで埋めない。

## 未確認事項

- 各UGEのSong Version、OrderMatrix、pattern、Instrument、Wave/Noise、loop表現、内部Song Nameの安全な読み取り。
- Pack #1/#2の実ファイルにはASM/INCが同梱されていない。UGEからのASM exportは未実施であり、ASMが必要な後続解析では別途exportまたは別配布元調査が必要。
- hUGEDriver ASMが同梱されるか、またはUGEから再ExportしたASMを解析対象としてよいか。
- 個別UGEに作者・著作権・ライセンス情報が埋め込まれているか。
- lillstrumpa vol.4/#5の個別曲数、曲名、個別ページのライセンス表示。
- 追加候補の実ファイル、ライセンス、用途・曲調、構造。
- 試聴に基づく用途・曲調、CH4/Noise使用傾向、4チャンネルの多様性。
- Doug T、Beatscribe、TipTopTomCat等の追加候補は、今回の調査では一次情報とファイル内容を十分確認できなかったため、候補一覧の集計に含めていない。

上記は後続の構造解析、試聴、追加素材選定に関する未確認事項であり、今回の14曲のA/4曲のD判定を保留する理由ではない。

## 実ファイルの取得・保管・確認手順

### 取得対象の優先順位

候補は次の順で確認する。

1. 認証不要かつ無料で直接取得できる公開ファイル
2. itch.io等で無料ダウンロード可能だが、画面上のDownload操作が必要な素材
3. 任意価格または支払いが必要な素材
4. 有料素材
5. 今回の採用基準を満たさず、公開ライセンス素材へ置き換える素材

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
