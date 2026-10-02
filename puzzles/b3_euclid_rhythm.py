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
# # ユークリッドのリズム：k 個の打点を n 拍にできるだけ均等に
#
# 8 拍の中に 3 回だけ手をたたく。できるだけ均等にばらまくと「タ・ン・ン・タ・ン・ン・タ・ン」。世界中の音楽にあるリズムが、これだけで出てくる。
#
# **問い：** k 個の打点を n 拍にできるだけ均等に置くと、どんなリズムになる？ k と n の最大公約数が 1 でないときは？
#
# **手で：** 印刷したリズムの円（8・12・16 拍）に、k = 3, 5, 7 の打点を「できるだけ均等に」●で置く。手をたたいて確かめる。
#
# ![リズムの円](https://jxta.github.io/kg-grounding-proto/hybrid/print/rhythm_circle.svg)
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
hand_pattern = {"3 in 8": "x..x..x.", "5 in 8": "x.xx.xx.", "4 in 8": "x.x.x.x."}   # x = たたく、. = 休み
hand_note = "3 in 8 は 3, 3, 2 の間隔。4 in 8 は 2 拍ごとで単調だった"
hand_guess = "k と n に共通の約数があると、同じ形のくり返しになる？"
TEMPO = 120                                 # 1 分間の拍数

# %% [markdown]
# ## 機械で
#
# 作り方：i 拍目に「k/n × (i+1) の整数部分」が「k/n × i の整数部分」より大きくなるなら、たたく。

# %%
def euclid(k, n):
    """k 個の打点を n 拍にできるだけ均等に（x = 打つ、. = 休み）"""
    return "".join("x" if (i + 1) * k // n > i * k // n else "." for i in range(n))

def play_rhythm(pattern, loops=4, tempo=TEMPO, freq=880):
    sec = 60 / tempo / 2                                   # 1 拍 = 8 分音符
    play([freq if c == "x" else 0 for c in pattern] * loops, sec=sec, kind="click")

def draw_rhythm(pattern, ax, title=None):
    n = len(pattern); ang = np.pi / 2 - np.linspace(0, 2 * np.pi, n, endpoint=False)   # 1 拍目が上、時計回り
    x, y = np.cos(ang), np.sin(ang)
    hits = [i for i, c in enumerate(pattern) if c == "x"]
    cm = colormaps["plasma"]
    for a, b in zip(hits, hits[1:] + hits[:1]):
        ax.plot([x[a], x[b]], [y[a], y[b]], color="#888888", lw=1)
    for i in range(n):
        ax.plot(x[i], y[i], "o", color=cm(i / n) if pattern[i] == "x" else "white", mec="#444444", ms=14 if pattern[i] == "x" else 8)
        ax.text(1.2 * x[i], 1.2 * y[i], str(i + 1), ha="center", va="center", fontsize=7, color="#555555")
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.35, 1.35)
    ax.set_title(title or pattern, fontsize=9.5, loc="left", color="#222222")

for k, n in [(3, 8), (5, 8), (5, 12), (7, 16)]:
    print(f"{k} in {n}：{euclid(k, n)}")
fig, axes = plt.subplots(1, 4, figsize=(13, 3.6))
for ax, (k, n) in zip(axes, [(3, 8), (5, 8), (5, 12), (7, 16)]):
    draw_rhythm(euclid(k, n), ax, f"{k} in {n}")
plt.show()
play_rhythm(euclid(3, 8))

# %% [markdown]
# ### 照合：手で置いた打点と、機械の打点
#
# 回して重なれば同じリズム（出発点が違うだけ）。

# %%
def same_rhythm(a, b):
    return len(a) == len(b) and any(a == b[i:] + b[:i] for i in range(len(b)))
for name, pat in hand_pattern.items():
    k, n = int(name.split()[0]), int(name.split()[2])
    m = euclid(k, n)
    print(f"{name}：手 {pat}　機械 {m}　→", "同じ（回して重なる）" if same_rhythm(pat, m) else "違う。手の方は均等？ 打点の間隔を数える")

# %% [markdown]
# ## 予想を試す
#
# 予想：「k と n に共通の約数があると、同じ形のくり返しになる」。k = 1〜7、n = 8 と、n = 12 を表にして、くり返しの回数を数える。

# %%
def repeats(p):
    """p が何回のくり返しか（最小の周期で割る）"""
    n = len(p)
    for d in range(1, n + 1):
        if n % d == 0 and p == p[:d] * (n // d):
            return n // d
for n in [8, 12]:
    print(f"n = {n}")
    for k in range(1, n):
        p = euclid(k, n)
        print(f"  k = {k:>2}  {p}  くり返し {repeats(p)} 回  gcd = {math.gcd(k, n)}")
play_rhythm(euclid(5, 12), loops=3)

# %% [markdown]
# ### なぜ「ユークリッド」？
#
# 3 in 8 を作る別の手：x を 3 個、. を 5 個用意し、「x.」を 3 組作ると . が 2 個余る。余った 2 個を 3 組のうち 2 組に配って「x..」「x..」「x.」。
# これは 8 を 3 で割って余り 2、3 を 2 で割って余り 1、…と、最大公約数を求める割り算（ユークリッドの互除法）と同じ手順。だからこの名前がついている。

# %%
def euclid_steps(k, n):
    a, b = n, k; steps = []
    while b:
        steps.append(f"{a} = {b} × {a // b} + {a % b}"); a, b = b, a % b
    return steps, a
for k, n in [(3, 8), (5, 12), (4, 8)]:
    s, g = euclid_steps(k, n); print(f"{k} in {n}：", "、".join(s), f"→ 最大公約数 {g}、くり返し {repeats(euclid(k, n))} 回")

# %% [markdown]
# **確かめること**：5 in 8 を手でたたいて、機械の音と同じか。3 in 8 と 5 in 8 を同時にたたくと？（2 人で）
#
# ここから先の問い：n = 16 で k を 1 から 15 まで鳴らして、いちばん気に入ったリズムを 1 つ選ぶ。それは何の曲に似ている？

# %%
report("b3_euclid_rhythm", "k 個の打点を n 拍に均等に置くリズム。gcd(k, n) が 1 でないと同じ形のくり返し。作り方はユークリッドの互除法",
       data={"patterns": {f"{k} in {n}": euclid(k, n) for k, n in [(3, 8), (5, 8), (5, 12), (7, 16), (4, 8)]}},
       hand={"patterns": hand_pattern, "note": hand_note, "guess": hand_guess}, params={"TEMPO": TEMPO}, notebook="b3_euclid_rhythm.ipynb")
