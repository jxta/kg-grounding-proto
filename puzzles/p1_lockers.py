# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # パズル1　100 個のロッカー
#
# 廊下に閉まったロッカーが 100 個。100 人が順番に通る。
# 1 人目は全部のロッカーを開ける。2 人目は 2, 4, 6, … 番のロッカーを閉める。3 人目は 3, 6, 9, … 番を「開いていれば閉め、閉まっていれば開ける」。
# k 人目は k の倍数のロッカーをひっくり返す。100 人が通ったあと、開いているロッカーはどれ？
#
# ## 手で（物理的な実験）
#
# **用意するもの**：カード 20 枚（トランプでも紙でも）。裏向きに 1 列に並べ、左から 1, 2, …, 20 番とする。
#
# **やり方**：1 人目は全部めくる。2 人目は 2, 4, 6, … 番をめくり返す。3 人目は 3, 6, 9, … 番。… 20 人目は 20 番だけ。
# 20 人が通ったあと、**表になっているカードの番号** を書きとめる。
#
# **記録すること**：表のカードの番号。それと、途中で気づいたこと（何番のカードは何回めくられた？）。

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

# 手で見た結果をここに書く（自分の結果に書き換える）
hand_open = [1, 4, 9, 16]        # 20 枚でやって、最後に表だった番号
hand_note = "何回めくられたかを数えたら…"

# %% [markdown]
# ## 機械で（コンピュータ上の実験）
#
# 同じことをコンピュータでやる。まず手と同じ 20 枚。手の結果と食い違ったら、どちらが間違えたかを考える（機械が正しいとは限らない。プログラムが間違うこともある）。

# %%
def lockers(n):
    open_ = [False] * (n + 1)
    for k in range(1, n + 1):
        for j in range(k, n + 1, k):
            open_[j] = not open_[j]
    return [j for j in range(1, n + 1) if open_[j]]

lockers_strip(20, 20)     # 手でやったことをそのまま絵に：人ごとの行
machine_20 = lockers(20)
print("機械（20 枚）：", machine_20)
print("手　（20 枚）：", hand_open)
diff = sorted(set(machine_20) ^ set(hand_open))
print("食い違い：", diff if diff else "なし")
compare_grid(20, hand_open, machine_20)

# %% [markdown]
# **見るところ**：食い違いがあれば、その番号のカードを手でもう一度やってみる。何回めくられる？（めくられる回数＝その番号の約数の個数）

# %%
for n in [100, 1000]:
    print(f"{n} 個のロッカー：開いているのは", lockers(n)[:12], "…" if n > 100 else "", f"（{len(lockers(n))} 個）")

# 何回めくられたか（＝約数の個数）を並べる
print()
print("番号 :", *[f"{j:>3}" for j in range(1, 21)])
print("回数 :", *[f"{len(sympy.divisors(j)):>3}" for j in range(1, 21)])
count_bars(100, sympy.divisor_count, highlight=lockers(100), title="何回めくられたか（1〜100）。黒＝最後に開いている", ylabel="回数")
number_grid(100, fill=lockers(100), title="100 個のロッカー：最後に開いているもの（黒）")

# %% [markdown]
# ## 予想を試す
#
# 「開いているロッカーの番号は ○○ な数」——自分の言葉で予想を書いてから、機械で N まで試す。

# %%
guess = "平方数"                       # ← 自分の予想を言葉で
def my_guess(j):                        # ← 予想を式にする（例：平方数）
    r = math.isqrt(j)
    return r * r == j

N = 10000
opened = set(lockers(N))
counter = [j for j in range(1, N + 1) if (j in opened) != my_guess(j)]
print(f"予想「{guess}」と機械の結果が食い違う番号（{N} まで）：", counter[:10] if counter else "なし")

# %% [markdown]
# ## 記録を送る
#
# 手の結果・機械の結果・条件・このノートの版を、地図アプリに届ける（再現できる記録＝接地のリンク）。

# %%
report("p1_lockers",
       f"20 枚を手でやって表だったのは {hand_open}。機械で 100 個だと {lockers(100)}。予想「{guess}」は {N} まで{'当たり' if not counter else '外れ'}",
       data={"open_100": lockers(100), "count_1000": len(lockers(1000)), "guess": guess, "counter_to_N": counter[:10], "N": N},
       hand={"n": 20, "open": hand_open, "note": hand_note},
       params={"n_hand": 20, "N": N},
       notebook="p1_lockers.ipynb")
