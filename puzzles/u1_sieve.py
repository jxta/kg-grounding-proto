# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 単元パズル1　消していくと、何が残る？
#
# 1 から 100 までの表がある。2 の倍数を消す（2 自身は残す）。次に 3 の倍数を消す（3 は残す）。次に 5、7、…。
# 消すものがなくなるのは、何の倍数まで消したとき？ 最後に残った数はどんな数？
#
# ## 手で（物理的な実験）
#
# **用意するもの**：1〜100 を書いた表（方眼紙に 10 × 10 で書く。印刷でもよい）、鉛筆。
#
# **やり方**：2 の倍数（4, 6, 8, …）に斜線を引く。次に、まだ消えていない数のうち一番小さい 3 の倍数（6, 9, 12, …。すでに消えていればそのまま）。次は 5、次は 7。
# 「7 の倍数を消したあと、11 の倍数で新しく消える数はあるか」を確かめる。
#
# **記録すること**：残った数の一覧。どの数の倍数まで消したら、それ以上消えなくなったか。1 はどうしたか。

# %%
import sys; sys.path.insert(0, "."); sys.path.insert(0, "../experiments")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *

# 手で見た結果（自分の結果に書き換える）
hand_left = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]   # 消えずに残った数（1 は入れなかった）
hand_stop = 7      # この数の倍数まで消したら、それ以上消えなくなった
hand_one = "1 は約数が 1 つしかないので、残った数の仲間に入れないことにした"

# %% [markdown]
# ## 機械で
#
# まず、手でやったことをそのまま絵にする。2 の倍数を消したところ、3 まで、5 まで、7 まで。

# %%
def crossed_by(upto, n=100):
    return {q for p in range(2, upto + 1) if sympy.isprime(p) for q in range(2 * p, n + 1, p)}

grid_panels(100, [2, 3, 5, 7], titles=[f"{p} の倍数まで消した" for p in [2, 3, 5, 7]], cross_fn=crossed_by, ncol=2)

# %%
def sieve_steps(n, upto):
    """upto までの素数の倍数を消したあとに残る数（1 は含めない）"""
    left = set(range(2, n + 1))
    for p in range(2, upto + 1):
        if p in left:
            for q in range(p * p, n + 1, p):
                left.discard(q)
    return sorted(left)

machine_left = sieve_steps(100, 100)
print("機械（100 まで、全部消したあと）：", machine_left)
print("手の結果との食い違い：", sorted(set(machine_left) ^ set(hand_left)) or "なし")
compare_grid(100, hand_left, machine_left)

# 何の倍数まで消したかと、残る個数：7 で止まる
xs = [p for p in range(2, 32) if sympy.isprime(p)]
fig, ax = plt.subplots(figsize=(7, 2.6))
ax.step(xs, [len(sieve_steps(100, p)) for p in xs], where="post", color="#111", lw=1.4, label="100 の表")
ax.step(xs, [len(sieve_steps(1000, p)) / 10 for p in xs], where="post", color="#9a9a9a", lw=1.4, label="1000 の表（個数 ÷ 10）")
ax.set_xlabel("何の倍数まで消したか"); ax.set_ylabel("残る個数"); ax.legend(fontsize=8, frameon=False)
ax.set_title("消していくと残りが減り、あるところから減らなくなる", fontsize=9.5, loc="left")
plt.show()

# %% [markdown]
# **見るところ**：7 の倍数まで消すと、あとは何も消えない。なぜ 7 で足りる？（100 より小さい合成数は、必ず 10 以下の約数をもつ？）

# %%
_ = sieve_grid(100, upto=hand_stop)     # 手で止めたところまで消した表
primes_100 = sieve_grid(100)             # 最後まで消した表

# %% [markdown]
# ## もっと先へ・予想を試す
#
# 「N までの表は、○○ までの素数で消せば足りる」——自分の言葉で書いてから、いろいろな N で試す。

# %%
guess = "√N までの素数で消せば足りる"
def enough(N):
    return math.isqrt(N)

for N in [100, 1000, 10000, 100000]:
    full = sieve_steps(N, N); partial = sieve_steps(N, enough(N))
    print(f"N = {N:>6}：{enough(N):>3} までで消した残り {len(partial):>5} 個、全部消した残り {len(full):>5} 個 → {'同じ' if partial == full else 'ちがう'}")

# 400 までの表で、残った数（素数）の並びを眺める
number_grid(400, fill=sieve_steps(400, 20), cols=20, title="1〜400：残った数（素数）を黒く")

# %%
report("u1_sieve",
       f"100 の表を手で消したら {len(hand_left)} 個残り、{hand_stop} の倍数まで消したら止まった。機械と{'一致' if sorted(hand_left) == machine_left else '食い違い'}。予想「{guess}」は 100000 まで成り立った",
       data={"primes_100": machine_left, "count_1000": len(sieve_steps(1000, 1000)), "guess": guess},
       hand={"left": hand_left, "stop": hand_stop, "one": hand_one},
       params={"n_hand": 100},
       notebook="u1_sieve.ipynb")
