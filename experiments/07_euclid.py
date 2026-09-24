# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 実験7（発展）素数は無限にある？ — 全部かけて 1 を足す
#
# 小さい方から k 個の素数を全部かけて、1 を足します。その数はどの素数で割っても 1 余るはず。素因数分解するとどうなる？
# 関係するノード：**素数は無限にある**（証明には **素因数分解**（どんな数にも素因数がある）を使う）

# %%
import sys; sys.path.insert(0, ".")
from kg_tools import *

rows = euclid_numbers(10)

# %% [markdown]
# **見るところ**：素数になることもあれば（3, 7, 31, …）、ならないこともある（30031 = 59 × 509）。でも、出てくる素因数はいつも **リストにない新しい素数**。
#
# **証明（言葉で）**：素数が有限個だったとして、全部かけて 1 を足した数を N とする。N はどの素数で割っても 1 余る。
# でも N には素因数が必ずある（実験2）。その素因数はリストにない新しい素数。矛盾。だから素数は無限にある。
#
# 自分の言葉で言い直せたら、地図で「証明できる」に上げてよい。そのとき、この証明が「どんな数にも素因数がある」を使っていることも書いておく。

# %%
new_always = all(all(q > p for q in new) for i, p, n, fs, new in rows)
report("exp07", f"k = 1〜10 で、2×3×…×p + 1 の素因数はいつも p より大きい新しい素数だった（{new_always}）。素数が有限個なら矛盾する、という証明の筋を追えた",
       {"k": 10, "new_always": bool(new_always), "uses": ["factorization"]})
