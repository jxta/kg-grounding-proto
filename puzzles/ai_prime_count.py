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
#
# （AI）**2 版**：最初の版は 10^6 までしか数えなかった（素数を一つずつ並べる数え方だったので）。
# 「10^15 まで、と言ったのに」と言われて、数え方を変えた。素数を並べずに **個数だけ** を出す方法（Lucy の方法）にすると、
# 10^12 までなら数十秒、10^15 までも手元の Python なら 10〜15 分ほどで、機械が自分で数えられる。

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
N = 10**12          # 機械がこのノートで数える範囲。ブラウザで 10**12 は数十秒。10**13 は 1〜2 分、10**14 は 5〜10 分（下の表を見て決める）

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
# （AI）次に「どのくらいあるか」を数で言う。10 まで、100 まで、1000 まで、…と、**素数が何個あるか**（数学では π(x) と書く）を数える。
#
# 数え方：素数を一つずつ見つけて数える（篩）と、10^12 で 1 兆個を調べることになって終わらない。
# そこで、**素数を並べずに個数だけを出す** 方法を使う（Lucy_Hedgehog の方法。`kg_tools.prime_count`）。
# 「2 から v までの整数の個数」から出発して、素数 p ごとに「p で消える数の個数」を引いていく。数える手間は N の 3/4 乗くらいで済む。
#
# | N | 手元の Python | ブラウザ（JupyterLite） | メモリ |
# |:--|:--|:--|:--|
# | 10^12 | 4 秒 | 十数秒 | 小さい |
# | 10^13 | 20 秒 | 1〜2 分 | 130 MB |
# | 10^14 | 2 分 | 5〜10 分 | 250 MB |
# | 10^15 | 10〜15 分（見積もり） | 30〜60 分（できないこともある） | 600 MB |

# %%
# [AI] N までの素数の個数を数える（10 のべきごとの個数も同時に出る）
import time
t0 = time.time()
count, powers = prime_count(N)
print(f"{N} までの素数：{count:,} 個（{time.time() - t0:.1f} 秒）")
print()
print(f"{'x':>18} {'x までの素数':>18} {'10 倍ごとの増え方':>14} {'100 個に何個':>10} {'Li(x) との比':>10}")
prev = None
for x, c in powers.items():
    ratio = f"{c / prev:.2f} 倍" if prev else ""
    print(f"{x:>18,} {c:>18,} {ratio:>14} {100 * c / x:>9.2f} 個 {c / li(x):>10.5f}")
    prev = c

# %% [markdown]
# （AI）**機械の結果を、人が公表している値と照らす。** 素数の個数の表は昔から計算されて公表されている。
# 機械が数えた値と一致すれば、数え方が正しい証拠が一つ増える。一致しなければ、どちらかが間違えている。

# %%
# [AI] 公表されている素数の個数（10 のべきごと）。機械の結果と照らす
published = {10: 4, 100: 25, 10**3: 168, 10**4: 1229, 10**5: 9592, 10**6: 78498, 10**7: 664579, 10**8: 5761455,
             10**9: 50847534, 10**10: 455052511, 10**11: 4118054813, 10**12: 37607912018,
             10**13: 346065536839, 10**14: 3204941750802, 10**15: 29844570422669}
bad = [x for x, c in powers.items() if published.get(x) not in (None, c)]
print("機械と公表値：", "すべて一致" if not bad else f"食い違い {bad}")
print()
print(f"{'x':>18} {'公表された個数':>18} {'機械':>10} {'Li(x)':>18} {'Li(x) − 個数':>12} {'x/ln x との比':>12}")
for x, c in published.items():
    mine = "数えた" if x in powers else "まだ"
    print(f"{x:>18,} {c:>18,} {mine:>10} {round(li(x)):>18,} {round(li(x)) - c:>12,} {c / (x / numpy.log(x)):>12.4f}")

# %%
# [AI] 絵にする：10 のべきごとの個数（黒丸＝機械が数えた、白丸＝公表値のみ）と、Li(x)・x/ln x の目安。両軸とも対数
xs = numpy.array(list(published))
fig, ax = plt.subplots(figsize=(8, 3.4))
grid = numpy.logspace(1, 15, 300)
ax.plot(grid, [li(g) for g in grid], color="#9a9a9a", lw=1.2, label="Li(x)")
ax.plot(grid, grid / numpy.log(grid), color="#bbbbbb", lw=1.2, ls="--", label="x ÷ ln x")
mine = numpy.array([x in powers for x in xs])
ax.plot(xs[mine], [published[x] for x in xs[mine]], "o", color="#111111", ms=5, label="機械が数えた")
ax.plot(xs[~mine], [published[x] for x in xs[~mine]], "o", mfc="white", mec="#111111", ms=5, label="公表値のみ")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("x"); ax.set_ylabel("x までの素数の個数")
ax.legend(frameon=False, fontsize=8)
ax.set_title("素数はどのくらいある？（両軸とも対数。直線に近いが、少しだけ下に曲がる）", fontsize=9.5, loc="left", color="#222222")
plt.show()

# %%
# [AI] 100 個ずつの区間に素数は何個？（こちらは篩で 10^7 まで。だんだん減る？ 0 個の区間はある？）
M = 10**7; block = 100
is_p = numpy.ones(M + 1, dtype=bool); is_p[:2] = False
for i in range(2, int(M ** 0.5) + 1):
    if is_p[i]:
        is_p[i * i::i] = False
pi_small = numpy.cumsum(is_p)
counts = [int(pi_small[min(M, b + block)] - pi_small[b]) for b in range(0, M, block)]
fig, ax = plt.subplots(figsize=(8, 2.6))
ax.plot(range(0, M, block), counts, color="#111111", lw=0.3)
ax.set_xlabel("x"); ax.set_ylabel(f"{block} 個の中の素数")
ax.set_title("100 個ずつ数えると、素数は減っていく。0 個の区間（すき間）も出てくるが、そのあとまた出てくる（10^7 まで）", fontsize=9.5, loc="left", color="#222222")
plt.show()
print("最初の 100 個に", counts[0], "個。最後の 100 個に", counts[-1], "個。0 個の区間は", sum(1 for c in counts if c == 0), "つ")

# %% [markdown]
# ## 10^15 まで
#
# （AI）付箋の「どこまで」は 10^15。上の表のとおり、機械が自分で数えたのは N まで（最初は 10^12）。
# 10^15 まで数えるには、次のセルの `RUN_BIG` を `True` にして実行する。手元の Python で 10〜15 分（10^14 が 2 分だったことからの見積もり）、メモリ 600 MB。
# ブラウザでは 30 分以上かかり、途中で止まることもある（そのときはページを開き直す）。
#
# 数え終わったら、公表値 29,844,570,422,669 と照らす。**機械が自分で数えた値と、人が公表した値が一致する** ところまでが、この実験の「確かめた」範囲。
#
# 数えなくても分かることもある：Li(10^15) の目安は 29,844,571,475,287 で、公表値との差は約 105 万。30 兆に対して 1 億分の 3.5。
# 「どのくらいあるか」なら、目安で 8 桁まで当たる。「ぴったり何個か」は、数えるしかない。

# %%
# [AI] N_hand（10^15）まで機械で数える。時間がかかるので、やるときだけ True にする
RUN_BIG = False
if RUN_BIG:
    t0 = time.time()
    big, big_powers = prime_count(N_hand)
    print(f"{N_hand:,} までの素数：{big:,} 個（{(time.time() - t0) / 60:.1f} 分）")
    print("公表値：", f"{published[N_hand]:,}", "→", "一致" if big == published[N_hand] else "食い違い。どちらが間違えた？")
    powers.update(big_powers); count, N = big, N_hand
else:
    print(f"まだ数えていない。目安 Li(10^15) = {round(li(N_hand)):,}、公表値 = {published[N_hand]:,}、差 = {round(li(N_hand)) - published[N_hand]:,}")

# %% [markdown]
# ## 予想を試す
#
# （AI）予想は「無茶苦茶いっぱいある」。機械の表は、10 倍ごとに素数の個数が 6.25 倍、6.72 倍、…、9.1 倍（10^12 のとき）と増え、
# 増え方の倍率がじわじわ 10 倍に近づくことを示した。増え方は鈍るが、止まらない。**いっぱい、を数で言うと**：
#
# - 10 までに 4 個、100 までに 25 個、…、10^12 までに 37,607,912,018 個（機械が数えた）、10^15 までに 29,844,570,422,669 個（公表値。`RUN_BIG` で機械でも）
# - 100 個の中の素数は、平均すると 10 までで 40 個、10^6 で 7.8 個、10^12 で 3.8 個、10^15 で 3.0 個と減る。区間ごとに見ると 0 個のところ（素数のすき間）も出てくるが、そのあとまた出てくる
# - Li(x) との比は 1 に近づく（10^12 で 0.99999）。「どのくらい」の答えは、ほぼ Li(x) で言い表せる
#
# ここから先の問い（きみが選ぶ）：
# - 「終わらない」と言い切れる？（数えるだけでは言えない。別の手がある → パズル「いちばん大きい素数はある？」）
# - Li(x) は、いつも素数の個数より **大きい**？（表の「Li(x) − 個数」はすべて正。ずっとそう？ → これは有名な問いで、答えはこの表の先にある）
#
# **確かめること**：機械が正しいとは限らない。10 までの 4 個、100 までの 25 個は、手の素数表で数え直せる。10^12 までは公表値と一致した。

# %%
# [AI] この実験の記録を地図アプリへ（自分で結果を書き換えてから実行する）
hand = {"primes_seen": hand_primes, "note": hand_note, "guess": hand_guess, "N_wanted": N_hand}
data = {"pi": {str(x): c for x, c in powers.items()}, "matches_published": not bad,
        "published_pi_1e15": published[N_hand], "li_1e15": round(li(N_hand)), "machine_counted_up_to": N}
report("ai_prime_count", f"{N:,} までの素数は {count:,} 個（公表値と{'一致' if not bad else '不一致'}）。10 倍ごとの増え方は 10 倍に近づく。10^15 は {'機械でも数えた' if N >= N_hand else '目安 Li と公表値を並べた'}",
       data=data, hand=hand, params={"N": N, "N_hand": N_hand, "method": "lucy"}, notebook="ai_prime_count.ipynb")
