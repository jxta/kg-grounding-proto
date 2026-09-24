"""実験ノート共通の道具（kg_tools）— 篩の表、因数の木、約数の表、素数レース、H の世界、ユークリッドの数。
どの実験ノートも `from kg_tools import *` で使う。
最後に report() で結果を「地図アプリ」に送る（JupyterLite では同じブラウザの別タブへ、それ以外ではファイルへ）。
"""
import json, os, sys, copy, math, random
from datetime import datetime

try:
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
except ModuleNotFoundError as e:   # JupyterLite：ノートの最初のセルの import numpy, matplotlib, sympy が部品を読み込む
    raise ModuleNotFoundError(f"{e}。JupyterLite では、ノートの最初のセルにある "
                              "`import numpy, matplotlib, sympy` の行を残して、そのセルを先に実行してください") from e
import logging
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)   # 太字のない同梱フォントで出る注意書きを出さない
from matplotlib.patches import FancyBboxPatch
import sympy
import unicodedata

def _w(t):
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in t)

def _pad(t, n):
    """表をそろえるための詰め物（全角を 2 文字幅として数える）"""
    return t + " " * max(0, n - _w(t))

pad = _pad

# ---------- 日本語フォント ----------
# 図の中の日本語を出すためのフォントを探す。見つける順番：
#   1. ノートと同じフォルダの fonts/ にある同梱フォント（Noto Sans CJK JP のサブセット）
#   2. パソコンに入っている日本語フォント
#   3. インターネットから取ってくる（1・2 がないときだけ。JupyterLite などで使う）
# どの場合も、その日本語フォントにない記号（≤ ⁴ ⚠ など）は DejaVu Sans で補う。
FONT_URLS = [
    "https://raw.githubusercontent.com/jxta/kg-grounding-proto/main/fonts/NotoSansCJKjp-Regular-subset.otf",  # 約 1.8 MB
    "https://jxta.github.io/kg-grounding-proto/files/fonts/NotoSansCJKjp-Regular-subset.otf",             # 同じもの（Pages）
    "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf",  # 約 16 MB
]
FONT_CANDIDATES = ["Noto Sans CJK JP", "Noto Sans JP", "Source Han Sans JP", "IPAexGothic", "IPAGothic",
                   "Hiragino Sans", "Hiragino Maru Gothic Pro", "Yu Gothic", "Meiryo", "MS Gothic",
                   "BIZ UDGothic", "TakaoGothic", "VL Gothic", "Noto Sans CJK SC"]

def _font_dirs():
    """fonts/ フォルダの候補（ノートのあるフォルダ、その上、ホームなど）"""
    dirs = ["fonts", os.path.join("..", "fonts"), os.path.expanduser("~/fonts"), os.path.expanduser("~/.fonts")]
    if sys.platform == "emscripten":                      # JupyterLite（Pyodide）：ドライブの浅い階層も見る
        dirs.append("/drive/fonts")
        try:
            for r, d, f in os.walk("/drive"):
                if r.count("/") <= 2:
                    dirs += [os.path.join(r, x) for x in d if x == "fonts"]
                else:
                    d[:] = []
        except Exception:
            pass
    return dirs

def _use_font_file(path):
    """フォントファイルを matplotlib に登録し、その名前を返す（読めなければ None）"""
    import shutil, tempfile
    import matplotlib.font_manager as fm
    try:
        tmp = os.path.join(tempfile.gettempdir(), os.path.basename(path))
        if os.path.abspath(path) != os.path.abspath(tmp):
            shutil.copyfile(path, tmp)                    # JupyterLite の仮想ドライブから読むより速くて確実
        fm.fontManager.addfont(tmp)
        return fm.FontProperties(fname=tmp).get_name()
    except Exception as e:
        print("※ フォントを読めませんでした:", path, e)
        return None

def _download_font():
    """同梱フォントも日本語フォントもないとき、ネットから取ってくる（失敗したら None）"""
    import tempfile
    for url in FONT_URLS:
        dst = os.path.join(tempfile.gettempdir(), url.rsplit("/", 1)[-1])
        try:
            if not os.path.exists(dst):
                if sys.platform == "emscripten":          # Pyodide：ワーカー内なら同期 XHR が使える
                    import js
                    xhr = js.XMLHttpRequest.new()
                    xhr.open("GET", url, False)
                    xhr.responseType = "arraybuffer"
                    xhr.send()
                    if xhr.status != 200:
                        continue
                    data = xhr.response.to_bytes()
                else:
                    import urllib.request
                    with urllib.request.urlopen(url, timeout=30) as r:
                        data = r.read()
                with open(dst, "wb") as f:
                    f.write(data)
            name = _use_font_file(dst)
            if name:
                print(f"※ 日本語フォントをダウンロードしました（{len(open(dst, 'rb').read()) // 1024} KB）")
                return name
        except Exception as e:
            print("※ ダウンロードできませんでした:", url.rsplit("/", 1)[-1], type(e).__name__)
    return None

def setup_font():
    import glob
    import matplotlib.font_manager as fm
    name = None
    for d in _font_dirs():                                # 1. 同梱フォント
        files = sorted(glob.glob(os.path.join(d, "*.otf")) + glob.glob(os.path.join(d, "*.ttf")))
        if files:
            name = _use_font_file(files[0])
            if name:
                break
    if name is None:                                      # 2. パソコンの日本語フォント
        installed = {f.name for f in fm.fontManager.ttflist}
        name = next((c for c in FONT_CANDIDATES if c in installed), None)
    if name is None:                                      # 3. ネットから
        name = _download_font()
    if name is None:
        try:
            import japanize_matplotlib  # noqa: F401
            name = "IPAexGothic"
        except Exception:
            return None
    # 日本語フォントにない記号は DejaVu Sans で補う（matplotlib 3.6 以降のフォールバック）
    matplotlib.rcParams["font.family"] = [name, "DejaVu Sans"]
    return name

FONT = setup_font()
matplotlib.rcParams.update({
    "axes.unicode_minus": False,
    "figure.dpi": 110,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#444444",
    "axes.labelcolor": "#222222",
    "xtick.color": "#444444",
    "ytick.color": "#444444",
    "axes.prop_cycle": matplotlib.cycler(color=["#000000", "#7a7a7a", "#bbbbbb"]),
})
if FONT is None:
    print("※ 日本語フォントが見つからないので、図の中の名前は英語IDで表示します。"
          "（ノートと同じフォルダに fonts/ を置くか、インターネットにつないで、このセルをもう一度実行してください）")

FIG_DIR = os.environ.get("KG_FIG_DIR")  # 図を PNG に保存したいときだけ設定
if FIG_DIR:
    os.makedirs(FIG_DIR, exist_ok=True)

def _save(fig, name):
    if FIG_DIR:
        fig.savefig(os.path.join(FIG_DIR, name + ".png"), dpi=200, bbox_inches="tight", facecolor="white")

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def sieve(n):
    """エラトステネスの篩。各数を「消した素数」を返す（素数は 0、1 は -1）"""
    crossed = [0] * (n + 1)
    crossed[1] = -1
    for p in range(2, n + 1):
        if crossed[p] == 0:
            for q in range(p * p, n + 1, p):
                if crossed[q] == 0:
                    crossed[q] = p
    return crossed

def sieve_grid(n=100, upto=None, title=None, save="sieve_grid"):
    """1〜n の表。消された数は薄く、消した素数を右下に小さく書く。upto を指定すると、その素数まで消した途中経過"""
    crossed = sieve(n)
    if upto is not None:
        crossed = [c if (c in (0, -1) or c <= upto) else 0 for c in crossed]
    cols = 10
    rows = math.ceil(n / cols)
    fig, ax = plt.subplots(figsize=(7.2, 0.72 * rows + 0.6))
    ax.set_xlim(0, cols); ax.set_ylim(0, rows); ax.set_aspect("equal"); ax.axis("off")
    for k in range(1, n + 1):
        r, c = divmod(k - 1, cols)
        x, y = c, rows - 1 - r
        st = crossed[k]
        if st == -1:      # 1
            ax.add_patch(FancyBboxPatch((x + 0.06, y + 0.06), 0.88, 0.88, boxstyle="square,pad=0",
                                        fc="white", ec="#666666", lw=0.9, ls=(0, (2, 2))))
            ax.text(x + 0.5, y + 0.5, "1", ha="center", va="center", fontsize=12, color="#444444")
            ax.text(x + 0.9, y + 0.12, "?", ha="right", va="bottom", fontsize=8, color="#444444")
        elif st == 0:     # 素数
            ax.add_patch(FancyBboxPatch((x + 0.06, y + 0.06), 0.88, 0.88, boxstyle="square,pad=0",
                                        fc="white", ec="black", lw=1.2))
            ax.text(x + 0.5, y + 0.5, str(k), ha="center", va="center", fontsize=12, color="black", fontweight="bold")
        else:             # 消された（合成数）
            ax.add_patch(FancyBboxPatch((x + 0.06, y + 0.06), 0.88, 0.88, boxstyle="square,pad=0",
                                        fc="#e6e6e6", ec="#bbbbbb", lw=0.6))
            ax.text(x + 0.5, y + 0.55, str(k), ha="center", va="center", fontsize=11, color="#9a9a9a")
            ax.text(x + 0.9, y + 0.12, str(st), ha="right", va="bottom", fontsize=6.5, color="#666666")
    t = title or (f"1〜{n} の表：太枠＝残った数（素数）、薄い数＝消された数（右下は消した素数）"
                  if upto is None else f"1〜{n} の表：{upto} までの素数で消したところ")
    ax.set_title(t, fontsize=9.5, loc="left", color="#222222")
    _save(fig, save)
    plt.show()
    return [k for k in range(2, n + 1) if crossed[k] == 0]

# ---------- 因数の木 ----------
def factor_tree(n, is_prime=None, splits=None, rng=None):
    """n を二つの因数に分けていく木。splits={n:(a,b)} で分け方を指定、なければ最小の素因数で分ける（rng で無作為）。
    戻り値：('leaf', n) または ('node', n, 左, 右)"""
    is_prime = is_prime or sympy.isprime
    if is_prime(n):
        return ("leaf", n)
    if splits and n in splits:
        a, b = splits[n]
    elif rng is not None:
        divs = [d for d in range(2, n) if n % d == 0 and d * d <= n]
        a = rng.choice(divs); b = n // a
    else:
        a = min(sympy.factorint(n)); b = n // a
    return ("node", n, factor_tree(a, is_prime, splits, rng), factor_tree(b, is_prime, splits, rng))

def leaves(t):
    return [t[1]] if t[0] == "leaf" else leaves(t[2]) + leaves(t[3])

def _depth(t):
    return 1 if t[0] == "leaf" else 1 + max(_depth(t[2]), _depth(t[3]))

def _layout(t, depth=0, x0=0, acc=None):
    """葉を左から順に並べ、親は子の真ん中に置く（戻り値：{id(node): (x, y)} と次の x）"""
    acc = acc if acc is not None else {}
    if t[0] == "leaf":
        acc[id(t)] = (x0, -depth)
        return acc, x0 + 1
    acc, x1 = _layout(t[2], depth + 1, x0, acc)
    acc, x2 = _layout(t[3], depth + 1, x1, acc)
    acc[id(t)] = ((acc[id(t[2])][0] + acc[id(t[3])][0]) / 2, -depth)
    return acc, x2

def _draw_tree(ax, t, pos, fs=10):
    x, y = pos[id(t)]
    if t[0] == "leaf":
        ax.add_patch(FancyBboxPatch((x - 0.32, y - 0.22), 0.64, 0.44, boxstyle="round,pad=0,rounding_size=0.1",
                                    fc="black", ec="black"))
        ax.text(x, y, str(t[1]), ha="center", va="center", fontsize=fs, color="white", fontweight="bold")
        return
    ax.add_patch(FancyBboxPatch((x - 0.36, y - 0.22), 0.72, 0.44, boxstyle="round,pad=0,rounding_size=0.1",
                                fc="white", ec="black", lw=0.9))
    ax.text(x, y, str(t[1]), ha="center", va="center", fontsize=fs, color="black")
    for child in (t[2], t[3]):
        cx, cy = pos[id(child)]
        ax.plot([x, cx], [y - 0.22, cy + 0.22], color="#666666", lw=0.9, zorder=0)
        _draw_tree(ax, child, pos, fs)

def show_trees(trees, titles=None, save="factor_trees", note=True):
    """いくつかの因数の木を並べて描く"""
    k = len(trees)
    depth = max(_depth(t) for t in trees)
    width = max(len(leaves(t)) for t in trees)
    fig, axes = plt.subplots(1, k, figsize=(0.85 * width * k + 0.8, 1.0 * depth + 1.2), squeeze=False)
    for i, t in enumerate(trees):
        ax = axes[0][i]
        pos, _ = _layout(t)
        n_leaf = len(leaves(t))
        xs = [p[0] for p in pos.values()]
        cx = (min(xs) + max(xs)) / 2
        pos = {kk: (p[0] - cx, p[1]) for kk, p in pos.items()}
        ax.set_xlim(-width / 2 - 0.6, width / 2 + 0.6); ax.set_ylim(-(depth - 1) - 1.0, 0.6)
        ax.set_aspect("equal"); ax.axis("off")
        _draw_tree(ax, t, pos)
        lv = sorted(leaves(t))
        if note:
            ax.text(0, -(depth - 1) - 0.75, "葉をそろえると： " + " × ".join(map(str, lv)),
                    ha="center", va="center", fontsize=9.5, color="#222222")
        if titles:
            ax.set_title(titles[i], fontsize=10, loc="left", color="#222222")
    fig.tight_layout()
    _save(fig, save)
    plt.show()

def sup(e):
    """指数を上付き文字に（2 → ²）"""
    return str(e).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))

def factorization_str(n):
    """素因数分解を 2³ × 3² の形の文字列で"""
    if n == 1:
        return "1"
    f = sympy.factorint(n)
    return " × ".join(f"{p}{sup(e)}" if e > 1 else f"{p}" for p, e in sorted(f.items()))

# ---------- 約数の表 ----------
def divisor_grid(n, save="divisor_grid"):
    """n の約数を「素因数ごとの指数の組み合わせ」の表として描く（素因数 2 種類まで）"""
    f = sorted(sympy.factorint(n).items())
    assert 1 <= len(f) <= 2, "素因数が 1〜2 種類の数で"
    (p, e), = f[:1]
    q, g = f[1] if len(f) == 2 else (None, 0)
    rows = [p ** i for i in range(e + 1)]
    cols = [q ** j for j in range(g + 1)] if q else [1]
    fig, ax = plt.subplots(figsize=(1.1 * (len(cols) + 1) + 1.2, 0.6 * (len(rows) + 1) + 0.9))
    ax.set_xlim(-0.2, len(cols) + 1); ax.set_ylim(-0.2, len(rows) + 1); ax.axis("off"); ax.set_aspect("equal")
    H = len(rows) + 1
    for j, cv in enumerate(cols):
        lab = f"{q}{sup(j)}" if q and j > 1 else (str(cv))
        ax.text(j + 1.5, H - 0.5, lab, ha="center", va="center", fontsize=10, color="#444444")
    for i, rv in enumerate(rows):
        lab = f"{p}{sup(i)}" if i > 1 else str(rv)
        ax.text(0.5, H - 1.5 - i, lab, ha="center", va="center", fontsize=10, color="#444444")
        for j, cv in enumerate(cols):
            ax.add_patch(FancyBboxPatch((j + 1.05, H - 1.95 - i), 0.9, 0.9, boxstyle="square,pad=0",
                                        fc="#eeeeee", ec="#999999", lw=0.6))
            ax.text(j + 1.5, H - 1.5 - i, str(rv * cv), ha="center", va="center", fontsize=11, color="black")
    ax.plot([1, 1], [0, H - 1], color="#444444", lw=0.8); ax.plot([0, len(cols) + 1], [H - 1, H - 1], color="#444444", lw=0.8)
    n_div = (e + 1) * (g + 1)
    ax.set_title(f"{n} = {factorization_str(n)} の約数： {e+1} 行 × {g+1} 列 = {n_div} 個", fontsize=10, loc="left", color="#222222")
    _save(fig, save)
    plt.show()

# ---------- 素数レース ----------
def prime_race(N=30000, save="prime_race"):
    """4 で割って 3 余る素数の個数 − 1 余る素数の個数、を x まで数えて描く"""
    s = np.ones(N + 1, dtype=bool); s[:2] = False
    for i in range(2, int(N ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    primes = np.nonzero(s)[0]
    d = np.zeros(N + 1, dtype=int)
    d[primes[primes % 4 == 3]] += 1
    d[primes[primes % 4 == 1]] -= 1
    D = np.cumsum(d)
    x = np.arange(N + 1)
    neg = np.nonzero(D < 0)[0]
    first = int(neg[0]) if len(neg) else None
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 3.6), gridspec_kw={"width_ratios": [2.2, 1]})
    ax1.step(x, D, where="post", color="black", lw=0.8)
    ax1.axhline(0, color="#999999", lw=0.8)
    ax1.set_xlabel("x"); ax1.set_ylabel("（3余る素数）−（1余る素数）")
    ax1.set_title(f"x 以下の素数を数える：4 で割って 3 余る方が多い？（x は {N} まで）", fontsize=10, loc="left", color="#222222")
    ax1.set_ylim(min(D.min(), 0) - 0.3 * D.max(), D.max() * 1.1)
    if first:
        ax1.annotate(f"x = {first}：初めて 1 余る方が多くなる", xy=(first, D[first]), xytext=(first * 0.35, -0.22 * D.max()),
                     fontsize=9, color="#222222", va="center",
                     arrowprops=dict(arrowstyle="-|>", color="#222222", lw=0.8, shrinkB=3))
        lo, hi = first - 300, first + 300
        ax2.step(x[lo:hi], D[lo:hi], where="post", color="black", lw=1.0)
        ax2.plot([first], [D[first]], "o", color="black", ms=4)
        ax2.axhline(0, color="#999999", lw=0.8)
        ax2.set_xlim(lo, hi); ax2.set_title(f"{first} のまわりを拡大", fontsize=10, loc="left", color="#222222")
        ax2.set_xlabel("x")
    fig.tight_layout()
    _save(fig, save)
    plt.show()
    lead3 = int(np.sum(D[2:] > 0)); lead1 = int(np.sum(D[2:] < 0)); tie = int(np.sum(D[2:] == 0))
    print(f"x = 2〜{N} のうち、3 余る方が多い x：{lead3} 個、同数：{tie} 個、1 余る方が多い x：{lead1} 個")
    print(f"初めて 1 余る方が多くなる x：{first}")
    return D

# ---------- 発展：4 で割って 1 余る数だけの世界（H の世界） ----------
def h_numbers(limit):
    return [h for h in range(1, limit + 1) if h % 4 == 1]

def is_h_prime(h, _cache={}):
    """H の世界の「素数」：1 より大きく、H の世界の二つの数（どちらも 1 より大きい）の積に書けない"""
    if h in _cache:
        return _cache[h]
    ok = h > 1 and h % 4 == 1 and not any(h % a == 0 and (h // a) % 4 == 1 for a in range(5, int(h ** 0.5) + 1, 4))
    _cache[h] = ok
    return ok

def h_factorizations(n):
    """H の世界で n を H-素数の積に分けるやり方をすべて（順序は無視）"""
    res = set()
    def rec(m, start, cur):
        if m == 1:
            res.add(tuple(cur)); return
        for q in range(start, int(m ** 0.5) + 1, 4):
            if m % q == 0 and is_h_prime(q):
                rec(m // q, q, cur + [q])
        if m >= start and is_h_prime(m):
            res.add(tuple(cur + [m]))
    rec(n, 5, [])
    return sorted(res)

def h_split(n):
    """H の世界での分け方（因数の木用）：最小の H-因数で分ける"""
    for a in range(5, int(n ** 0.5) + 1, 4):
        if n % a == 0:
            return a, n // a
    return None

# ---------- 発展：素数は無限にある（ユークリッドの数） ----------
def euclid_numbers(k=10):
    rows = []
    prod = 1
    for i, p in enumerate(sympy.primerange(2, 1000), 1):
        if i > k:
            break
        prod *= p
        n = prod + 1
        f = sympy.factorint(n)
        new = [q for q in f if q > p]
        rows.append((i, p, n, factorization_str(n), new))
    print(f"{'k':>2} {'最後の素数 p':>10} {'2×3×…×p + 1':>14}  {_pad('素因数分解', 22)}新しく出た素数")
    for i, p, n, fs, new in rows:
        print(f"{i:>2} {p:>10} {n:>14}  {_pad(fs, 22)}{', '.join(map(str, new))}")
    return rows


# ---------- 結果を地図アプリへ送る ----------
def report(exp, summary, data=None):
    """実験の結果を「自分の地図」アプリに届ける。
    JupyterLite：同じブラウザで開いている地図アプリのタブに BroadcastChannel で送る。
    それ以外：evidence_<exp>.json に書く。どちらの場合も画面にも表示する。"""
    msg = {"type": "evidence", "exp": exp, "summary": summary, "data": data or {}, "t": now()}
    sent = False
    if sys.platform == "emscripten":
        try:
            import js
            ch = js.BroadcastChannel.new("kg-map")
            ch.postMessage(json.dumps(msg, ensure_ascii=False))
            ch.close()
            sent = True
        except Exception:
            sent = False
    else:
        try:
            with open(f"evidence_{exp}.json", "w", encoding="utf-8") as f:
                json.dump(msg, f, ensure_ascii=False, indent=1)
        except Exception:
            pass
    print("■ 結果：", summary)
    if sent:
        print("→ 地図アプリに送りました（地図のタブを開いていれば「届いた結果」に出ます）")
    else:
        print("→ 地図アプリの「記録」で、この結果を自分で書き込んでください")
    return msg
