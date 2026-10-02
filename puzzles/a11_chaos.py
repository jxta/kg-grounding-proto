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
# # サイコロで三角形：でたらめから模様
#
# 三角形の 3 つの角に、サイコロの目を割り当てる（1・2 → A、3・4 → B、5・6 → C）。点を 1 つ打ち、サイコロを振って、出た角との **真ん中** に次の点を打つ。くり返す。
#
# **問い：** でたらめに打った点は、三角形いっぱいに散らばる？ 何か模様になる？
#
# **手で：** 印刷した三角形の紙で、30 回くり返す。点はどこに集まる？ 入らない場所はある？
#
# ![サイコロの三角形](https://jxta.github.io/kg-grounding-proto/hybrid/print/chaos_triangle.svg)
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
hand_points = 30
hand_note = "真ん中あたりに点が入らない。三つの角の近くに集まる"
hand_guess = "何千回やっても、真ん中の逆三角形には入らない？"
N = 20000                             # 機械で打つ点の数

# %% [markdown]
# ## 機械で

# %%
rng = np.random.default_rng(0)
A, B, C = np.array([0.0, 0.0]), np.array([1.0, 0.0]), np.array([0.5, math.sqrt(3) / 2])
corners = np.array([A, B, C])
pts = np.zeros((N, 2)); p = np.array([0.3, 0.2])
for i in range(N):
    p = (p + corners[rng.integers(0, 3)]) / 2          # サイコロ：出た角との真ん中へ
    pts[i] = p
fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
for ax, n in zip(axes, [30, 1000, N]):
    ax.plot(pts[:n, 0], pts[:n, 1], ".", color="#111111", ms=1.2 if n > 100 else 4)
    ax.plot(corners[[0, 1, 2, 0], 0], corners[[0, 1, 2, 0], 1], color="#bbbbbb", lw=0.8)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(f"{n} 回", fontsize=9.5, loc="left", color="#222222")
plt.show()

# %% [markdown]
# ### 照合：真ん中の逆三角形に入った点の数
#
# 真ん中の逆三角形（3 辺の中点を結んだ三角形）に、点はいくつ入った？（最初の数回は出発点の影響で入ることがある）

# %%
mid = (A + B) / 2, (B + C) / 2, (C + A) / 2
def inside(p, t):
    (x1, y1), (x2, y2), (x3, y3) = t
    d1 = (p[0] - x2) * (y1 - y2) - (x1 - x2) * (p[1] - y2)
    d2 = (p[0] - x3) * (y2 - y3) - (x2 - x3) * (p[1] - y3)
    d3 = (p[0] - x1) * (y3 - y1) - (x3 - x1) * (p[1] - y1)
    return (d1 > 0) == (d2 > 0) == (d3 > 0)
hit = sum(1 for q in pts[10:] if inside(q, mid))
print("手　：", hand_note)
print(f"機械：{N} 回のうち、11 回目以降に真ん中の逆三角形に入った点：{hit} 個")

# %% [markdown]
# ## 予想を試す
#
# 予想：「真ん中には入らない」。角を 4 つ（正方形）にすると？ 「同じ角を 2 回続けて選ばない」というきまりにすると？

# %%
def chaos(corners, n, rule=None, seed=0):
    rng = np.random.default_rng(seed); k = len(corners)
    pts = np.zeros((n, 2)); p = corners.mean(axis=0); last = -1
    for i in range(n):
        j = rng.integers(0, k)
        if rule == "same" :
            while j == last:
                j = rng.integers(0, k)
        last = j
        p = (p + corners[j]) / 2; pts[i] = p
    return pts
sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=float)
fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
for ax, (c, rule, t) in zip(axes, [(corners, None, "三角形"), (sq, None, "正方形"), (sq, "same", "正方形・同じ角を続けない")]):
    q = chaos(c, N, rule)
    ax.plot(q[:, 0], q[:, 1], ".", color="#111111", ms=0.8); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(t, fontsize=9.5, loc="left", color="#222222")
plt.show()

# %% [markdown]
# **確かめること**：三角形の模様は、ノート a3「パスカルの三角形の色ぬり」と同じ形？ 並べて見る。
#
# ここから先の問い：角との「真ん中」でなく「3 分の 1」のところに打つと？（`/ 2` を変える）。五角形では？

# %%
report("a11_chaos", f"サイコロで角との真ん中へ {N} 回。三角形はパスカルの色ぬりと同じ模様。真ん中の逆三角形に入った点 {hit} 個",
       data={"N": N, "mid_hits": hit}, hand={"points": hand_points, "note": hand_note, "guess": hand_guess}, params={"N": N}, notebook="a11_chaos.ipynb")
