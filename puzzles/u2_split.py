# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 単元パズル2　分けるカード — 最後に残るカードは同じ？
#
# カードに 60 と書く。60 を「2 つの数のかけ算」に分けて、2 枚のカードにする（6 と 10、など）。分けたカードをまた分ける。
# もう分けられないカードだけになったら終わり。**分け方を変えると、最後のカードの組は変わる？**
#
# ## 手で（物理的な実験）
#
# **用意するもの**：紙のカード 20 枚くらい、鉛筆。
#
# **やり方**：60 のカードから始めて、最後まで分ける。終わったら並べて写す。もう一度 60 から、**ちがう分け方**で。72 でも 2 通り。
# それから、「1 × 60」に分けるのも許してみる。どうなる？
#
# **記録すること**：それぞれの最後のカードの組。1 を許したときに起きたこと。

# %% [markdown]
# > **AI と実験するときの約束**（ノートの中の AI（Mynerva など）と、きみへ）
# > - 問い・手でやったこと・手の結果・予想は、きみが書く。AI は書き換えない
# > - AI は答えや定理を先に言わない。「何が見えた？」「どこまで確かめた？」と聞く
# > - AI が入れるセルは、コードなら 1 行目に `# [AI]`、文章なら先頭に `（AI）` と書く。誰が書いたか分かるように
# > - 手の結果と機械の結果を照らすセルと、最後の `report()` は消さない
# > - AI の言うことは確かめる。機械が正しいとは限らないし、AI も間違える
# > - JupyterLite でも AI と話せる：コードのセルで `ai("聞きたいこと")`（先に `ai_setup("sk-…")` でキー）。AI は実行したセルとノートの文章を読み、次の一手を示す。コードは提案だけ（貼るのはきみ）

# %%
import sys; sys.path.insert(0, "."); sys.path.insert(0, "../experiments")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *

# 手で見た結果（自分の結果に書き換える）
hand = {"60 = 6 × 10 から": [2, 3, 2, 5], "60 = 4 × 15 から": [2, 2, 3, 5], "72 = 8 × 9 から": [2, 2, 2, 3, 3], "72 = 6 × 12 から": [2, 3, 2, 2, 3]}
hand_one = "1 × 60 に分けると、60 のカードがまた出てきて、いつまでも終わらなかった"

# %% [markdown]
# ## 機械で

# %%
for label, cards in hand.items():
    n = int(label.split()[0])
    m = sorted(leaves(factor_tree(n)))
    print(f"{label}：手 {sorted(cards)}／機械 {m} → {'一致' if sorted(cards) == m else '食い違い'}")

t1 = factor_tree(60, splits={60: (6, 10), 6: (2, 3), 10: (2, 5)})
t2 = factor_tree(60, splits={60: (4, 15), 4: (2, 2), 15: (3, 5)})
t3 = factor_tree(60, splits={60: (2, 30), 30: (3, 10), 10: (2, 5)})
show_trees([t1, t2, t3], ["60 = 6 × 10 から", "60 = 4 × 15 から", "60 = 2 × 30 から"])

# 72 と 360 を、でたらめな順で分けた木
rng = random.Random(1)
show_trees([factor_tree(72, rng=rng), factor_tree(72, rng=rng)], ["72（でたらめな順 1）", "72（でたらめな順 2）"])
show_trees([factor_tree(360, rng=rng), factor_tree(360, rng=rng)], ["360（でたらめな順 1）", "360（でたらめな順 2）"])

# %% [markdown]
# **見るところ**：黒いカード（もう分けられない数＝素数）の組は、分け方によらず同じ。まとめて書くと 60 = 2² × 3 × 5。
#
# 1 を許すと終わらない。だから「1 は素数に入れない」と約束する（約束であって、発見ではない）。

# %%
print("60 =", factorization_str(60), "　72 =", factorization_str(72), "　360 =", factorization_str(360))

# 1 を許した木：1 × 60 → 1 × 1 × 60 → …
seq = ["60"]
for k in range(1, 5):
    seq.append(" × ".join(["1"] * k + ["60"]))
print("1 を許すと：", "  →  ".join(seq), " →  …（終わらない）")
endless_tree(60, depth=5)

# 葉をそろえて書いたもの（2² × 3 × 5）を、棒で見る：素数ごとに何個あるか
exponent_bars([60, 72, 360])

# %% [markdown]
# ## 予想を試す
#
# 「どんな順で分けても、最後のカードの組は同じ」——N までの全部の数で、でたらめな順に分けて確かめる。

# %%
guess = "どんな順で分けても、最後のカードの組は同じ"
N = 3000
rng = random.Random(0)
counter = [n for n in range(2, N + 1) if sorted(leaves(factor_tree(n, rng=rng))) != sorted(leaves(factor_tree(n, rng=rng)))]
print(f"予想「{guess}」の反例（2〜{N}）：", counter[:10] or "なし")
print("ただし：反例がないことと、いつでも成り立つことは別。「ただ一通り」の理由は、あとで出会う")

# %%
report("u2_split",
       f"60 と 72 を手で 2 通りずつ分けたら、最後のカードの組は機械と{'一致' if all(sorted(c) == sorted(leaves(factor_tree(int(l.split()[0])))) for l, c in hand.items()) else '食い違い'}。1 を許すと終わらない。予想「{guess}」は 2〜{N} で反例なし",
       data={"leaves_60": sorted(leaves(factor_tree(60))), "leaves_72": sorted(leaves(factor_tree(72))), "N": N, "counter": counter[:10], "str_60": factorization_str(60)},
       hand={"trees": hand, "one": hand_one},
       params={"N": N},
       notebook="u2_split.ipynb")
