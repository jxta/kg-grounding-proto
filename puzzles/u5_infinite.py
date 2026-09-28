# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 単元パズル5　いちばん大きい素数はある？
#
# 「素数は 2, 3, 5, 7 で全部だ」と言う人がいる。反論できる？ ヒント：全部かけて 1 を足してみる。
#
# ## 手で（物理的な実験）
#
# **用意するもの**：素数を書いたカード（2, 3, 5, 7, 11）、紙と鉛筆（筆算）。
#
# **やり方**：2 × 3 + 1、2 × 3 × 5 + 1、2 × 3 × 5 × 7 + 1 を筆算で計算する。できた数を、カードの素数（2, 3, 5, 7）で割ってみて、余りを書く。
# できた数は素数か？ 素数でなければ、何で割り切れる？
#
# **記録すること**：3 つの数と、それぞれをカードの素数で割った余り。素数かどうか。

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
hand_values = {"2×3+1": 7, "2×3×5+1": 31, "2×3×5×7+1": 211}
hand_remainders = "どれも、2, 3, 5, 7 で割ると余りは 1 だった"
hand_prime = {"7": True, "31": True, "211": True}   # 素数だと思ったか

# %% [markdown]
# ## 機械で

# %%
prod = 1
for k, p in enumerate([2, 3, 5, 7, 11, 13], 1):
    prod *= p; n = prod + 1
    rem = [n % q for q in [2, 3, 5, 7][:min(k, 4)]]
    print(f"{'×'.join(map(str, [2, 3, 5, 7, 11, 13][:k])):>16} + 1 = {n:>6}　余り {rem}　{'素数' if sympy.isprime(n) else '素数ではない：' + factorization_str(n)}")

for label, v in hand_values.items():
    n = eval(label.replace("×", "*"))
    print(f"手の計算 {label} = {v} → 機械 {n} → {'一致' if v == n else '計算ちがい'}")

# %% [markdown]
# **見るところ**：全部かけて 1 を足した数は、かけた素数のどれで割っても 1 余る。だからその素因数は、かけた素数の中にない **新しい素数**。
# 素数になることもあれば（7, 31, 211）、ならないこともある（30031 = 59 × 509）。でも新しい素数が必ず出る。
#
# **反論**：「2, 3, 5, 7 で全部」なら 211 の素因数はどこから来た？ 何個並べても同じ反論ができる → いちばん大きい素数はない。

# %%
rows = euclid_numbers(10)

# 「どれで割っても 1 余る」を絵で：31 個の点を 2 個ずつ、3 個ずつ、5 個ずつ並べると、必ず 1 個余る
remainder_panels(31, [2, 3, 5])
remainder_panels(211, [2, 3, 5, 7])

# ユークリッドの数の大きさ（対数目盛）と、素数かどうか
fig, ax = plt.subplots(figsize=(7, 2.8))
ks = [i for i, p, n, fs, new in rows]; ns = [n for i, p, n, fs, new in rows]
ax.plot(ks, ns, "-", color="#9a9a9a", lw=1)
for i, p, n, fs, new in rows:
    ax.plot([i], [n], "o", color="#111" if sympy.isprime(n) else "white", mec="#111", ms=7)
ax.set_yscale("log"); ax.set_xlabel("k（かけた素数の個数）"); ax.set_ylabel("2×3×…×p + 1")
ax.set_title("黒＝素数、白＝素数ではない（でも新しい素数を含む）", fontsize=9.5, loc="left")
plt.show()

# %% [markdown]
# ## 予想を試す
#
# 「全部かけて 1 を足すと素数になる」という予想は？ 「新しい素数が必ず出る」は？

# %%
guess1 = "全部かけて 1 を足した数は、いつも素数"
guess2 = "全部かけて 1 を足した数の素因数は、いつも新しい素数"
c1 = [i for i, p, n, fs, new in rows if not sympy.isprime(n)]
c2 = [i for i, p, n, fs, new in rows if any(q <= p for q in sympy.factorint(n))]
print(f"予想 1「{guess1}」の反例（k = 1〜10）：", c1 or "なし", "（k=6 は 30031 = 59 × 509）" if 6 in c1 else "")
print(f"予想 2「{guess2}」の反例（k = 1〜10）：", c2 or "なし")

# %%
report("u5_infinite",
       f"手で 7, 31, 211 を作り、2,3,5,7 で割ると余りは 1 だった。機械と{'一致' if all(v == eval(l.replace('×', '*')) for l, v in hand_values.items()) else '計算ちがい'}。予想 1「{guess1}」は k=6 で外れ、予想 2「{guess2}」は k=1〜10 で反例なし → 反論の筋が立つ",
       data={"euclid": [[i, n, fs] for i, p, n, fs, new in rows], "counter1": c1, "counter2": c2},
       hand={"values": hand_values, "remainders": hand_remainders, "prime": hand_prime},
       params={"k": 10},
       notebook="u5_infinite.ipynb")
