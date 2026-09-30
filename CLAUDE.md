# vrc-shor-braket-LT

## プロジェクト概要

**VRChat 物理学集会 LT 用スライド資料**。
[shor-braket](https://github.com/s-sasaki-earthsea-wizard/shor-braket)（Shor のアルゴリズムの位数発見回路を
Amazon Braket の実機で動かしたプロジェクト）の成果を発表する。

スライド本体は `slides-jp/index.html`（reveal.js）。構成と数字の出典は `docs/talk_outline.md` にまとめてある。

## 発表の主題（この LT のスコープ）

- **対象集会**: VRChat 物理学集会（物理に興味のある一般の聴衆。量子計算の予備知識は仮定しない）
- **切り口**: 「うまくいった」ではなく「どう、どれだけうまくいかなかったかを数字で確かめた」
- **物理の聞きどころ**: 周期構造のフーリエ変換、T1 / T2 とデコヒーレンス、「何を測っているのか」という問い
- **話さないこと**: AWS 側のインフラ設計（IAM、Terraform、課金ガードレール）の詳細。Appendix で 1 枚触れるだけ

## 絶対に守る表現の約束

元プロジェクトの約束をそのまま引き継ぐ。

1. **「15 の因数分解に成功した」と書かない。** 回路は $N = 15$ 専用の乗算分解と $t = 2$（位数は 4 以下という知識）を
   使っている。結果は「手掛かりの量 × 機械 → 信号残存率 λ」として書く
2. **「因数が出た」を成功の証拠として扱わない。** 一様乱数を返す装置でも $t = 2$ では 75% で正しい位数に辿り着く
3. **$t = 2$ の λ を干渉やコヒーレンスの証拠として書かない。** $N = 15$ では位数が 2 のべきなので、
   λ は乗算ネットワークの忠実度の言い換えでしかない
4. **$t = 3$ の可視度は「待機 qubit の位相保持」であり、count qubit どうしの干渉ではない**
5. **「Amazon Braket で初めて」のような先行例の不存在を主張しない**
6. **CHSH を「ベルの不等式の検証実験」と書かない。** 1 チップ上の測定はエンタングルメントの質の測定
7. 減衰モデルのゲート時間は**仮定**。「主因は待機中のデコヒーレンス」は示唆として書く

## スライドに載せてよい情報

- 元プロジェクトで公開されているもの（リポジトリ、Wiki、issue）は書いてよい
- **AWS のアカウント ID、バケット名、タスク ARN、メールアドレス、ローカルやリモートのマシンの参照先は書かない**
- ローカルの参照先や作業メモは `.claude-notes/`（gitignore 対象）に置く

## 関連リンク

- 元プロジェクト: <https://github.com/s-sasaki-earthsea-wizard/shor-braket>
- 元プロジェクトの Wiki: <https://github.com/s-sasaki-earthsea-wizard/shor-braket/wiki>
- スライドテンプレート: <https://github.com/s-sasaki-earthsea-wizard/lt-slide-template>
- 参考フォーマット（姉妹 LT リポ）: <https://github.com/s-sasaki-earthsea-wizard/vrc-gw150914-einstein-toolkit-LT>

## 言語設定

ユーザへの応答は **日本語**。スライド本文は日本語。
コード内のコメント、ログメッセージ、エラーメッセージ、docstring は **英語**。

## 開発ルール

### スライド作成

- ベース: [reveal.js](https://github.com/hakimel/reveal.js) 5.1.0
- メインファイル: `slides-jp/index.html`
- 脚本: `slides-jp/yt_script.md` / `slides-jp/youtube_description.md`
- カスタムスタイル: `slides-jp/styles/custom-style.css`
- 数式は KaTeX（`$...$` / `$$...$$`）。`slides-jp/vendor/katex` に同梱した版を読み込む
- スライドの区切りは「`---` だけの行」
- **見出しに数式を入れない。** テーマが見出しを大文字化するので λ が Λ になる
- **Markdown の中の数式で `\{`、`\,`、`\|` を使わない。** Markdown のエスケープとして消える
  （`\lbrace`、`\lvert` などで書く）
- 表は HTML の `<table>` で書き、`results-box` か `simple-box` に入れる
- 1 枚の高さは 700 px。はみ出したら文を削るか図を小さくする（図のあるスライドは図を優先する）

### 図

- 実機結果の図は `scripts/make_figures.py` が `data/garnet_2026-09-23.json` から生成する。手で編集しない
- 色の意味は全図で固定: 青 = 理想、橙 = 実機、緑 = モデルの予測
- `slides-jp/assets/images/wiki/` は元プロジェクトの Wiki の図のコピー。元の図が更新されたらコピーし直す

### コーディング規約

- Python: PEP 8 準拠、関数 snake_case、クラス PascalCase、定数 UPPER_SNAKE_CASE、Docstring は Google Style
- HTML / JS: インデントはスペース 2 文字

### Git 運用

- ブランチ戦略: `feature/*`, `fix/*`, `refactor/*`
- コミットメッセージ: 英文を使用、動詞から始める
- PR は main ブランチへ

### コミットメッセージ規約

- **1 コミット = 1 つの主要な変更**

プレフィックスと絵文字:

- ✨ feat: 新機能
- 🐞 fix: バグ修正
- 📚 docs: ドキュメント
- 🎨 style: コードスタイル修正
- 🛠️ refactor: リファクタリング
- ⚡ perf: パフォーマンス改善
- ✅ test: テスト追加・修正
- 🏗️ chore: ビルド・補助ツール
- 🚀 deploy: デプロイ
- 🔒 security: セキュリティ修正
- 📝 update: 更新・改善
- 🗑️ remove: 削除

**重要**: Claude Code を使用してコミットする場合は、必ず以下の署名を含める:

```text
🤖 Assisted by [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## 現在の状態

- 2026-09-30: テンプレートからリポジトリを作成し、スライドのドラフト（本編 50 枚 + Appendix 10 枚）を作成
- 未決事項は `docs/talk_outline.md` の末尾
