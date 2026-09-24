# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 実験8（発展）素数のレース — 「たしかめた」と「証明できる」はちがう
#
# 2 以外の素数を 4 で割ると、余りは 1 か 3。どちらの素数が多いでしょう？ 数えてみます。
# 関係するノード：**素数の偏り（4で割った余り）**、**素数**

# %%
import sys; sys.path.insert(0, ".")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *

D = prime_race(30000)

# %% [markdown]
# **見るところ**
#
# - 26860 まで数えても、ずっと「3 余る素数」の方が多い。ここで「いつも 3 余る方が多い」と言いたくなる。
# - でも 26861 で初めて逆転し、すぐ戻る。ずっと先（およそ 62 万）でも、また逆転する。
# - 「何回でも逆転する」ことは 1914 年に証明されている（Littlewood）。でも、その証明は中学の道具では書けない。
#   3 万まで見たことと、いつでも成り立つことは、別のこと。
#
# もっと先まで見る：`prime_race(700000)`（少し時間がかかる）

# %%
import numpy as np
neg = np.nonzero(D < 0)[0]
first = int(neg[0]) if len(neg) else None
report("exp08", f"30000 まで数えた。26860 までは 3 余る素数がずっと多く、x = {first} で初めて 1 余る方が多くなり、すぐ戻った。『いつも』も『何回も逆転する』も、自分では証明できない",
       {"N": 30000, "first_flip": first})
