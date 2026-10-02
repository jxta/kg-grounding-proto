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
# # 余りの模様：掛け算表を m で割った余りで色分け
#
# 掛け算表（i × j）を作り、m で割った余りで色を決める。m を変えると、模様がまるで違う。
#
# **問い：** m が素数のときと、そうでないときで、模様はどう違う？ 対称な線はどこにある？
#
# **手で：** 印刷した 10 × 10 の掛け算表を、5 で割った余り（0, 1, 2, 3, 4）で 5 色にぬる。
#
# ![掛け算表の色ぬり](https://jxta.github.io/kg-grounding-proto/hybrid/print/mod_table_10.svg)
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
hand_m = 5
hand_note = "5 の倍数の行と列が全部同じ色（余り 0）。斜めに同じ色が並ぶ"
hand_guess = "m が素数だと、余り 0 は m の倍数の行と列だけ。m が合成数だと、ほかにも余り 0 が出る"
MS = [5, 6, 7, 8, 12, 13]                  # 機械で試す m
SIZE = 60                                  # 表の大きさ（1〜SIZE）

# %% [markdown]
# ## 機械で

# %%
def mod_table(size, m, ax, cmap="tab20", title=None):
    i = np.arange(1, size + 1)
    T = np.outer(i, i) % m
    ax.imshow(T, cmap=cmap, vmin=0, vmax=max(m - 1, 1), interpolation="nearest"); ax.axis("off")
    ax.set_title(title or f"i × j を {m} で割った余り（1〜{size}）", fontsize=9.5, loc="left", color="#222222")
    return T

fig, axes = plt.subplots(2, 3, figsize=(13, 8.4))
for ax, m in zip(axes.flat, MS):
    mod_table(SIZE, m, ax)
plt.show()

# %% [markdown]
# ### 照合：手の 10 × 10（余り 0 のマスの数）

# %%
T = np.outer(np.arange(1, 11), np.arange(1, 11)) % hand_m
zeros = int((T == 0).sum())
print(f"m = {hand_m} の 10 × 10 で、余り 0 のマス：機械 {zeros} 個（手で数えて照らす）")
fig, ax = plt.subplots(figsize=(4, 4))
mod_table(10, hand_m, ax, title=f"手と同じ 10 × 10、m = {hand_m}")
for r in range(10):
    for c in range(10):
        ax.text(c, r, str((r + 1) * (c + 1)), ha="center", va="center", fontsize=6, color="white")
plt.show()

# %% [markdown]
# ## 予想を試す
#
# 予想：「m が素数だと、余り 0 は m の倍数の行と列だけ」。m = 2〜16 で、余り 0 のマスの数を数え、「m の倍数の行と列だけ」なら何個になるかと比べる。

# %%
print(f"{'m':>3} {'余り 0 の数':>8} {'倍数の行・列だけなら':>12} {'素数？':>5}")
for m in range(2, 17):
    T = np.outer(np.arange(1, SIZE + 1), np.arange(1, SIZE + 1)) % m
    z = int((T == 0).sum()); q = SIZE // m
    only = 2 * q * SIZE - q * q
    print(f"{m:>3} {z:>8} {only:>12} {'素数' if sympy.isprime(m) else '':>5}  {'一致' if z == only else '余分がある'}")

# %% [markdown]
# ### パスカルの三角形にも色を（m で割った余り）

# %%
def pascal_mod(rows, m, ax, cmap="tab20"):
    T = np.zeros((rows, 2 * rows), dtype=int) - 1
    row = [1]
    for r in range(rows):
        for c, v in enumerate(row):
            T[r, rows - r + 2 * c - 1] = v % m
        row = [1] + [(row[i] + row[i + 1]) % m for i in range(len(row) - 1)] + [1]
    img = np.ma.masked_less(T, 0)
    ax.imshow(img, cmap=cmap, vmin=0, vmax=max(m - 1, 1), interpolation="nearest", aspect=2); ax.axis("off")
    ax.set_title(f"パスカルの三角形を {m} で割った余り（{rows} 行）", fontsize=9.5, loc="left", color="#222222")
fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
for ax, m in zip(axes, [3, 5, 7]):
    pascal_mod(81, m, ax)
plt.show()

# %% [markdown]
# **確かめること**：m = 6 の表で「余分な余り 0」はどのマス？（2 × 3 のように、m の倍数でない数同士の積が m の倍数になるところ）
#
# ここから先の問い：i + j（足し算表）を m で割った余りだと？ 色の順を hsv にすると？（`cmap="hsv"`）

# %%
report("b5_mod_table", f"i × j を m で割った余りの模様。m が素数だと余り 0 は m の倍数の行・列だけ、合成数だと余分が出る（{SIZE} まで確認）",
       data={"SIZE": SIZE, "MS": MS}, hand={"m": hand_m, "note": hand_note, "guess": hand_guess}, params={"SIZE": SIZE, "MS": MS}, notebook="b5_mod_table.ipynb")
