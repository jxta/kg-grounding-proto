# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # π の音楽と色紙：数字を音と色にする
#
# π の数字 3, 1, 4, 1, 5, 9, … を、0〜9 の音に当てて順に鳴らす。同じ数字を色にして並べると、π の色紙になる。
#
# **問い：** π のメロディは「でたらめ」に聞こえる？ 1 ÷ 7 = 0.142857142857… のメロディと何が違う？ 色紙に模様は出る？
#
# **手で：** π の最初の 16 個の数字を、ドレミファソラシド（0〜7）＋高いレミ（8, 9）で鳴らす（鍵盤アプリやピアニカ）。1 ÷ 7 も同じ対応で。
# %% [markdown]
# > **AI と実験するときの約束**
# >
# > - 問い・手でやったこと・手の結果・予想は、きみが書く。AI は書き換えない（頼まれても、きみに書いてもらう）
# > - AI は答えや定理を先に言わない。次の一手を一つ示す
# > - AI が入れるセルは、コードなら 1 行目に `# [AI]`、文章なら先頭に（AI）と書く
# > - 照合のセル（手と機械を照らすところ）と、最後の `report()` は消さない
# > - AI の言うことは確かめる。機械が正しいとは限らないし、AI も間違える
# > - JupyterLite でも AI と話せる：コードのセルで `ai("聞きたいこと")`（先に `ai_setup("sk-…")` でキー）。提案のコードは `ai_accept()` で下に入る（動かすのはきみ）
# %%
import sys; sys.path.insert(0, "."); sys.path.insert(0, "../experiments")
import numpy, matplotlib, sympy   # JupyterLite はこの行を見て部品を読み込む（消さない）
from kg_tools import *
import numpy as np, math
from matplotlib import colormaps
# %%
# 音を出す道具（このノートの中だけ）。ブラウザのスピーカーで鳴る。音量は小さめから
from IPython.display import Audio, display
RATE = 22050
def tone(freq, sec=0.35, kind="sine"):
    """1 つの音。freq = 0 なら休み"""
    t = np.linspace(0, sec, int(RATE * sec), endpoint=False)
    if freq <= 0:
        return np.zeros_like(t)
    env = np.minimum(1, t / 0.01) * np.exp(-3.0 * t / sec)             # 立ち上がりと減衰
    if kind == "click":
        return env * np.sin(2 * np.pi * freq * t) * np.exp(-30 * t / sec)
    return env * (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * 2 * freq * t))
def play(freqs, sec=0.35, kind="sine"):
    """周波数のリストを順に鳴らす（0 は休み）"""
    wave = np.concatenate([tone(f, sec, kind) for f in freqs])
    display(Audio(0.6 * wave / max(1e-9, np.abs(wave).max()), rate=RATE, normalize=False))
NOTE_NAMES = ["ド", "ド#", "レ", "レ#", "ミ", "ファ", "ファ#", "ソ", "ソ#", "ラ", "ラ#", "シ"]
def note_freq(n, base=0):
    """n = 0 がド（C4 = 261.6 Hz）。1 増えると半音上がる"""
    return 261.6256 * 2 ** ((n + base) / 12)

# 手で見た結果（自分の結果に書き換える）
hand_note = "π はどこに行くか分からない。1 ÷ 7 は 6 音でぐるぐる回る"
hand_guess = "割り算の答えはくり返すので、メロディもくり返す。π はくり返さない"
D = 64                                     # 鳴らす桁数
SCALE = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16]  # 0〜9 を ド レ ミ ファ ソ ラ シ ド レ ミ に

# %% [markdown]
# ## 機械で

# %%
import mpmath
mpmath.mp.dps = 1200
def digits_of(x, n):
    return [int(ch) for ch in mpmath.nstr(x, n + 2, strip_zeros=False).replace(".", "")[:n]]
pi_d = digits_of(mpmath.pi, 1000)
sev_d = digits_of(mpmath.mpf(1) / 7, 1000)
print("π   ：", "".join(map(str, pi_d[:D])))
print("1÷7 ：", "".join(map(str, sev_d[:D])))
print("π のメロディ（最初の", D, "音）")
play([note_freq(SCALE[d]) for d in pi_d[:D]], sec=0.22)
print("1 ÷ 7 のメロディ")
play([note_freq(SCALE[d]) for d in sev_d[:D]], sec=0.22)

# %%
# 色紙：数字を色に（tab10 の 10 色）。左上から右へ、π は 40 × 25 = 1000 桁
def color_sheet(ds, cols, ax, title):
    rows = len(ds) // cols
    img = np.array(ds[:rows * cols]).reshape(rows, cols)
    ax.imshow(img, cmap="tab10", vmin=0, vmax=9, interpolation="nearest"); ax.axis("off")
    ax.set_title(title, fontsize=9.5, loc="left", color="#222222")
fig, axes = plt.subplots(1, 2, figsize=(13, 4.4), gridspec_kw={"width_ratios": [2, 1]})
color_sheet(pi_d, 40, axes[0], "π の色紙（1000 桁、1 マス 1 桁）")
color_sheet(sev_d[:600], 30, axes[1], "1 ÷ 7 の色紙（600 桁）")
plt.show()

# %% [markdown]
# ### 照合：手で鳴らした 16 音と、機械の 16 音

# %%
hand_notes = ["ミ", "レ", "ソ", "レ", "ラ", "高いミ", "ミ", "シ", "ラ", "ファ", "ラ", "高いレ", "高いミ", "シ", "ソ", "ミ"]   # 手で鳴らした音（自分で書く）
names = ["ド", "レ", "ミ", "ファ", "ソ", "ラ", "シ", "高いド", "高いレ", "高いミ"]
machine_notes = [names[d] for d in pi_d[:16]]
print("手  ：", hand_notes); print("機械：", machine_notes)
print("一致" if hand_notes == machine_notes else "食い違い。数字と音の対応表を見直す（0 がド、3 がファ）")

# %% [markdown]
# ## 予想を試す
#
# 予想：「割り算の答えはくり返す。π はくり返さない」。1000 桁の中で、同じ 6 桁が何回出てくるかを数える。

# %%
def count_repeats(ds, L=6):
    from collections import Counter
    c = Counter("".join(map(str, ds[i:i + L])) for i in range(len(ds) - L))
    return c.most_common(3)
print("π   の 6 桁の並びで、いちばん多いもの：", count_repeats(pi_d))
print("1÷7 の 6 桁の並びで、いちばん多いもの：", count_repeats(sev_d))
print("→ 1 ÷ 7 は 142857 のくり返し（6 通りの回し方だけ）。π は 1000 桁の中で同じ 6 桁がほとんど出ない")

# %% [markdown]
# ### 自分の数で
#
# 分数（1 ÷ 13、22 ÷ 7）や √2 でも鳴らしてみる。くり返しが聞こえる？

# %%
for name, x in [("1 ÷ 13", mpmath.mpf(1) / 13), ("22 ÷ 7", mpmath.mpf(22) / 7), ("√2", mpmath.sqrt(2))]:
    ds = digits_of(x, 32)
    print(name, "：", "".join(map(str, ds)))
    play([note_freq(SCALE[d]) for d in ds], sec=0.2)

# %% [markdown]
# **確かめること**：1 ÷ 7 のくり返しの長さは 6。1 ÷ 13 は？ 1 ÷ 17 は？（くり返しの長さが分母 − 1 になる分数と、ならない分数がある）
#
# ここから先の問い：数字を「音の長さ」にしたら？ 2 桁ずつ読んで 0〜99 を色にしたら？

# %%
report("b4_pi_music", f"π の {D} 桁を 10 音に当てて鳴らした。1÷7 は 142857 のくり返し、π は 1000 桁で同じ 6 桁がほぼ出ない",
       data={"D": D, "pi_top6": count_repeats(pi_d), "sev_top6": count_repeats(sev_d)}, hand={"note": hand_note, "guess": hand_guess, "notes16": hand_notes},
       params={"D": D, "SCALE": SCALE}, notebook="b4_pi_music.ipynb")
