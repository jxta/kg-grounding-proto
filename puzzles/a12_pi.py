# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # π の散歩：数字で歩く
#
# 円周率 3.14159265… の数字を 1 つずつ読んで、0・1 なら上、2・3 なら右、4・5 なら下、6・7 なら左に 1 マス歩く。8・9 はその場で一休み。
#
# **問い：** π の数字はでたらめ？ どの数字も同じくらい出る？ 歩いた道はどんな形？
#
# **手で：** 印刷した紙の π の数字 30 個で、方眼を歩く（8・9 は休み）。各数字が何回出たか、正の字で数える。
#
# ![π の散歩](https://jxta.github.io/kg-grounding-proto/hybrid/print/pi_walk.svg)
# %% [markdown]
# > **AI と実験するときの約束**
# >
# > - 問い・手でやったこと・手の結果・予想は、きみが書く。AI は書き換えない（頼まれても、きみに書いてもらう）
# > - AI は答えや定理を先に言わない。次の一手を一つ示す
# > - AI が入れるセルは、コードなら 1 行目に `# [AI]`、文章なら先頭に（AI）と書く
# > - 照合のセル（手と機械を照らすところ）と、最後の `report()` は消さない
# > - AI の言うことは確かめる。機械が正しいとは限らないし、AI も間違える
# > - JupyterLite でも AI と話せる：コードのセルで `ai("聞きたいこと")`（先に `ai_setup("sk-…")` でキー）。提案のコードは `ai_accept()` で下に入る（動かすのはきみ）
# %%
import sys; sys.path.insert(0, "."); sys.path.insert(0, "../experiments")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *
import numpy as np, math

# 手で見た結果（自分の結果に書き換える）
hand_counts = [1, 2, 3, 5, 3, 4, 3, 1, 2, 6]    # 0〜9 が 30 個の中に出た回数（自分で数えた値に）
hand_note = "右にずれていった。9 が多かった"
hand_guess = "たくさん読めば、どの数字も同じくらいになる？"
D = 10000                                       # 機械で読む桁数

# %% [markdown]
# ## 機械で

# %%
import mpmath
mpmath.mp.dps = D + 10
digits = [int(ch) for ch in mpmath.nstr(mpmath.pi, D + 2, strip_zeros=False).replace(".", "")[:D]]
print("π の数字（最初の 40 個）：", "".join(map(str, digits[:40])))

def walk(ds):
    moves = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}       # 0・1 → 上、2・3 → 右、4・5 → 下、6・7 → 左。8・9 → 休み
    x = y = 0; xs = [0]; ys = [0]
    for d in ds:
        if d >= 8:
            continue
        dx, dy = moves[d // 2]; x += dx; y += dy; xs.append(x); ys.append(y)
    return xs, ys

fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
for ax, n in zip(axes, [30, 1000, D]):
    xs, ys = walk(digits[:n])
    ax.plot(xs, ys, color="#111111", lw=0.6 if n > 100 else 1.5); ax.plot([0], [0], "o", color="#111111", ms=4)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(f"{n} 歩", fontsize=9.5, loc="left", color="#222222")
plt.show()

# %% [markdown]
# ### 照合：30 個の数字の出た回数

# %%
machine_counts = [digits[:30].count(k) for k in range(10)]
print("手  ：", hand_counts); print("機械：", machine_counts)
print("一致" if hand_counts == machine_counts else "食い違い。数え直す（3 は最初の 1 個も数える）")

# %% [markdown]
# ## 予想を試す
#
# 予想：「たくさん読めば、どの数字も同じくらい」。D 桁で数えて、棒グラフにする。ほかの数（√2、1/7）の数字と比べる。

# %%
sqrt2 = [int(ch) for ch in mpmath.nstr(mpmath.sqrt(2), D + 2, strip_zeros=False).replace(".", "")[:D]]
one7 = [int(ch) for ch in mpmath.nstr(mpmath.mpf(1) / 7, D + 2, strip_zeros=False).replace(".", "")[:D]]
fig, axes = plt.subplots(1, 3, figsize=(13, 3.4))
for ax, (name, ds) in zip(axes, [("π", digits), ("√2", sqrt2), ("1 ÷ 7", one7)]):
    cnt = [ds.count(k) for k in range(10)]
    ax.bar(range(10), cnt, color="#111111", width=0.6); ax.set_xticks(range(10)); ax.set_ylim(0, max(cnt) * 1.15)
    ax.set_title(f"{name} の数字 {D} 個：0〜9 の回数", fontsize=9.5, loc="left", color="#222222")
plt.show()
cnt = [digits.count(k) for k in range(10)]
print("π：", cnt, "（それぞれ 1000 回くらい）。1 ÷ 7 はくり返しなので偏る")

# %% [markdown]
# **確かめること**：π の 1000 歩の道と、でたらめな数字で決めた 1000 歩の道（`np.random.default_rng(1).integers(0, 10, 1000)`）は見分けがつく？
#
# ここから先の問い：0〜9 を 10 方向（36° ずつ）にすると、道はどう変わる？ 数字を色にして 100 × 100 の絵にすると？

# %%
report("a12_pi", f"π の数字 {D} 個で歩いた。0〜9 の回数は {cnt}（ほぼ同じ）。1÷7 は偏る",
       data={"D": D, "counts": cnt}, hand={"counts": hand_counts, "note": hand_note, "guess": hand_guess}, params={"D": D}, notebook="a12_pi.ipynb")
