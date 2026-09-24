# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 実験1b　なぜ 7 までの素数で消すだけで 100 まで足りる？
#
# 合成数 n = a × b（a ≤ b）なら、小さい方の a は √n 以下のはず。だから √n 以下の素数で割れなければ、n は素数。
# 本当にそうか、数えて確かめます。関係するノード：**エラトステネスの篩**、**合成数**

# %%
import sys; sys.path.insert(0, ".")
from kg_tools import *

def smallest_prime_factor(n):
    return min(sympy.factorint(n))

for N in [100, 1000, 10000]:
    composites = [n for n in range(4, N + 1) if not sympy.isprime(n)]
    over = [n for n in composites if smallest_prime_factor(n) > math.isqrt(N)]
    print(f"N = {N:>5}：合成数 {len(composites):>5} 個のうち、最小の素因数が √N = {math.isqrt(N)} より大きいもの：{len(over)} 個")

# %% [markdown]
# **見るところ**：√N より大きい素因数しか持たない合成数は、一つもない。
#
# その理由を自分の言葉で：n = a × b で a も b も √n より大きいと、a × b は n より大きくなってしまう。

# %%
# 90〜100 の合成数について、最小の素因数を見る
for n in range(90, 101):
    if not sympy.isprime(n):
        print(f"{n} = {factorization_str(n):<14} 最小の素因数 {smallest_prime_factor(n)}（√{n} ≒ {n ** 0.5:.1f}）")

# %%
report("exp01b", "N = 100, 1000, 10000 のどれでも、√N より大きい素因数しか持たない合成数は 0 個だった。理由：n = a×b で両方が √n より大きいと積が n を超える",
       {"N": [100, 1000, 10000], "over": [0, 0, 0]})
