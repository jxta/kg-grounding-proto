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
# # パスカルの三角形の色ぬり
#
# 上から 1、その下は両どなりの和。数の三角形の、奇数のマスだけ黒くぬると、何が見える？
#
# **問い：** 奇数だけぬると、どんな模様？ 3 の倍数「でない」マスをぬると？ 各行の黒いマスの数には決まりがある？
#
# **手で：** 印刷した 16 行の三角形（または Miro の三角形）で、奇数を黒くぬる。各行の黒の数を数える。
#
# ![パスカルの三角形 16 行](https://jxta.github.io/kg-grounding-proto/hybrid/print/pascal_16.svg)
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
hand_black = [1, 2, 2, 4, 2, 4, 4, 8]      # 0 行目から順に、黒（奇数）のマスの数（数えたところまで）
hand_note = "大きい三角の中に、白い逆三角がくり返し出てきた"
hand_guess = "黒の数は 1, 2, 4, 8 しか出てこない？"
R = 64                                     # 機械で描く行数
N = 128                                    # 予想を試す行数

# %% [markdown]
# ## 機械で

# %%
def pascal(rows):
    T = np.zeros((rows, rows), dtype=object)
    for r in range(rows):
        T[r, 0] = 1
        for c in range(1, r + 1):
            T[r, c] = T[r - 1, c - 1] + (T[r - 1, c] if c <= r - 1 else 0)
    return T

def paint(rows, mod, keep=lambda v: v != 0, ax=None, title=None):
    """rows 行。T mod mod が keep を満たすマスを黒に"""
    T = pascal(rows)
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(6, 5.3))
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-0.5, rows); ax.set_ylim(-rows - 0.5, 1)
    for r in range(rows):
        for c in range(r + 1):
            if keep(int(T[r, c]) % mod):
                ax.add_patch(plt.Rectangle((c + (rows - r) / 2 - 0.5, -r - 0.5), 1, 1, fc="#111111", ec="none"))
    ax.set_title(title or f"{rows} 行、{mod} で割った余りが 0 でないマスを黒", fontsize=9, loc="left", color="#222222")
    if own:
        plt.show()
    return T

T = paint(R, 2, title=f"{R} 行、奇数を黒")

# %% [markdown]
# ### 照合：各行の黒の数

# %%
machine_black = [sum(1 for c in range(r + 1) if int(T[r, c]) % 2 == 1) for r in range(len(hand_black))]
print("手  ：", hand_black); print("機械：", machine_black)
print("一致" if hand_black == machine_black else "食い違い。どの行？ 手の三角形を見直す")

# %% [markdown]
# ### 余りを変えると？

# %%
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
for ax, mod in zip(axes, [2, 3, 5]):
    paint(R, mod, ax=ax)
plt.show()

# %% [markdown]
# ## 予想を試す
#
# 予想：「奇数の数は 1, 2, 4, 8, … の形しか出ない」。N 行まで数えて、出てきた数の種類を並べる。行番号（0 から）を 2 進法で書いたときの 1 の数と比べてみる。

# %%
T = pascal(N)
blacks = [sum(1 for c in range(r + 1) if int(T[r, c]) % 2 == 1) for r in range(N)]
kinds = sorted(set(blacks))
print("出てきた数の種類：", kinds)
print("すべて 2 のべき？", all(k & (k - 1) == 0 for k in kinds))
print(f"{'行':>4} {'黒':>4} {'行番号を 2 進法で':>16} {'1 の数':>6}")
for r in [1, 2, 3, 4, 5, 6, 7, 15, 31, 100]:
    print(f"{r:>4} {blacks[r]:>4} {bin(r)[2:]:>16} {bin(r).count('1'):>6}")

# %% [markdown]
# **確かめること**：行 7 と行 15 の黒の数を、手の三角形で数え直す。
#
# ここから先の問い：3 の倍数でないマスをぬった模様は、何回くり返している？ 素数 p で割った余りの模様は、どれも似た形？

# %%
report("a3_pascal", f"奇数のマスの数は {N} 行まで {kinds}（2 のべきだけ）。行番号の 2 進法の 1 の数と対応",
       data={"rows": N, "kinds": kinds}, hand={"black": hand_black, "note": hand_note, "guess": hand_guess},
       params={"R": R, "N": N}, notebook="a3_pascal.ipynb")
