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
# # しきつめ：どんな四角形でも、すき間なく並べられる？
#
# 正方形やタイルはしきつめられる。では、四つの辺の長さも角もばらばらな四角形は？
#
# **問い：** どんな四角形でも平面をすき間なくしきつめられる？ できるなら、どんな並べ方？ 三角形は？ 五角形は？
#
# **手で：** 好きな四角形を 1 つ描いて、同じものを 8 枚切る（Miro なら台形の部品を使う）。回したり、すべらせたりして、すき間なく並べる。1 つの点のまわりに、どの角が集まったか記録する。
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
hand_ok = True                                          # しきつめられた？
hand_corner = "1 つの点のまわりに、四角形の 4 つの角が 1 回ずつ集まった"
hand_angles = [70, 110, 95, 85]                          # 自分の四角形の 4 つの角（分度器で）
hand_guess = "4 つの角の和が 360 度だから、1 点に全部集めればすき間ができない"
quad = [(0, 0), (4, 0.6), (3.2, 3.0), (0.6, 2.2)]        # 自分の四角形の頂点（方眼の座標で。書き換える）
N = 6                                                    # 機械で並べる枚数（縦横 N × N）

# %% [markdown]
# ## 機械で
#
# 辺の真ん中の点を中心に 180° 回すと、となりの四角形になる。この 2 枚を、対角線の向きにずらして並べる。

# %%
def tile_quad(P, N, ax=None):
    """四角形 P（4 頂点）と、辺 BC の中点で 180° 回した相棒 Q を、対角線の向きにずらして並べる"""
    P = np.array(P, dtype=float)
    A, B, C, D = P
    Q = (B + C) - P                # 辺 BC の中点を中心に 180° 回した四角形（頂点の順は逆回り）
    v1, v2 = C - A, D - B          # ずらすベクトル：2 本の対角線（中点で回す操作を 2 回続けると、この平行移動になる）
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_aspect("equal"); ax.axis("off")
    for i in range(-N, N + 1):
        for j in range(-N, N + 1):
            s = i * v1 + j * v2
            for poly, fc in ((P, "#ffffff"), (Q, "#cfcfcf")):
                ax.add_patch(plt.Polygon(poly + s, closed=True, fc=fc, ec="#111111", lw=0.8))
    ax.set_xlim(-N * 2.0, N * 2.0); ax.set_ylim(-N * 1.6, N * 1.6)
    ax.set_title("同じ四角形（白）と 180° 回したもの（灰）を並べる", fontsize=9, loc="left", color="#222222")
    if own:
        plt.show()
    return v1, v2

v1, v2 = tile_quad(quad, N)

# %% [markdown]
# ### 照合：角の和と、1 点に集まる角

# %%
def angles(P):
    P = np.array(P, dtype=float); out = []
    for i in range(4):
        a, b, c = P[i - 1], P[i], P[(i + 1) % 4]
        u, v = a - b, c - b
        out.append(math.degrees(math.acos(np.dot(u, v) / np.linalg.norm(u) / np.linalg.norm(v))))
    return out
mach = angles(quad)
print("手（分度器）：", hand_angles, "和 =", sum(hand_angles))
print("機械（座標）：", [round(a) for a in mach], "和 =", round(sum(mach)))
print("1 点のまわりに 4 つの角が 1 回ずつ集まると、和は 360 になる（手の記録：", hand_corner, "）")

# %% [markdown]
# ## 予想を試す
#
# 予想：「どんな四角形でもしきつめられる」。四角形を無作為に 6 つ作って、同じ並べ方で描く。すき間や重なりが出るものはある？（へこんだ四角形も含めて）

# %%
rng = np.random.default_rng(3)
fig, axes = plt.subplots(2, 3, figsize=(13, 7))
for ax in axes.flat:
    P = [(0, 0), (rng.uniform(2, 4), rng.uniform(-1, 1)), (rng.uniform(2, 4), rng.uniform(2, 3.5)), (rng.uniform(-0.5, 1.5), rng.uniform(1.5, 3))]
    tile_quad(P, 3, ax=ax)
plt.show()
print("目で確かめる：すき間・重なりがあるか。あれば、その四角形の 4 つの角の和を計算する")

# %% [markdown]
# **確かめること**：機械の並べ方は「辺の中点で 180° 回す」。手でやった並べ方と同じ？ 違う並べ方でもできた？
#
# ここから先の問い：三角形 2 枚で四角形になる → 三角形もしきつめられる？ 五角形は？（正五角形はできない。できる五角形は 15 種類しか知られていない）

# %%
report("a4_shikitsume", f"四角形 {quad} は 180° 回転と平行移動でしきつめられた。角の和 {round(sum(mach))} 度",
       data={"quad": quad, "angles": [round(a, 1) for a in mach], "v1": [round(float(x), 2) for x in v1], "v2": [round(float(x), 2) for x in v2]},
       hand={"ok": hand_ok, "corner": hand_corner, "angles": hand_angles, "guess": hand_guess}, params={"N": N}, notebook="a4_shikitsume.ipynb")
