# vrc-shor-braket-LT

VRChat 物理学集会 LT 用スライド資料 — **Shor のアルゴリズムの位数発見回路を、Amazon Braket 経由で
超伝導量子コンピュータ IQM Garnet に投げてみた話** の発表用プロジェクト。

スライド本体は [reveal.js](https://github.com/hakimel/reveal.js) で構成し、
[lt-slide-template](https://github.com/s-sasaki-earthsea-wizard/lt-slide-template) をベースにしている。

## 概要

元プロジェクト [shor-braket](https://github.com/s-sasaki-earthsea-wizard/shor-braket) の成果を、
物理に興味のある一般の聴衆向けに紹介する。主題は「うまくいった」ではなく
**「どう、どれだけうまくいかなかったかを数字で確かめた」** こと。

- $N = 15$ 専用の位数発見回路（6 qubit、2 qubit ゲート 88 個）を IQM Garnet で 3000 ショット実行
- 信号残存率 λ は 0.272 ± 0.012（エミュレータの予測 0.564）。差の主因は待機中の qubit のデコヒーレンス
- $N = 15$ では位数がすべて 2 のべきなので、この λ は量子的な干渉を見ていなかった
- count qubit を 1 つ増やした追加実験では、待機 qubit の位相がほぼ完全に失われていた（可視度 0.087 ± 0.018）
- 費用は 3 タスクで 9.61 USD

**この発表は因数分解の成功を主張しない。** 回路は $N = 15$ の構造と「位数は 4 以下」という手掛かりを使っており、
結果は「手掛かりの量 × 機械 → 残った信号」として紹介する。

## 元プロジェクトの資料

数字と図の出典はすべて元プロジェクトの公開資料にある。

| 資料 | 内容 |
|---|---|
| [図で追う Shor のアルゴリズム](https://github.com/s-sasaki-earthsea-wizard/shor-braket/wiki/Shor-Algorithm-Visual-Walkthrough) | アルゴリズムの流れと図 |
| [N=15 を QPU 互換回路で](https://github.com/s-sasaki-earthsea-wizard/shor-braket/wiki/Shor-N15-on-Local-Emulator) | 回路、配置、誤り予算、エミュレータの予測 |
| [実機で最初の 3000 ショット](https://github.com/s-sasaki-earthsea-wizard/shor-braket/wiki/First-Hardware-Run-on-IQM-Garnet) | 実機の結果、減衰モデル、区切りの判断 |
| [Amazon Braket で Shor を動かした先行事例](https://github.com/s-sasaki-earthsea-wizard/shor-braket/wiki/Amazon-Braket-Shor-Prior-Art) | 先行事例の分類と、言ってよいこと・避ける表現 |
| [issue #31](https://github.com/s-sasaki-earthsea-wizard/shor-braket/issues/31) | 次の実験の候補（CHSH 不等式） |

## ディレクトリ構成

```text
.
├── data/                  # スライドの図に使う分布（理想 / エミュレータ / 実機）
├── docs/
│   └── talk_outline.md    # 構成、各スライドの数字の出典、表現の約束、未決事項
├── scripts/
│   ├── extract_run_data.py  # shor-braket の実行結果から data/ を作る
│   └── make_figures.py      # data/ から実機結果の図を描く
└── slides-jp/             # reveal.js スライド
    ├── index.html
    └── assets/images/
        ├── garnet_*.svg   # make_figures.py が生成
        └── wiki/          # 元プロジェクトの Wiki の図
```

## 開発環境

- Node.js 18 以上（reveal.js 5.x の要求）
- Python 3.12 以上、matplotlib、numpy（図を描き直す場合のみ）
- 必要に応じて [decktape](https://github.com/astefanutti/decktape)（PDF エクスポート用）

## 使い方

### スライドのプレビュー

```bash
cd slides-jp
npm install
npm start
```

ブラウザで <http://localhost:8000> にアクセスする。

### 図の描き直し

```bash
python scripts/make_figures.py
```

`data/garnet_2026-09-23.json` から `slides-jp/assets/images/garnet_*.svg` と `title.png` を生成する。
`data/` を作り直すには shor-braket の実行結果（`runs/raw`、バージョン管理の対象外）が手元に必要。

```bash
python scripts/extract_run_data.py --shor-braket-root <shor-braket のチェックアウト>
```

### スライドの PDF エクスポート

```bash
cd slides-jp
decktape --size 1920x1080 index.html slides.pdf
```

## 免責事項

本スライドの内容に従ったいかなる結果においても著者は一切の責任を負いません。

本プロジェクトは [reveal.js](https://github.com/hakimel/reveal.js)（MIT License）と
[KaTeX](https://github.com/KaTeX/KaTeX)（MIT License、`slides-jp/vendor/katex` に同梱）を利用している。
