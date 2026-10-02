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
# # 万華鏡：図形を回して、裏返して
#
# 一つの小さな図形を、回転移動と対称移動で 6 回・8 回・12 回と写していくと、万華鏡の模様になる。
#
# **問い：** 回すだけの模様と、裏返しもある模様は、どう違う？ 何回対称にすると、いちばんきれい？
#
# **手で：** 印刷した 12 等分の円の、1 つの扇形に好きな線を描く。トレーシングペーパー（または写し取り）で、となりの扇形に **裏返して** 写す。次はその先に **回して** 写す。一周させる。
#
# ![万華鏡の台紙](https://jxta.github.io/kg-grounding-proto/hybrid/print/kaleido_12.svg)
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
hand_k = 12                           # 扇形の数（何回対称にしたか）
hand_note = "裏返しを入れると、線が扇形の境目でつながって見えた"
hand_guess = "裏返しがあると鏡みたいに左右対称、回すだけだと風車みたいにねじれる"
K = 8                                 # 機械で描く対称の回数
SEED = 3                              # 図形の種（変えると別の図形になる）

# %% [markdown]
# ## 機械で
#
# 扇形の中に無作為な折れ線を 1 つ作り、「回転だけ」と「回転 ＋ 裏返し」の 2 通りで写す。

# %%
def wedge_shape(rng, k):
    """角度 0〜360/k の扇形の中の折れ線（半径 0.2〜1）"""
    n = 6
    r = rng.uniform(0.2, 1.0, n); t = np.sort(rng.uniform(0, 2 * np.pi / k, n))
    return np.stack([r * np.cos(t), r * np.sin(t)], axis=1)

def rotate(P, ang):
    c, s = np.cos(ang), np.sin(ang)
    return P @ np.array([[c, -s], [s, c]]).T

def reflect(P, theta):
    """角度 theta の直線（原点を通る）での対称移動：その直線を x 軸に回してから裏返し、元に戻す"""
    Q = rotate(P, -theta)
    Q = Q * np.array([1, -1])
    return rotate(Q, theta)

def kaleido(P, k, mirror, ax, title):
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.1, 1.1)
    for i in range(k):
        ang = 2 * np.pi * i / k
        if mirror and i % 2 == 1:
            Q = reflect(P, ang)                         # となりの扇形へは、境目の線で裏返す（対称移動）
        else:
            Q = rotate(P, ang)                          # 回転移動
        ax.plot(Q[:, 0], Q[:, 1], color="#111111", lw=1.2)
        ax.fill(Q[:, 0], Q[:, 1], color="#bbbbbb", alpha=0.5, lw=0)
    ax.set_title(title, fontsize=9.5, loc="left", color="#222222")

rng = np.random.default_rng(SEED)
P = wedge_shape(rng, K)
fig, axes = plt.subplots(1, 2, figsize=(9, 4.6))
kaleido(P, K, False, axes[0], f"回転だけ（{K} 回）")
kaleido(P, K, True, axes[1], f"回転 ＋ 裏返し（{K} 回）")
plt.show()

# %% [markdown]
# ### 照合：手の模様と機械の模様
#
# 手で作った模様は、右（裏返しあり）と左（回転だけ）のどちらに近い？ 扇形の境目で線がつながるのはどちら？

# %%
print("手：", hand_note)
print("機械：裏返しありは、境目の線が鏡になる（線が境目でつながる）。回転だけは、境目で線がつながらず、模様が一方向にねじれる")

# %% [markdown]
# ## 予想を試す
#
# 予想：「回すだけだと風車のようにねじれる」。k を 3, 6, 12, 24 と変えて、同じ図形で試す。

# %%
fig, axes = plt.subplots(2, 4, figsize=(13, 6.6))
for j, k in enumerate([3, 6, 12, 24]):
    P = wedge_shape(np.random.default_rng(SEED), k)
    kaleido(P, k, False, axes[0][j], f"回転だけ k = {k}")
    kaleido(P, k, True, axes[1][j], f"裏返しあり k = {k}")
plt.show()

# %% [markdown]
# **確かめること**：「裏返し」は教科書の **対称移動**、「回す」は **回転移動**。右の絵で、鏡になっている線（対称の軸）は何本ある？
#
# ここから先の問い：裏返しを 1 つおきでなく、2 つおきにすると？（`i % 2` を `i % 3` に）。SEED を変えて、自分の好きな図形を探す。

# %%
report("a8_kaleido", f"扇形の図形を k = {K} で回転だけ／回転＋裏返しで写した。裏返しありは境目が鏡になる",
       data={"K": K, "seed": SEED}, hand={"k": hand_k, "note": hand_note, "guess": hand_guess}, params={"K": K, "SEED": SEED}, notebook="a8_kaleido.ipynb")
