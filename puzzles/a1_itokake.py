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
# # 糸かけ：k ずつ進むと、何本の糸で回りきる？
#
# 釘を円に並べて、決まった数ずつ飛ばして糸をかけていくと、星の模様ができる（千葉市科学館の「科学×アート」展の糸かけと同じ）。
#
# **問い：** 釘が 24 本のとき、k 本ずつ飛ばして糸をかける。最初の釘に戻ってきたとき、全部の釘を通っている？ 通っていないなら、糸は何本いる？ 模様は k でどう変わる？
#
# **手で：** 印刷した 24 釘の盤（または Miro の糸かけ盤）で、k = 5, 6, 8, 9 を試す。糸（線）が何本で全部の釘を回りきるか数える。
#
# ![糸かけ 24 釘](https://jxta.github.io/kg-grounding-proto/hybrid/print/itokake_24.svg)
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
hand = {5: 1, 6: 6, 8: 8, 9: 3}          # k → 回りきるまでに要った糸の本数（自分で数えた値に書き換える）
hand_note = "6 のときは四角が 6 つ、9 のときは八角形が 3 つに見えた"
hand_guess = "k と 24 の最大公約数と同じ本数になる？"
n = 24                                   # 釘の数
N = 60                                   # 予想を試す範囲（釘の数をここまで）

# %% [markdown]
# ## 機械で
#
# 釘 i から釘 (i + k) mod n へ糸をかけ続け、出発点に戻ったら 1 本。まだ通っていない釘があれば、そこから次の糸。

# %%
def itokake(n, k, ax=None, color="#111111", lw=1.0, title=True):
    """釘 n 本、k ずつ。戻り値：糸の本数（別々の輪の数）"""
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False) + np.pi / 2
    x, y = np.cos(ang), np.sin(ang)
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(3.6, 3.6))
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15)
    ax.plot(x, y, "o", color="#9a9a9a", ms=2.5)
    seen, loops = set(), 0
    for start in range(n):
        if start in seen:
            continue
        i = start; pts = []
        while True:
            seen.add(i); pts.append(i); i = (i + k) % n
            if i == start:
                break
        pts.append(start)
        ax.plot(x[pts], y[pts], color=color, lw=lw)
        loops += 1
    if title:
        ax.set_title(f"n = {n}, k = {k}：糸 {loops} 本", fontsize=9, loc="left", color="#222222")
    if own:
        plt.show()
    return loops

fig, axes = plt.subplots(1, 4, figsize=(13, 3.4))
machine = {}
for ax, k in zip(axes, [5, 6, 8, 9]):
    machine[k] = itokake(n, k, ax=ax)
plt.show()

# %% [markdown]
# ### 照合：手と機械

# %%
print(f"{'k':>3} {'手':>4} {'機械':>4}")
for k in hand:
    print(f"{k:>3} {hand[k]:>4} {machine[k]:>4}  {'一致' if hand[k] == machine[k] else '食い違い。どちらが間違えた？ 盤を見直す'}")

# %% [markdown]
# ### k を全部試す（1〜23）と、糸の本数はどう変わる？

# %%
print(f"{'k':>3} {'糸の本数':>6} {'1 本が通る釘':>10} {'gcd(24, k)':>10}")
rows = []
for k in range(1, n):
    fig = plt.figure(); loops = itokake(n, k, ax=fig.add_subplot(111), title=False); plt.close(fig)
    rows.append((k, loops, n // loops, math.gcd(n, k)))
    print(f"{k:>3} {loops:>6} {n // loops:>10} {math.gcd(n, k):>10}")

# %% [markdown]
# ## 予想を試す
#
# 予想：「糸の本数は、n と k の最大公約数と同じ」。24 だけでなく、釘の数を N まで変えて、すべての k で試す。一つでも外れたら予想は直す。

# %%
def loops_count(n, k):
    seen, loops = set(), 0
    for s in range(n):
        if s in seen: continue
        i = s
        while i not in seen:
            seen.add(i); i = (i + k) % n
        loops += 1
    return loops
bad = [(m, k) for m in range(3, N + 1) for k in range(1, m) if loops_count(m, k) != math.gcd(m, k)]
print(f"釘 3〜{N} 本、すべての k で試した：予想の外れは {len(bad)} 件", bad[:5])
print("→ この範囲では合っていた。N の先は分からない（もっと大きな N で試すか、なぜそうなるかを考える）")

# %% [markdown]
# ## 模様を重ねる（曼荼羅）
#
# 同じ盤に、k をいくつか重ねると展示のような模様になる。濃さを変えて重ねてみる。

# %%
fig, ax = plt.subplots(figsize=(4.5, 4.5))
for k, c, w in [(11, "#111111", 0.7), (7, "#777777", 0.9), (5, "#bbbbbb", 1.2)]:
    itokake(36, k, ax=ax, color=c, lw=w, title=False)
ax.set_title("釘 36 本：k = 5, 7, 11 を重ねる", fontsize=9, loc="left", color="#222222")
plt.show()

# %% [markdown]
# **確かめること**：糸の本数は「輪」の数。輪が 1 本になる k は、24 とどんな関係？（表の gcd の列を見る）
#
# ここから先の問い（きみが選ぶ）：釘 36 本なら 1 本で回りきる k はいくつある？ 釘の数が素数なら？

# %%
data = {"n": n, "loops_by_k": {str(k): l for k, l, _, _ in rows}, "guess_ok_up_to": N, "guess_fail": len(bad)}
report("a1_itokake", f"釘 {n} 本：糸の本数は k ごとに {sorted(set(l for _, l, _, _ in rows))}。予想「本数 = gcd」は釘 {N} 本まで外れなし",
       data=data, hand={"loops": hand, "note": hand_note, "guess": hand_guess}, params={"n": n, "N": N}, notebook="a1_itokake.ipynb")
