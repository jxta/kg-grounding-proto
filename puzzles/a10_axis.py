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
# # 軸の糸かけ：直線だけで曲線を描く
#
# 縦の軸の 1 と横の軸の 12 を結ぶ。縦の 2 と横の 11、縦の 3 と横の 10、…。直線しか引いていないのに、曲線が浮かぶ。
#
# **問い：** 浮かんだ曲線は何？ 線を増やすと形は変わる？ 結ぶ相手の決め方を変えると？
#
# **手で：** 印刷した軸の紙で、縦の k と横の 13 − k を結ぶ（k = 1〜12）。できたら、4 つの角に同じものを描いて花にする。
#
# ![軸の糸かけ](https://jxta.github.io/kg-grounding-proto/hybrid/print/axis_string.svg)
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
hand_note = "まっすぐな線だけなのに、丸い曲線が見えた。線が多いところが濃い"
hand_guess = "線を増やしても曲線は同じ場所に出る？"
M = 40                                # 機械で引く本数

# %% [markdown]
# ## 機械で

# %%
def axis_string(m, ax, rule="k ↔ m+1−k", color="#111111"):
    for k in range(1, m + 1):
        if rule == "k ↔ m+1−k":
            ax.plot([0, m + 1 - k], [k, 0], color=color, lw=0.6)
        elif rule == "k ↔ k":
            ax.plot([0, k], [k, 0], color=color, lw=0.6)
        elif rule == "k ↔ 2k":
            ax.plot([0, min(2 * k, m)], [k, 0], color=color, lw=0.6)
    ax.set_aspect("equal"); ax.axis("off")

fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
for ax, m in zip(axes, [12, 24, M]):
    axis_string(m, ax); ax.set_title(f"{m} 本", fontsize=9.5, loc="left", color="#222222")
plt.show()

# %% [markdown]
# ### 照合：手の 12 本と、機械の 12 本
#
# 左の絵が手の紙と同じ。曲線のいちばんふくらむところ（軸から遠いところ）は、手の紙ではどのあたり？

# %%
print("手：", hand_note)
print("機械：12 本でも曲線が見える。本数を増やすと曲線が同じ場所でなめらかになる（線の集まりが曲線を作る：包絡線）")

# %% [markdown]
# ## 予想を試す
#
# 予想：「結ぶ相手の決め方を変えると、曲線が変わる」。3 つの決め方で比べる。

# %%
fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
for ax, rule in zip(axes, ["k ↔ m+1−k", "k ↔ k", "k ↔ 2k"]):
    axis_string(24, ax, rule); ax.set_title(rule, fontsize=9.5, loc="left", color="#222222")
plt.show()
print("k ↔ k は全部平行（曲線は出ない）。相手がずれていくと曲線が出る")

# %% [markdown]
# ### 花にする（4 つの角）

# %%
fig, ax = plt.subplots(figsize=(6, 6))
for sx in (1, -1):
    for sy in (1, -1):
        for k in range(1, M + 1):
            ax.plot([0, sx * (M + 1 - k)], [sy * k, 0], color="#111111", lw=0.5)
ax.set_aspect("equal"); ax.axis("off"); ax.set_title(f"4 つの角 × {M} 本", fontsize=9.5, loc="left", color="#222222")
plt.show()

# %% [markdown]
# **確かめること**：「k ↔ k」の線が平行なのはなぜ？（縦 k・横 k を結ぶ線の傾きを 2 本で比べる）
#
# ここから先の問い：軸を 3 本（120° ずつ）にすると？ 軸を円にすると、ノート a2 の「掛け算の糸かけ」になる。

# %%
report("a10_axis", f"縦 k と横 {M + 1}−k を結ぶ {M} 本の直線から曲線（包絡線）が浮かぶ。k↔k は平行",
       data={"M": M}, hand={"note": hand_note, "guess": hand_guess}, params={"M": M}, notebook="a10_axis.ipynb")
