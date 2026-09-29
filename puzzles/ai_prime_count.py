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
# # 素数はいくつある？
#
# **問い（きみの言葉、Miro の付箋から）：** どのくらいあるのか知りたい。
#
# 手でやったこと・見えたこと：2,3,5,7,11,13,17,19,23,29, ...と眺めた。素数表をながめた。
#
# 手の結果（数や一覧）：かなり多そうとしかわからない。
#
# 予想（自分の言葉で）：無茶苦茶いっぱいある
#
# 機械に頼むこと：素数の多さを調べて欲しい。　どこまで：10^15 まで
#
# （AI）このノートは、上の付箋の言葉から AI（Claude）が機械の部分を書いたもの。問い・手の結果・予想は書き換えていない。
# 「どのくらい」を **数で言う** のがこのノートの仕事。「いっぱい」を、10 までに何個、100 までに何個、…と数えていく。

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

# 手で見た結果（自分の結果に書き換える）
hand_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]     # 眺めた素数（付箋のとおり）
hand_note = "かなり多そうとしかわからない"                 # 手の結果
hand_guess = "無茶苦茶いっぱいある"                        # 予想
N_hand = 10**15                                          # 付箋の「どこまで」
N = 10**6                                                # 機械がこのノートで実際に数える範囲（下の注を読む）

# %% [markdown]
# ## 機械で
#
# （AI）まず、手で眺めた素数と機械の素数が同じかどうかを照らす。ここがずれたら、先に進まない。

# %%
# [AI] 照合：手で書いた素数の並びと、機械が数えた 30 までの素数
machine_30 = [n for n in range(2, 31) if sympy.isprime(n)]
print("手  ：", hand_primes)
print("機械：", machine_30)
print("一致" if hand_primes == machine_30 else "食い違いあり。どちらが間違えた？ 手の表と機械の表を見比べる")

# %% [markdown]
# （AI）次に「どのくらいあるか」を数で言う。
# 10 まで、100 まで、1000 まで、…と、**素数が何個あるか**（数学では π(x) と書く）を数える。
# 10 倍ごとに何倍に増えるかも並べる。

# %%
# [AI] N までの素数を全部数える（エラトステネスの篩。N = 10**6 なら 1 秒くらい）
import numpy as np
is_p = np.ones(N + 1, dtype=bool); is_p[:2] = False
for i in range(2, int(N ** 0.5) + 1):
    if is_p[i]:
        is_p[i * i::i] = False
pi = np.cumsum(is_p)                     # pi[x] = x までの素数の個数
rows = []
print(f"{'x':>10} {'x までの素数':>12} {'10 倍ごとの増え方':>16} {'100 個に何個':>12}")
prev = None
for k in range(1, int(np.log10(N)) + 1):
    x = 10 ** k
    c = int(pi[x])
    ratio = f"{c / prev:.2f} 倍" if prev else ""
    print(f"{x:>10} {c:>12} {ratio:>16} {100 * c / x:>10.1f} 個")
    rows.append({"x": x, "pi": c})
    prev = c

# %%
# [AI] 絵にする：x までの素数の個数（黒）と、x ÷ (x の自然対数) という目安（灰色）
xs = np.arange(2, N + 1, max(1, N // 2000))
fig, ax = plt.subplots(figsize=(8, 3.2))
ax.plot(xs, pi[xs], color="#111111", lw=1.4, label="x までの素数の個数")
ax.plot(xs, xs / np.log(xs), color="#9a9a9a", lw=1.2, ls="--", label="x ÷ ln x（目安）")
ax.set_xlabel("x"); ax.set_ylabel("個数"); ax.legend(frameon=False, fontsize=8)
ax.set_title(f"素数はどのくらいある？（{N} まで数えた）", fontsize=9.5, loc="left", color="#222222")
plt.show()

# %%
# [AI] 100 個ずつの区間に素数は何個？（だんだん減る？ でも 0 にはならない？）
block = 100
counts = [int(pi[min(N, b + block)] - pi[b]) for b in range(0, N, block)]
fig, ax = plt.subplots(figsize=(8, 2.6))
ax.plot(range(0, N, block), counts, color="#111111", lw=0.5)
ax.set_xlabel("x"); ax.set_ylabel(f"{block} 個の中の素数")
ax.set_title("100 個ずつ数えると、素数は減っていくが、なくならない", fontsize=9.5, loc="left", color="#222222")
plt.show()
print("最初の 100 個に", counts[0], "個。最後の 100 個に", counts[-1], "個。0 個の区間は", sum(1 for c in counts if c == 0), "つ")

# %% [markdown]
# ## 10^15 まで、について
#
# （AI）付箋の「どこまで」は 10^15。正直に言うと、この機械（ブラウザの中の Python）では 10^15 までの素数を一つずつ数えることはできない。
# 10^6 までで 1 秒、10^7 までで十数秒。10^15 は、その 1 億倍。
#
# でも、人は別の方法で 10^15 までの素数の個数を計算して公表している（一つずつ数えずに個数だけを出す方法がある）。
# 公表されている値：**29,844,570,422,669 個**（約 30 兆）。
# 下のセルは、その値と「x ÷ ln x」の目安を並べる。目安がどのくらい近いかを見て、上の表の傾向とつながるか考える。
#
# ただし、このノートの機械が **自分で確かめた** のは N = 10^6 までだけ。10^6 の先は、機械の結果ではなく「人が公表した値」。そこは分けて考える。

# %%
# [AI] 公表されている値と目安を並べる（機械が数えたのではない、ことに注意）
published = {10**9: 50_847_534, 10**12: 37_607_912_018, 10**15: 29_844_570_422_669}
print(f"{'x':>18} {'公表された素数の個数':>20} {'x ÷ ln x':>20} {'比':>6}")
for x, c in published.items():
    est = x / np.log(x)
    print(f"{x:>18,} {c:>20,} {int(est):>20,} {c / est:>6.3f}")
print("→ 比が 1 に近づいていくなら、上の表で見た傾向と同じ形")

# %% [markdown]
# ## 予想を試す
#
# （AI）予想は「無茶苦茶いっぱいある」。機械の表は、10 倍ごとに素数の個数がだいたい 6〜8 倍に増え、その倍率が少しずつ 10 倍に近づくことを示した。
# 増え方は鈍るが、止まらない。**いっぱい、を数で言うと**：
#
# - 10 までに 4 個、100 までに 25 個、1000 までに 168 個、…、10^6 までに 78,498 個（上の表）
# - 100 個ずつ数えると、素数はだんだんまばらになるが、0 個の区間は（10^6 までには）出てこなかった
#
# ここから先の問い（きみが選ぶ）：
# - 「終わらない」と言い切れる？（数えるだけでは言えない。別の手がある → パズル「いちばん大きい素数はある？」）
# - 10 倍ごとの増え方は、このまま 10 倍に近づく？ 超えることはない？（表の「10 倍ごとの増え方」と「100 個に何個」を見る）
#
# **確かめること**：機械が正しいとは限らない。10 までの 4 個、100 までの 25 個は、手の素数表で数え直せる。

# %%
# [AI] この実験の記録を地図アプリへ（自分で結果を書き換えてから実行する）
hand = {"primes_seen": hand_primes, "note": hand_note, "guess": hand_guess, "N_wanted": N_hand}
data = {"pi": {str(r["x"]): r["pi"] for r in rows}, "blocks_with_zero": sum(1 for c in counts if c == 0),
        "published_pi_1e15": 29844570422669, "machine_counted_up_to": N}
report("ai_prime_count", f"{N} までの素数は {int(pi[N])} 個。10 倍ごとに約 {pi[N] / pi[N // 10]:.1f} 倍に増える。10^15 は機械では数えず、公表値と目安を並べた",
       data=data, hand=hand, params={"N": N, "N_hand": N_hand, "method": "sieve"}, notebook="ai_prime_count.ipynb")
