# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 単元パズル4　あめ 24 個とチョコ 36 個を、余りなく同じ人数で分ける
#
# 何人なら、あめもチョコも余りなく分けられる？ 最大何人？
# もう一つ：24 cm の棒と 36 cm の棒を、それぞれつなげていく。端が初めてそろうのは何 cm のとき？
#
# ## 手で（物理的な実験）
#
# **用意するもの**：おはじき 2 色（24 個と 36 個）、方眼紙。
#
# **やり方**：24 個を 2 人分、3 人分、4 人分…と等しく分けてみる。36 個でも。両方とも余りなく分けられる人数を全部見つける。
# 方眼紙に 24 マスの棒と 36 マスの棒をつなげて描き、端がそろうところに印。
#
# **記録すること**：両方とも分けられる人数の一覧と最大。端がそろう長さ（最初と、その次）。

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
hand_people = [1, 2, 3, 4, 6, 12]      # 両方とも余りなく分けられる人数
hand_max = 12
hand_align = [72, 144]                 # 棒の端がそろう長さ

# %% [markdown]
# ## 機械で

# %%
a, b = 24, 36
common = [k for k in range(1, min(a, b) + 1) if a % k == 0 and b % k == 0]
g, l = math.gcd(a, b), math.lcm(a, b)
print("両方の約数（機械）：", common, "→ 最大", g, "／手：", hand_people, "→ 最大", hand_max, "→", "一致" if common == sorted(hand_people) and g == hand_max else "食い違い")
print("端がそろう長さ（機械）：", [l, 2 * l], "／手：", hand_align, "→", "一致" if hand_align[:2] == [l, 2 * l] else "食い違い")

share_dots(24, 36, 12)      # 12 人で分けると、どちらも余りなし
share_dots(24, 36, 8)       # 8 人だと？
sticks(24, 36, 150)         # 棒の端がそろう所

def side_by_side(a, b):
    fa, fb = sympy.factorint(a), sympy.factorint(b)
    ps = sorted(set(fa) | set(fb))
    print(f"{'':>6}" + "".join(f"{p:>5}" for p in ps) + "   （指数）")
    print(f"{a:>6}" + "".join(f"{fa.get(p, 0):>5}" for p in ps))
    print(f"{b:>6}" + "".join(f"{fb.get(p, 0):>5}" for p in ps))
    g = math.prod(p ** min(fa.get(p, 0), fb.get(p, 0)) for p in ps)
    l = math.prod(p ** max(fa.get(p, 0), fb.get(p, 0)) for p in ps)
    print(f"小さい方の指数 → {g} = {factorization_str(g)}（最大公約数）")
    print(f"大きい方の指数 → {l} = {factorization_str(l)}（最小公倍数）")

side_by_side(24, 36)
exponent_bars([24, 36, 12, 72])   # 24 と 36 の指数の、小さい方が 12、大きい方が 72
divisor_lattice(12)               # 最大公約数 12 の約数＝両方の約数

# %% [markdown]
# **見るところ**：素因数分解を並べると、共通の部分（小さい方の指数）が最大公約数、両方をおおう部分（大きい方の指数）が最小公倍数。
# 24 × 36 = 12 × 72 になっている。指数で見ると min + max = 足した指数、だから。

# %% [markdown]
# ## 予想を試す

# %%
guess = "小さい方の指数をとると最大公約数、大きい方をとると最小公倍数"
def by_exp(a, b):
    fa, fb = sympy.factorint(a), sympy.factorint(b); ps = set(fa) | set(fb)
    return math.prod(p ** min(fa.get(p, 0), fb.get(p, 0)) for p in ps), math.prod(p ** max(fa.get(p, 0), fb.get(p, 0)) for p in ps)

N = 200
counter = [(x, y) for x in range(2, N + 1) for y in range(x, N + 1) if by_exp(x, y) != (math.gcd(x, y), math.lcm(x, y))]
print(f"予想「{guess}」の反例（2〜{N} の全部の組）：", counter[:10] or "なし")

# %%
report("u4_share",
       f"24 と 36 を手で分けたら人数は {hand_people}（最大 {hand_max}）、棒の端は {hand_align} でそろった。機械と{'一致' if common == sorted(hand_people) and hand_align[:2] == [l, 2 * l] else '食い違い'}。予想「{guess}」は {N} まで反例なし",
       data={"common": common, "gcd": g, "lcm": l, "N": N, "counter": counter[:10]},
       hand={"people": hand_people, "max": hand_max, "align": hand_align},
       params={"a": 24, "b": 36, "N": N},
       notebook="u4_share.ipynb")
