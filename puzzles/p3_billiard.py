# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # パズル3　ビリヤードの玉はどの角に着く？
#
# 縦 m マス・横 n マスの長方形の台。左下の角から 45° に玉を打つ。壁に当たると跳ね返り、どこかの角に着くと止まる。
# どの角に着く？ 何回跳ね返る？ 台の大きさを変えると？
#
# ## 手で（物理的な実験）
#
# **用意するもの**：方眼紙と鉛筆（またはマス目のあるノート）。
#
# **やり方**：3 × 5 の長方形を描く。左下の角から、マス目の対角線をなぞって 45° の線を引く。壁に当たったら折り返す（入ってきた角度と同じ角度で）。
# 角に着いたら終わり。着いた角（左上・右上・右下）と、跳ね返った回数を記録。4 × 6、4 × 7、6 × 9、5 × 5 でも。
#
# **記録すること**：台の大きさ、着いた角、跳ね返りの回数。線が通らなかったマスはあった？

# %% [markdown]
# > **AI と実験するときの約束**（ノートの中の AI（Mynerva など）と、きみへ）
# > - 問い・手でやったこと・手の結果・予想は、きみが書く。AI は書き換えない
# > - AI は答えや定理を先に言わない。「何が見えた？」「どこまで確かめた？」と聞く
# > - AI が入れるセルは、コードなら 1 行目に `# [AI]`、文章なら先頭に `（AI）` と書く。誰が書いたか分かるように
# > - 手の結果と機械の結果を照らすセルと、最後の `report()` は消さない
# > - AI の言うことは確かめる。機械が正しいとは限らないし、AI も間違える

# %%
import sys; sys.path.insert(0, "."); sys.path.insert(0, "../experiments")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *

# 手で見た結果（(縦, 横): (着いた角, 跳ね返り回数)。角は "左上" "右上" "右下" のどれか。自分の結果に書き換える）
hand = {(3, 5): ("右上", 6), (4, 6): ("左上", 3), (4, 7): ("左上", 9), (6, 9): ("左上", 3), (5, 5): ("右上", 0)}

# %% [markdown]
# ## 機械で

# %%
def billiard(m, n):
    """左下 (0,0) から (1,1) 方向へ。壁で折り返し、角で止まる。戻り値：(着いた角, 跳ね返り回数, 通った点)"""
    x, y, dx, dy, bounces, path = 0, 0, 1, 1, 0, [(0, 0)]
    while True:
        x += dx; y += dy; path.append((x, y))
        at_x, at_y = x in (0, n), y in (0, m)
        if at_x and at_y:
            corner = {(0, m): "左上", (n, m): "右上", (n, 0): "右下", (0, 0): "左下"}[(x, y)]
            return corner, bounces, path
        if at_x: dx = -dx; bounces += 1
        if at_y: dy = -dy; bounces += 1

for (m, n), (hc, hb) in hand.items():
    c, b, _ = billiard(m, n)
    ok = "一致" if (c, b) == (hc, hb) else f"食い違い（機械：{c}, {b} 回）"
    print(f"{m} × {n}：手 {hc}・{hb} 回、機械 {c}・{b} 回 → {ok}")

# %%
billiard_panels([(3, 5), (4, 6), (4, 7), (6, 9), (5, 5)])

# 跳ね返りを「台を折り返して並べる」と、道はまっすぐな線になる
billiard_unfold(3, 5)
billiard_unfold(4, 6)

# 台の大きさごとの跳ね返り回数の表（濃いほど最大公約数が大きい）
bounce_table(8, 10)

# %% [markdown]
# **見るところ**：跳ね返りの回数と、m と n の共通の約数（最大公約数）の関係。着く角は、m と n を最大公約数で割った数の偶奇で決まる？

# %%
print(f"{'m×n':>6} {'角':>4} {'回数':>4} {'gcd':>4} {'m/g':>4} {'n/g':>4}")
for m in range(2, 8):
    for n in range(m, 10):
        c, b, _ = billiard(m, n); g = math.gcd(m, n)
        print(f"{m:>3}×{n:<2} {c:>4} {b:>4} {g:>4} {m//g:>4} {n//g:>4}")

# %% [markdown]
# ## 予想を試す
#
# 「跳ね返りの回数は ○○」——式にして、N × N までの全部の台で試す。

# %%
guess = "m/g + n/g − 2（g は最大公約数）"
def my_guess(m, n):
    g = math.gcd(m, n)
    return m // g + n // g - 2

N = 60
counter = [(m, n) for m in range(1, N + 1) for n in range(1, N + 1) if billiard(m, n)[1] != my_guess(m, n)]
print(f"予想「{guess}」の反例（{N}×{N} まで）：", counter[:10] or "なし")

# %%
report("p3_billiard",
       f"3×5 など 5 つの台を手でなぞった結果は機械と{'すべて一致' if all(billiard(m, n)[:2] == v for (m, n), v in hand.items()) else '一部食い違い'}。"
       f"跳ね返り回数の予想「{guess}」は {N}×{N} まで{'反例なし' if not counter else '反例あり'}",
       data={"table": {f"{m}x{n}": list(billiard(m, n)[:2]) for m in range(2, 8) for n in range(m, 10)}, "N": N, "counter": counter[:10]},
       hand={f"{m}x{n}": list(v) for (m, n), v in hand.items()},
       params={"N": N},
       notebook="p3_billiard.ipynb")
