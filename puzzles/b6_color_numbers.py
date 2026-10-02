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
# # 数の色紙：1〜100 を、いちばん小さい素因数で色分け
#
# 2 で割れる数は黄色、3 で割れる（2 では割れない）数は緑、5 は青、7 は赤、… と、「いちばん小さい素因数」で色をつける。素数は黒。
#
# **問い：** 色紙に模様は出る？ 黒（素数）はどこに多い？ 「約数の個数」で色をつけると？
#
# **手で：** 印刷した 1〜100 の表を、いちばん小さい素因数で色分けする（2：黄、3：緑、5：青、7：赤、素数：黒、1：白）。
#
# ![1〜100 の色紙](https://jxta.github.io/kg-grounding-proto/hybrid/print/numbers_100.svg)
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
hand_counts = {"黄(2)": 50, "緑(3)": 17, "青(5)": 7, "赤(7)": 3, "黒(素数)": 25, "白(1)": 1}   # 自分で数えた値に
hand_note = "黄色が半分。黒は 1 の位が 1, 3, 7, 9 のところだけ。縦に並ぶ"
hand_guess = "100 より先も、黄色が半分、緑が 6 分の 1 のまま？ 黒は減っていく？"
N = 400                                     # 機械で描く範囲（1〜N）
COLS = 20                                   # 1 行のマス数

# %% [markdown]
# ## 機械で

# %%
PALETTE = {1: "#ffffff", 2: "#f6d55c", 3: "#7bc47f", 5: "#5b8dd9", 7: "#e06666", 11: "#b07cc6", 13: "#f2a65a", 0: "#111111"}  # 0 = 素数
def least_factor_color(n):
    if n == 1:
        return PALETTE[1]
    if sympy.isprime(n):
        return PALETTE[0]
    p = min(sympy.factorint(n))
    return PALETTE.get(p, "#9e9e9e")

def paper(N, cols, ax, colorf, title, numbers=True):
    rows = math.ceil(N / cols)
    for n in range(1, N + 1):
        r, c = divmod(n - 1, cols)
        ax.add_patch(plt.Rectangle((c, rows - 1 - r), 1, 1, fc=colorf(n), ec="white", lw=0.5))
        if numbers:
            ax.text(c + 0.5, rows - 0.5 - r, str(n), ha="center", va="center", fontsize=5.5, color="white" if colorf(n) in ("#111111", "#5b8dd9", "#e06666", "#b07cc6") else "#222222")
    ax.set_xlim(0, cols); ax.set_ylim(0, rows); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=9.5, loc="left", color="#222222")

fig, ax = plt.subplots(figsize=(10, 10 * math.ceil(N / COLS) / COLS))
paper(N, COLS, ax, least_factor_color, f"1〜{N}：いちばん小さい素因数の色（黒 = 素数）")
plt.show()

# %% [markdown]
# ### 照合：1〜100 の色の数

# %%
cnt = {"黄(2)": 0, "緑(3)": 0, "青(5)": 0, "赤(7)": 0, "黒(素数)": 0, "白(1)": 0, "その他": 0}
for n in range(1, 101):
    c = least_factor_color(n)
    key = {"#f6d55c": "黄(2)", "#7bc47f": "緑(3)", "#5b8dd9": "青(5)", "#e06666": "赤(7)", "#111111": "黒(素数)", "#ffffff": "白(1)"}.get(c, "その他")
    cnt[key] += 1
print("手  ：", hand_counts); print("機械：", cnt)
print("一致" if all(hand_counts.get(k) == v for k, v in cnt.items() if k != "その他") else "食い違い。どの色？ 49 や 77 の色を見直す（7 で割れる）")

# %% [markdown]
# ## 予想を試す
#
# 予想：「黄色は半分のまま、黒は減っていく」。100、400、1600、10000 で割合を出す。

# %%
print(f"{'まで':>6} {'黄(2)':>7} {'緑(3)':>7} {'青(5)':>7} {'黒(素数)':>8}")
for M in [100, 400, 1600, 10000]:
    y = M // 2; g = M // 3 - M // 6; b = M // 5 - M // 10 - M // 15 + M // 30
    k = int(sympy.primepi(M))
    print(f"{M:>6} {y / M:>7.3f} {g / M:>7.3f} {b / M:>7.3f} {k / M:>8.3f}")
print("→ 黄・緑・青の割合はほぼ一定（1/2、1/6、1/15）。黒（素数）の割合だけ、だんだん減る")

# %% [markdown]
# ### もう一つの色紙：約数の個数で

# %%
cm = colormaps["viridis"]
def divisor_color(n):
    d = int(sympy.divisor_count(n))
    return cm(min(d, 12) / 12)
fig, ax = plt.subplots(figsize=(10, 10 * math.ceil(N / COLS) / COLS))
paper(N, COLS, ax, divisor_color, f"1〜{N}：約数の個数の色（暗い = 少ない、明るい = 多い。12 個以上は同じ色）", numbers=False)
plt.show()
most = max(range(1, N + 1), key=lambda n: int(sympy.divisor_count(n)))
print(f"1〜{N} で約数がいちばん多い数：{most}（{int(sympy.divisor_count(most))} 個）")

# %% [markdown]
# **確かめること**：黒（素数）が 1 の位 1, 3, 7, 9 の列にしか出ないのはなぜ？（2 の列と 5 の列には何がある？）
#
# ここから先の問い：1 行を 6 にすると（COLS = 6）、黒はどの列に出る？ 1 行を 30 にすると？

# %%
report("b6_color_numbers", f"1〜{N} をいちばん小さい素因数で色分け。黄 1/2・緑 1/6・青 1/15 は一定、素数の割合は減る。約数最多は {most}",
       data={"N": N, "counts_100": cnt, "most_divisors": int(most)}, hand={"counts": hand_counts, "note": hand_note, "guess": hand_guess},
       params={"N": N, "COLS": COLS}, notebook="b6_color_numbers.ipynb")
