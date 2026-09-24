# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 実験6　平方数 — 指数を見る
#
# 平方数（1, 4, 9, 16, …）の素因数分解には、どんな特徴がある？ 関係するノード：**平方数**、**累乗の表し方**

# %%
import sys; sys.path.insert(0, ".")
from kg_tools import *

for n in [4, 9, 36, 100, 144, 225, 900, 1296]:
    r = math.isqrt(n)
    print(f"{n:>5} = {factorization_str(n):<12} = ({factorization_str(r)})²")
print("平方数でない例：", "、".join(f"{n} = {factorization_str(n)}" for n in [8, 12, 18, 50, 72]))

# 予想：指数がすべて偶数 ⇔ 平方数。1〜10000 で確かめる
def all_even(n):
    return all(e % 2 == 0 for e in sympy.factorint(n).values())

ok = all(all_even(n) == (math.isqrt(n) ** 2 == n) for n in range(1, 10001))
print("\n『指数がすべて偶数 ⇔ 平方数』が 1〜10000 で全部あっている：", ok)

# %% [markdown]
# **見るところ**
#
# - 指数がすべて偶数なら、半分ずつに分けて (…)² と書ける → 平方数。
# - 逆（平方数なら指数はすべて偶数）を言うには、分解が **ただ一通り** であることを使う。

# %%
report("exp06", f"指数がすべて偶数 ⇔ 平方数 を 1〜10000 で確認した（{ok}）。→ の向きは半分ずつに分けて説明できる。← の向きは一意性を借りる",
       {"range": [1, 10000], "ok": bool(ok), "uses": ["exponent", "factorization"]})
