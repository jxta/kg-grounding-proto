"""handan — 文字列を入れると、候補ごとの数を返す判定器。

ノートの中の AI の役を、文章を作らない形でやる。
  1. 反応の候補（問い返す／次の実験を促す／地図への記入を促す／黙って待つ）は、人が先に書いておく
  2. 生徒が書いた文を入れると、候補ごとに数（確率）が返る
  3. いちばん大きい候補の反応だけが出る。文章を生成しないので、先回りして説明してしまうことがない

判定の中身は二つある。
  - 判定モデル：手元の Mac で動かした kev（TypeSafe の Jev と同じ /v1/systemone API を話す、公開重みの判定モデル。
    https://github.com/jaredpalmer/kev ）に、Choice 1 本（4 候補）と Noul 4 本（文の特徴）を一度に投げる。
    `kiku()` は最初に http://127.0.0.1:8009 を探し、動いていればそれを使う。別の場所や Jev なら `setup()` で指定する
  - 規則版：文の特徴（数が書いてあるか、まばら・なくならない・わからない などの言葉、長さ）に重みをつけて足す、
    いちばん小さい形の判定器。モデルに届かないときはこちらで動く。表示は同じ
候補と反応文は共通。モデルを替えるときも `score()` より下は触らなくてよい。
"""
import json
import math
import re
import sys
import time
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

# 問い返すときの問いの候補。これも人が先に書く。どれを出すかは特徴から同じ仕組みで選ぶ
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

# ---------- 規則版：文の特徴 ----------
_SPARSE = ("まばら", "少な", "すくな", "減", "へる", "へって", "間が", "あいだが", "広が", "ひろが", "散", "ちら")
_FOREVER = ("なくならない", "無くならない", "ずっと", "いつまでも", "無限", "必ず", "ぜったい", "絶対", "全部", "かならず")
_DONTKNOW = ("わからない", "分からない", "わかんない", "わかりません", "分かりません")


def _clean(text):
    return (text or "").replace(PLACEHOLDER, "").strip()


def features(text):
    """文 → 特徴の集合（名前の集まり）。何に反応したかが見えるように名前で返す"""
    t = _clean(text)
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

# 問いの選び方（特徴 → 問いの候補ごとの重み）。モデル版でも規則版でも、特徴からこの表で選ぶ
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


def _linear(feats, candidates, weights, bias):
    """特徴の集合 → 候補ごとの確率（重みを足して softmax）"""
    cands = [k for k, _ in candidates]
    raw = {c: bias.get(c, 0.0) + sum(weights[x].get(c, 0.0) for x in feats if x in weights) for c in cands}
    return _softmax(raw)


# ---------- 判定モデル（kev / Jev）----------
# 一度の呼び出しで投げる質問。id は模型には見えない。instructions と criteria が模型の読むすべて
SHITSUMON = {
    "hannou": {
        "type": "choice",
        "instructions": ("中学生が、1 から N までの数の上に、その数を割り切る 2 以上の数の個数だけ点を打った絵を見て、"
                         "見えたことを自分の言葉で書いた文です（点がひとつだけの数は素数）。"
                         "先生役として、この文にいま返す反応として最もよいものを選んでください。答えや教科書の言葉は先に教えません。"),
        "criteria": {
            "toikaesu": "問い返す。観察や主張は書いてあるが、根拠（どこまで見たか、どのくらいの速さか、何を見てそう思ったか）がまだ言葉になっていない",
            "tsugi":    "次の実験を促す。短い、分からないと言っている、まだほとんど見ていない、具体的な観察がない",
            "chizu":    "地図への記入を促す。見た範囲や数えた結果が具体的に書けていて、『たしかめた』として記録できる",
            "matsu":    "黙って待つ。まだ書きかけで、考えている途中",
        },
    },
    "kazoeta":   {"type": "noul", "instructions": "数えた結果（個数や範囲の数字）が具体的に書いてある"},
    "mabara":    {"type": "noul", "instructions": "点がひとつだけの数が、先に行くほど少なくなる・まばらになる、ということに触れている"},
    "sonosaki":  {"type": "noul", "instructions": "見た範囲を超えて、ずっと続く・なくならない・無限にある、など先のことまで主張している"},
    "wakaranai": {"type": "noul", "instructions": "分からない、と言っている"},
}
NOUL_NAMES = {"kazoeta": "数えた", "mabara": "まばら", "sonosaki": "その先", "wakaranai": "わからない"}

MODEL = {"base_url": None, "key": None, "model": "kev-latest", "timeout": 30, "probed": False, "last": None}
DEFAULT_URL = "http://127.0.0.1:8009"


def _http(method, url, body=None, key=None, timeout=30):
    """JupyterLite（Pyodide のワーカー）では同期 XHR、手元では urllib"""
    headers = {"content-type": "application/json"}
    if key:
        headers["authorization"] = "Bearer " + key
    data = json.dumps(body, ensure_ascii=False) if body is not None else None
    if sys.platform == "emscripten":
        import js
        xhr = js.XMLHttpRequest.new()
        xhr.open(method, url, False)
        try:
            xhr.timeout = int(timeout * 1000)
        except Exception:
            pass
        for k, v in headers.items():
            xhr.setRequestHeader(k, v)
        xhr.send(data)
        status, text = int(xhr.status), str(xhr.responseText)
    else:
        import urllib.request, urllib.error
        req = urllib.request.Request(url, data=data.encode("utf-8") if data else None, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                status, text = r.status, r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            status, text = e.code, e.read().decode("utf-8", "replace")
    if status != 200:
        raise RuntimeError(f"HTTP {status}：{text[:200]}")
    return json.loads(text)


def setup(base_url=DEFAULT_URL, key=None, model="kev-latest", quiet=False):
    """判定モデルの場所を指定する。手元の kev なら既定のまま。TypeSafe の Jev なら
    setup("https://api.typesafe.ai", key="…", model="jev-latest")。届かなければ規則版で動く"""
    MODEL.update(base_url=(base_url or "").rstrip("/") or None, key=key, model=model, probed=True)
    if not MODEL["base_url"]:
        if not quiet:
            print("判定モデルは使いません（規則版で動きます）")
        return False
    try:
        info = _http("GET", MODEL["base_url"] + "/v1/models", key=key, timeout=5)
        names = [m.get("name") for m in info.get("data", info.get("models", []))] if isinstance(info, dict) else []
        if not quiet:
            print(f"判定モデルにつながりました：{MODEL['base_url']}" + (f"（{', '.join(n for n in names if n)}）" if names else ""))
        return True
    except Exception as e:
        if not quiet:
            print(f"判定モデルに届きません（規則版で動きます）：{e}")
        MODEL["base_url"] = None
        return False


def _probe():
    """最初の一回だけ、手元の kev が動いているかを探す"""
    if not MODEL["probed"]:
        setup(DEFAULT_URL, quiet=True)


def _score_model(text):
    """判定モデルに聞く → (候補ごとの確率, 特徴の集合, 来歴)"""
    t0 = time.time()
    body = {"state": _clean(text), "model": MODEL["model"], "questions": SHITSUMON}
    res = _http("POST", MODEL["base_url"] + "/v1/systemone", body, key=MODEL["key"], timeout=MODEL["timeout"])
    ans = res["answers"]
    probs = ans["hannou"]["probabilities"]
    p = {k: float(probs.get(k, 0.0)) for k, _ in KOUHO}
    s = sum(p.values()) or 1.0
    p = {k: v / s for k, v in p.items()}
    nouls = {NOUL_NAMES[k]: float(ans[k]["noul"]) for k in NOUL_NAMES if k in ans}
    feats = {name for name, v in nouls.items() if v >= 0.5}
    meta = {"source": "model", "model": res.get("model", MODEL["model"]), "url": MODEL["base_url"],
            "ms": int((time.time() - t0) * 1000), "nouls": {k: round(v, 2) for k, v in nouls.items()},
            "confidence": ans["hannou"].get("confidence")}
    return p, feats, meta


def score(text):
    """文字列 → (候補ごとの確率, 特徴の集合)。モデルに届けばモデル、届かなければ規則版"""
    _probe()
    if not _clean(text):                       # 何も書いていないときはモデルに聞かない
        f = features(text)
        MODEL["last"] = {"source": "rules"}
        return _linear(f, KOUHO, WEIGHTS, BIAS), f
    if MODEL["base_url"]:
        try:
            p, f, meta = _score_model(text)
            MODEL["last"] = meta
            return p, f
        except Exception as e:
            MODEL["last"] = {"source": "rules", "error": str(e)}
    else:
        MODEL["last"] = {"source": "rules"}
    f = features(text)
    return _linear(f, KOUHO, WEIGHTS, BIAS), f


def erabu(text):
    """文 → (選ばれた候補の id, 候補ごとの確率, 反応の文, 反応した特徴)"""
    p, f = score(text)
    best = max(p, key=p.get)
    if best == "toikaesu":
        q = _linear(f, TOI, TOI_WEIGHTS, TOI_BIAS)
        line = dict(TOI)[max(q, key=q.get)]
    else:
        line = HANNOU[best]
    return best, p, line, f


def kiku(text, show=True):
    """生徒が書いた文を判定器に聞く。候補ごとの数と、選ばれた反応だけを出す"""
    best, p, line, f = erabu(text)
    meta = MODEL["last"] or {}
    if show:
        names = dict(KOUHO)
        t = _clean(text)
        print("入力：" + (("「" + t.replace("\n", " ") + "」") if t else "（まだ何も書いていない）"))
        if meta.get("source") == "model":
            nl = "、".join(f"{k} {v:.2f}" for k, v in meta["nouls"].items())
            print(f"判定：{meta['model']}（{meta['url']}、{meta['ms']} ms）　特徴の確率：{nl}")
        else:
            print("判定：規則版" + ("（判定モデルに届かず：" + meta["error"][:60] + "）" if meta.get("error") else "（手元に判定モデルなし）"))
        print("反応した特徴：" + ("、".join(sorted(f)) if f else "なし"))
        print()
        print("  " + _pad("候補", 20) + "  数")
        for k, name in KOUHO:
            bar = "█" * int(round(p[k] * 20))
            mark = "→" if k == best else " "
            print(f"{mark} {_pad(name, 20)}{p[k]:6.2f}  {bar}")
        print()
        print(f"{names[best]}：{line}")
    return {"erabareta": best, "kakuritsu": {k: round(v, 3) for k, v in p.items()}, "hannou": line,
            "tokuchou": sorted(f), "hantei": meta}
