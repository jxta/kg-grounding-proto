# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 自由実験 — 自分で試す
#
# 地図アプリの AI と相談して決めた実験を、ここに書きます。道具（篩の表、因数の木、約数の表、素数レース、H の世界）はそのまま使えます。
#
# 使える道具：`sieve_grid(n)`, `factor_tree(n)`, `show_trees([...])`, `factorization_str(n)`, `divisor_grid(n)`, `prime_race(N)`, `h_numbers`, `is_h_prime`, `h_factorizations`, `euclid_numbers(k)`。数学の道具として `sympy`（`sympy.isprime`, `sympy.factorint`, `sympy.divisors`）も使えます。

# %%
import sys; sys.path.insert(0, ".")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *

# 例：360 の因数の木を、自分の分け方で
t = factor_tree(360, splits={360: (36, 10), 36: (6, 6), 10: (2, 5), 6: (2, 3)})
show_trees([t], ["360 = 36 × 10 から"])

# %% [markdown]
# ## 見たこと・わかったこと
#
# ここに自分の言葉で書く（何を試した？ 何が見えた？ どこまで確かめた？）

# %%
# 結果を地図アプリに送る（文は自分の言葉で書き換える）
report("scratch", "自分の実験：ここに見たことを一文で書く")
