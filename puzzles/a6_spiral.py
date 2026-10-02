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
# # 数のらせん：素数を黒くぬると？
#
# 1 を真ん中に置き、2, 3, 4, … をぐるぐる外側へ並べる。素数のマスだけ黒くぬると、何か見える？
#
# **問い：** 素数はばらばらに散らばる？ それとも何か並び方がある？
#
# **手で：** 印刷した 11 × 11 のらせん（1〜121）で、素数を黒くぬる。何個ぬった？ 黒は何かの線に乗っている？
#
# ![数のらせん 11×11](https://jxta.github.io/kg-grounding-proto/hybrid/print/spiral_11.svg)
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
hand_count = 30                      # 1〜121 で黒くぬった数（自分で数えた値に）
hand_note = "斜めに並んでいるところがある。横や縦の線はあまりない"
hand_guess = "大きな表でも、斜めの線が見える？"
N = 201                              # 機械で描く 1 辺のマス数（奇数）。201 なら 1〜40401

# %% [markdown]
# ## 機械で
#
# らせんの並べ方を機械に教えて、大きな表を描く。

# %%
def spiral(N):
    """N×N のらせん。真ん中が 1。各マスの数を返す"""
    S = np.zeros((N, N), dtype=np.int64)
    x = y = N // 2; S[y, x] = 1
    n, step, d = 2, 1, 0
    dirs = [(1, 0), (0, -1), (-1, 0), (0, 1)]          # 右・上・左・下（画面の上を y 小さい側にする）
    while n <= N * N:
        for _ in range(2):
            dx, dy = dirs[d % 4]
            for _ in range(step):
                x += dx; y += dy
                if 0 <= x < N and 0 <= y < N and n <= N * N:
                    S[y, x] = n; n += 1
            d += 1
        step += 1
    return S

S = spiral(N)
is_p = np.vectorize(sympy.isprime)(S)
fig, ax = plt.subplots(figsize=(6.5, 6.5))
ax.imshow(is_p, cmap="gray_r", interpolation="nearest"); ax.axis("off")
ax.set_title(f"1〜{N * N} のらせん。黒＝素数", fontsize=9.5, loc="left", color="#222222")
plt.show()

# %% [markdown]
# ### 照合：1〜121 の素数の数

# %%
S11 = spiral(11)
machine_count = int(np.vectorize(sympy.isprime)(S11).sum())
print("手：", hand_count, "個 ／ 機械：", machine_count, "個 →", "一致" if hand_count == machine_count else "食い違い。手の表を見直す（1 は素数ではない、2 は素数）")
fig, ax = plt.subplots(figsize=(4, 4))
ax.imshow(np.vectorize(sympy.isprime)(S11), cmap="gray_r", interpolation="nearest"); ax.axis("off")
for (r, c), v in np.ndenumerate(S11):
    ax.text(c, r, str(v), ha="center", va="center", fontsize=6.5, color="white" if sympy.isprime(int(v)) else "#555555")
ax.set_title("11 × 11（手の表と同じ）", fontsize=9.5, loc="left", color="#222222")
plt.show()

# %% [markdown]
# ## 予想を試す
#
# 予想：「斜めの線が見える」。偶然かどうかを一つ確かめる：斜めの線の上の数には、偶数がある？（表の対角線をいくつか拾う）

# %%
diag = [int(S[i, i]) for i in range(0, N, N // 10)]          # 左上から右下への対角線を 10 個ほど
anti = [int(S[i, N - 1 - i]) for i in range(0, N, N // 10)]
print("対角線の数：", diag)
print("もう一方　：", anti)
print("偶数の数：", sum(1 for v in diag + anti if v % 2 == 0), "/", len(diag + anti))
print("→ 斜めの線の上は、ぜんぶ奇数（偶数は 2 以外素数にならないので、斜めに黒が集まりやすい）。でも線によって濃さが違うのは、それだけでは説明がつかない")

# %% [markdown]
# **確かめること**：斜めに濃い線を 1 本選び、その上の数を 5 つ書き出す。どんな数？（AI に聞くなら：「この 5 つの数に共通の作り方はある？」。答えを聞く前に、自分で差を取ってみる）
#
# ここから先の問い：らせんの始まりを 1 でなく 41 にすると？（`spiral` の `n = 2` と `S[y, x] = 1` を変える）

# %%
report("a6_spiral", f"1〜{N * N} のらせんに素数をぬると、斜めの線が見える。1〜121 の素数は {machine_count} 個",
       data={"N": N, "primes_121": machine_count}, hand={"count": hand_count, "note": hand_note, "guess": hand_guess}, params={"N": N}, notebook="a6_spiral.ipynb")
