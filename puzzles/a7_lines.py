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
# # 直線で分けて、2 色でぬる
#
# 紙に直線を何本か引く。紙はいくつの「部屋」に分かれる？ となり合う部屋が必ず違う色になるように、2 色だけでぬれる？
#
# **問い：** n 本の直線で、部屋は最大いくつ？ 2 色でぬれるのは偶然？
#
# **手で：** 白い紙に直線を 1 本、2 本、…、5 本と増やしながら、部屋の数を数える（直線はどれも交わるように、3 本が 1 点で交わらないように）。5 本のとき、2 色でぬる。
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
hand_regions = [2, 4, 7, 11, 16]     # 直線 1〜5 本のときの部屋の数（自分で数えた値に）
hand_two_color = True                # 2 色でぬれた？
hand_note = "増え方が 2, 3, 4, 5 と増えていく"
hand_guess = "n 本目を引くと、部屋は n 個増える？"
N = 12                               # 機械で引く直線の本数

# %% [markdown]
# ## 機械で
#
# 直線を無作為に引いて、交点を数える。部屋の数は「1 + 直線の本数 + 交点の数」で出る（3 本以上が 1 点で交わらないとき）。

# %%
rng = np.random.default_rng(7)
def random_lines(n):
    """y = a x + b の形で n 本（傾きも切片も無作為）"""
    return [(rng.uniform(-2, 2), rng.uniform(-1, 1)) for _ in range(n)]

def crossings(lines):
    pts = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            a1, b1 = lines[i]; a2, b2 = lines[j]
            if abs(a1 - a2) > 1e-9:
                x = (b2 - b1) / (a1 - a2); pts.append((x, a1 * x + b1))
    return pts

def paint(lines, ax=None, title=None):
    """2 色ぬり：点ごとに「何本の直線より上にあるか」を数え、偶数なら白、奇数なら灰色"""
    xs = np.linspace(-1.5, 1.5, 600); ys = np.linspace(-1.5, 1.5, 600)
    X, Y = np.meshgrid(xs, ys)
    above = np.zeros_like(X, dtype=int)
    for a, b in lines:
        above += (Y > a * X + b)
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.imshow(above % 2, extent=(-1.5, 1.5, -1.5, 1.5), origin="lower", cmap="gray_r", vmin=0, vmax=3, interpolation="nearest")
    for a, b in lines:
        ax.plot(xs, a * xs + b, color="#111111", lw=0.8)
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title or f"直線 {len(lines)} 本、2 色ぬり", fontsize=9.5, loc="left", color="#222222")
    if own:
        plt.show()

lines = random_lines(N)
paint(lines)
print(f"直線 {N} 本、交点 {len(crossings(lines))} 個 → 部屋は 1 + {N} + {len(crossings(lines))} = {1 + N + len(crossings(lines))}")

# %% [markdown]
# ### 照合：手で数えた部屋の数と、機械の式

# %%
print(f"{'本数':>4} {'手':>4} {'1 + n + 交点':>12}")
for n, h in enumerate(hand_regions, start=1):
    m = 1 + n + n * (n - 1) // 2          # どの 2 本も交わるとき、交点は n(n−1)/2 個
    print(f"{n:>4} {h:>4} {m:>12}  {'一致' if h == m else '食い違い。平行な線や、3 本が 1 点で交わるところがない？'}")

# %% [markdown]
# ## 予想を試す
#
# 予想：「n 本目を引くと、部屋は n 個増える」。本数を 1〜N まで変えて表にする。2 色でぬれるかも機械で（2 色ぬりの絵に、同じ色が接しているところはある？）。

# %%
print(f"{'本数 n':>6} {'部屋（最大）':>10} {'増えた数':>8}")
prev = 1
for n in range(1, N + 1):
    r = 1 + n + n * (n - 1) // 2
    print(f"{n:>6} {r:>10} {r - prev:>8}"); prev = r
fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
for ax, n in zip(axes, [3, 6, 20]):
    paint(random_lines(n), ax=ax)
plt.show()
print("2 色ぬりの決まり：ある点から見て「上にある直線の本数」が偶数か奇数かで色を決める。直線を 1 本またぐと本数が 1 変わるので、となりは必ず違う色になる")

# %% [markdown]
# **確かめること**：手でぬった 5 本の絵で、「上にある直線の本数」を 2 つの部屋で数え、色と合っているか見る。
#
# ここから先の問い：直線でなく円を何個か重ねても 2 色でぬれる？（丸をいくつか描いて試す）

# %%
report("a7_lines", f"直線 n 本で部屋は 1 + n + n(n−1)/2。{N} 本で {1 + N + N * (N - 1) // 2} 部屋。2 色ぬりは「上にある直線の本数」の偶奇",
       data={"N": N, "regions": [1 + n + n * (n - 1) // 2 for n in range(1, N + 1)]}, hand={"regions": hand_regions, "two_color": hand_two_color, "note": hand_note, "guess": hand_guess},
       params={"N": N}, notebook="a7_lines.ipynb")
