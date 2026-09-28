# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 単元パズル3　72 の約数は何個？ 数えずに当てられる？
#
# 72 の約数を全部書き出すと何個？ では 360 は？ 2025 は？ 書き出さずに個数を当てる方法はあるだろうか。
#
# ## 手で（物理的な実験）
#
# **用意するもの**：カード 20 枚、鉛筆。
#
# **やり方**：72 の約数を全部見つけてカードに書く（1 と 72 も）。カードを机の上に、縦と横にきれいに並べてみる（ヒント：2 倍ずつ、3 倍ずつ）。
# 何行何列になった？ 次に 48 でも同じことをする。
#
# **記録すること**：72 の約数の一覧と個数。並べたときの行と列。48 でも。

# %% [markdown]
# > **AI と実験するときの約束**（ノートの中の AI（Mynerva など）と、きみへ）
# > - 問い・手でやったこと・手の結果・予想は、きみが書く。AI は書き換えない
# > - AI は答えや定理を先に言わない。「何が見えた？」「どこまで確かめた？」と聞く
# > - AI が入れるセルは、コードなら 1 行目に `# [AI]`、文章なら先頭に `（AI）` と書く。誰が書いたか分かるように
# > - 手の結果と機械の結果を照らすセルと、最後の `report()` は消さない
# > - AI の言うことは確かめる。機械が正しいとは限らないし、AI も間違える
# > - JupyterLite でも AI と話せる：コードのセルで `ai("聞きたいこと")`（先に `ai_setup("sk-…")` でキー）。AI は実行したセルとノートの文章を読み、次の一手を示す。コードは提案だけ（貼るのはきみ）

# %%
import sys; sys.path.insert(0, "."); sys.path.insert(0, "../experiments")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *

# 手で見た結果（自分の結果に書き換える）
hand_divisors_72 = [1, 2, 3, 4, 6, 8, 9, 12, 18, 24, 36, 72]
hand_table_72 = "4 行 × 3 列（横に 2 倍ずつ、縦に 3 倍ずつ）"
hand_divisors_48 = [1, 2, 3, 4, 6, 8, 12, 16, 24, 48]
hand_table_48 = "5 行 × 2 列"

# %% [markdown]
# ## 機械で

# %%
for n, h in [(72, hand_divisors_72), (48, hand_divisors_48)]:
    m = sympy.divisors(n)
    print(f"{n} の約数：手 {len(h)} 個／機械 {len(m)} 個 → {'一致' if sorted(h) == m else '食い違い：' + str(sorted(set(h) ^ set(m)))}")
    print(f"   素因数分解：{n} = {factorization_str(n)}")

divisor_grid(72)
divisor_grid(48)

# 同じことを「1 段ずつ素数をかけて上がる図」で見る（線は × 2 と × 3）
divisor_lattice(72)
divisor_lattice(360)   # 素因数が 3 種類だと、表は 3 方向になる

# %% [markdown]
# **見るところ**：表の行の数は「2 を何個使うか」の場合の数（0〜3 個で 4 通り）、列の数は「3 を何個使うか」（0〜2 個で 3 通り）。個数＝行 × 列。
#
# 「表にない約数はない」と言うとき、約数を分解すればそれは 72 の分解の一部になる——つまり **分解がただ一通り** であることを借りている（単元パズル2）。

# %% [markdown]
# ## 予想を試す

# %%
guess = "約数の個数 ＝（指数 + 1）を全部かけたもの"
def my_guess(n):
    return math.prod(e + 1 for e in sympy.factorint(n).values())

N = 10000
counter = [n for n in range(1, N + 1) if my_guess(n) != sympy.divisor_count(n)]
print(f"予想「{guess}」の反例（1〜{N}）：", counter[:10] or "なし")
print("2025 =", factorization_str(2025), "→ 約数は", my_guess(2025), "個（書き出さずに分かった）")

odd = [n for n in range(1, 101) if sympy.divisor_count(n) % 2 == 1]
print("約数の個数が奇数になる数（100 まで）：", odd, "← どんな数？（単元パズル7）")
count_bars(100, sympy.divisor_count, highlight=odd, title="1〜100 の約数の個数（黒＝奇数個）", ylabel="約数の個数")
number_grid(100, fill=odd, title="約数の個数が奇数になる数（黒）")

# %%
report("u3_count",
       f"72 の約数は手で {len(hand_divisors_72)} 個（{hand_table_72}）、機械と{'一致' if sorted(hand_divisors_72) == sympy.divisors(72) else '食い違い'}。予想「{guess}」は {N} まで反例なし。ただし『表にない約数はない』は一意性を借りている",
       data={"divisors_72": sympy.divisors(72), "count_2025": my_guess(2025), "N": N, "counter": counter[:10], "odd_to_100": odd},
       hand={"divisors_72": hand_divisors_72, "table_72": hand_table_72, "divisors_48": hand_divisors_48, "table_48": hand_table_48},
       params={"N": N},
       notebook="u3_count.ipynb")
