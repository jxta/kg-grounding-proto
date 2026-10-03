"""放課後「AI と数学でアート」のボードを Excalidraw 形式で作る（Miro の代わり）。

    python tools/make_excalidraw.py [出力先ディレクトリ]   # 既定: hybrid/excalidraw

出力：ai_math_art_board.excalidraw（メニュー →「開く」で読み込む）、
      ai_math_art_board_clipboard.json（中身をコピーしてキャンバスに Ctrl+V で追加する用）。
Excalidraw で直接開くリンク：https://excalidraw.com/#url=https://jxta.github.io/kg-grounding-proto/hybrid/excalidraw/ai_math_art_board.excalidraw
"""
import json, math, random, time, unicodedata
random.seed(7)
NOW = int(time.time() * 1000)
EL = []
BASE = "https://jxta.github.io/kg-grounding-proto/"
NB = BASE + "notebooks/index.html?path=puzzles/"
PR = BASE + "hybrid/print/"
RUNS = BASE + "runs/"
INK = "#1e1e1e"; GREY = "#868e96"
def nid():
    return "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(16))
def base(t, x, y, w, h, **kw):
    e = {"id": nid(), "type": t, "x": x, "y": y, "width": w, "height": h, "angle": 0,
         "strokeColor": INK, "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 1,
         "strokeStyle": "solid", "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
         "roundness": None, "seed": random.randint(1, 2**31), "version": 1, "versionNonce": random.randint(1, 2**31),
         "isDeleted": False, "boundElements": [], "updated": NOW, "link": None, "locked": False}
    e.update(kw); EL.append(e); return e
def cw(ch, fs):
    return fs * (1.0 if unicodedata.east_asian_width(ch) in "WF" else 0.56)
def wrap(s, fs, maxw):
    out = []
    for para in s.split("\n"):
        line, w = "", 0
        for ch in para:
            c = cw(ch, fs)
            if w + c > maxw and line:
                out.append(line); line, w = "", 0
            line += ch; w += c
        out.append(line)
    return out
def text(x, y, s, fs=14, maxw=None, color=INK, align="left", frame=None, link=None, bold=False):
    lines = wrap(s, fs, maxw) if maxw else s.split("\n")
    w = max(sum(cw(c, fs) for c in l) for l in lines) if lines else fs
    h = len(lines) * fs * 1.25
    t = "\n".join(lines)
    return base("text", x, y, w, h, text=t, originalText=s, fontSize=fs, fontFamily=2, textAlign=align,
                verticalAlign="top", containerId=None, lineHeight=1.25, autoResize=not bool(maxw), strokeColor=color,
                frameId=frame, link=link)
def box(x, y, w, h, s=None, fill="#f1f3f5", fs=14, frame=None, link=None, stroke="transparent", color=INK, align="center", rounded=True, dash=False):
    r = base("rectangle", x, y, w, h, backgroundColor=fill, strokeColor=stroke, frameId=frame, link=link,
             roundness={"type": 3} if rounded else None, strokeStyle="dashed" if dash else "solid")
    if s is not None:
        lines = wrap(s, fs, w - 16)
        t = base("text", x + 8, y + 8, w - 16, len(lines) * fs * 1.25, text="\n".join(lines), originalText=s, fontSize=fs, fontFamily=2,
                 textAlign=align, verticalAlign="middle", containerId=r["id"], lineHeight=1.25, autoResize=False, strokeColor=color, frameId=frame, link=link)
        r["boundElements"] = [{"id": t["id"], "type": "text"}]
    return r
def frame(x, y, w, h, name):
    return base("frame", x, y, w, h, name=name, strokeColor="#bbb", backgroundColor="transparent")
def line(pts, frame=None, color=INK, width=1):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = pts[0]
    return base("line", x0, y0, max(xs) - min(xs), max(ys) - min(ys), points=[[p[0] - x0, p[1] - y0] for p in pts],
                lastCommittedPoint=None, startBinding=None, endBinding=None, startArrowhead=None, endArrowhead=None, frameId=frame, strokeColor=color, strokeWidth=width)
def arrow(a, b, frame=None, color=GREY):
    e = line([a, b], frame, color)
    e["type"] = "arrow"; e["endArrowhead"] = "arrow"; e["roundness"] = {"type": 2}
    return e
def ellipse(x, y, d, fill=INK, frame=None, stroke=INK):
    return base("ellipse", x - d / 2, y - d / 2, d, d, backgroundColor=fill, strokeColor=stroke, frameId=frame)
def chips(x, y, items, frame):
    for i, (lab, url) in enumerate(items):
        box(x + i * 92, y, 86, 24, lab, fill="#e9ecef", fs=11, frame=frame, link=url, color="#1864ab")

# ================= Row 0: title =================
text(0, -70, "放課後「AI と数学でアートをしようよ」— 中 1・90 分・好きな題材を 1 つ選ぶ（Excalidraw 版）", 30, bold=True)

# ================= F1 流れ =================
F1 = frame(0, 0, 1800, 720, "① 放課後の 90 分：流れと用意するもの")
text(20, 20, "見る → 手で → 機械で → AI に 1 つ頼む → 貼る", 24, frame=F1["id"])
flow = [("0〜10 分　見る", "展示の糸かけと機械の絵 3 枚（曼荼羅・サイコロの三角形・万華鏡）。説明はしない。「どうやって描いたと思う？」だけ"),
        ("10〜35 分　手で", "題材メニューから 1 つ選び、印刷した紙で手を動かす。数えた数・気づきを紙の下に書く"),
        ("35〜60 分　機械で", "同じ題材のノートを JupyterLite で開き、上から実行。「自分の結果に書き換える」セルに手の数を入れ、N を大きくする"),
        ("60〜75 分　AI に 1 つ頼む", "付箋に「頼むこと」を書いて AI の席へ（先生の PC）。提案のコードを読んでから、自分の PC で動かす"),
        ("75〜90 分　貼る", "できた絵をギャラリーに貼り、一言（何が見えた？）。次にやりたい題材に印")]
for i, (t, d) in enumerate(flow):
    y = 70 + i * 120
    box(20, y, 230, 100, t, fill="#ffec99", fs=15, frame=F1["id"])
    box(260, y, 620, 100, d, fill="#f8f9fa", fs=13, frame=F1["id"], align="left")
text(910, 70, "用意するもの", 18, frame=F1["id"])
text(910, 105, "・印刷用の紙（13 種類）を各 5 枚ほど。色鉛筆・定規・分度器・サイコロ・トレーシングペーパー（万華鏡用）\n・PC かタブレット（1〜2 人に 1 台）。JupyterLite を最初に 1 冊開いて部品を読み込んでおく（初回 30 秒）\n・先生の PC = AI の席。API キーはこの 1 台だけに入れる（生徒の PC には入れない）\n・この Excalidraw（ギャラリー用）。絵は画像を貼る（ドラッグ＆ドロップ）\n・音の出る題材はイヤホンか、鳴らす係を 1 人決めて小さめの音量で", 13, maxw=860, frame=F1["id"], color="#495057")
chips(910, 330, [("印刷用の紙", PR), ("JupyterLite", NB + "a1_itokake.ipynb"), ("README", "https://github.com/jxta/kg-grounding-proto")], F1["id"])
text(910, 380, "先生の役", 18, frame=F1["id"])
text(910, 415, "答えを言わない。「何が見えた？」「数えると？」「N を変えると？」。AI への頼みごとは、生徒の言葉のまま打つ。音を出す前に「どんな音になると思う？」と予想を言ってもらう。", 13, maxw=860, frame=F1["id"], color="#495057")

# ================= F2 AI 約束 =================
F2 = frame(1900, 0, 1800, 720, "② AI との約束と、頼み方の例（中 1 向け）")
fx = 1920
text(fx, 20, "AI はコードを書く。何を描くかは自分が決める", 24, frame=F2["id"])
text(fx, 70, "5 つの約束", 18, frame=F2["id"])
text(fx, 105, "1. 答えを先に聞かない（手でやってから）\n2. 問い・手の結果・予想は自分の言葉で書く。AI に書かせない\n3. AI が出したコードは、読んでから動かす（何を描くか説明できる？）\n4. AI も間違える。絵が変なら「どこが変？」を自分で言う\n5. できた絵には「自分がやったこと」と「AI に頼んだこと」を両方書く", 14, maxw=800, frame=F2["id"])
text(fx, 300, "AI の席のやり方", 18, frame=F2["id"])
text(fx, 335, "先生の PC で ai_setup(\"sk-…\") → 生徒の付箋の言葉で ai(\"…\") → 提案（# [AI] のコード）→ ai_accept() で下にセルが入る → 生徒が読む → 自分の PC に同じコードを打って動かす", 13, maxw=800, frame=F2["id"], color="#495057")
prompts = ["この模様を 7 回対称にするコードを提案して", "線を細くして、色は黒のまま。釘を 100 本に", "N を 2 倍にしたらどう変わる？ 答えでなく、確かめるコードを",
           "斜めの線に乗っている数の共通点を、答えを言わずに調べる方法を 1 つ", "らせんを 1 でなく 41 から始めて", "枝を 2 本でなく 3 本に分ける木に",
           "サイコロの角を 5 つ（五角形）にして", "π でなく √2 の数字で歩かせて", "この絵を 2 色でなく 3 色でぬれる？ 確かめ方を"]
for i, p in enumerate(prompts):
    col, row = i % 3, i // 3
    box(fx + 840 + col * 275, 70 + row * 200, 260, 180, p, fill="#fff3bf", fs=13, frame=F2["id"])

# ================= F3 中1 map =================
F3 = frame(3800, 0, 1800, 720, "③ 中 1 の教科書とのつながり（線は「この題材で出会う」）")
mx = 3820
text(mx, 20, "題材 → 中 1 の単元（単元の名前は先に言わない）", 22, frame=F3["id"])
units = ["素数と素因数分解", "正の数・負の数（余り・周期）", "文字式（2ⁿ、n(n−1)/2）", "比例と反比例", "平面図形（移動・作図・角）", "資料の活用（度数）", "音楽（五度圈・リズム）"]
acts = ["糸かけ", "掛け算の糸かけ", "軸の糸かけ", "数のらせん", "パスカル", "サイコロの三角形", "万華鏡", "しきつめ", "枝分かれの木", "直線で 2 色", "π の散歩", "正方形のらせん", "色の糸かけ", "音の糸かけ", "ユークリッドのリズム", "π の音楽", "余りの模様", "数の色紙"]
edges = [(0, 0), (0, 4), (1, 1), (1, 3), (2, 3), (3, 0), (4, 1), (4, 2), (5, 5), (6, 4), (7, 4), (8, 2), (9, 2), (9, 4), (10, 5), (11, 3), (12, 4), (13, 0), (13, 6), (14, 0), (14, 6), (15, 5), (16, 1), (17, 0)]
upos = {}
for i, u in enumerate(units):
    x = mx + i * 250; upos[i] = (x, 80)
    box(x, 80, 235, 70, u, fill="#d0ebff", fs=13, frame=F3["id"])
apos = {}
for i, a in enumerate(acts):
    col, row = i % 9, i // 9
    x = mx + col * 195; y = 400 + row * 110; apos[i] = (x, y)
    box(x, y, 185, 60, a, fill="#ffec99", fs=13, frame=F3["id"])
for a, u in edges:
    ax, ay = apos[a]; ux, uy = upos[u]
    arrow((ax + 92, ay), (ux + 117, uy + 70), F3["id"])
text(mx, 630, "単元の名前は、終わってから「たぶん教科書のあれ」と本人が結びつける。先に言わない。", 13, frame=F3["id"], color="#495057")

# ================= F4 題材メニュー 18 =================
cards = [
 ("1 糸かけ：k ずつ進む", "24 釘の盤で k = 5, 6, 8, 9。糸は何本で回りきる？", "全部の k の表。曼荼羅（k を重ねる）", "k = 7 と 11 を重ねて、色を変えて", "a1_itokake", "itokake_24.svg"),
 ("2 掛け算の糸かけ", "20 釘で n → 2n（と 3n）", "釘 200 本で 2〜9 倍。ハート形", "n → n² にしたらどうなるか、コードを", "a2_kakezan", "kakezan_20.svg"),
 ("3 軸の糸かけ", "縦の k と横の 13 − k を結ぶ 12 本", "40 本・4 つの角で花", "軸を 3 本（120° ずつ）にして", "a10_axis", "axis_string.svg"),
 ("4 数のらせん", "1〜121 のらせんで素数を黒く", "1〜40401 のらせん。斜めの線", "らせんを 41 から始めて", "a6_spiral", "spiral_11.svg"),
 ("5 パスカルの色ぬり", "16 行で奇数を黒く。各行の黒の数", "64 行。3・5 で割った余り", "7 で割った余りの模様に", "a3_pascal", "pascal_16.svg"),
 ("6 サイコロの三角形", "サイコロで角との真ん中へ 30 回", "2 万回。正方形・同じ角を続けない", "角を 5 つ（五角形）にして", "a11_chaos", "chaos_triangle.svg"),
 ("7 万華鏡", "12 等分の台紙に描いて、裏返し・回して写す", "回転だけ／裏返しあり、k = 3〜24", "7 回対称にして", "a8_kaleido", "kaleido_12.svg"),
 ("8 しきつめ", "同じ四角形を 8 枚切って並べる", "180° 回して対角線の向きにずらす。無作為な 6 つ", "五角形で試して", "a4_shikitsume", None),
 ("9 枝分かれの木", "幹 8 cm、0.7 倍、30° を 4 段。各段の本数", "10 段・角度をゆらす。本数は 2ⁿ", "枝を 3 本に分けて", "a9_tree", None),
 ("10 直線で分けて 2 色", "5 本引いて部屋を数え、2 色でぬる", "20 本。部屋 = 1 + n + 交点", "円を混ぜても 2 色でぬれる？ 確かめ方を", "a7_lines", None),
 ("11 π の散歩", "30 個の数字で方眼を歩く。数字の回数", "1 万歩。0〜9 の回数の棒グラフ", "10 方向（36° ずつ）にして", "a12_pi", "pi_walk.svg"),
 ("12 正方形のらせん（発展）", "方眼紙に 1, 1, 2, 3, 5, 8 の正方形", "20 番目までの比の表。近づく数", "最初の 2 つを 2, 5 にして", "a5_golden", None),
 ("13 色の糸かけ（曼荼羅・虹）", "36 釘に k = 5, 7, 11 を違う色で重ねる", "k ごとの色・線の順で虹。穴の半径 cos(πk/n)", "色を糸の本数（gcd）で決めて", "b1_color_itokake", "itokake_36.svg"),
 ("14 音の糸かけ ♪", "12 音の円で k = 7 ずつ結び、通った音を書く", "k = 7 のメロディ（五度圈）。全部通る k は gcd = 1", "3 音ずつ同時に鳴らして和音に", "b2_sound_circle", "sound_circle_12.svg"),
 ("15 ユークリッドのリズム ♪", "8・12・16 拍の円に k 個の●を均等に。手をたたく", "3 in 8、5 in 8、5 in 12 を鳴らす。作り方は互除法", "2 つのリズムを同時に鳴らして", "b3_euclid_rhythm", "rhythm_circle.svg"),
 ("16 π の音楽と色紙 ♪", "π の 16 桁を ドレミ… で鳴らす。1 ÷ 7 も", "64 音のメロディ、1000 桁の色紙。1÷7 は 142857 のくり返し", "数字を音の長さにして", "b4_pi_music", None),
 ("17 余りの模様", "10 × 10 の掛け算表を 5 で割った余りで 5 色", "60 × 60 を m = 5〜13 で。パスカルも色で", "足し算表の余りで。色を hsv に", "b5_mod_table", "mod_table_10.svg"),
 ("18 数の色紙", "1〜100 を小さい素因数で色分け（素数は黒）", "1〜400 の色紙。約数の個数の色紙も", "1 行を 6 にして。らせんに並べて", "b6_color_numbers", "numbers_100.svg"),
]
F4 = frame(0, 820, 5600, 1150, "④ 題材メニュー：18 の入口（黄 = 手で、青 = 機械で、桃 = AI に 1 つ頼む。♪ は音が出る）")
text(20, 840, "どれも 3 段：手で（紙と色鉛筆）→ 機械で（JupyterLite のノート）→ AI に 1 つ頼む（先生の席で）。1〜12 は白黒、13〜18 は色と音", 18, frame=F4["id"])
for i, (t, h, m, a, nb, pr) in enumerate(cards):
    col, row = i % 6, i // 6
    x = 20 + col * 930; y = 890 + row * 355
    box(x, y, 910, 335, None, fill="#f1f3f5", frame=F4["id"])
    text(x + 14, y + 10, t, 17, frame=F4["id"])
    box(x + 14, y + 44, 882, 70, "手で　" + h, fill="#fff3bf", fs=13, frame=F4["id"], align="left")
    box(x + 14, y + 122, 882, 70, "機械で　" + m, fill="#d0ebff", fs=13, frame=F4["id"], align="left")
    box(x + 14, y + 200, 882, 70, "AI に頼む例　「" + a + "」", fill="#ffdeeb", fs=13, frame=F4["id"], align="left")
    items = [("ノート", NB + nb + ".ipynb"), ("公開の記録", RUNS + nb + ".html")] + ([("印刷", PR + pr)] if pr else [])
    chips(x + 14, y + 284, items, F4["id"])

# ================= F5 ギャラリー =================
F5 = frame(0, 2070, 5600, 900, "⑤ 作品ギャラリー：できた絵を貼る（画像をドラッグ＆ドロップ）＋ 一言")
text(20, 2090, "貼ったら一言：何が見えた？ 自分がやったこと／AI に頼んだこと（下の付箋に）", 18, frame=F5["id"])
for i in range(12):
    col, row = i % 6, i // 6
    x = 20 + col * 930; y = 2140 + row * 400
    box(x, y, 910, 270, "ここに貼る", fill="#ffffff", fs=14, frame=F5["id"], stroke="#adb5bd", color="#adb5bd", dash=True)
    box(x, y + 280, 445, 100, "見えたこと：", fill="#fff3bf", fs=13, frame=F5["id"], align="left")
    box(x + 465, y + 280, 445, 100, "AI に頼んだこと：", fill="#ffdeeb", fs=13, frame=F5["id"], align="left")

# ================= F6 音と絵の種 ＋ 広場 =================
F6 = frame(0, 3070, 2750, 800, "⑥ 音と絵をつなぐ：組み合わせの種")
text(20, 3090, "同じ数の列を、絵にも音にもする。見えるものと聞こえるものは同じ？", 20, frame=F6["id"])
seeds = ["糸かけの釘の番号（k ずつ）→ 音にすると五度圈。絵は星形。星の角の数と、メロディの音の数は同じ？",
         "ユークリッドのリズム → 円の絵（回転対称になる？）。3 in 8 と 5 in 8 の絵は裏返し？",
         "π の数字 → 色紙と散歩とメロディ。1 ÷ 7 だけ、3 つとも「くり返し」が見える・聞こえる",
         "パスカルの余り（m = 2）→ 黒を打点にして 1 行ずつ鳴らすと？ 行が進むとリズムはどう変わる？",
         "素数の並び → 素数の位置で音を鳴らす（1〜60）。間隔が広がるのは聞こえる？ 双子素数は？",
         "枝分かれの木 → 段ごとに音を高く・短く。10 段で何音？ 2ⁿ 本を全部鳴らしたら何秒？",
         "掛け算表の余り（m = 12）→ 1 行を 12 の音にして鳴らす。i = 5 の行と i = 7 の行は逆回り？"]
for i, s in enumerate(seeds):
    col, row = i % 4, i // 4
    box(20 + col * 680, 3140 + row * 230, 660, 210, s, fill="#fff3bf", fs=13, frame=F6["id"], align="left")
ai_seeds = ["AI に頼む（例）：「この数の列を、低いド〜高いミの 10 音で鳴らすコードを提案して。b2 の play() を使って」",
            "AI に頼む（例）：「絵の色の順と、音の高さの順を同じにして」", "AI に頼む（例）：「2 つのリズムを左右のスピーカーに分けて」"]
for i, s in enumerate(ai_seeds):
    box(20 + i * 680, 3590, 660, 130, s, fill="#ffdeeb", fs=13, frame=F6["id"], align="left")
text(20, 3735, "先生へ　音は部屋で混ざるので、PC ごとにイヤホンか、鳴らす係を 1 人決めて順番に。音を出す前に「どんな音になると思う？」と予想を言ってもらう。くり返しが聞こえたら、絵のどこに同じくり返しが見えるかを探す。", 13, maxw=2700, frame=F6["id"], color="#495057")

F7 = frame(2850, 3070, 2750, 800, "⑦ 広場：見えたこと → 気づき → 予想 → きまり（付箋を複製して書く。名前は書かなくてよい）")
cols = ["見えたこと", "気づき", "予想", "きまり（機械で試してから書く）"]
for i, c in enumerate(cols):
    x = 2870 + i * 680
    box(x, 3120, 660, 690, None, fill="#f8f9fa", frame=F7["id"])
    text(x + 14, 3130, c, 16, frame=F7["id"])
seedst = ["k = 6 のとき、四角が 6 つできた", "k と 24 に共通の約数があると、糸が分かれる？", "糸の本数は、k と釘の数の最大公約数", "（機械で 60 本まで試してから書く）"]
for i, s in enumerate(seedst):
    box(2890 + i * 680, 3170, 300, 150, s, fill="#fff3bf" if i < 3 else "#fff9db", fs=13, frame=F7["id"])

# ================= Row 4: hand boards =================
def nails_board(cx, cy, r, n, start_zero, title, fid, example=None, color="#e03131"):
    text(cx - r, cy - r - 60, title, 16, frame=fid)
    base("ellipse", cx - r, cy - r, 2 * r, 2 * r, strokeColor="#ced4da", frameId=fid)
    pts = []
    for i in range(n):
        a = math.pi / 2 - 2 * math.pi * i / n
        x, y = cx + r * math.cos(a), cy - r * math.sin(a); pts.append((x, y))
        ellipse(x, y, 8, frame=fid)
        lx, ly = cx + (r + 22) * math.cos(a), cy - (r + 22) * math.sin(a)
        text(lx - 8, ly - 8, str(i if start_zero else i + 1), 11, frame=fid, color="#495057")
    if example:
        kind, k = example
        if kind == "k":
            seen = set()
            for s in range(n):
                if s in seen: continue
                i = s
                while True:
                    j = (i + k) % n; line([pts[i], pts[j]], fid, color); seen.add(i); i = j
                    if i == s: break
        else:
            for i in range(n):
                j = (k * i) % n
                if i != j: line([pts[i], pts[j]], fid, color)
F8 = frame(0, 3970, 5600, 1100, "⑧ 手で：盤（線ツールで糸をかける。釘の中心から中心へ。複製して自分の盤に）")
nails_board(330, 4490, 240, 24, False, "糸かけ盤 24 釘（空）", F8["id"])
nails_board(1030, 4490, 240, 24, False, "例：24 釘、k = 5（糸 1 本）", F8["id"], ("k", 5), "#e03131")
nails_board(1730, 4490, 240, 24, False, "例：24 釘、k = 6（糸 6 本）", F8["id"], ("k", 6), "#1971c2")
nails_board(2430, 4490, 240, 20, True, "掛け算の糸かけ 0〜19（空）", F8["id"])
nails_board(3130, 4490, 240, 20, True, "例：n → 2n（ハート形）", F8["id"], ("m", 2), "#2f9e44")
# 12 音の円
cx, cy, r = 3830, 4490, 240
names = ["ド", "ド#", "レ", "レ#", "ミ", "ファ", "ファ#", "ソ", "ソ#", "ラ", "ラ#", "シ"]
text(cx - r, cy - r - 60, "音の糸かけ：12 の音の円（k = 7 で五度圈）", 16, frame=F8["id"])
base("ellipse", cx - r, cy - r, 2 * r, 2 * r, strokeColor="#ced4da", frameId=F8["id"])
for i in range(12):
    a = math.pi / 2 - 2 * math.pi * i / 12
    x, y = cx + r * math.cos(a), cy - r * math.sin(a)
    ellipse(x, y, 10, frame=F8["id"])
    lx, ly = cx + (r + 30) * math.cos(a), cy - (r + 30) * math.sin(a)
    text(lx - 12, ly - 8, names[i], 12, frame=F8["id"])
# リズムの円 8 と 12
for j, (n, cxx) in enumerate([(8, 4550), (12, 5150)]):
    rr = 180; cyy = 4490
    text(cxx - rr, cyy - rr - 60, f"リズムの円 {n} 拍（●をぬる）", 16, frame=F8["id"])
    base("ellipse", cxx - rr, cyy - rr, 2 * rr, 2 * rr, strokeColor="#ced4da", frameId=F8["id"])
    for i in range(n):
        a = math.pi / 2 - 2 * math.pi * i / n
        x, y = cxx + rr * math.cos(a), cyy - rr * math.sin(a)
        ellipse(x, y, 16, fill="#ffffff", frame=F8["id"])
        lx, ly = cxx + (rr + 26) * math.cos(a), cyy - (rr + 26) * math.sin(a)
        text(lx - 6, ly - 8, str(i + 1), 11, frame=F8["id"], color="#495057")

scene = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com", "elements": EL,
         "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": {}}
import os, sys
out_dir = sys.argv[1] if len(sys.argv) > 1 else "hybrid/excalidraw"
os.makedirs(out_dir, exist_ok=True)
json.dump(scene, open(os.path.join(out_dir, "ai_math_art_board.excalidraw"), "w", encoding="utf-8"), ensure_ascii=False)
clip = {"type": "excalidraw/clipboard", "elements": EL, "files": {}}
json.dump(clip, open(os.path.join(out_dir, "ai_math_art_board_clipboard.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(len(EL), "elements ->", out_dir)
