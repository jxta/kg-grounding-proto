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
# # 色の糸かけ：k ごとに色を変えて重ねる
#
# ノート a1 の糸かけに色をつける。k ごとに色を変えて重ねると曼荼羅、線の順番で色を変えると虹の糸かけ。
#
# **問い：** 同じ釘の数でも、k の組み合わせで模様はどう変わる？ 色の順番は何で決める？（線の順？ 糸の本数？）
#
# **手で：** 36 釘の盤に、k = 5, 7, 11 を違う色の糸（線）で重ねる。どの k がいちばん外側に見える？
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
from matplotlib import colormaps

# 手で見た結果（自分の結果に書き換える）
hand_ks = [5, 7, 11]                       # 重ねた k と、その順
hand_note = "k が小さいほど外側の輪、大きいほど内側に空く穴が小さくなった"
hand_guess = "内側の穴の大きさは k で決まる？ k が 18 に近いほど穴が小さい？"
n = 36
KS = [5, 7, 11, 13]                        # 機械で重ねる k
CMAP = "twilight"                          # 色の決め方（viridis, plasma, twilight, hsv, tab10 …）

# %% [markdown]
# ## 機械で

# %%
def nails(n):
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False) + np.pi / 2
    return np.cos(ang), np.sin(ang)

def itokake_color(n, k, ax, color=None, cmap=None, lw=1.0, alpha=0.9):
    """k ずつ。color が無く cmap があれば、線を引く順番で色を変える（虹の糸かけ）"""
    x, y = nails(n)
    cm = colormaps[cmap] if cmap else None
    seen = set(); order = 0
    for start in range(n):
        if start in seen:
            continue
        i = start
        while True:
            j = (i + k) % n
            c = color if color else cm(order / n)
            ax.plot([x[i], x[j]], [y[i], y[j]], color=c, lw=lw, alpha=alpha)
            seen.add(i); order += 1; i = j
            if i == start:
                break
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-1.08, 1.08); ax.set_ylim(-1.08, 1.08)

fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
cm = colormaps["tab10"]
for i, k in enumerate(hand_ks):
    itokake_color(n, k, axes[0], color=cm(i), lw=1.2)
axes[0].set_title(f"手と同じ：k = {hand_ks}（k ごとに色）", fontsize=9.5, loc="left", color="#222222")
for i, k in enumerate(KS):
    itokake_color(n, k, axes[1], color=colormaps[CMAP](0.15 + 0.7 * i / max(1, len(KS) - 1)), lw=1.0)
axes[1].set_title(f"k = {KS} を {CMAP} の色で", fontsize=9.5, loc="left", color="#222222")
itokake_color(n, 7, axes[2], cmap="hsv", lw=1.3)
axes[2].set_title("k = 7 を、線の順番で虹に", fontsize=9.5, loc="left", color="#222222")
plt.show()

# %% [markdown]
# ### 照合：内側の穴の大きさ
#
# k ずつの糸は、中心から一定の距離より内側には入らない。その距離（穴の半径）を、手の絵と機械で比べる。

# %%
print(f"{'k':>4} {'穴の半径（機械）':>12}  手で見た順（外側→内側）：{hand_ks}")
for k in sorted(set(hand_ks + KS)):
    r = abs(math.cos(math.pi * k / n))         # 弦の中点までの距離 = cos(πk/n)
    print(f"{k:>4} {r:>12.3f}")
print("→ 穴の半径は cos(πk/n)。k が n/2（ここでは 18）に近いほど穴が小さい。手の見え方と合っている？")

# %% [markdown]
# ## 予想を試す
#
# 予想：「内側の穴の大きさは k で決まる」。k を 1〜17 まで変えて、穴の半径を並べる。同じ穴になる k の組はある？（k と n − k）

# %%
fig, axes = plt.subplots(2, 6, figsize=(13, 4.8))
for ax, k in zip(axes.flat, range(1, 13)):
    itokake_color(n, k, ax, cmap="viridis", lw=0.8)
    ax.set_title(f"k = {k}　穴 {abs(math.cos(math.pi * k / n)):.2f}", fontsize=8.5, loc="left", color="#222222")
plt.show()

# %% [markdown]
# ### 掛け算の糸かけに色を（n → 2n、線の順番で色）

# %%
fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
for ax, (k, cmap) in zip(axes, [(2, "plasma"), (3, "viridis"), (5, "twilight")]):
    m = 200; x, y = nails(m); cm = colormaps[cmap]
    for i in range(m):
        j = (k * i) % m
        ax.plot([x[i], x[j]], [y[i], y[j]], color=cm(i / m), lw=0.5)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(f"n → {k}n、{cmap}", fontsize=9.5, loc="left", color="#222222")
plt.show()

# %% [markdown]
# **確かめること**：穴の半径が k = 7 と k = 29 で同じになるのはなぜ？（29 = 36 − 7。逆回りに 7 ずつ）
#
# ここから先の問い：色を「糸の本数（gcd）」で決めると、どんな絵になる？ 自分の好きな CMAP と KS で 1 枚作って、右クリックで保存する。

# %%
report("b1_color_itokake", f"釘 {n} 本に k = {KS} を {CMAP} の色で重ねた。穴の半径は cos(πk/n)",
       data={"n": n, "KS": KS, "cmap": CMAP, "hole": {str(k): round(abs(math.cos(math.pi * k / n)), 3) for k in KS}},
       hand={"ks": hand_ks, "note": hand_note, "guess": hand_guess}, params={"n": n, "KS": KS, "CMAP": CMAP}, notebook="b1_color_itokake.ipynb")
