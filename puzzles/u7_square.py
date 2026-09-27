# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 単元パズル7　正方形に並ぶ枚数の、素因数分解
#
# タイルを正方形にすきまなく並べられる枚数（1, 4, 9, 16, …）。その素因数分解を見ると、何か共通点はある？
# 逆に、素因数分解を見ただけで「正方形にできる」と分かる？
#
# ## 手で（物理的な実験）
#
# **用意するもの**：タイル 64 枚（おはじきや碁石でも）、鉛筆。
#
# **やり方**：16, 24, 36, 48, 64 枚で正方形を作ってみる。できた枚数とできなかった枚数に分ける。それぞれ素因数分解を手で書く（単元パズル2 のやり方で）。
#
# **記録すること**：できた枚数・できなかった枚数と、それぞれの素因数分解。気づいたこと。

# %%
import sys; sys.path.insert(0, "."); sys.path.insert(0, "../experiments")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *

# 手で見た結果（自分の結果に書き換える）
hand_square = {16: True, 24: False, 36: True, 48: False, 64: True}
hand_factor = {16: "2×2×2×2", 24: "2×2×2×3", 36: "2×2×3×3", 48: "2×2×2×2×3", 64: "2×2×2×2×2×2"}
hand_note = "できた枚数は、同じ素数が偶数個ずつ出てくる"

# %% [markdown]
# ## 機械で

# %%
for n, ok in hand_square.items():
    m = math.isqrt(n) ** 2 == n
    exps = list(sympy.factorint(n).values())
    print(f"{n:>3} 枚：手 {'できた' if ok else 'できない'}／機械 {'できる' if m else 'できない'} → {'一致' if ok == m else '食い違い'}　{factorization_str(n)}　指数 {exps}")

# %% [markdown]
# **見るところ**：指数がすべて偶数なら、半分ずつに分けて（…）² と書ける → 正方形。
# 逆（正方形なら指数はすべて偶数）を言うときは、分解がただ一通りであることを借りる（単元パズル2）。
# もう一つ：正方形に並ぶ枚数は、約数の個数が奇数（単元パズル3）。なぜ？

# %% [markdown]
# ## 予想を試す

# %%
guess = "指数がすべて偶数 ⇔ 正方形にできる"
def all_even(n):
    return all(e % 2 == 0 for e in sympy.factorint(n).values())

N = 10000
counter = [n for n in range(1, N + 1) if all_even(n) != (math.isqrt(n) ** 2 == n)]
print(f"予想「{guess}」の反例（1〜{N}）：", counter[:10] or "なし")
odd_div = [n for n in range(1, N + 1) if sympy.divisor_count(n) % 2 == 1]
print("約数の個数が奇数の数 ＝ 正方形の枚数？（1〜N）：", "同じ集まり" if odd_div == [n for n in range(1, N + 1) if math.isqrt(n) ** 2 == n] else "ちがう")

# %%
report("u7_square",
       f"16・24・36・48・64 枚を手で試した結果は機械と{'一致' if all((math.isqrt(n) ** 2 == n) == ok for n, ok in hand_square.items()) else '食い違い'}。予想「{guess}」は {N} まで反例なし。約数が奇数個の数と正方形の枚数は {N} まで同じ集まり",
       data={"squares_to_100": [n for n in range(1, 101) if math.isqrt(n) ** 2 == n], "N": N, "counter": counter[:10]},
       hand={"square": {str(k): v for k, v in hand_square.items()}, "factor": {str(k): v for k, v in hand_factor.items()}, "note": hand_note},
       params={"N": N},
       notebook="u7_square.ipynb")
