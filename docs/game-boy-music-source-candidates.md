[サウンド仕様へ戻る](sound-spec.md) / [PROJECT.mdへ戻る](../PROJECT.md)

# Game Boy楽曲解析元候補の曲数・偏り調査

## 調査範囲と結論

確認日：2026-08-01。対象は、hUGETrackerのUGEまたはhUGEDriver ASMとして論理構造を解析できる可能性があるGame Boy向け楽曲配布元である。配布ページ上の説明とライセンス表示を一次情報として確認したが、購入・ダウンロードが必要なZIPの内部ファイル、UGE個数、ASM export、README、同梱ライセンスファイルはこの調査環境から取得できなかった。したがって、ページ記載曲数と実ファイル確認数を混同しない。

配布ページ上で収録曲数を確認できた候補は29曲である。個別曲名まで確認できたのはYogi #1/#2の18曲で、lillstrumpa vol.1〜3の11曲はパック単位の曲数だけを確認した。前回の暫定31曲に含まれていた lillstrumpa vol.4（6曲）とvol.5（4曲）は、作者ページで商品の存在と方向性は確認できるが、個別ページ本文で収録曲数を確認できなかったため、29曲の合計には含めない。

この29曲について実ファイルを確認できたUGEは0曲、ASMは0曲である。したがって、現時点の「商用ゲーム向けルールの根拠として利用可能な曲数」「元データをGitHubで管理できる曲数」は、確認済みの実ファイルを母数にすると0曲である。これは配布元が利用を禁止しているという意味ではなく、取得内容・対象ファイル・ライセンス適用範囲を確認できていないため、Pocket SweeperのA〜D受入判定を確定していないという意味である。

## 配布元の確認記録

| 配布元・作者 | 配布ページ上の曲数 | ページで確認できた形式 | ページ上のライセンス | 実ファイル確認 | 受入判定 | 用途・曲調の根拠と未確認事項 |
|---|---:|---|---|---:|---|---|
| lillstrumpa（Pia / Lil’Sock）vol.1 | 4 | UGE、WAV | CC BY 4.0 | UGE 0、ASM 0 | 未判定（A候補） | calm、playful、mysterious、warm/happy。ZIP内部、曲名、UGE個数、同梱条件は未確認 |
| lillstrumpa vol.2 | 3 | UGE、WAV | CC BY 4.0 | UGE 0、ASM 0 | 未判定（A候補） | 3 original loops。個別曲の用途・曲調、ZIP内部、同梱条件は未確認 |
| lillstrumpa vol.3 | 4 | UGE、WAV | CC BY 4.0 | UGE 0、ASM 0 | 未判定（A候補） | 4 loops、calm/background向けの説明。個別曲の用途・曲調、ZIP内部は未確認 |
| lillstrumpa vol.4 | 6（作者ページの暫定表示。個別本文未確認） | UGEを含む旨の作者説明 | CC BY 4.0の個別適用未確認 | UGE 0、ASM 0 | 未判定 | 商品の存在、Soft chiptune loops for GB Studio and GameBoyは作者ページで確認。曲数・個別ライセンス・ZIP内部は未確認 |
| lillstrumpa vol.5 | 4（作者ページの暫定表示。個別本文未確認） | UGEを含む旨の作者説明 | CC BY 4.0の個別適用未確認 | UGE 0、ASM 0 | 未判定 | 商品の存在、Cute loops in uge-formatは作者ページで確認。曲数・個別ライセンス・ZIP内部は未確認 |
| Yogi（Tronimal）Game Boy Music Pack #1 | 8 | UGE | CC BY 4.0 | UGE 0、ASM 0 | 曲単位で判定 | remix、tribute、influence等が混在。原曲権利者・編曲許諾・UGE再配布条件は未確認 |
| Yogi（Tronimal）Game Boy Music Pack #2 | 10 | UGE | CC BY 4.0 | UGE 0、ASM 0 | 未判定（A候補） | Decampment、Only Hope、Walking Outdoors、Absent、Roam The World、Whirlwind、Tech、Gone Missing、That Morning、Closing。個別曲の権利関係、ZIP内部、UGE個数は未確認 |

### 一次情報

- [lillstrumpa Game Boy Music Pack vol.1](https://lillstrumpa.itch.io/game-boy-music-pack-cozy-playful-loops-for-gb-studio)：4 original loops、UGE/WAV、作者、CC BY 4.0を確認。購入が必要なZIP名もページに表示されるが、内部は未取得。
- [lillstrumpa Game Boy Music Pack vol.2](https://lillstrumpa.itch.io/game-boy-music-pack-vol-2)：3 original loops、UGE/WAV、作者、CC BY 4.0を確認。ZIP内部は未取得。
- [lillstrumpa Game Boy Music for GB Studio vol.3](https://lillstrumpa.itch.io/music-pack-for-gb-studio-vol3)：4 loops、UGE/WAV、作者、CC BY 4.0を確認。ZIP内部は未取得。
- [lillstrumpa作者ページ](https://lillstrumpa.itch.io/)：vol.4、vol.5の存在、作者の制作方針、UGEを含むパックであることを確認。ただし個別ページの曲数・適用ライセンスは未確認。
- [Yogi Game Boy Music Pack #1](https://yogi-tronimal.itch.io/game-boy-music-pack)：8曲、各曲名、UGE、CC BY 4.0、remix/tribute/influenceの記載を確認。作者コメントの「commercial games」許可も確認したが、原曲権利者の許諾を代替しない。
- [Yogi Game Boy Music Pack #2](https://yogi-tronimal.itch.io/game-boy-music-pack-2)：10曲、各曲名、UGE、CC BY 4.0を確認。ZIP内部は未取得。

ライセンス本文の一般条件は、既存の [`docs/sound-spec.md`](sound-spec.md) に記録したCreative Commons公式情報を参照する。今回の候補調査では、配布ページの「Asset license」表示を確認しただけであり、各ZIP内のライセンスファイルや個別UGEへの著作権表示までは確認していない。

### Yogi Game Boy Music Pack #1の曲単位判定

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
| 実ファイル名確認済み | 0 | ZIPを取得してファイル一覧を確認できた曲 |
| 実ファイル確認済みUGE | 0 | UGEを取得して内容を確認できた曲 |
| 実ファイル確認済みASM | 0 | ASMを取得して内容を確認できた曲 |
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

- 20曲程度を選べるページ上の候補母数はあるが、実ファイル確認済みは0曲なので、解析コーパスとしての利用可能母数はまだ0曲である。
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

- 各ZIPを取得した後のUGEファイル数、ファイル名、Song Version、OrderMatrix、pattern、Instrument、Wave/Noise、loop表現。
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

元素材はリポジトリ外のローカル専用ディレクトリ `local/music-source-candidates/` に保存する。このディレクトリは今回 `.gitignore` に追加し、次の構成を使う。

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
