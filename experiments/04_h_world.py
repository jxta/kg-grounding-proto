# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 実験4（発展）「ただ一通り」は当たり前？ — 4 で割って 1 余る数だけの世界
#
# 1, 5, 9, 13, 17, 21, … （4 で割って 1 余る数）だけを使う「H の世界」を考えます。
# この世界の数どうしをかけても、世界の外には出ません（5 × 9 = 45 も 4 で割って 1 余る）。
# この世界の「素数」は、世界の中の 2 つの数（どちらも 1 より大きい）の積に書けない数、と約束します。
# 関係するノード：**分解はただ一通り（一意性）**

# %%
import sys; sys.path.insert(0, ".")
from kg_tools import *

H = h_numbers(100)
print("H の世界の数（100 まで）  ：", H)
print("H の世界の『素数』（100 まで）：", [h for h in H if is_h_prime(h)])
print("\nH の世界で、分け方が 2 通り以上ある数（1500 まで）：")
multi = []
for n in h_numbers(1500):
    fs = h_factorizations(n)
    if len(fs) > 1:
        multi.append(n)
        print(f"  {n} = " + " = ".join(" × ".join(map(str, f)) for f in fs))

ta = factor_tree(441, is_prime=is_h_prime, splits={441: (21, 21)})
tb = factor_tree(441, is_prime=is_h_prime, splits={441: (9, 49)})
show_trees([ta, tb], ["H の世界：441 = 21 × 21", "H の世界：441 = 9 × 49"], save="h_trees")

# %% [markdown]
# **見るところ**
#
# 同じ 441 なのに、葉がちがう。H の世界では「ただ一通り」は成り立ちません。
# ふつうの整数の世界で「ただ一通り」が成り立つのは、当たり前ではなく、整数の世界の **特別な性質** です。
# （なぜ成り立つかの証明は、高校・大学で出会います。）

# %%
report("exp04", f"4 で割って 1 余る数だけの世界では、441 = 21×21 = 9×49 のように 2 通りに分かれる数が 1500 までに {len(multi)} 個あった。『ただ一通り』は当たり前ではない",
       {"first": 441, "count_to_1500": len(multi)})
