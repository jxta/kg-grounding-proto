# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 実験1　エラトステネスの篩 — 素数を「見つける」
#
# 2 の倍数、3 の倍数、5 の倍数、… と順に消していきます。消されずに残った数が素数です。
# 関係するノード：**素数**、**合成数**、**エラトステネスの篩**、**約数と倍数**

# %%
import sys; sys.path.insert(0, ".")
from kg_tools import *

primes = sieve_grid(100)
print(f"100 までの素数は {len(primes)} 個：", primes)

# %% [markdown]
# **見るところ**
#
# - 1 は消されなかった。でも 1 は素数？（素数の約束：約数が「1 とその数」の **2 つ** ある数。1 の約数は 1 つだけ）
# - 消された数の右下の小さい数は、その数を消した素数。7 までの素数で消すだけで、100 まで全部きまったのはなぜ？（→ 実験1b）
#
# 表の途中経過も見られます：`sieve_grid(100, upto=3)` は 3 の倍数まで消したところ。

# %%
_ = sieve_grid(100, upto=3)

# %%
report("exp01", f"100 までの表で篩をかけた。残った素数は {len(primes)} 個。1 は消されなかったが、約数が 1 つしかない",
       {"n": 100, "primes": len(primes)})
