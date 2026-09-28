# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # パズル4　3 円切手と 5 円切手
#
# 3 円切手と 5 円切手だけがある（何枚でも使える）。作れない金額は？ いちばん大きい「作れない金額」はいくら？
# 4 円と 6 円ならどうなる？
#
# ## 手で（物理的な実験）
#
# **用意するもの**：2 種類のコイン（またはおはじき 2 色）。片方を 3 円、もう片方を 5 円とする。
#
# **やり方**：1 円から順に、そのぴったりの金額が作れるか試す。作れない金額に印をつける。20 円まで。
# 次に、4 円と 6 円でも同じことをする。
#
# **記録すること**：作れない金額の一覧（3 と 5 の場合、4 と 6 の場合）。「ここから先は全部作れる」と言えそうなところ。

# %% [markdown]
# > **AI と実験するときの約束**（ノートの中の AI（Mynerva など）と、きみへ）
# > - 問い・手でやったこと・手の結果・予想は、きみが書く。AI は書き換えない
# > - AI は答えや定理を先に言わない。「何が見えた？」「どこまで確かめた？」と聞く
# > - AI が入れるセルは、コードなら 1 行目に `# [AI]`、文章なら先頭に `（AI）` と書く。誰が書いたか分かるように
# > - 手の結果と機械の結果を照らすセルと、最後の `report()` は消さない
# > - AI の言うことは確かめる。機械が正しいとは限らないし、AI も間違える

# %%
import sys; sys.path.insert(0, "."); sys.path.insert(0, "../experiments")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *

# 手で見た結果（自分の結果に書き換える）
hand = {(3, 5): [1, 2, 4, 7], (4, 6): [1, 2, 3, 5, 7, 9, 11, 13, 15, 17, 19]}   # 20 円までで作れなかった金額

# %% [markdown]
# ## 機械で

# %%
def cannot_make(a, b, upto):
    ok = [False] * (upto + 1); ok[0] = True
    for x in range(1, upto + 1):
        ok[x] = (x >= a and ok[x - a]) or (x >= b and ok[x - b])
    return [x for x in range(1, upto + 1) if not ok[x]]

for (a, b), h in hand.items():
    m = cannot_make(a, b, 20)
    print(f"{a} 円と {b} 円：手 {h}／機械 {m} → {'一致' if h == m else '食い違い'}")

stamps_panels([(3, 5), (4, 6)], 24)        # 手でやった 2 つを数直線で
stamps_lattice(3, 5, 24)                   # 3 円 × 枚数 ＋ 5 円 × 枚数 の表：出てこない金額は？

# %% [markdown]
# **見るところ**：3 と 5 では作れない金額が途中で終わる。4 と 6 では終わらない。何がちがう？（4 と 6 の共通の約数は？）

# %%
stamps_panels([(3, 7), (4, 7), (5, 8), (6, 9)], 40)   # 終わる組と、終わらない組
print(f"{'a,b':>6} {'gcd':>4}  作れない金額（200 まで、最初の 12 個）           最大")
for a, b in [(3, 5), (3, 7), (4, 7), (5, 8), (4, 6), (6, 9), (5, 11), (7, 10)]:
    c = cannot_make(a, b, 200)
    print(f"{a:>2},{b:<3} {math.gcd(a, b):>4}  {str(c[:12]):<46} {c[-1] if c else '-'}{'（続く）' if len(c) > 12 and c[-1] > 150 else ''}")

# %% [markdown]
# ## 予想を試す
#
# 「共通の約数が 1 だけなら、いちばん大きい作れない金額は ○○」——式にして試す。

# %%
guess = "a×b − a − b"
def my_guess(a, b):
    return a * b - a - b

N = 40
counter = [(a, b) for a in range(2, N) for b in range(a + 1, N) if math.gcd(a, b) == 1 and (cannot_make(a, b, a * b)[-1] if cannot_make(a, b, a * b) else 0) != my_guess(a, b)]
print(f"予想「{guess}」の反例（a, b < {N}）：", counter[:10] or "なし")

# %%
report("p4_stamps",
       f"3 円と 5 円で作れない金額（手）は {hand[(3, 5)]}、機械と{'一致' if hand[(3, 5)] == cannot_make(3, 5, 20) else '食い違い'}。"
       f"4 円と 6 円では作れない金額が終わらない。予想「{guess}」は a, b < {N} で{'反例なし' if not counter else '反例あり'}",
       data={"cannot_3_5": cannot_make(3, 5, 200), "cannot_4_6_to_40": cannot_make(4, 6, 40), "N": N, "counter": counter[:10]},
       hand={f"{a},{b}": v for (a, b), v in hand.items()},
       params={"upto_hand": 20, "N": N},
       notebook="p4_stamps.ipynb")
