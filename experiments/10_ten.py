# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 実験10　てん

# %%
import sys; sys.path.insert(0, ".")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *
from handan import kiku, tsunagu

ten(30)

# %% [markdown]
# 何が見える？
#
# 点がひとつだけの数は、どこにある？

# %%
ten(100)     # ← 数を変えて、もっと先まで

# %%
kazoeru(100, 10);    # 10 ごとに、点がひとつだけの数は何個？（数と区切りは変えてよい）

# %% [markdown]
# ## 見えたことを、自分の言葉で
#
# 下の `mita` に書いて、そのセルを実行する。
# 文章を作る AI はいない。きみの文を読んで、用意してある反応（問い返す／次の実験を促す／地図への記入を促す／黙って待つ）の
# どれを出すかを、数で決めるだけ。候補ごとの数も見える。
#
# 手元のパソコンで判定モデルを動かしていれば（`handan.py` の説明を見る）、`kiku()` はそれに聞く。なければ、言葉の規則で決める。表はどちらも同じ。
#
# 判定モデルを動かしているとき、初回だけブラウザが「ローカルネットワーク…への接続」の許可を聞いてくるので「許可」。
# 聞かれないのに「規則版」と出るなら、新しいセルで `tsunagu()` を一度実行してから、もう一度。

# %%
mita = """
（ここに書く）
"""   # 自分の結果に書き換える

kiku(mita);

# %% [markdown]
# ## 地図に送る
#
# 自分の言葉で書けたら、地図アプリに送る。どのノードの根拠にするか、印をどうするかは、地図の側で自分が決める。
# `TEN` には、最後に描いた数と、数えた結果が入っている（同じ条件なら同じ値になる）。

# %%
report("exp10", mita.replace("（ここに書く）", "").strip() or "（まだ書いていない）",
       {"N": TEN["N"], "block": TEN["block"], "counts": TEN["counts"]},
       params={"N": TEN["N"], "block": TEN["block"]}, notebook="10_ten.ipynb");
