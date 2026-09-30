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
# # 正方形を並べて、らせんを描く
#
# 1, 1, 2, 3, 5, 8, 13, … と、前の 2 つの和で正方形を大きくして並べる。できた長方形の縦と横の比は？ 角をつないで四分円を描くと、らせんになる。
#
# **問い：** 長方形の「横 ÷ 縦」はどう変わる？ ある数に近づく？ その数は何？
#
# **手で：** 方眼紙に 1, 1, 2, 3, 5, 8 の正方形を並べて、できた長方形の横と縦を測り、横 ÷ 縦 を計算する。
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
hand_ratios = {"2×1": 2.0, "3×2": 1.5, "5×3": 1.67, "8×5": 1.6, "13×8": 1.63}   # 横 ÷ 縦（自分の計算）
hand_note = "だんだん 1.6 くらいに近づいた"
hand_guess = "1.6 と 1.7 の間の数に落ち着く。分数では書けない？"
K = 20                                                                           # 機械で何番目まで計算するか

# %% [markdown]
# ## 機械で

# %%
fib = [1, 1]
while len(fib) < K:
    fib.append(fib[-1] + fib[-2])

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.set_aspect("equal"); ax.axis("off")
x0, y0, x1, y1 = 0, 0, 0, 0                    # いままでの長方形
for i in range(8):
    d = (i + 3) % 4                            # 置く向き：3 = 下（最初）、0 = 右、1 = 上、2 = 左、3 = 下 …
    if i == 0:
        X, Y, s = 0, 0, 1
    elif d == 0:
        s = y1 - y0; X, Y = x1, y0             # 右に、いまの高さの正方形
    elif d == 1:
        s = x1 - x0; X, Y = x0, y1             # 上に、いまの幅の正方形
    elif d == 2:
        s = y1 - y0; X, Y = x0 - s, y0         # 左に
    else:
        s = x1 - x0; X, Y = x0, y0 - s         # 下に
    x0, y0, x1, y1 = min(x0, X), min(y0, Y), max(x1, X + s), max(y1, Y + s)
    ax.add_patch(plt.Rectangle((X, Y), s, s, fc="#f2f2f2", ec="#111111", lw=0.8))
    ax.text(X + s / 2, Y + s / 2, str(s), ha="center", va="center", fontsize=8)
    # 四分円：向きごとに、中心の角と角度の範囲が決まる
    center, th0 = {0: ((X, Y + s), -90), 1: ((X, Y), 0), 2: ((X + s, Y), 90), 3: ((X + s, Y + s), 180)}[d]
    th = np.radians(np.linspace(th0, th0 + 90, 30))
    ax.plot(center[0] + s * np.cos(th), center[1] + s * np.sin(th), color="#111111", lw=1.2)
ax.set_xlim(x0 - 1, x1 + 1); ax.set_ylim(y0 - 1, y1 + 1)
ax.set_title("1, 1, 2, 3, 5, 8, 13, 21 の正方形と、四分円をつないだらせん", fontsize=9, loc="left", color="#222222")
plt.show()

# %% [markdown]
# ### 照合：横 ÷ 縦

# %%
print(f"{'長方形':>8} {'手':>6} {'機械':>10}")
for key, h in hand_ratios.items():
    a, b = map(int, key.split("×"))
    print(f"{key:>8} {h:>6} {a / b:>10.4f}  {'ほぼ一致' if abs(h - a / b) < 0.02 else '食い違い。測り直す'}")

# %% [markdown]
# ## 予想を試す
#
# 予想：「ある数に落ち着く」。K 番目まで比を出す。となり同士の比の差がどう小さくなるかも見る。

# %%
ratios = [fib[i + 1] / fib[i] for i in range(K - 1)]
print(f"{'i':>3} {'F(i+1)/F(i)':>12} {'前との差':>10}")
for i, r in enumerate(ratios):
    print(f"{i+1:>3} {r:>12.6f} {'' if i == 0 else f'{r - ratios[i-1]:>+10.6f}'}")
fig, ax = plt.subplots(figsize=(7, 2.6))
ax.plot(range(1, K), ratios, "o-", color="#111111", ms=3, lw=0.8)
ax.set_xlabel("i"); ax.set_ylabel("比"); ax.set_title("比は、上下しながら一つの数に近づく", fontsize=9, loc="left", color="#222222")
plt.show()

# %% [markdown]
# ### その数は何？ 候補を照らす
#
# 落ち着く先を x とすると、比の作り方から x = 1 + 1/x が成り立ちそう（前の比の逆数に 1 を足す）。これを満たす x を、いくつかの候補で試す。

# %%
cands = {"1.6": 1.6, "8/5": 8 / 5, "5/3": 5 / 3, "(1+√5)/2": (1 + 5 ** 0.5) / 2}
print(f"{'候補':>10} {'値':>10} {'1 + 1/x':>10} {'差':>10}")
for name, v in cands.items():
    print(f"{name:>10} {v:>10.6f} {1 + 1 / v:>10.6f} {abs(v - (1 + 1 / v)):>10.6f}")
print("最後の比：", ratios[-1])

# %% [markdown]
# **確かめること**：x = 1 + 1/x を満たす x は、x² = x + 1 の解。二次方程式を習っていれば解いて照らす。習っていなくても、√5 を電卓で出して候補の値を確かめられる。
#
# ここから先の問い：最初の 2 つを 1, 1 ではなく 2, 5 にしても、比は同じ数に近づく？

# %%
report("a5_golden", f"{K} 番目までの比は {ratios[-1]:.6f} に近づく。候補 (1+√5)/2 = {(1 + 5 ** 0.5) / 2:.6f} と差 {abs(ratios[-1] - (1 + 5 ** 0.5) / 2):.6f}",
       data={"K": K, "last_ratio": ratios[-1], "fib": fib}, hand={"ratios": hand_ratios, "note": hand_note, "guess": hand_guess}, params={"K": K}, notebook="a5_golden.ipynb")
