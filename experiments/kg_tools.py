"""実験ノート共通の道具（kg_tools）— 篩の表、因数の木、約数の表、素数レース、H の世界、ユークリッドの数。
どの実験ノートも `from kg_tools import *` で使う。
最後に report() で結果を「地図アプリ」に送る（JupyterLite では同じブラウザの別タブへ、それ以外ではファイルへ）。
"""
import json, os, sys, copy, math, random, time
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

# ---------- 素数の個数を、並べずに数える（Lucy_Hedgehog の方法） ----------
def prime_count(n, progress=None, chunk=1 << 20):
    """n までの素数の個数 pi(n) を、素数を一つずつ並べずに数える（Lucy_Hedgehog の方法。計算量はだいたい n^(3/4)）。
    戻り値：(pi(n), 10 のべきごとの個数の辞書 {10: 4, 100: 25, ...})
    目安（手元の Python）：10**12 で 4 秒、10**13 で 20 秒、10**14 で 2 分・250 MB、10**15 で 10〜15 分・600 MB（見積もり）。ブラウザ（JupyterLite）はその 2〜3 倍"""
    n = int(n)
    r = math.isqrt(n)
    lo = np.arange(r + 1, dtype=np.int64) - 1; lo[0] = 0        # lo[v]   ：「2〜v の整数の個数」から出発し、合成数を消していくと pi(v) になる
    hi = n // np.arange(1, r + 1, dtype=np.int64) - 1            # hi[i-1] ：同じことを n//i について
    if progress is None:
        progress = n >= 10 ** 12
    t0 = time.time(); nxt = 0.1
    for p in range(2, r + 1):
        if lo[p] == lo[p - 1]:                                    # p が素数でなければ何もしない
            continue
        sp = int(lo[p - 1]); p2 = p * p
        m = min(r, n // p2)                                       # hi の更新（i = 1..m）。参照するのは更新前の値だけ
        for a in range(0, m, chunk):
            b = min(m, a + chunk)
            ip = np.arange(a + 1, b + 1, dtype=np.int64) * p
            small = ip <= r
            sub = np.empty(b - a, dtype=np.int64)
            sub[small] = hi[ip[small] - 1]
            sub[~small] = lo[n // ip[~small]]
            hi[a:b] -= sub - sp
        if p2 <= r:                                               # lo の更新（v = r..p2、大きい方から。lo[v//p] は必ず更新前の値）
            for b in range(r + 1, p2, -chunk):
                a = max(p2, b - chunk)
                v = np.arange(a, b, dtype=np.int64)
                lo[a:b] -= lo[v // p] - sp
        if progress and p / r >= nxt:
            print(f"  …{round(nxt * 100)}%（{time.time() - t0:.0f} 秒）"); nxt += 0.1
    powers = {}
    k = 1
    while 10 ** k <= n:
        x = 10 ** k
        powers[x] = int(lo[x]) if x <= r else int(hi[n // x - 1])
        k += 1
    return int(hi[0]), powers

def li(x):
    """対数積分 Li(x) = ∫₂ˣ dt / ln t。素数の個数の目安として x / ln x より近い"""
    try:
        import mpmath                             # sympy と一緒に入っている。精度が高い
        return float(mpmath.li(mpmath.mpf(int(x)), offset=True))
    except Exception:
        pass
    from math import log
    L = log(float(x))
    s = 0.57721566490153286 + log(L)          # γ + ln ln x
    term = 1.0
    for k in range(1, 200):
        term *= L / k
        s += term / k
        if term / k < 1e-16 * abs(s):
            break
    return s - 1.0451637801174927            # li(x) - li(2)


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


# ---------- 絵の道具（パズルノート用。モノクロ） ----------
_INK, _GRAY, _LIGHT, _LINE = "#111111", "#9a9a9a", "#e6e6e6", "#bbbbbb"

def _as_set(x, N):
    """集合・リスト・判定関数のどれでも受けて、1〜N の集合にする"""
    if x is None:
        return set()
    if callable(x):
        return {n for n in range(1, N + 1) if x(n)}
    return set(x)

def number_grid(N, fill=None, ring=None, cross=None, cols=10, title=None, ax=None, cell=0.62, numbers=True, save=None):
    """1〜N の表。fill：黒く塗る数、ring：丸をつける数、cross：斜線で消す数（どれも集合か判定関数）"""
    F, R, C = _as_set(fill, N), _as_set(ring, N), _as_set(cross, N)
    rows = math.ceil(N / cols)
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(cell * cols + 0.4, cell * rows + 0.7))
    ax.set_xlim(0, cols); ax.set_ylim(0, rows); ax.set_aspect("equal"); ax.axis("off")
    fs = max(5, min(11, 110 / cols))
    for k in range(1, N + 1):
        r, c = divmod(k - 1, cols)
        x, y = c, rows - 1 - r
        f = k in F
        ax.add_patch(FancyBboxPatch((x + 0.05, y + 0.05), 0.9, 0.9, boxstyle="round,pad=0,rounding_size=0.12",
                                    fc=_INK if f else "white", ec=_LINE if not f else _INK, lw=0.6))
        if k in R:
            ax.add_patch(plt.Circle((x + 0.5, y + 0.5), 0.36, fc="none", ec="white" if f else _INK, lw=1.6))
        if k in C:
            ax.plot([x + 0.2, x + 0.8], [y + 0.2, y + 0.8], color=_GRAY, lw=1.2)
        if numbers:
            ax.text(x + 0.5, y + 0.5, str(k), ha="center", va="center", fontsize=fs, color="white" if f else (_GRAY if k in C else _INK))
    if title:
        ax.set_title(title, fontsize=9.5, loc="left", color="#222222")
    if own:
        if save:
            _save(fig, save)
        plt.show()

def grid_panels(N, steps, titles=None, cols=10, cross_fn=None, ncol=None, save=None):
    """表を何枚も並べる。steps の各要素を cross_fn(step) に渡して、消す数の集合を作る（例：篩の途中経過）"""
    k = len(steps); ncol = ncol or k
    nrow = math.ceil(k / ncol); rows = math.ceil(N / cols)
    fig, axes = plt.subplots(nrow, ncol, figsize=(0.42 * cols * ncol + 0.6, 0.42 * rows * nrow + 0.8), squeeze=False)
    for i, st in enumerate(steps):
        ax = axes[i // ncol][i % ncol]
        number_grid(N, cross=cross_fn(st) if cross_fn else st, cols=cols, ax=ax, cell=0.42,
                    title=(titles[i] if titles else None))
    for j in range(k, nrow * ncol):
        axes[j // ncol][j % ncol].axis("off")
    fig.tight_layout()
    if save:
        _save(fig, save)
    plt.show()

def compare_grid(N, hand, machine, cols=10, title=None, save=None):
    """手の結果と機械の結果を一枚の表で照らす：両方＝黒、機械だけ＝丸、手だけ＝斜線"""
    H, M = _as_set(hand, N), _as_set(machine, N)
    both, only_m, only_h = H & M, M - H, H - M
    t = title or f"手と機械を照らす（1〜{N}）：黒＝両方、丸＝機械だけ、斜線＝手だけ"
    number_grid(N, fill=both, ring=only_m, cross=only_h, cols=cols, title=t, save=save)
    if not only_m and not only_h:
        print("手と機械は一致（食い違いなし）")
    else:
        print("機械だけ：", sorted(only_m) or "なし", "／ 手だけ：", sorted(only_h) or "なし")

def count_bars(N, f, highlight=None, title=None, ylabel="", save=None):
    """1〜N の棒グラフ。highlight（集合か判定関数）の数は黒、それ以外は灰色"""
    Hs = _as_set(highlight, N)
    vals = [f(n) for n in range(1, N + 1)]
    fig, ax = plt.subplots(figsize=(min(12, 0.11 * N + 1.5), 2.8))
    ax.bar(range(1, N + 1), vals, color=[_INK if n in Hs else _GRAY for n in range(1, N + 1)], width=0.75)
    ax.set_xlim(0, N + 1); ax.set_xlabel("n"); ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=9.5, loc="left", color="#222222")
    if save:
        _save(fig, save)
    plt.show()

def dots_remainder(n, d, title=None, ax=None, save=None):
    """n 個の点を d 個ずつの行に並べる。余りの点は黒。「d で割って何余る」の絵"""
    q, r = divmod(n, d)
    rows = q + (1 if r else 0)
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(min(10, 0.28 * d + 1.5), min(8, 0.28 * rows + 0.9)))
    ax.set_xlim(-0.6, d + 0.6); ax.set_ylim(-0.6, rows + 0.6); ax.set_aspect("equal"); ax.axis("off")
    for i in range(n):
        rr, cc = divmod(i, d)
        leftover = i >= q * d
        ax.add_patch(plt.Circle((cc + 0.5, rows - 1 - rr + 0.5), 0.34, fc=_INK if leftover else "white", ec=_INK, lw=0.7))
    ax.set_title(title or f"{n} = {d} × {q} + {r}　（{d} で割ると {r} 余る）", fontsize=9.5, loc="left", color="#222222")
    if own:
        if save:
            _save(fig, save)
        plt.show()

def remainder_panels(n, ds, save=None):
    """同じ n を、いろいろな d で割った余りの絵を並べる"""
    fig, axes = plt.subplots(1, len(ds), figsize=(3.2 * len(ds), 4.2))
    for ax, d in zip(axes, ds):
        dots_remainder(n, d, ax=ax)
    fig.tight_layout()
    if save:
        _save(fig, save)
    plt.show()

def share_dots(a, b, groups, labels=("あめ", "チョコ"), save=None):
    """a 個と b 個を groups 人で分ける絵：列が人。余りは列の外に出す"""
    fig, axes = plt.subplots(1, 2, figsize=(0.55 * groups + 4, 3.4), gridspec_kw={"width_ratios": [1, 1]})
    for ax, n, lab in zip(axes, (a, b), labels):
        q, r = divmod(n, groups)
        ax.set_xlim(-0.6, groups + 1.8); ax.set_ylim(-0.6, max(q, 1) + 1.2); ax.set_aspect("equal"); ax.axis("off")
        for i in range(n):
            if i < q * groups:
                c, rr = i % groups, i // groups
                ax.add_patch(plt.Circle((c + 0.5, rr + 0.5), 0.36, fc="white", ec=_INK, lw=0.8))
            else:
                j = i - q * groups
                ax.add_patch(plt.Circle((groups + 1.2, j + 0.5), 0.36, fc=_INK, ec=_INK))
        for c in range(groups):
            ax.text(c + 0.5, -0.35, str(c + 1), ha="center", va="center", fontsize=7, color=_GRAY)
        ax.set_title(f"{lab} {n} 個を {groups} 人で：1 人 {q} 個、余り {r}", fontsize=9.5, loc="left", color="#222222")
    fig.tight_layout()
    if save:
        _save(fig, save)
    plt.show()

def sticks(a, b, upto, save=None):
    """長さ a と b の棒をつなげて並べ、端がそろう位置に印"""
    fig, ax = plt.subplots(figsize=(10, 2.2))
    for row, L, lab in ((1, a, f"{a} cm"), (0, b, f"{b} cm")):
        x = 0
        while x < upto:
            ax.add_patch(plt.Rectangle((x, row * 0.9), min(L, upto - x), 0.6, fc="white" if row else _LIGHT, ec=_INK, lw=0.8))
            x += L
        ax.text(-0.5, row * 0.9 + 0.3, lab, ha="right", va="center", fontsize=9)
    common = [x for x in range(1, upto + 1) if x % a == 0 and x % b == 0]
    for x in common:
        ax.plot([x, x], [-0.2, 1.7], color=_INK, lw=1.4, ls="--")
        ax.text(x, 1.85, str(x), ha="center", va="bottom", fontsize=9, color=_INK)
    ax.set_xlim(-6, upto + 1); ax.set_ylim(-0.4, 2.3); ax.axis("off")
    ax.set_title(f"端がそろう長さ：{', '.join(map(str, common)) or 'なし'}（{upto} まで）", fontsize=9.5, loc="left", color="#222222")
    if save:
        _save(fig, save)
    plt.show()

def rectangles_of(n, ax=None, title=None):
    """n 枚のタイルで作れる長方形をすべて描く"""
    rects = [(a, n // a) for a in range(1, math.isqrt(n) + 1) if n % a == 0]
    own = ax is None
    W = sum(b for _, b in rects) + 1.2 * len(rects)
    H = max(a for a, _ in rects) + 1
    if own:
        fig, ax = plt.subplots(figsize=(min(12, 0.22 * W + 0.5), min(5, 0.22 * H + 0.9)))
    x = 0
    for a, b in rects:
        for i in range(a):
            for j in range(b):
                ax.add_patch(plt.Rectangle((x + j, i), 0.92, 0.92, fc=_INK if a == b else _GRAY, ec="white", lw=0.3))
        ax.text(x, a + 0.25, f"{a} × {b}", fontsize=8, color=_INK)
        x += b + 1.2
    ax.set_xlim(-0.3, W); ax.set_ylim(-0.3, H + 0.6); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title or f"{n} 枚：{len(rects)} 通り", fontsize=9.5, loc="left", color="#222222")
    if own:
        plt.show()

def rectangles_panels(ns, save=None):
    fig, axes = plt.subplots(len(ns), 1, figsize=(10, 1.6 * len(ns) + 1.5), squeeze=False)
    for ax, n in zip(axes[:, 0], ns):
        rectangles_of(n, ax=ax)
    fig.tight_layout()
    if save:
        _save(fig, save)
    plt.show()

def tiles_square(ns, save=None):
    """それぞれの枚数で、正方形ができるなら正方形、できなければ一番正方形に近い長方形を描く"""
    fig, axes = plt.subplots(1, len(ns), figsize=(2.6 * len(ns), 3.2))
    for ax, n in zip(axes, ns):
        a = max(d for d in range(1, math.isqrt(n) + 1) if n % d == 0); b = n // a
        sq = a == b
        for i in range(a):
            for j in range(b):
                ax.add_patch(plt.Rectangle((j, i), 0.92, 0.92, fc=_INK if sq else _GRAY, ec="white", lw=0.3))
        ax.set_xlim(-0.5, max(b, 9) + 0.5); ax.set_ylim(-0.5, max(a, 9) + 0.5); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(f"{n} 枚：{'正方形' if sq else f'{a} × {b}'}\n{factorization_str(n)}", fontsize=9.5, loc="left", color="#222222")
    fig.tight_layout()
    if save:
        _save(fig, save)
    plt.show()

def exponent_bars(ns, save=None):
    """素因数分解の指数を棒で描く。偶数の指数は黒、奇数は白"""
    fig, axes = plt.subplots(1, len(ns), figsize=(2.4 * len(ns), 2.6))
    if len(ns) == 1:
        axes = [axes]
    for ax, n in zip(axes, ns):
        f = sorted(sympy.factorint(n).items())
        ax.bar([str(p) for p, _ in f], [e for _, e in f], color=[_INK if e % 2 == 0 else "white" for _, e in f], edgecolor=_INK, width=0.6)
        ax.set_ylim(0, max([e for _, e in f] + [1]) + 0.8); ax.set_yticks(range(0, max([e for _, e in f] + [1]) + 1))
        ax.set_title(f"{n} = {factorization_str(n)}", fontsize=9.5, loc="left", color="#222222")
        ax.set_xlabel("素数"); ax.set_ylabel("指数（個数）")
    fig.tight_layout()
    if save:
        _save(fig, save)
    plt.show()

def divisor_lattice(n, save=None):
    """n の約数を、素数を 1 つかけるごとに 1 段上がる図（ハッセ図）で描く。素因数が 3 種類まで"""
    f = sorted(sympy.factorint(n).items())
    ps = [p for p, _ in f]
    divs = sympy.divisors(n)
    def exps(d):
        return tuple(sympy.multiplicity(p, d) for p in ps)
    levels = {}
    for d in divs:
        levels.setdefault(sum(exps(d)), []).append(d)
    top = max(levels)
    fig, ax = plt.subplots(figsize=(1.1 * max(len(v) for v in levels.values()) + 1.5, 0.9 * (top + 1) + 0.8))
    pos = {}
    for lv, ds in levels.items():
        ds.sort(key=lambda d: exps(d))
        for i, d in enumerate(ds):
            pos[d] = (i - (len(ds) - 1) / 2, lv)
    for d in divs:
        for p in ps:
            if (d * p) in pos:
                (x1, y1), (x2, y2) = pos[d], pos[d * p]
                ax.plot([x1, x2], [y1, y2], color=_LINE if p == ps[0] else (_GRAY if p == ps[-1] and len(ps) > 1 else _INK), lw=0.9, zorder=0)
    for d, (x, y) in pos.items():
        ax.add_patch(FancyBboxPatch((x - 0.36, y - 0.2), 0.72, 0.4, boxstyle="round,pad=0,rounding_size=0.1", fc="white", ec=_INK, lw=0.8))
        ax.text(x, y, str(d), ha="center", va="center", fontsize=8.5, color=_INK)
    ax.set_xlim(-max(len(v) for v in levels.values()) / 2 - 0.7, max(len(v) for v in levels.values()) / 2 + 0.7)
    ax.set_ylim(-0.6, top + 0.6); ax.axis("off")
    ax.set_title(f"{n} = {factorization_str(n)} の約数（{len(divs)} 個）：線は「× {'、× '.join(map(str, ps))}」で 1 段上がる", fontsize=9.5, loc="left", color="#222222")
    if save:
        _save(fig, save)
    plt.show()

def endless_tree(n, depth=5, save=None):
    """1 で分けるのを許すと終わらない木"""
    fig, ax = plt.subplots(figsize=(4.2, 0.85 * depth + 1))
    for k in range(depth):
        y = -k
        ax.add_patch(FancyBboxPatch((0.6, y - 0.22), 0.9, 0.44, boxstyle="round,pad=0,rounding_size=0.1", fc="white", ec=_INK, lw=0.8))
        ax.text(1.05, y, str(n), ha="center", va="center", fontsize=10)
        if k < depth - 1:
            ax.add_patch(FancyBboxPatch((-0.9, y - 1.22), 0.9, 0.44, boxstyle="round,pad=0,rounding_size=0.1", fc=_INK, ec=_INK))
            ax.text(-0.45, y - 1, "1", ha="center", va="center", fontsize=10, color="white")
            ax.plot([1.05, -0.45], [y - 0.22, y - 0.78], color="#666666", lw=0.9)
            ax.plot([1.05, 1.05], [y - 0.22, y - 0.78], color="#666666", lw=0.9)
    ax.text(1.05, -depth + 0.55, "…", ha="center", va="center", fontsize=14)
    ax.set_xlim(-1.6, 2.2); ax.set_ylim(-depth + 0.2, 0.6); ax.axis("off")
    ax.set_title(f"{n} = 1 × {n} を許すと、木が終わらない", fontsize=9.5, loc="left", color="#222222")
    if save:
        _save(fig, save)
    plt.show()

def billiard_path(m, n):
    """左下から 45° に出た玉の道。戻り値：(着いた角, 跳ね返り回数, 通った点)"""
    x, y, dx, dy, bounces, path = 0, 0, 1, 1, 0, [(0, 0)]
    while True:
        x += dx; y += dy; path.append((x, y))
        at_x, at_y = x in (0, n), y in (0, m)
        if at_x and at_y:
            return {(0, m): "左上", (n, m): "右上", (n, 0): "右下"}[(x, y)], bounces, path
        if at_x:
            dx = -dx; bounces += 1
        if at_y:
            dy = -dy; bounces += 1

def billiard_panels(pairs, save=None):
    fig, axes = plt.subplots(1, len(pairs), figsize=(3 * len(pairs), 3))
    if len(pairs) == 1:
        axes = [axes]
    for ax, (m, n) in zip(axes, pairs):
        c, b, path = billiard_path(m, n)
        ax.plot([p[0] for p in path], [p[1] for p in path], color=_INK, lw=1.3)
        ax.plot([0], [0], "o", color=_INK, ms=5)
        ax.set_xticks(range(n + 1)); ax.set_yticks(range(m + 1)); ax.grid(True, color="#dddddd", lw=0.6)
        ax.set_xlim(0, n); ax.set_ylim(0, m); ax.set_aspect("equal"); ax.tick_params(labelsize=7)
        ax.set_title(f"{m} × {n}：{c}、{b} 回", fontsize=9.5, loc="left", color="#222222")
    fig.tight_layout()
    if save:
        _save(fig, save)
    plt.show()

def billiard_unfold(m, n, save=None):
    """跳ね返りを「台を折り返して並べる」と、玉の道はまっすぐな線になる。角に着くのは (L, L)、L は最小公倍数"""
    L = math.lcm(m, n)
    fig, ax = plt.subplots(figsize=(min(10, 0.35 * L + 1), min(8, 0.35 * L + 1)))
    for i in range(L // n):
        for j in range(L // m):
            ax.add_patch(plt.Rectangle((i * n, j * m), n, m, fc="white" if (i + j) % 2 == 0 else _LIGHT, ec=_LINE, lw=0.7))
    ax.plot([0, L], [0, L], color=_INK, lw=1.6)
    ax.plot([0], [0], "o", color=_INK, ms=5); ax.plot([L], [L], "s", color=_INK, ms=6)
    ax.set_xlim(0, L); ax.set_ylim(0, L); ax.set_aspect("equal"); ax.set_xticks(range(0, L + 1, n)); ax.set_yticks(range(0, L + 1, m)); ax.tick_params(labelsize=7)
    ax.set_title(f"{m} × {n} の台を折り返して並べると、道はまっすぐ。着くのは ({L}, {L})　L = 最小公倍数", fontsize=9.5, loc="left", color="#222222")
    if save:
        _save(fig, save)
    plt.show()

def bounce_table(M, N, save=None):
    """縦 m・横 n の台ごとの跳ね返り回数の表。最大公約数が大きいほど濃い"""
    fig, ax = plt.subplots(figsize=(0.6 * N + 1.2, 0.6 * M + 1.0))
    for m in range(1, M + 1):
        for n in range(1, N + 1):
            _, b, _ = billiard_path(m, n)
            g = math.gcd(m, n)
            shade = 1 - min(0.75, 0.15 * (g - 1))
            ax.add_patch(plt.Rectangle((n - 0.5, m - 0.5), 1, 1, fc=(shade, shade, shade), ec="white", lw=0.5))
            ax.text(n, m, str(b), ha="center", va="center", fontsize=7.5, color=_INK if shade > 0.5 else "white")
    ax.set_xlim(0.5, N + 0.5); ax.set_ylim(0.5, M + 0.5); ax.set_aspect("equal")
    ax.set_xticks(range(1, N + 1)); ax.set_yticks(range(1, M + 1)); ax.tick_params(labelsize=7)
    ax.set_xlabel("横 n"); ax.set_ylabel("縦 m")
    ax.set_title("跳ね返りの回数（濃いほど最大公約数が大きい）", fontsize=9.5, loc="left", color="#222222")
    if save:
        _save(fig, save)
    plt.show()

def stamps_line(a, b, upto, ax=None, save=None):
    """a 円と b 円で作れる金額を黒、作れない金額を白で、1〜upto の数直線に"""
    ok = [False] * (upto + 1); ok[0] = True
    for x in range(1, upto + 1):
        ok[x] = (x >= a and ok[x - a]) or (x >= b and ok[x - b])
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(min(12, 0.32 * upto + 1), 1.3))
    for x in range(1, upto + 1):
        ax.add_patch(FancyBboxPatch((x - 0.45, 0), 0.9, 0.9, boxstyle="round,pad=0,rounding_size=0.15", fc=_INK if ok[x] else "white", ec=_INK, lw=0.6))
        ax.text(x, 0.45, str(x), ha="center", va="center", fontsize=7, color="white" if ok[x] else _INK)
    ax.set_xlim(0, upto + 1); ax.set_ylim(-0.2, 1.1); ax.set_aspect("equal"); ax.axis("off")
    bad = [x for x in range(1, upto + 1) if not ok[x]]
    ax.set_title(f"{a} 円と {b} 円：作れない金額（白）は {bad if len(bad) < 15 else str(bad[:12]) + ' …'}", fontsize=9, loc="left", color="#222222")
    if own:
        if save:
            _save(fig, save)
        plt.show()

def stamps_panels(pairs, upto, save=None):
    fig, axes = plt.subplots(len(pairs), 1, figsize=(min(12, 0.32 * upto + 1), 1.25 * len(pairs)))
    for ax, (a, b) in zip(axes, pairs):
        stamps_line(a, b, upto, ax=ax)
    fig.tight_layout()
    if save:
        _save(fig, save)
    plt.show()

def stamps_lattice(a, b, upto, save=None):
    """i 枚の a 円と j 枚の b 円で作れる金額の表。upto より大きい金額は薄く"""
    I, J = upto // a + 1, upto // b + 1
    fig, ax = plt.subplots(figsize=(0.75 * I + 1.2, 0.6 * J + 1.0))
    for i in range(I):
        for j in range(J):
            v = i * a + j * b
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, fc="white" if v <= upto else _LIGHT, ec=_LINE, lw=0.5))
            ax.text(i, j, str(v), ha="center", va="center", fontsize=7.5, color=_INK if v <= upto else _GRAY)
    ax.set_xlim(-0.5, I - 0.5); ax.set_ylim(-0.5, J - 0.5); ax.set_aspect("equal")
    ax.set_xticks(range(I)); ax.set_yticks(range(J)); ax.tick_params(labelsize=7)
    ax.set_xlabel(f"{a} 円の枚数"); ax.set_ylabel(f"{b} 円の枚数")
    ax.set_title(f"{a} 円 × 枚数 ＋ {b} 円 × 枚数：{upto} までに出てこない金額は？", fontsize=9.5, loc="left", color="#222222")
    if save:
        _save(fig, save)
    plt.show()

def two_squares_pics(ns, save=None):
    """n 枚を正方形 2 つに並べた絵（できないときは印）"""
    fig, axes = plt.subplots(1, len(ns), figsize=(2.6 * len(ns), 2.8))
    for ax, n in zip(axes, ns):
        found = None
        for a in range(0, math.isqrt(n) + 1):
            b2 = n - a * a; b = math.isqrt(b2)
            if b * b == b2:
                found = (max(a, b), min(a, b)); break
        ax.set_aspect("equal"); ax.axis("off")
        if found:
            a, b = found
            for i in range(a):
                for j in range(a):
                    ax.add_patch(plt.Rectangle((j, i), 0.92, 0.92, fc=_INK, ec="white", lw=0.3))
            for i in range(b):
                for j in range(b):
                    ax.add_patch(plt.Rectangle((a + 1 + j, i), 0.92, 0.92, fc=_GRAY, ec="white", lw=0.3))
            ax.set_xlim(-0.5, a + b + 1.5); ax.set_ylim(-0.5, a + 0.5)
            ax.set_title(f"{n} = {a}² + {b}²", fontsize=9.5, loc="left", color="#222222")
        else:
            ax.set_xlim(0, 6); ax.set_ylim(0, 4)
            ax.text(3, 2, "できない", ha="center", va="center", fontsize=11, color=_GRAY)
            ax.set_title(f"{n} 枚", fontsize=9.5, loc="left", color="#222222")
    fig.tight_layout()
    if save:
        _save(fig, save)
    plt.show()

def lockers_strip(n_lockers, persons, save=None):
    """ロッカーの開閉を、人ごとの行で描く。黒＝開いている"""
    state = [False] * (n_lockers + 1)
    fig, ax = plt.subplots(figsize=(0.32 * n_lockers + 1.4, 0.3 * persons + 0.8))
    for k in range(1, persons + 1):
        for j in range(k, n_lockers + 1, k):
            state[j] = not state[j]
        y = persons - k
        for j in range(1, n_lockers + 1):
            ax.add_patch(plt.Rectangle((j - 0.45, y + 0.05), 0.9, 0.9, fc=_INK if state[j] else "white", ec=_LINE, lw=0.5))
        ax.text(0.2, y + 0.5, f"{k} 人目", ha="right", va="center", fontsize=7, color=_GRAY)
    for j in range(1, n_lockers + 1):
        ax.text(j, persons + 0.35, str(j), ha="center", va="center", fontsize=7, color=_GRAY)
    ax.set_xlim(-2.2, n_lockers + 0.6); ax.set_ylim(-0.1, persons + 0.8); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"{n_lockers} 個のロッカー、{persons} 人が通ったあと（黒＝開いている）", fontsize=9.5, loc="left", color="#222222")
    if save:
        _save(fig, save)
    plt.show()

def race_lines(N, m=4, a=3, b=1, save=None):
    """余り a の素数と余り b の素数の個数を、x まで数えて 2 本の線で描く"""
    s = np.ones(N + 1, dtype=bool); s[:2] = False
    for i in range(2, int(N ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    primes = np.nonzero(s)[0]
    ca = np.cumsum(np.isin(np.arange(N + 1), primes[primes % m == a]))
    cb = np.cumsum(np.isin(np.arange(N + 1), primes[primes % m == b]))
    fig, ax = plt.subplots(figsize=(9, 3))
    ax.plot(np.arange(N + 1), ca, color=_INK, lw=1.2, label=f"{m} で割って {a} 余る素数の個数")
    ax.plot(np.arange(N + 1), cb, color=_GRAY, lw=1.2, label=f"{m} で割って {b} 余る素数の個数")
    ax.set_xlabel("x"); ax.set_ylabel("個数"); ax.legend(fontsize=8, frameon=False)
    ax.set_title(f"x までの素数を余りで数える（{N} まで）：黒と灰色、どっちが上？", fontsize=9.5, loc="left", color="#222222")
    if save:
        _save(fig, save)
    plt.show()
    print(f"{N} まで：余り {a} が {int(ca[-1])} 個、余り {b} が {int(cb[-1])} 個")


# ---------- ノートの中の AI（サーバなし。JupyterLite でも手元でも動く） ----------
# jupyter-mynerva の「ノートの物語を読んで会話する」を、カーネルの中だけで小さく作ったもの。
# 見るもの：このセッションで実行したセル（コードと表示）と、保存されたノートの文章。
# できないこと：セルを勝手に入れる・動かす。コードは提案として出すだけ（貼るのはきみ）。それがこの実験室の約束にも合う。
_AI = {"key": None, "model": "claude-sonnet-5", "workspace": None, "log": [], "cells": [], "hooked": False, "buf": None}

_AI_RULES = """あなたは中学生の「手と機械の実験室」で、Jupyter ノートの中にいる相談相手です。日本語で、短く、やさしく答えます。
守ること：
- 答えや定理を先に言わない。まず「何が見えた？」「どこまで確かめた？」と聞き返す。生徒が自分で気づけるように、次の一手を一つだけ示す
- 問い・手でやったこと・手の結果・予想は生徒のもの。書き換えを頼まれても、生徒に書いてもらう
- コードを提案するときは、Python のコードブロック 1 つだけ。1 行目に「# [AI]」と書く。生徒が ai_accept() で新しいセルとして入れ、自分で動かす。ファイル・ネットワークは使わない。すでに実行済みのセルの結果は使ってよい
- 使える道具：math, random, numpy, sympy, matplotlib.pyplot(plt)、kg_tools（sieve_grid, factor_tree/leaves/show_trees, divisor_grid, divisor_lattice, number_grid, compare_grid, count_bars, prime_race, race_lines, euclid_numbers, factorization_str など）
- 機械が正しいとは限らないし、あなたも間違える。「確かめてみて」と添える
- 手の結果と機械の結果が食い違っていたら、どちらが間違えたかを一緒に考える（機械が正しいと決めつけない）"""

def _ai_hook():
    """実行した各セルのコードと表示（print の中身）を覚える。IPython のとき"""
    if _AI["hooked"]:
        return
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is None:
            return
        class _Tee:
            def __init__(self, base):
                self.base = base
            def write(self, t):
                self.base.write(t)
                if _AI["buf"] is not None:
                    _AI["buf"].append(t)
            def flush(self):
                self.base.flush()
            def __getattr__(self, k):
                return getattr(self.base, k)
        def pre(info):
            _AI["buf"] = []
            _AI["_src"] = getattr(info, "raw_cell", "")
            if not isinstance(sys.stdout, _Tee):
                sys.stdout = _Tee(sys.stdout)
        def post(result):
            out = "".join(_AI["buf"] or [])
            _AI["buf"] = None
            src = _AI.get("_src", "")
            if src.strip() and not src.strip().startswith(("ai(", "%%ai", "ai_setup(")):
                _AI["cells"].append({"source": src, "output": out[-1500:]})
                _AI["cells"] = _AI["cells"][-40:]
        ip.events.register("pre_run_cell", pre)
        ip.events.register("post_run_cell", post)
        _AI["hooked"] = True
    except Exception:
        pass

# --- ノート画面とのやりとり（JS の出力を通す。JupyterLite の設定 exposeAppInBrowser で window.jupyterapp が見える） ---
_JS_SYNC = r"""(function(){try{
var app=window.jupyterapp; var p=app&&app.shell&&app.shell.currentWidget; var nb=p&&p.content; if(!nb||!nb.model){return;}
var txt=function(t){return Array.isArray(t)?t.join(""):(t==null?"":String(t));};
var cells=nb.model.sharedModel.cells.map(function(c){var t=c.cell_type; var src=c.getSource?c.getSource():txt(c.source); var out="";
 if(t==="code"&&c.getOutputs){c.getOutputs().forEach(function(o){ if(o.output_type==="stream") out+=txt(o.text); else if(o.output_type==="error") out+="ERROR "+(o.ename||"")+": "+(o.evalue||"")+"\n"; else if(o.data&&o.data["text/plain"]) out+=txt(o.data["text/plain"])+"\n"; else if(o.data&&o.data["image/png"]) out+="[図]\n"; });}
 return {t:t, s:src, o:out.slice(-1500)};});
var b64=btoa(unescape(encodeURIComponent(JSON.stringify(cells))));
var k=p.sessionContext&&p.sessionContext.session&&p.sessionContext.session.kernel; if(!k){return;}
k.requestExecute({code:"import kg_tools as _k; _k._ai_live('"+b64+"')", silent:true, store_history:false});
}catch(e){console.warn("kg sync",e);}})();"""

_JS_INSERT = r"""(function(){try{
var app=window.jupyterapp; var p=app&&app.shell&&app.shell.currentWidget; var nb=p&&p.content; if(!nb||!nb.model){console.warn("kg insert: no notebook");return;}
var src=decodeURIComponent(escape(atob("__B64__")));
var cells=nb.model.sharedModel.cells; var i=nb.activeCellIndex;
for(var j=cells.length-1;j>=0;j--){var s=cells[j].getSource?cells[j].getSource():String(cells[j].source||""); if(s.indexOf("ai_accept(")>=0){i=j;break;}}
if(i+1<cells.length){var nxt=cells[i+1].getSource?cells[i+1].getSource():String(cells[i+1].source||""); if(nxt===src){return;}}
nb.model.sharedModel.insertCell(i+1,{cell_type:"code",source:src,metadata:{tags:["ai"]}});
nb.activeCellIndex=i+1;
}catch(e){console.warn("kg insert",e);}})();"""

def _ai_display_js(code):
    """JS をノート画面で実行させる（出力として渡す）。IPython でなければ何もしない"""
    try:
        from IPython.display import display, Javascript
        display(Javascript(code))
        return True
    except Exception:
        return False

def _ai_live(b64):
    """ノート画面から届いた、いまのノート全体（文章・コード・表示）。JS から呼ばれる"""
    try:
        import base64
        _AI["live"] = json.loads(base64.b64decode(b64).decode("utf-8"))
    except Exception:
        pass

def _ai_last_proposal():
    """いちばん新しい AI の返事から、# [AI] で始まるコードブロックを取り出す"""
    for m in reversed(_AI["log"]):
        if m["role"] != "assistant":
            continue
        import re
        blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", m["content"], re.S)
        blocks = [b.strip("\n") for b in blocks if "# [AI]" in b]
        if blocks:
            return blocks[-1]
    return None

def ai_accept():
    """いちばん新しい提案のコードを、このセルのすぐ下に新しいセルとして入れる（動かすのはきみ）。
    ノート画面と話せないとき（手元の Jupyter など）は、コードを表示するので自分で貼る。"""
    code = _ai_last_proposal()
    if not code:
        print("入れられる提案がまだありません。先に ai(\"…\") で聞いてください（提案は # [AI] で始まるコードブロック）")
        return
    import base64
    b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")
    if _ai_display_js(_JS_INSERT.replace("__B64__", b64)):
        print("提案のコードをこの下に新しいセルとして入れました（1 行目が # [AI]）。読んでから、自分で動かしてください。入っていなければ下のコードを貼る：")
    print(code)
    _ai_display_js(_JS_SYNC)

def ai_help():
    print("""ノートの中の AI の使い方
  ai_setup("sk-…")            キーをこのセッションだけ覚える（どこにも保存しない）
  ai("聞きたいこと")           実行したセルの表示とノートの文章を読んで答える。答えは言わず、次の一手を一つ。続けて聞ける
  %%ai                        セルの 2 行目以降に、長い質問を書く
  ai_accept()                 いちばん新しい提案のコードを、下に新しいセルとして入れる（入れるだけ。動かすのはきみ）
  ai_forget()                 会話をやり直す
できないこと：セルを勝手に入れる・書き換える・消す・動かす。手の結果・予想を書き換える。答えを先に言う""")

def ai_forget():
    """会話を最初から"""
    _AI["log"] = []; _AI["logname"] = None
    print("会話を忘れました（ノートの記録 .kgchat/ は残ります）")

def ai_setup(key=None, model=None, workspace=None):
    """API キーを覚える（このセッションだけ。どこにも保存しない）。model は API の ID（例：claude-sonnet-5, claude-opus-5-5）"""
    if key:
        _AI["key"] = key.strip()
    if model:
        _AI["model"] = model.strip()
    if workspace:
        _AI["workspace"] = workspace.strip()
    _ai_hook()
    print("AI の準備：", "キーあり" if _AI["key"] else "キーなし（ai_setup(\"sk-…\") で入れる）", "／モデル", _AI["model"], "／使い方は ai_help()")
    _ai_display_js(_JS_SYNC)

def _find_notebook(notebook=None):
    """このノートのファイルを探す：指定があればそれ、なければ実行したセルと同じコードを含む .ipynb"""
    import glob
    if notebook and os.path.exists(notebook):
        return notebook
    srcs = [c["source"].strip() for c in _AI["cells"] if len(c["source"].strip()) > 20]
    best, best_n = None, 0
    for f in glob.glob("*.ipynb"):
        try:
            with open(f, encoding="utf-8") as fh:
                text = fh.read()
        except Exception:
            continue
        n = sum(1 for src in srcs if src.splitlines()[0][:60] in text)
        if n > best_n:
            best, best_n = f, n
    return best

def _ai_context(notebook=None, max_chars=7000):
    """AI に渡す文脈：ノート画面から届いたいまのノート全体（あれば）。なければノートの文章と、実行したセル（コードと表示）"""
    parts = []
    live = _AI.get("live")
    if live:
        rows = []
        for c in live:
            if c.get("t") == "markdown":
                rows.append(c.get("s", "").strip())
            else:
                src = c.get("s", "").strip()
                if not src or src.startswith(("ai(", "%%ai", "ai_setup(", "ai_accept(", "ai_help(")):
                    continue
                rows.append("```python\n" + src + "\n```\n表示：\n" + (c.get("o", "").strip() or "（まだ実行していない、または表示なし）"))
        text = "## いまのノート（上から順に。文章と、コードとその表示）\n" + "\n\n".join(rows)
        return text[-max_chars:] if len(text) > max_chars else text
    nb = _find_notebook(notebook)
    if nb:
        try:
            with open(nb, encoding="utf-8") as f:
                cells = json.load(f).get("cells", [])
            md = []
            for c in cells:
                if c.get("cell_type") == "markdown":
                    src = c.get("source", "")
                    src = "".join(src) if isinstance(src, list) else src
                    md.append(src.strip())
            parts.append(f"## ノート {nb} の文章\n" + "\n\n".join(md))
        except Exception:
            pass
    if _AI["cells"]:
        runs = []
        for c in _AI["cells"][-12:]:
            runs.append("```python\n" + c["source"].strip() + "\n```\n表示：\n" + (c["output"].strip() or "（表示なし、または図）"))
        parts.append("## このセッションで実行したセル（古い順）\n" + "\n\n".join(runs))
    text = "\n\n".join(parts)
    return text[-max_chars:] if len(text) > max_chars else text

def _ai_request(messages, system):
    """Anthropic API を呼ぶ。JupyterLite（Pyodide のワーカー）では同期 XHR、手元では urllib"""
    body = json.dumps({"model": _AI["model"], "max_tokens": 1200, "system": system, "messages": messages})
    headers = {"content-type": "application/json", "x-api-key": _AI["key"], "anthropic-version": "2023-06-01",
               "anthropic-dangerous-direct-browser-access": "true"}
    if _AI["workspace"]:
        headers["anthropic-workspace-id"] = _AI["workspace"]
    url = "https://api.anthropic.com/v1/messages"
    if sys.platform == "emscripten":
        import js
        xhr = js.XMLHttpRequest.new()
        xhr.open("POST", url, False)
        for k, v in headers.items():
            xhr.setRequestHeader(k, v)
        xhr.send(body)
        status, text = int(xhr.status), str(xhr.responseText)
    else:
        import urllib.request, urllib.error
        req = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                status, text = r.status, r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            status, text = e.code, e.read().decode("utf-8", "replace")
    if status != 200:
        try:
            detail = json.loads(text).get("error", {}).get("message", text[:200])
        except Exception:
            detail = text[:200]
        raise RuntimeError(f"API {status}：{detail}")
    data = json.loads(text)
    return "\n".join(c.get("text", "") for c in data.get("content", []) if c.get("type") == "text").strip()

def _ai_save_log(notebook):
    """会話を .kgchat/ に残す（report() が ai_session として来歴に入れる）"""
    try:
        os.makedirs(".kgchat", exist_ok=True)
        name = f"{(notebook or 'notebook').replace('.ipynb', '')}-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
        path = os.path.join(".kgchat", _AI.get("logname") or name)
        _AI["logname"] = os.path.basename(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"notebook": notebook, "model": _AI["model"], "log": _AI["log"]}, f, ensure_ascii=False, indent=1)
        return _AI["logname"]
    except Exception:
        return None

def ai(question, notebook=None):
    """ノートの中で AI に聞く。例：ai("手の結果と機械の結果がずれた。どこを見ればいい？")
    AI はこのセッションで実行したセルと、ノートの文章を読んで答える。答えは言わず、次の一手を示す。
    コードを提案するときは 1 行目が # [AI] のブロック。自分で新しいセルに貼って動かす（勝手には入れない）。"""
    _ai_hook()
    if not _AI["key"]:
        print("API キーがまだです。ai_setup(\"sk-…\") を先に実行してください（地図アプリの設定に入れたキーと同じでよい。このセッションだけ覚えます）")
        return
    ctx = _ai_context(notebook)
    system = _AI_RULES + "\n\n以下は生徒のノートの文脈です。\n\n" + ctx
    _AI["log"].append({"role": "user", "content": question, "t": now()})
    messages = [{"role": m["role"], "content": m["content"]} for m in _AI["log"][-12:]]
    try:
        reply = _ai_request(messages, system)
    except Exception as e:
        _AI["log"].pop()
        print("AI に聞けませんでした：", e)
        return
    _AI["log"].append({"role": "assistant", "content": reply, "t": now()})
    name = _ai_save_log(_find_notebook(notebook))
    print("AI：", reply)
    if "# [AI]" in reply:
        print("\n（この提案を入れるなら、次のセルで ai_accept()。新しいセルとして入るだけで、動かすのはきみ。動かす前に何を数えるか読む）")
    if name:
        print(f"（会話は .kgchat/{name} に残る）")
    _ai_display_js(_JS_SYNC)      # 次に聞くときのために、いまのノート全体を受け取っておく

try:
    from IPython.core.magic import register_cell_magic
    @register_cell_magic
    def ai_magic(line, cell):
        """%%ai のセルで、複数行の質問を書く"""
        ai(cell.strip(), notebook=line.strip() or None)
    try:
        from IPython import get_ipython
        get_ipython().register_magic_function(ai_magic, "cell", "ai")
    except Exception:
        pass
except Exception:
    pass


# ---------- 結果を地図アプリへ送る（来歴つき） ----------
def _nb_sha(notebook):
    """ノートの本文（コードと文章）だけから作る指紋。出力・実行順・手の結果を書くセルは含めない。同じ版なら同じ値になる"""
    try:
        import hashlib
        with open(notebook, encoding="utf-8") as f:
            nb = json.load(f)
        parts = []
        for c in nb.get("cells", []):
            src = c.get("source", "")
            src = "".join(src) if isinstance(src, list) else src
            if "自分の結果に書き換える" in src:      # 手の結果を書き込むセルは指紋に含めない（書き換えるのが前提）
                continue
            parts.append(src)
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]
    except Exception:
        return None

def _ai_cells(notebook):
    """AI（Mynerva など）が入れたセルの数：コードは 1 行目に # [AI]、文章は先頭に（AI）と書く約束"""
    try:
        with open(notebook, encoding="utf-8") as f:
            nb = json.load(f)
        n = 0
        for c in nb.get("cells", []):
            src = c.get("source", "")
            src = ("".join(src) if isinstance(src, list) else src).lstrip()
            if src.startswith("# [AI]") or src.startswith("（AI）") or src.startswith("(AI)"):
                n += 1
        return n
    except Exception:
        return None

def _ai_session():
    """ノートの中の AI（ai() か jupyter-mynerva）の会話の記録があれば、いちばん新しいものの名前"""
    try:
        import glob
        files = []
        for d in [".mynerva/sessions", "../.mynerva/sessions", os.path.expanduser("~/.mynerva/sessions")]:
            files += glob.glob(os.path.join(d, "*.mnchat"))
        files += glob.glob(os.path.join(".kgchat", "*.json"))      # ノートの中の ai() の会話
        if not files:
            return None
        return os.path.basename(max(files, key=os.path.getmtime))
    except Exception:
        return None

def report(exp, summary, data=None, hand=None, params=None, notebook=None):
    """実験の結果を「自分の地図」アプリに届ける。
    JupyterLite：同じブラウザで開いている地図アプリのタブに BroadcastChannel で送る。
    それ以外：evidence_<exp>.json に書く。どちらの場合も画面にも表示する。
    data：機械の結果（同じ条件なら同じ値になるもの）。hand：手でやった結果。params：条件。
    notebook：このノートのファイル名（渡すと本文の指紋 nb_sha を来歴に入れる → 再現性の接地リンク）"""
    msg = {"type": "evidence", "exp": exp, "summary": summary, "data": data or {}, "t": now()}
    if hand is not None:
        msg["hand"] = hand
    if params is not None:
        msg["params"] = params
    msg["provenance"] = {"notebook": notebook, "nb_sha": _nb_sha(notebook) if notebook else None,
                         "platform": sys.platform, "python": sys.version.split()[0], "t": msg["t"]}
    if notebook:
        ai_n = _ai_cells(notebook)
        if ai_n:
            msg["provenance"]["ai_cells"] = ai_n          # AI が入れたセルの数（約束どおり印がついたもの）
        sess = _ai_session()
        if sess:
            msg["provenance"]["ai_session"] = sess        # AI との会話の記録（jupyter-mynerva のセッション名）
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
    if msg["provenance"]["nb_sha"]:
        print(f"　来歴：{notebook}（本文の指紋 {msg['provenance']['nb_sha']}）／{sys.platform}／{msg['t']}")
    if msg["provenance"].get("ai_cells"):
        print(f"　AI が入れたセル：{msg['provenance']['ai_cells']} 個" + (f"／会話の記録：{msg['provenance']['ai_session']}" if msg["provenance"].get("ai_session") else ""))
    if sent:
        print("→ 地図アプリに送りました（地図のタブを開いていれば「記録」に出ます）")
    else:
        print(f"→ evidence_{exp}.json に書きました（地図アプリの「記録」から読み込めます）")
    return msg
