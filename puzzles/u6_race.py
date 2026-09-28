# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 単元パズル6　素数を 4 で割った余りは、1 と 3 のどっちが多い？
#
# 2 以外の素数を 4 で割ると、余りは 1 か 3。100 までの素数で数えると、どっちが多い？ もっと先まで数えると？
#
# ## 手で（物理的な実験）
#
# **用意するもの**：単元パズル1 で作った 100 までの素数の表（または素数の一覧）、2 色のおはじき。
#
# **やり方**：素数を 4 で割った余りで 2 つの山に分ける（余り 1 に白、余り 3 に黒を置く）。2 だけは別。数える。
#
# **記録すること**：余り 1 の素数の個数と一覧、余り 3 の個数と一覧。どっちが多いか。

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
hand_r1 = [5, 13, 17, 29, 37, 41, 53, 61, 73, 89, 97]
hand_r3 = [3, 7, 11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83]
hand_note = "余り 3 の方が 2 個多かった"

# %% [markdown]
# ## 機械で

# %%
r1 = [p for p in sympy.primerange(3, 101) if p % 4 == 1]
r3 = [p for p in sympy.primerange(3, 101) if p % 4 == 3]
print(f"余り 1（100 まで）：機械 {len(r1)} 個、手 {len(hand_r1)} 個 → {'一致' if sorted(hand_r1) == r1 else '食い違い：' + str(sorted(set(hand_r1) ^ set(r1)))}")
print(f"余り 3（100 まで）：機械 {len(r3)} 個、手 {len(hand_r3)} 個 → {'一致' if sorted(hand_r3) == r3 else '食い違い：' + str(sorted(set(hand_r3) ^ set(r3)))}")

number_grid(100, fill=r3, ring=r1, title="100 までの素数：黒＝余り 3、丸＝余り 1（2 は白）")
compare_grid(100, hand_r3, r3, title="余り 3 の素数：手と機械を照らす（黒＝両方、丸＝機械だけ、斜線＝手だけ）")

race_lines(1000)      # 2 本の線で見る：どっちが上？
race_lines(30000)
D = prime_race(30000)  # 差で見る：0 を割るところ

# %% [markdown]
# **見るところ**：100 まででは余り 3 が多い。1000 でも 10000 でも余り 3 が多い。ここで「いつも余り 3 が多い」と言いたくなる。
# でも 26861 で初めて余り 1 の方が多くなる。手で 100 まで数えたことと、いつでも成り立つことは、別。

# %% [markdown]
# ## 予想を試す

# %%
guess = "どこまで数えても、余り 3 の素数の方が多いか同じ"
import numpy as np
neg = np.nonzero(D < 0)[0]
first = int(neg[0]) if len(neg) else None
print(f"予想「{guess}」の反例：", f"x = {first} で余り 1 の方が多くなる" if first else "30000 までなし")
print("さらに先（62 万あたり）でも逆転が起きる。何回でも逆転することは 1914 年に証明されている（Littlewood）。中学の道具ではその証明は書けない")

# %%
report("u6_race",
       f"100 までを手で分けると余り 1 が {len(hand_r1)} 個、余り 3 が {len(hand_r3)} 個。機械と{'一致' if sorted(hand_r1) == r1 and sorted(hand_r3) == r3 else '食い違い'}。予想「{guess}」は x = {first} で外れた",
       data={"r1_100": r1, "r3_100": r3, "first_flip": first, "N": 30000},
       hand={"r1": hand_r1, "r3": hand_r3, "note": hand_note},
       params={"n_hand": 100, "N": 30000},
       notebook="u6_race.ipynb")
