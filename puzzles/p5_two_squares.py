# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # パズル5　タイルを正方形 2 つに
#
# タイルが n 枚。全部使って、正方形を 2 つ作れる？（片方は 1 枚でもよい。片方が 0 枚＝正方形 1 つ、も許す）
# 5 枚なら 4 + 1。13 枚なら 9 + 4。3 枚は？ 7 枚は？ 作れる枚数と作れない枚数に、きまりはある？
#
# ## 手で（物理的な実験）
#
# **用意するもの**：タイル 30 枚。
#
# **やり方**：1 枚から 30 枚まで、正方形 2 つ（または 1 つ）に並べられるか試す。できた枚数と、できなかった枚数を分けて書く。
#
# **記録すること**：できた枚数の一覧。できなかった枚数のうち、素数はどれ？（素数の一覧：2, 3, 5, 7, 11, 13, 17, 19, 23, 29）

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

# 手で見た結果（30 枚まで。自分の結果に書き換える）
hand_ok = [1, 2, 4, 5, 8, 9, 10, 13, 16, 17, 18, 20, 25, 26, 29]

# %% [markdown]
# ## 機械で

# %%
def two_squares(n):
    for a in range(0, math.isqrt(n) + 1):
        b2 = n - a * a; b = math.isqrt(b2)
        if b * b == b2:
            return (a, b)
    return None

machine_ok = [n for n in range(1, 31) if two_squares(n)]
print("機械（30 まで）：", machine_ok)
print("手　（30 まで）：", hand_ok)
print("食い違い：", sorted(set(machine_ok) ^ set(hand_ok)) or "なし")
two_squares_pics([5, 13, 25, 3, 29])
compare_grid(30, hand_ok, machine_ok)
number_grid(100, fill=lambda n: two_squares(n) is not None, title="正方形 2 つにできる枚数（黒）")

# %% [markdown]
# **見るところ**：できなかった枚数のうち素数のもの（3, 7, 11, 19, 23…）と、できた素数（2, 5, 13, 17, 29…）。4 で割った余りは？

# %%
number_grid(100, fill=lambda n: sympy.isprime(n) and two_squares(n) is not None, ring=lambda n: sympy.isprime(n) and two_squares(n) is None,
            title="素数だけ：黒＝正方形 2 つにできる、丸＝できない")
print(f"{'素数':>4} {'2 つの正方形':>10} {'4 で割った余り':>10}")
for p in sympy.primerange(2, 60):
    t = two_squares(p)
    print(f"{p:>4} {('%d²+%d²' % (t[0], t[1])) if t else 'できない':>10} {p % 4:>10}")

# %% [markdown]
# ## 予想を試す
#
# 「素数 p が 2 つの正方形にできる ⇔ ○○」——自分の言葉で書いてから、N まで試す。

# %%
guess = "p = 2 か、p を 4 で割ると 1 余る"
def my_guess(p):
    return p == 2 or p % 4 == 1

N = 10000
counter = [p for p in sympy.primerange(2, N) if (two_squares(p) is not None) != my_guess(p)]
print(f"予想「{guess}」の反例（素数 {N} まで）：", counter[:10] or "なし")

# %% [markdown]
# **つながり**：4 で割って 1 余る素数と 3 余る素数——「レース」のパズルで数えた 2 種類の素数が、ここでは正方形の形で見分けられる。

# %%
report("p5_two_squares",
       f"30 枚まで手で試した結果は機械と{'一致' if sorted(hand_ok) == machine_ok else '食い違い'}。"
       f"素数について予想「{guess}」は {N} まで{'反例なし' if not counter else '反例あり'}",
       data={"ok_to_60": [n for n in range(1, 61) if two_squares(n)], "primes_ok_to_100": [p for p in sympy.primerange(2, 100) if two_squares(p)], "N": N, "counter": counter[:10]},
       hand={"ok_to_30": hand_ok},
       params={"N": N},
       notebook="p5_two_squares.ipynb")
