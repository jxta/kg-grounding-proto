"""handan — 文字列を入れると、候補ごとの数を返す判定器。

ノートの中の AI の役を、文章を作らない形でやる。
  1. 反応の候補（問い返す／次の実験を促す／地図への記入を促す／黙って待つ）は、人が先に書いておく
  2. 生徒が書いた文を入れると、候補ごとに数（確率）が返る
  3. いちばん大きい候補の反応だけが出る。文章を生成しないので、先回りして説明してしまうことがない

判定の中身は二つある。
  - 判定モデル：手元の Mac で動かした kev（TypeSafe の Jev と同じ /v1/systemone API を話す、公開重みの判定モデル。
    https://github.com/jaredpalmer/kev ）に、Choice 1 本（4 候補）と Noul 4 本（文の特徴）を一度に投げる。
    `kiku()` は最初に http://127.0.0.1:8009 を探し、動いていればそれを使う。別の場所や Jev なら `setup()` で指定する。
    JupyterLite（公開サイト）から 127.0.0.1 へつなぐ初回だけ、Chrome が「ローカルネットワークへの接続」の許可を聞く。
    聞かれずに規則版へ落ちるときは `tsunagu()` を一度（ページの側から許可を取る）
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

# 問い返すときの問いの候補（id、短い名、問いの文）。これも人が先に書く。
# どれを出すかは、判定モデルがあれば Choice 1 本（SHITSUMON["toi"]）で選び、なければ特徴から規則で選ぶ
TOI = [
    ("hayasa",   "どのくらいの速さ",  "まばらになるのは、どのくらいの速さ？ 10 ごとに数えてみると、数で言える。`kazoeru(100, 10)`"),
    ("kurabe",   "何と何を比べて",    "どのくらい減る、というのは、何と何を比べて？ どこからどこまで？ 10 ごとに数えると、数で比べられる。`kazoeru(100, 10)`"),
    ("dokomade", "どこまで見た",      "どこまで見た？ 見た範囲のことと、その先のことは、分けて書けそう？"),
    ("nani",     "何を見て",          "何を見て、そう思った？ 絵のどこ？"),
]
TOI_BUN = {k: bun for k, _, bun in TOI}
TOI_NA = {k: na for k, na, _ in TOI}

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
_RATIO = ("半分", "はんぶん", "倍", "割", "％", "%", "パーセント", "分の", "ぐっと", "急に", "きゅうに", "ゆっくり", "じょじょに", "徐々に", "ほとんど")


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
    if len(t) <= 4 and not any(w in t for w in _DONTKNOW):
        f.add("ひとこと")                     # 「えっと」「まだ」：書きかけ
    if len(t) > 40:
        f.add("長い")
    if any(w in t for w in _SPARSE):
        f.add("まばら")
    if any(w in t for w in _FOREVER):
        f.add("その先")
    if any(w in t for w in _DONTKNOW):
        f.add("わからない")
    if any(w in t for w in _RATIO):
        f.add("割合")
    if "？" in t or "?" in t:
        f.add("問い")
    return f

# 特徴 → 候補ごとの重み。表にしてあるので、手で直せる
WEIGHTS = {
    #  特徴         問い返す  次の実験  地図     待つ
    "空":          {"toikaesu": -1.0, "tsugi": -1.0, "chizu": -1.0, "matsu": 3.0},
    "数えた":      {"toikaesu": -1.0, "tsugi": -0.5, "chizu": 2.5, "matsu": 0.0},
    "短い":        {"toikaesu": 0.0,  "tsugi": 1.5,  "chizu": -0.5, "matsu": 0.0},
    "ひとこと":    {"toikaesu": -0.5, "tsugi": -0.5, "chizu": -0.5, "matsu": 3.0},
    "長い":        {"toikaesu": 0.0,  "tsugi": -0.5, "chizu": 0.5, "matsu": 0.0},
    "まばら":      {"toikaesu": 1.5,  "tsugi": 0.0,  "chizu": 0.0, "matsu": 0.0},
    "その先":      {"toikaesu": 1.5,  "tsugi": 0.0,  "chizu": -0.5, "matsu": 0.0},
    "わからない":  {"toikaesu": 0.5,  "tsugi": 2.0,  "chizu": -1.0, "matsu": 0.0},
    "問い":        {"toikaesu": 1.0,  "tsugi": 0.0,  "chizu": 0.0, "matsu": 0.0},
}
BIAS = {"toikaesu": 0.3, "tsugi": 0.0, "chizu": -0.5, "matsu": -1.0}

# 問いの選び方の規則版（特徴 → 問いの候補ごとの重み）。モデルに届かないときはこの表で選ぶ
TOI_WEIGHTS = {
    "まばら":  {"hayasa": 1.2,  "kurabe": 0.0,  "dokomade": 0.0, "nani": 0.0},
    "割合":    {"hayasa": -1.0, "kurabe": 2.0,  "dokomade": 0.0, "nani": 0.0},
    "その先":  {"hayasa": 0.0,  "kurabe": 0.0,  "dokomade": 1.0, "nani": 0.0},
    "数えた":  {"hayasa": -1.0, "kurabe": -0.5, "dokomade": 0.5, "nani": 0.0},
}
TOI_BIAS = {"hayasa": 0.0, "kurabe": 0.0, "dokomade": 0.0, "nani": 0.2}


def _softmax(raw):
    m = max(raw.values())
    e = {k: math.exp(v - m) for k, v in raw.items()}
    s = sum(e.values())
    return {k: v / s for k, v in e.items()}


def _linear(feats, candidates, weights, bias):
    """特徴の集合 → 候補ごとの確率（重みを足して softmax）"""
    cands = [c[0] for c in candidates]
    raw = {c: bias.get(c, 0.0) + sum(weights[x].get(c, 0.0) for x in feats if x in weights) for c in cands}
    return _softmax(raw)


# ---------- 判定モデル（kev / Jev）----------
# 一度の呼び出しで投げる質問。id は模型には見えない。instructions と criteria が模型の読むすべて
# 文面は 2026-10-26 に手元の kev-4b（MLX）で、14 の試し文に対して合わせた。方針を「上から順に当てはめる」形で書くと
# 判定が安定し、Noul は yes／no の両側を書くと、書いていない文で 0.5 付近にぶれなくなる。
SHITSUMON = {
    "hannou": {
        "type": "choice",
        "instructions": "\n".join([
            "場面：中学生が、1 から N までの数の上に、その数を割り切る 2 以上の数の個数だけ点を打った絵（点がひとつだけの数は素数）を見て、"
            "見えたことを自分の言葉で書いた。先生役は答えを教えず、反応を一つだけ返す。",
            "方針（上から順に見て、最初に当てはまったものを選ぶ。下の方針は見ない）：",
            "1. 文が空、または「えっと」「まだ」のようなひとことだけで、まだ書きかけ → matsu",
            "2. 「わからない」「分からない」と書いてある → tsugi",
            "3. 数字が 2 つ以上書いてある（数えた個数、10 ごとの個数、見た範囲など）。「減る」「まばら」などの感想が一緒に書いてあっても、数字があれば chizu → chizu",
            "4. 数字がなく、観察や主張（減る、まばら、なくならない、無限、など）だけが書いてある → toikaesu",
            "5. 観察がまだ何も書かれていない → tsugi",
        ]),
        "criteria": {
            "toikaesu": "問い返す（観察や主張が書いてあるときだけ。「わからない」と書いてある文には使わない）",
            "tsugi":    "次の実験を促す（「わからない」と書いてあるときは必ずこれ。観察がないときもこれ。もっと先まで描かせる）",
            "chizu":    "地図への記入を促す（数字が 2 つ以上書いてあるので、記録させる）",
            "matsu":    "黙って待つ（まだ書きかけ）",
        },
    },
    # 問いの選択。候補は「文に何が書いてあるか」で書く。「〜を聞く」という行動や「どれにも当てはまらないとき」という
    # 否定条件で書くと、4B のモデルは最後の候補に寄る（2026-10-26 の実測：どの文でも nani が 0.5〜0.8）。
    # 書いてあることの形にそろえたら 10 文中 9 文が狙いどおり
    "toi": {
        "type": "choice",
        "instructions": "中学生が、数の上に点を打った絵（点がひとつだけの数は素数）を見て書いた文です。文に書いてあることに最も近いものを一つ選んでください。",
        "criteria": {
            "hayasa":   "「減る」「まばら」「少なくなる」「間があく」と書いてある（どのくらい減るかは書いていない）",
            "kurabe":   "「半分」「倍」「ぐっと」「じょじょに」「急に」のように、どのくらい減るか・どんな速さで減るかが書いてある",
            "dokomade": "「なくならない」「無限」「ずっと」「いつまでも」のように、見た範囲の先のことが書いてある",
            "nani":     "減ること・速さ・先のことのどれも書いていない（別のこと、疑問、間違った観察）",
        },
    },
    "kazoeta":   {"type": "noul", "instructions": "数えた結果（個数や見た範囲）が数字で具体的に書いてあるか",
                  "criteria": {"true": "数字で具体的に書いてある", "false": "数字は書いていない、または 1 つの数だけ"}},
    "mabara":    {"type": "noul", "instructions": "点がひとつだけの数が先に行くほど少なくなる・まばらになる・減る、と言っているか",
                  "criteria": {"true": "言っている", "false": "言っていない"}},
    "sonosaki":  {"type": "noul", "instructions": "見た範囲を超えて、ずっと続く・なくならない・無限にある、と先のことまで主張しているか",
                  "criteria": {"true": "主張している", "false": "していない"}},
    "wakaranai": {"type": "noul", "instructions": "「わからない」「分からない」と書いているか",
                  "criteria": {"true": "書いている", "false": "書いていない"}},
}
# 探り（つながっているか）に使う、いちばん小さい質問。GET /v1/models ではなく POST にする理由：JupyterLite の
# service worker は GET を自分で取りに行き、service worker はローカルネットワークの許可を聞けない（Chrome）。POST は素通し
PING = {"state": "ping", "questions": {"ok": {"type": "noul", "instructions": "文が「ping」である"}}}
NOUL_NAMES = {"kazoeta": "数えた", "mabara": "まばら", "sonosaki": "その先", "wakaranai": "わからない"}

MODEL = {"base_url": None, "key": None, "model": "kev-latest", "timeout": 90, "probed": False, "last": None,
         "auto": True, "tries": 0, "probe_error": None, "probe_ms": None}
DEFAULT_URL = "http://127.0.0.1:8009"
PROBE_TRIES = 3          # 自動で探る回数（届かないときは接続拒否で即返るので、繰り返しても待ちは出ない）
PROBE_TIMEOUT = 90       # 起動直後の kev は最初の一回に 30 秒ほどかかる（Metal の暖機）。許可を聞かれている間も待つ


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
        try:
            xhr.send(data)
        except Exception as e:                 # 同期 XHR は、つながらない／時間切れだと send() が例外を投げる
            raise ConnectionError("つながらない（" + str(e).split("\n")[0][:60] + "）") from None
        status, text = int(xhr.status), str(xhr.responseText)
        if status == 0:                        # 届かない・ブラウザが止めた（CORS、ローカルネットワークの許可、混在コンテンツ）は全部これ
            raise ConnectionError("つながらない（status 0）")
    else:
        import urllib.request, urllib.error
        req = urllib.request.Request(url, data=data.encode("utf-8") if data else None, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                status, text = r.status, r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            status, text = e.code, e.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as e:
            raise ConnectionError(f"つながらない（{getattr(e, 'reason', e)}）") from None
    if status != 200:
        raise RuntimeError(f"HTTP {status}：{text[:200]}")
    return json.loads(text)


def setup(base_url=DEFAULT_URL, key=None, model="kev-latest", quiet=False, _auto=False):
    """判定モデルの場所を指定する。手元の kev なら既定のまま。TypeSafe の Jev なら
    setup("https://api.typesafe.ai", key="…", model="jev-latest")。届かなければ規則版で動く"""
    MODEL.update(base_url=(base_url or "").rstrip("/") or None, key=key, model=model, probed=True,
                 auto=_auto, probe_error=None)
    if not MODEL["base_url"]:
        if not quiet:
            print("判定モデルは使いません（規則版で動きます）")
        return False
    try:
        t0 = time.time()
        res = _http("POST", MODEL["base_url"] + "/v1/systemone", dict(PING, model=model), key=key, timeout=PROBE_TIMEOUT)
        if not isinstance(res, dict) or "answers" not in res:
            raise RuntimeError("返事の形が違う：" + str(res)[:80])
        MODEL["probe_ms"] = int((time.time() - t0) * 1000)
        if not quiet:
            print(f"判定モデルにつながりました：{MODEL['base_url']}（{res.get('model', model)}、{MODEL['probe_ms']} ms）")
        return True
    except Exception as e:
        if not quiet:
            print(f"判定モデルに届きません（規則版で動きます）：{e}")
        MODEL.update(base_url=None, probe_error=str(e))
        return False


def _probe():
    """手元の kev が動いているかを探す。見つからなければ、何回かまでは次の呼び出しでもう一度探す
    （ブラウザの許可を押したあとの呼び出しで、自動的につながるように）"""
    if MODEL["base_url"] or (MODEL["probed"] and not MODEL["auto"]):
        return
    if MODEL["tries"] >= PROBE_TRIES:
        return
    MODEL["tries"] += 1
    setup(DEFAULT_URL, quiet=True, _auto=True)


def tsunagu(base_url=DEFAULT_URL, model=None, keep=60):
    """ブラウザ（JupyterLite）で、ページの側から判定モデルにつなぐ（暖機も兼ねる）。
    Chrome 142 以降は、公開サイトから 127.0.0.1 へ初めてつなぐとき「ローカルネットワーク上のデバイス…」の許可を
    聞いてくる。ノートの計算はワーカーの中で動いていて、そこからは許可を聞けないことがあるので、ここで一度
    ページから聞く。許可はサイト（jxta.github.io）に対して記憶されるので、次からは聞かれない。
    起動直後の kev は最初の一回に 30 秒ほどかかる。しばらく使わないとまた冷える（メモリから退避される）ので、
    keep 秒ごと（既定 60）に小さな ping を送って温め続ける。keep=0 で止める。
    手元の Python（JupyterLab）では setup() と同じ"""
    url = (base_url or DEFAULT_URL).rstrip("/")
    model = model or MODEL["model"]
    MODEL.update(base_url=None, probed=False, auto=True, tries=0, probe_error=None)
    if sys.platform != "emscripten":
        return setup(url, model=model, _auto=True)
    from IPython.display import display, HTML
    import uuid
    uid = "tsunagu-" + uuid.uuid4().hex[:8]
    body = json.dumps(dict(PING, model=model), ensure_ascii=False)
    display(HTML(f"""
<div id="{uid}" style="font-family:sans-serif;font-size:0.95em;line-height:1.6">
  <span class="msg">つないでいます… ブラウザが「ローカルネットワーク…への接続」の許可を求めたら「許可」。起動直後は 30 秒ほどかかる。</span>
  <button style="margin-left:0.6em">もう一度つなぐ</button>
  <div class="keep" style="color:#777;font-size:0.85em"></div>
</div>
<script>
(function(){{
  var box = document.getElementById("{uid}"); if (!box) return;
  var msg = box.querySelector(".msg"), btn = box.querySelector("button"), keepEl = box.querySelector(".keep");
  var keep = {int(keep or 0)}, timer = null;
  function post(){{
    return fetch("{url}/v1/systemone", {{method: "POST", headers: {{"content-type": "application/json"}}, body: {json.dumps(body, ensure_ascii=False)}}})
      .then(function(r){{ if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); }});
  }}
  function ping(){{
    if (!document.contains(box)) {{ clearInterval(timer); return; }}   // 出力が消えたら止める
    var t0 = Date.now();
    post().then(function(){{ keepEl.textContent = "温め続けています（" + keep + " 秒ごと）　最終 " + new Date().toLocaleTimeString() + "（" + (Date.now() - t0) + " ms）"; }})
          .catch(function(e){{ keepEl.textContent = "温めの ping が失敗（" + e + "）"; }});
  }}
  function go(){{
    msg.textContent = "つないでいます… ブラウザが「ローカルネットワーク…への接続」の許可を求めたら「許可」。起動直後は 30 秒ほどかかる。";
    var t0 = Date.now();
    post().then(function(j){{
      msg.textContent = "つながりました：{url}（" + (j.model || "{model}") + "、" + (Date.now() - t0) + " ms）　この後の kiku() はこのモデルに聞きます。";
      if (keep > 0 && !timer) {{ timer = setInterval(ping, keep * 1000); keepEl.textContent = "温め続けています（" + keep + " 秒ごと）"; }}
    }}).catch(function(e){{
      msg.textContent = "つながりません（" + e + "）。kev が動いているか（ターミナルで curl localhost:8009/v1/models）、"
        + "このサイトのローカルネットワークへのアクセスを「ブロック」していないか（アドレス欄左のアイコン → サイトの設定）を見て、もう一度。";
    }});
  }}
  btn.onclick = go; go();
}})();
</script>"""))


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
    toi = None
    if "toi" in ans and isinstance(ans["toi"].get("probabilities"), dict):
        tp = {k: float(ans["toi"]["probabilities"].get(k, 0.0)) for k, _, _ in TOI}
        ts = sum(tp.values()) or 1.0
        toi = {k: v / ts for k, v in tp.items()}
    meta = {"source": "model", "model": res.get("model", MODEL["model"]), "url": MODEL["base_url"],
            "ms": int((time.time() - t0) * 1000), "nouls": {k: round(v, 2) for k, v in nouls.items()},
            "confidence": ans["hannou"].get("confidence"), "toi": toi}
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
        MODEL["last"] = {"source": "rules", "probe_error": MODEL["probe_error"]}
    f = features(text)
    return _linear(f, KOUHO, WEIGHTS, BIAS), f


def erabu(text):
    """文 → (選ばれた候補の id, 候補ごとの確率, 反応の文, 反応した特徴, 問いの候補ごとの確率 or None)
    問いは、モデルが答えていればモデルの Choice（SHITSUMON["toi"]）、なければ特徴からの規則で選ぶ"""
    p, f = score(text)
    best = max(p, key=p.get)
    q = None
    if best == "toikaesu":
        meta = MODEL["last"] or {}
        q = meta.get("toi") if meta.get("source") == "model" and meta.get("toi") else _linear(f, TOI, TOI_WEIGHTS, TOI_BIAS)
        line = TOI_BUN[max(q, key=q.get)]
    else:
        line = HANNOU[best]
    return best, p, line, f, q


KIROKU_FILE = "handan_log.jsonl"   # kiku() の入力と判定をためる（あとで先生が正解を付け、微調整の学習データにする）


def _kiroku(text, best, p, q, meta):
    try:
        row = {"toki": time.strftime("%Y-%m-%d %H:%M:%S"), "bun": _clean(text), "hantei": meta.get("source"),
               "model": meta.get("model"), "kouho": {k: round(v, 3) for k, v in p.items()}, "erabareta": best,
               "toi": ({k: round(v, 3) for k, v in q.items()} if q else None),
               "toi_erabareta": (max(q, key=q.get) if q else None), "nouls": meta.get("nouls"),
               "seikai": None, "seikai_toi": None}      # ← 先生があとで埋める欄
        with open(KIROKU_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass


def kiku(text, show=True, log=True):
    """生徒が書いた文を判定器に聞く。候補ごとの数と、選ばれた反応だけを出す。
    log=True なら、入力と判定を handan_log.jsonl に一行ためる（手元だけ。どこにも送らない）"""
    best, p, line, f, q = erabu(text)
    meta = MODEL["last"] or {}
    if log and _clean(text):
        _kiroku(text, best, p, q, meta)
    if show:
        names = dict(KOUHO)
        t = _clean(text)
        print("入力：" + (("「" + t.replace("\n", " ") + "」") if t else "（まだ何も書いていない）"))
        if meta.get("source") == "model":
            nl = "、".join(f"{k} {v:.2f}" for k, v in meta["nouls"].items())
            print(f"判定：{meta['model']}（{meta['url']}、{meta['ms']} ms）　特徴の確率：{nl}")
        else:
            if meta.get("error"):                       # つながっていたのに、この一回が失敗した
                why = "（判定モデルに届かず：" + meta["error"][:60] + "）"
            elif meta.get("probe_error") and sys.platform == "emscripten":
                why = "（手元に判定モデルなし。動かしているのにこう出るなら、tsunagu() を一度）"
            else:
                why = "（手元に判定モデルなし）"
            print("判定：規則版" + why)
        print("反応した特徴：" + ("、".join(sorted(f)) if f else "なし"))
        print()
        print("  " + _pad("候補", 20) + "  数")
        for k, name in KOUHO:
            bar = "█" * int(round(p[k] * 20))
            mark = "→" if k == best else " "
            print(f"{mark} {_pad(name, 20)}{p[k]:6.2f}  {bar}")
        if q:
            qbest = max(q, key=q.get)
            print()
            print("  " + _pad("問いの候補", 20) + "  数" + ("" if meta.get("toi") else "（規則で選択）"))
            for k, na, _ in TOI:
                bar = "█" * int(round(q[k] * 20))
                mark = "→" if k == qbest else " "
                print(f"{mark} {_pad(na, 20)}{q[k]:6.2f}  {bar}")
        print()
        print(f"{names[best]}：{line}")
    return {"erabareta": best, "kakuritsu": {k: round(v, 3) for k, v in p.items()}, "hannou": line,
            "tokuchou": sorted(f), "toi": ({k: round(v, 3) for k, v in q.items()} if q else None), "hantei": meta}


# ---------- 文面を直すときの道具 ----------
# (文, 期待する反応, 期待する問い or None)。反応や問いの文面を直したら shiken() で一度に確かめる。
# 先生の判断で増やしてよい。期待は「こう返してほしい」であって正解ではない
JIREI = [
    ("まばらになる。でも、なくならない",                                   "toikaesu", "hayasa"),
    ("まだらになってじょじょにひんどが半分くらいになります。",             "toikaesu", "kurabe"),
    ("点がひとつの数は、だんだん少なくなる気がする",                       "toikaesu", "hayasa"),
    ("素数は無限にある",                                                   "toikaesu", "dokomade"),
    ("右に行くほど、点がひとつの数が減っている。でも 90 のあたりにもある", "toikaesu", "hayasa"),
    ("右のほうは、点がひとつだけの数が 100 のあたりで 1 個しかない。急に減った", "toikaesu", "kurabe"),
    ("点がひとつの数は、ずっと出てくると思う",                             "toikaesu", "dokomade"),
    ("2 と 3 だけが隣どうし。あとは離れている",                           "toikaesu", "nani"),
    ("なぜ 1 には点がないの？",                                            "toikaesu", "nani"),
    ("全部の数に点がある",                                                 "toikaesu", "nani"),
    ("10 ごとに 4, 4, 2, 2, 3, 2, 2, 3, 2, 1 個。だんだん減る",             "chizu", None),
    ("1 から 100 まで見た。点がひとつだけの数は 25 個あった",               "chizu", None),
    ("点がひとつだけの数は、2, 3, 5, 7, 11, 13 …",                         "chizu", None),
    ("10 ごとに数えたら、4 個、4 個、2 個、2 個、3 個。だんだん減るけど、ゼロにはならないと思う", "chizu", None),
    ("わからない",                                                         "tsugi", None),
    ("えっと",                                                             "matsu", None),
    ("まだ",                                                               "matsu", None),
]


def shiken(jirei=None, show=True):
    """事例をまとめて判定器に通し、期待と合うかを表にする。文面（SHITSUMON の指示文・候補の説明、TOI の問い）を
    直したら、これで一度に確かめる。モデルがあればモデル、なければ規則版で判定する（表の見出しに出る）。
    戻り値：(反応が合った数, 問いが合った数, 問いを比べた数, 行のリスト)"""
    jirei = jirei or JIREI
    names = dict(KOUHO)
    rows, hit, hit_q, n_q = [], 0, 0, 0
    for case in jirei:
        bun, want, want_q = (list(case) + [None, None])[:3]
        best, p, line, f, q = erabu(bun)
        meta = MODEL["last"] or {}
        ok = best == want
        hit += ok
        qbest = max(q, key=q.get) if q else None
        ok_q = None
        if want_q and q:
            n_q += 1
            ok_q = qbest == want_q
            hit_q += ok_q
        rows.append({"bun": bun, "want": want, "got": best, "ok": ok, "p": p, "want_q": want_q, "got_q": qbest, "ok_q": ok_q,
                     "source": meta.get("source"), "ms": meta.get("ms")})
    if show:
        src = (MODEL["last"] or {}).get("source")
        print(f"判定：{'モデル ' + str(MODEL['model']) if src == 'model' else '規則版'}　{len(jirei)} 文")
        print("  " + _pad("文", 30) + _pad("期待", 10) + _pad("判定", 10) + "   " + _pad("期待の問い", 10) + _pad("判定の問い", 10) + "  候補ごとの数")
        for r in rows:
            mark = "○" if r["ok"] else "×"
            mq = "" if r["ok_q"] is None else ("○" if r["ok_q"] else "×")
            ps = " ".join(f"{names[k][:2]}{r['p'][k]:.2f}" for k, _ in KOUHO)
            print(f"{mark} " + _pad(r["bun"][:14], 30) + _pad(r["want"], 10) + _pad(r["got"], 10) + f" {mq} " +
                  _pad(r["want_q"] or "-", 10) + _pad(r["got_q"] or "-", 10) + "  " + ps)
        print(f"反応 {hit}/{len(jirei)}" + (f"　問い {hit_q}/{n_q}" if n_q else ""))
    return hit, hit_q, n_q, rows
