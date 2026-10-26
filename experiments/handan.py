"""handan — 文字列を入れると、候補ごとの数を返す小さな判定器。

ノートの中の AI の役を、文章を作らない形でやる。
  1. 反応の候補（問い返す／次の実験を促す／地図への記入を促す／黙って待つ）は、人が先に書いておく
  2. 生徒が書いた文を入れると、候補ごとに数（確率）が返る
  3. いちばん大きい候補の反応だけが出る。文章を生成しないので、先回りして説明してしまうことがない

この版は、文の特徴（数が書いてあるか、まばら・なくならない・わからない などの言葉、長さ）に
重みをつけて足す、いちばん小さい形の判定器。本物の判定モデル（文字列 → 数値）に差し替えるときは
`score()` の中身だけを替える。候補と反応文はそのまま使える。
"""
import math
import re
import unicodedata


def _pad(t, n):
    """表をそろえるための詰め物（全角を 2 文字幅として数える）"""
    w = sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in t)
    return t + " " * max(0, n - w)

# ---------- 候補（反応）。人が先に書く ----------
KOUHO = [
    ("toikaesu", "問い返す"),
    ("tsugi",    "次の実験を促す"),
    ("chizu",    "地図への記入を促す"),
    ("matsu",    "黙って待つ"),
]

# 問い返すときの問いの候補。これも人が先に書く。どれを出すかは score() と同じ仕組みで選ぶ
TOI = [
    ("hayasa", "まばらになるのは、どのくらいの速さ？ 10 ごとに数えてみると、数で言える。`kazoeru(100, 10)`"),
    ("dokomade", "どこまで見た？ 見た範囲のことと、その先のことは、分けて書けそう？"),
    ("nani", "何を見て、そう思った？ 絵のどこ？"),
]

HANNOU = {
    "tsugi": "もっと先まで描いてみよう。`ten(1000)`。点がひとつだけの数は、どうなる？",
    "chizu": "数で言えている。それは『たしかめた』と書けそう。下の `report()` で地図に送って、どのノードの根拠にするかを選ぼう",
    "matsu": "（まだ書いていないので、待っています）",
}

PLACEHOLDER = "（ここに書く）"

# ---------- 文の特徴 ----------
_SPARSE = ("まばら", "少な", "すくな", "減", "へる", "へって", "間が", "あいだが", "広が", "ひろが", "散", "ちら")
_FOREVER = ("なくならない", "無くならない", "ずっと", "いつまでも", "無限", "必ず", "ぜったい", "絶対", "全部", "かならず")
_DONTKNOW = ("わからない", "分からない", "わかんない", "わかりません", "分かりません")


def features(text):
    """文 → 特徴の集合（名前の集まり）。何に反応したかが見えるように名前で返す"""
    t = (text or "").replace(PLACEHOLDER, "").strip()
    f = set()
    if not t:
        f.add("空")
        return f
    nums = re.findall(r"\d+", t)
    if len(nums) >= 2 or "個" in t or "ごと" in t:
        f.add("数えた")
    if len(t) < 8:
        f.add("短い")
    if len(t) > 40:
        f.add("長い")
    if any(w in t for w in _SPARSE):
        f.add("まばら")
    if any(w in t for w in _FOREVER):
        f.add("その先")
    if any(w in t for w in _DONTKNOW):
        f.add("わからない")
    if "？" in t or "?" in t:
        f.add("問い")
    return f

# 特徴 → 候補ごとの重み。表にしてあるので、手で直せる
WEIGHTS = {
    #  特徴         問い返す  次の実験  地図     待つ
    "空":          {"toikaesu": -1.0, "tsugi": -1.0, "chizu": -1.0, "matsu": 3.0},
    "数えた":      {"toikaesu": -1.0, "tsugi": -0.5, "chizu": 2.5, "matsu": 0.0},
    "短い":        {"toikaesu": 0.0,  "tsugi": 1.5,  "chizu": -0.5, "matsu": 0.0},
    "長い":        {"toikaesu": 0.0,  "tsugi": -0.5, "chizu": 0.5, "matsu": 0.0},
    "まばら":      {"toikaesu": 1.5,  "tsugi": 0.0,  "chizu": 0.0, "matsu": 0.0},
    "その先":      {"toikaesu": 1.5,  "tsugi": 0.0,  "chizu": -0.5, "matsu": 0.0},
    "わからない":  {"toikaesu": 0.5,  "tsugi": 2.0,  "chizu": -1.0, "matsu": 0.0},
    "問い":        {"toikaesu": 1.0,  "tsugi": 0.0,  "chizu": 0.0, "matsu": 0.0},
}
BIAS = {"toikaesu": 0.3, "tsugi": 0.0, "chizu": -0.5, "matsu": -1.0}

TOI_WEIGHTS = {
    "まばら":  {"hayasa": 1.2, "dokomade": 0.0, "nani": 0.0},
    "その先":  {"hayasa": 0.0, "dokomade": 1.0, "nani": 0.0},
    "数えた":  {"hayasa": -1.0, "dokomade": 0.5, "nani": 0.0},
}
TOI_BIAS = {"hayasa": 0.0, "dokomade": 0.0, "nani": 0.2}


def _softmax(raw):
    m = max(raw.values())
    e = {k: math.exp(v - m) for k, v in raw.items()}
    s = sum(e.values())
    return {k: v / s for k, v in e.items()}


def score(text, candidates=None, weights=None, bias=None):
    """文字列 → 候補ごとの数（確率）。ここだけ差し替えれば本物の判定モデルになる"""
    cands = [k for k, _ in (candidates or KOUHO)]
    W, B = (weights or WEIGHTS), (bias or BIAS)
    f = features(text)
    raw = {c: B.get(c, 0.0) + sum(W[x].get(c, 0.0) for x in f if x in W) for c in cands}
    return _softmax(raw), f


def erabu(text):
    """文 → (選ばれた候補の id, 候補ごとの確率, 反応の文, 反応した特徴)"""
    p, f = score(text)
    best = max(p, key=p.get)
    if best == "toikaesu":
        q, _ = score(text, TOI, TOI_WEIGHTS, TOI_BIAS)
        qid = max(q, key=q.get)
        line = dict(TOI)[qid]
    else:
        line = HANNOU[best]
    return best, p, line, f


def kiku(text, show=True):
    """生徒が書いた文を判定器に聞く。候補ごとの数と、選ばれた反応だけを出す"""
    best, p, line, f = erabu(text)
    if show:
        names = dict(KOUHO)
        t = (text or "").replace(PLACEHOLDER, "").strip()
        print("入力：" + (("「" + t.replace("\n", " ") + "」") if t else "（まだ何も書いていない）"))
        print("反応した特徴：" + ("、".join(sorted(f)) if f else "なし"))
        print()
        print("  " + _pad("候補", 20) + "  数")
        for k, name in KOUHO:
            bar = "█" * int(round(p[k] * 20))
            mark = "→" if k == best else " "
            print(f"{mark} {_pad(name, 20)}{p[k]:6.2f}  {bar}")
        print()
        print(f"{names[best]}：{line}")
    return {"erabareta": best, "kakuritsu": {k: round(v, 3) for k, v in p.items()}, "hannou": line, "tokuchou": sorted(f)}
