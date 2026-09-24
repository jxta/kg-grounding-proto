# 素因数分解の「地図」— 実験で「わかった」を接地させる Jupyter Notebook

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jxta/kg-grounding-proto/HEAD?labpath=kg_prime_factorization.ipynb)
[![JupyterLite](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://jxta.github.io/kg-grounding-proto/lab/index.html?path=kg_prime_factorization.ipynb)
[![build-and-deploy](https://github.com/jxta/kg-grounding-proto/actions/workflows/deploy.yml/badge.svg)](https://github.com/jxta/kg-grounding-proto/actions/workflows/deploy.yml)

教科書の知識グラフ（単元の **地図**）を土台に、生徒が Jupyter Notebook の **実験** でノードを一つずつ確かめ、
「どこまで納得したか」の **印**（接地レベル）を根拠つきで **自分の地図** に記録していく――その教育実践のプロトタイプです。
題材は中学1年「素因数分解」（14 ノード）。ノート 1 冊で完結します。

## 動かし方（3 通り）

| 方法 | リンク | 備考 |
|:--|:--|:--|
| **地図アプリ ＋ 実験ノート**（ブラウザだけ） | [自分の地図を開く](https://jxta.github.io/kg-grounding-proto/app/) | 地図を見て・編集し、ノードごとに実験ノートを別タブで開く。結果は地図に届く。そばにいる AI と相談しながら進める（下の「もう一つの形」） |
| **JupyterLite**（ブラウザだけ。インストール不要） | [Lab 画面](https://jxta.github.io/kg-grounding-proto/lab/index.html?path=kg_prime_factorization.ipynb) ／ [Notebook 画面](https://jxta.github.io/kg-grounding-proto/notebooks/index.html?path=kg_prime_factorization.ipynb) | 初回は Pyodide の読み込みに 20〜30 秒。全セル実行は 15 秒ほど。保存した地図はブラウザの中に残る |
| **Binder**（本物の Python カーネル） | [mybinder.org で開く](https://mybinder.org/v2/gh/jxta/kg-grounding-proto/HEAD?labpath=kg_prime_factorization.ipynb) | 起動に 1〜数分。日本語フォントは `apt.txt` で入る |
| **手元の Jupyter** | `git clone` → `pip install -r requirements.txt` → ノートを開いて上から実行 | SageMath カーネルでもそのまま動く。日本語フォントは fonts/ → パソコン → ネット の順に探す（`python tools/make_font_subset.py` で fonts/ に置いておけばオフラインでも出る） |

動かさずに読むだけなら [実行結果つきの HTML](https://jxta.github.io/kg-grounding-proto/kg_prime_factorization.html)
（道具のコードは非表示。スマホでも読める）。

## 印（接地レベル）と地図の見た目

| 印 | 意味 | 見た目 |
|:--|:--|:--|
| 0 まだ | まだ触れていない | 点線の白 |
| 1 聞いた | 先生や教科書から聞いた | 白 |
| 2 たしかめた | 実験して、自分の目で見た | 薄い灰色 |
| 3 説明できる | なぜそうなるかを、自分の言葉で言える | 濃い灰色 |
| 4 証明できる | いつでも成り立つ理由を示せる | 黒 |

薄い灰色の矢印＝教科書の道（並べ方の一案）。黒の矢印＝生徒が自分でつないだ道。
黒の **点線** ＝「借りている」印（弱い材料を使った説明）。二重枠と ↑ ＝前回の記録からの変化。

| 教科書の地図 | すべての実験のあと（実験1〜3 のあとからの変化） |
|:--:|:--:|
| ![](https://jxta.github.io/kg-grounding-proto/figures/ref_map.png) | ![](https://jxta.github.io/kg-grounding-proto/figures/map_2_final_diff.png) |

## ノートの流れ

1. **単元の地図を見る** — 14 ノード。定義／約束／方法／書き方／性質を区別。発展 2 つは点線
2. **自分の地図を作る** — 授業のあと。発展以外の 12 個に「聞いた」の印。記録 [0]
3. **実験 1〜8** — 確かめては `mark()` で印を上げ、`link()` で道をつなぐ

| 実験 | 内容 | 印が動くノード |
|:--|:--|:--|
| 1 篩 | 100 までの表を自分で消す | 素数・合成数・篩・約数と倍数 → 2 |
| 2 割っていく | 割り算で分解。2〜10000 を sympy と照合 | 素因数分解・手順・累乗 → 3 |
| 3 因数の木 | 360 を 3 通りに分けても葉は同じ。2〜2000 を無作為順で確認。1 を素数にすると壊れる | 一意性 → **2 のまま**、1は素数ではない → 3。記録 [1] |
| 4（発展）H の世界 | 4n+1 の数だけの世界では 441 = 9×49 = 21×21 | 一意性は「当たり前ではない」と分かる。印は 2 のまま、わけを更新 |
| 5 約数の個数 | 表から (指数+1) の積を予想し 1〜10000 で確認 | 約数の個数 → 3。ただし一意性（2）を **借りている** ⚠ |
| 6 平方数 | 指数がすべて偶数なら平方数 | 平方数 → 3 |
| 7（発展）ユークリッド | 2·3·…·p + 1 の表から証明を組み立てる | 素数は無限にある → **4**。その証明が使う素因数分解も 3 → 4 に上げ直す |
| 8（発展）素数レース | 4 で割って 3 余る素数と 1 余る素数の数くらべ。26861 で初めて逆転 | 素数の偏り → 2（30000 まで見ただけ） |

4. **成長を見る** — 記録 [2]。`diff` と二重枠の地図、3 枚の縮小履歴
5. **問いかけ** — `ask_me()` が地図の状態から問いを作る（規則ベース）。生成 AI 用の指示文の例も付属（API は呼ばない）
6. **保存** — `save_map()` / `load_map()`（JSON）

| 実験4：H の世界の 441 | 実験8：素数レース |
|:--:|:--:|
| ![](https://jxta.github.io/kg-grounding-proto/figures/h_trees.png) | ![](https://jxta.github.io/kg-grounding-proto/figures/prime_race.png) |

## もう一つの形：地図アプリ ＋ 実験ノート（[開く](https://jxta.github.io/kg-grounding-proto/app/)）

ノート 1 冊にすべてを入れる上の形とは別に、**地図を表示・編集する Web アプリ** を前に置き、そこから **「たしかめる」ための実験ノート** を必要なだけ別々に開く形も用意した。

```
 地図アプリ（app/）                      実験ノート（experiments/、JupyterLite）
 ┌────────────────────────┐   開く   ┌──────────────────────┐
 │ 単元の地図（教科書の道は薄く） │ ───────→ │ 01_sieve … 09_gcd_lcm │
 │ 自分の印・わけ・道       │          │ 00_scratch（自由実験）  │
 │ そばにいる AI（問うだけ）  │ ←─────── │ 最後のセル report() が  │
 │ 記録・比べる・JSON       │  結果が届く │ 結果を地図に送る       │
 └────────────────────────┘          └──────────────────────┘
```

- **地図はアプリで、実験はノートで**。ノードを押すと、そのノードを確かめる実験が並ぶ（複数あってよい。1 つのノードに 2〜3 本）。「Notebook で開く」で JupyterLite の実験ノートが別タブに開き、上から実行すると最後のセルの `report()` が結果を地図アプリに届ける（同じブラウザの中で BroadcastChannel を使う。届かなければ自分で書く）
- **AI は提案するだけ、書き換えるのは生徒**。届いた結果を見て、AI が「何を見た？ どこまで確かめた？」と聞く。生徒が「わけ」を自分の言葉で書いてから印をつける。既定の AI は規則で動く（通信なし）。設定で自分の API キーを入れると生成 AI（Anthropic API）に切り替わり、同じルール（地図を作り直さない・答えを言わない・根拠を尋ねる）のもとで、印・道・実験を **提案カード** として返す。採用ボタンを押すまで地図は変わらない
- **実験は各自の好みで**。「次に何をたしかめる？」と聞くと、弱いノードに向く短い実験から勧める。用意した実験に無いことは「自由実験」ノートで試し、結果を `report("scratch", "…")` で送る
- **地図の編集も AI と一緒に**。「一意性を説明できるにしたい」→ AI が理由を聞き、印の提案カードを出す。「素数と篩をつなぎたい」→ 道の提案カード
- 地図は JSON に書き出せ、ノート版の `my_map.json` と同じ形。ブラウザにも自動保存される

| ファイル | 用途 |
|:--|:--|
| `app/index.html` | 地図アプリ本体（1 ファイル、依存なし）。別の単元にするには先頭の `UNIT` を差し替える |
| `experiments/*.py` | 実験ノートの元（jupytext の percent 形式）。CI が `.ipynb` に変換し、動くことを確かめてから JupyterLite に入れる |
| `experiments/kg_tools.py` | 実験ノート共通の道具（篩の表・因数の木・約数の表・素数レース・H の世界）と `report()` |

## 設計の原則との対応

| 原則 | 実装 |
|:--|:--|
| (a) ノードに根拠と接地状態 | `mark(node, level, why, evidence, uses)`。上げるときは「わけ」と「どの実験か」を必ず書く |
| (b) 差分＝成長の実感 | `snapshot` / `diff` / `show_map(compare=)` / `show_history` |
| (c) 事実は定まるが矢印は選択 | 教科書の道は薄い灰色の背景。生徒の道は黒。一致度は採点しない |
| (d) 観察と証明の区別 | 「たしかめた」と「証明できる」を分ける。一意性・素数の偏りは 2 で止める。26861 の逆転 |
| (d′) 説明が何を借りているかを見せる | `uses` と `check()`：弱い材料は ⚠ と黒の点線（「〜が正しいとすれば」） |
| (e) 小さく始める | 14 ノード・1 ファイル・依存は sympy / networkx / matplotlib のみ。紙から始めてもよい |
| (f) AI は作らず問う | `ask_me()`。LLM 用指示文も「地図を作り直さない・答えを言わない・根拠を尋ねる」 |
| (g) グラフ由来の指標を目的化しない | ノード数・接地率・採点の機能を付けていない。評価は転移課題・説明課題・動機づけ尺度で |

## ファイル

| ファイル | 用途 |
|:--|:--|
| `kg_prime_factorization.ipynb` | 本体。道具のセル（先頭 5 つ）は折りたたんである |
| `PRESENTATION_GUIDE.md` | 10 分デモの順序と想定 Q&A |
| `requirements.txt` / `apt.txt` | 依存（Binder もこれを読む） |
| `tools/make_font_subset.py` | Noto Sans CJK JP のサブセット（約 1.8 MB）を `fonts/` に作る。JupyterLite・CI・CJK フォントのない環境用。その字体にない記号（≤ ⁴ ⚠ など）は DejaVu Sans で補う |
| `fonts/NotoSansCJKjp-Regular-subset.otf` | 同梱の日本語フォント（上のツールで作ったもの、約 1.8 MB）。`fonts/LICENSE-OFL.txt` はそのライセンス（SIL OFL 1.1） |
| `.github/workflows/deploy.yml` | push のたびにノートを実行し、実験ノートを生成・検証し、図・HTML・地図アプリ・JupyterLite を GitHub Pages に置く |

GitHub Pages に置かれるもの：[地図アプリ](https://jxta.github.io/kg-grounding-proto/app/)、[JupyterLite](https://jxta.github.io/kg-grounding-proto/)（実験ノートは `experiments/`）、
[図 11 枚](https://jxta.github.io/kg-grounding-proto/figures/map_2_final.png)（`figures/*.png`、モノクロ 200 dpi）、
[実行結果つき HTML](https://jxta.github.io/kg-grounding-proto/kg_prime_factorization.html)、
[実行結果つきノート](https://nbviewer.org/url/jxta.github.io/kg-grounding-proto/kg_prime_factorization_executed.ipynb)。
どれも push のたびに作り直されるので、リポジトリには入れていない（フォントだけは同梱）。

## ライセンス

コードは MIT、文章・図・教材の構成は CC BY 4.0（クレジット：Shigetoshi Yokoyama）。詳しくは [LICENSE-CONTENT.md](LICENSE-CONTENT.md)。

## 限界

- プロトタイプ。**教室では未検証**。「Aさん」の印と「わけ」は作者が書いた想定例
- 印は自己申告。先生が確認する枠は未実装（`my_map.json` のログで後から追える）
- 実験 4・7・8 は発展。単元の本体は実験 1・2・3・5・6
- 別の単元に使うには `UNIT` 辞書（道具セル）のノードと矢印を書き換える。ノードは 10〜20 個に絞る
