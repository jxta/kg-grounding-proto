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
# # 音の糸かけ：12 本の釘を 12 の音にする
#
# 釘を 12 本にして、ド・ド#・レ・…・シ の 12 の音を当てる。k ずつ回って、通った釘の音を順に鳴らす。
#
# **問い：** k = 7 で回ると、どんなメロディになる？ 全部の音を通る k はどれ？（糸 1 本で回りきる k と同じ？）
#
# **手で：** 印刷した 12 音の円で、k = 7 ずつ線を結び、通った音を書き出す。鍵盤アプリやピアニカがあれば鳴らしてみる。
#
# ![12 音の円](https://jxta.github.io/kg-grounding-proto/hybrid/print/sound_circle_12.svg)
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
hand_k = 7
hand_sequence = ["ド", "ソ", "レ", "ラ", "ミ", "シ", "ファ#", "ド#", "ソ#", "レ#", "ラ#", "ファ"]   # k = 7 で通った音
hand_note = "ド・ソ・レ・ラ…と、知っている音の並びが出た。12 個全部を通って戻った"
hand_guess = "糸 1 本で回りきる k（gcd が 1）なら、12 の音を全部通る"
K = 7                                      # 機械で鳴らす k

# %% [markdown]
# ## 機械で

# %%
def circle_notes(k, start=0, n=12):
    """start の音から k ずつ。出発に戻るまでの音の番号"""
    seq = [start]; i = start
    while True:
        i = (i + k) % n
        if i == start:
            break
        seq.append(i)
    return seq

seq = circle_notes(K)
print(f"k = {K}：", " → ".join(NOTE_NAMES[i] for i in seq), f"（{len(seq)} 音、糸 {math.gcd(12, K)} 本）")
play([note_freq(i) for i in seq] + [note_freq(0)], sec=0.35)

# %%
# 絵：12 の音を色で（色相環）、線は鳴らした順
def draw_circle(k, ax, start=0):
    ang = np.linspace(0, 2 * np.pi, 12, endpoint=False) + np.pi / 2
    x, y = np.cos(ang), np.sin(ang); cm = colormaps["hsv"]
    seq = circle_notes(k, start)
    for t, (a, b) in enumerate(zip(seq, seq[1:] + [start])):
        ax.plot([x[a], x[b]], [y[a], y[b]], color=cm(t / 12), lw=2)
    for i in range(12):
        ax.plot(x[i], y[i], "o", color=cm(i / 12), ms=12, mec="#333333")
        ax.text(1.18 * x[i], 1.18 * y[i], NOTE_NAMES[i], ha="center", va="center", fontsize=8)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.35, 1.35)
    ax.set_title(f"k = {k}：{len(seq)} 音で戻る", fontsize=9.5, loc="left", color="#222222")
fig, axes = plt.subplots(1, 4, figsize=(13, 3.6))
for ax, k in zip(axes, [1, 5, 7, 4]):
    draw_circle(k, ax)
plt.show()

# %% [markdown]
# ### 照合：手で書いた音の並びと、機械の並び

# %%
machine_sequence = [NOTE_NAMES[i] for i in circle_notes(hand_k)]
print("手  ：", hand_sequence); print("機械：", machine_sequence)
print("一致" if hand_sequence == machine_sequence else "食い違い。どこから？（ド# とレ# の読み間違いが多い）")

# %% [markdown]
# ## 予想を試す
#
# 予想：「糸 1 本で回りきる k は、12 の音を全部通る」。k = 1〜11 で、通る音の数と糸の本数（gcd）を表にして、全部鳴らす。

# %%
print(f"{'k':>3} {'通る音の数':>8} {'gcd(12,k)':>10}  並び")
for k in range(1, 12):
    s = circle_notes(k)
    print(f"{k:>3} {len(s):>8} {math.gcd(12, k):>10}  {' '.join(NOTE_NAMES[i] for i in s)}")
# k = 1, 3, 4 を続けて鳴らす（間に休み）
wave_freqs = []
for k in [1, 3, 4]:
    wave_freqs += [note_freq(i) for i in circle_notes(k)] + [note_freq(0), 0, 0]
play(wave_freqs, sec=0.25)

# %% [markdown]
# **確かめること**：k = 7 の並びは、音楽では「五度圈」と呼ばれる並び（ドの次がソ）。k = 5 は逆回り（ドの次がファ）。k = 4 で 3 音だけになるのは、ノート a1 の「糸 3 本」と同じこと？
#
# ここから先の問い：k = 7 の並びを、3 音ずつ同時に鳴らすと（和音）？ 釘を 7 本（ドレミファソラシ）にして k = 2 で回ると？（`circle_notes(2, n=7)`）

# %%
report("b2_sound_circle", f"12 の音を k = {K} で回ると {len(seq)} 音で戻る（五度圈）。全部の音を通る k は gcd(12, k) = 1 の k",
       data={"K": K, "sequence": machine_sequence, "all": {str(k): len(circle_notes(k)) for k in range(1, 12)}},
       hand={"k": hand_k, "sequence": hand_sequence, "note": hand_note, "guess": hand_guess}, params={"K": K}, notebook="b2_sound_circle.ipynb")
