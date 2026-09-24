# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 実験3　因数の木を、ちがう順番で作る — 分解は「ただ一通り」？
#
# 360 を、ちがう分け方で木にしてみます。葉（黒）に出てくる素数は同じになる？
# 関係するノード：**分解はただ一通り（一意性）**、**1は素数ではない**

# %%
import sys; sys.path.insert(0, ".")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *

t1 = factor_tree(360)                                          # 小さい素数から割る
t2 = factor_tree(360, splits={360: (12, 30), 12: (3, 4), 30: (5, 6)})
t3 = factor_tree(360, splits={360: (20, 18), 20: (4, 5), 18: (2, 9)})
show_trees([t1, t2, t3], ["① 小さい素数から", "② 360 = 12 × 30 から", "③ 360 = 20 × 18 から"])

# 2〜2000 のすべての数で、でたらめな順番に分けても葉の組が同じになるか
rng = random.Random(0)
same = all(sorted(leaves(factor_tree(n, rng=rng))) == sorted(leaves(factor_tree(n, rng=rng)))
           for n in range(2, 2001))
print("2〜2000 のすべての数で、どんな順番に分けても葉（素数）の組は同じ：", same)

# %% [markdown]
# **見るところ**
#
# - 順番を変えても、葉の組は同じだった（2000 まで）。では 2001 以上でも「必ず」同じと言える？
#   → 見た範囲では同じ。でも「必ず」と言うには、理由が要る。
# - もし 1 を素数に入れたら？ → 6 = 2×3 = 1×2×3 = 1×1×2×3 = … と、分解がいくらでも作れて「ただ一通り」が壊れる。
#
# 自分の数で試す：`show_trees([factor_tree(n), factor_tree(n, rng=random.Random(1))])`

# %%
n = 840
show_trees([factor_tree(n), factor_tree(n, rng=random.Random(1)), factor_tree(n, rng=random.Random(2))],
           ["小さい素数から", "でたらめ①", "でたらめ②"])

# %%
report("exp03", f"360 を 3 通りに分けても葉は同じ。2〜2000 のすべてで、でたらめな順に分けても葉の組は同じだった（{same}）。2001 以上は見ていない",
       {"range": [2, 2000], "same": bool(same)})
