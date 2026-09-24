# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 実験2　割っていく — 素因数分解の手順
#
# 小さい素数から順に、割れるだけ割ります。出てきた素数を並べたものが素因数分解です。
# 関係するノード：**素因数分解**、**素因数分解の手順**、**累乗の表し方**

# %%
import sys; sys.path.insert(0, ".")
from kg_tools import *

def factorize(n):
    """小さい素数から順に割っていく"""
    steps, p = [], 2
    while n > 1:
        while n % p == 0:
            steps.append(p)
            n //= p
        p += 1
    return steps

for n in [12, 60, 360, 1001, 2024, 65536, 999999]:
    fs = factorize(n)
    print(f"{n:>7} = {' × '.join(map(str, fs)):<32} → {factorization_str(n)}")

# 自分の手順と sympy（数学ソフト）の答えが 2〜10000 で全部一致するか
agree = all(sorted(factorize(n)) == sorted(p for p, e in sympy.factorint(n).items() for _ in range(e))
            for n in range(2, 10001))
print("\n2〜10000 のすべてで sympy と一致：", agree)

# %% [markdown]
# **見るところ**
#
# - なぜ必ず終わる？ → 割るたびに数が小さくなるから。
# - なぜ出てくるのは素数だけ？ → 1 以外で **いちばん小さい約数** は、必ず素数（もし合成数なら、その約数がもっと小さい約数になってしまう）。
#
# 好きな数で試す：`factorize(2026)`

# %%
print(factorize(2026), "→", factorization_str(2026))

# %%
report("exp02", f"小さい素数から割っていく手順で 2〜10000 を分解し、すべて sympy と一致した（{agree}）。割るたびに小さくなるから必ず終わる",
       {"range": [2, 10000], "agree": bool(agree)})
