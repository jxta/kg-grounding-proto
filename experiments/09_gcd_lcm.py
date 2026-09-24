# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 実験9　最大公約数・最小公倍数 — 素因数分解を並べる
#
# 24 と 36 の素因数分解を並べて、共通の部分を見ます。関係するノード：**最大公約数・最小公倍数**、**素因数分解**

# %%
import sys; sys.path.insert(0, ".")
from kg_tools import *

def side_by_side(a, b):
    fa, fb = sympy.factorint(a), sympy.factorint(b)
    ps = sorted(set(fa) | set(fb))
    print(f"{'素数':>6} " + " ".join(f"{p:>4}" for p in ps))
    print(f"{a:>6} " + " ".join(f"{fa.get(p, 0):>4}" for p in ps) + "   （指数）")
    print(f"{b:>6} " + " ".join(f"{fb.get(p, 0):>4}" for p in ps))
    g = math.prod(p ** min(fa.get(p, 0), fb.get(p, 0)) for p in ps)
    l = math.prod(p ** max(fa.get(p, 0), fb.get(p, 0)) for p in ps)
    print(f"小さい方の指数をとる → 最大公約数 {g} = {factorization_str(g)}")
    print(f"大きい方の指数をとる → 最小公倍数 {l} = {factorization_str(l)}")
    return g, l

side_by_side(24, 36)
print()
side_by_side(360, 84)

# 予想：min の指数 → GCD、max の指数 → LCM。2〜200 のすべての組で math.gcd / math.lcm と一致するか
def by_exponents(a, b):
    fa, fb = sympy.factorint(a), sympy.factorint(b)
    ps = set(fa) | set(fb)
    return (math.prod(p ** min(fa.get(p, 0), fb.get(p, 0)) for p in ps),
            math.prod(p ** max(fa.get(p, 0), fb.get(p, 0)) for p in ps))

ok = all(by_exponents(a, b) == (math.gcd(a, b), math.lcm(a, b)) for a in range(2, 201) for b in range(a, 201))
print("\n2〜200 のすべての組で一致：", ok)

# %% [markdown]
# **見るところ**：最大公約数 × 最小公倍数 = 元の 2 数の積（24 × 36 = 12 × 72）。指数で見ると min + max = 元の指数の和、だから。
#
# **説明するときに借りるもの**：「共通の約数は、両方の分解の一部になっている」は、分解がただ一通りだから言える。

# %%
report("exp09", f"素因数分解を並べて、指数の min が最大公約数、max が最小公倍数になることを 2〜200 のすべての組で確認した（{ok}）。GCD × LCM = 積 も指数で説明できる",
       {"range": [2, 200], "ok": bool(ok), "uses": ["factorization", "uniqueness"]})
