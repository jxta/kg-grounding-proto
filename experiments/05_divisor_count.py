# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 実験5　約数の個数 — 規則を見つけて、説明する
#
# 素因数分解と、約数の個数を並べてみます。規則が見えるでしょうか。
# 関係するノード：**約数の個数**（説明には **分解はただ一通り** を使う）

# %%
import sys; sys.path.insert(0, ".")
from kg_tools import *

def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]

print(f"{'n':>4}  {pad('素因数分解', 14)}{pad('約数', 46)}個数")
for n in [6, 8, 12, 16, 36, 72, 100, 360]:
    ds = divisors(n)
    print(f"{n:>4}  {pad(factorization_str(n), 14)}{pad(str(ds), 46)}{len(ds)}")

# 予想：（指数＋1）を全部かける
def guess(n):
    return math.prod(e + 1 for e in sympy.factorint(n).values())

ok = all(guess(n) == sympy.divisor_count(n) for n in range(1, 10001))
print("\n予想『（指数＋1）をかける』が 1〜10000 で全部あっている：", ok)

# %% [markdown]
# **説明してみる**：72 = 2³ × 3² の約数は、「2 を何個使うか（0〜3 個の 4 通り）」と「3 を何個使うか（0〜2 個の 3 通り）」で決まる。

# %%
divisor_grid(72)

# %% [markdown]
# 表のマスが全部で 4 × 3 = 12 個。これが約数の個数です。
#
# ただし、「表にない約数はない」と言うとき、**約数を分解すると、それは 72 の分解の一部になる（分解はただ一通りだから）** を使っています。
# 地図に印をつけるときは、この説明が「一意性」を **借りている** ことを書いておきましょう。

# %%
report("exp05", f"約数の個数は（指数＋1）のかけ算になる予想を 1〜10000 で確認した（{ok}）。72 の表（4 行×3 列）で説明できる。ただし『表にない約数はない』は一意性を借りている",
       {"range": [1, 10000], "ok": bool(ok), "uses": ["uniqueness", "factorization"]})
