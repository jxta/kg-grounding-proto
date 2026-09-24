"""日本語フォントのサブセットを fonts/ に作る（JupyterLite・CI・CJK フォントのない環境用）。

Noto Sans CJK JP (Regular) を GitHub から取得し、JIS X 0208 の漢字・かな・記号だけを
抜き出して fonts/NotoSansCJKjp-Regular-subset.otf に保存する（約 1.8 MB）。
ノート側の setup_font() は fonts/*.otf を自動で拾う。

    python tools/make_font_subset.py

依存：fonttools（matplotlib と一緒に入る）
"""
import os
import sys
import urllib.request

from fontTools import subset

SRC_URL = "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf"
OUT = os.path.join("fonts", "NotoSansCJKjp-Regular-subset.otf")
CACHE = os.path.join(".cache", "NotoSansCJKjp-Regular.otf")

RANGES = [
    (0x0020, 0x007E), (0x00A0, 0x00FF),   # ASCII, Latin-1
    (0x2000, 0x206F), (0x2070, 0x209F),   # 一般句読点、上付き・下付き（²³）
    (0x2100, 0x214F), (0x2150, 0x218F),   # 文字様記号、数字に準じるもの
    (0x2190, 0x21FF), (0x2200, 0x22FF),   # 矢印（↑↓→）、数学記号（×）
    (0x2460, 0x24FF), (0x25A0, 0x25FF),   # 囲み英数字（①）、幾何学模様
    (0x2600, 0x26FF),                     # その他の記号（⚠）
    (0x3000, 0x30FF),                     # CJK 記号・句読点、ひらがな、カタカナ
    (0xFF00, 0xFFEF),                     # 全角英数・記号
]


def codepoints():
    cps = set()
    for a, b in RANGES:
        cps.update(range(a, b + 1))
    for cp in range(0x4E00, 0xA000):      # JIS X 0208 の漢字（第1・第2水準）
        try:
            chr(cp).encode("shift_jis")
            cps.add(cp)
        except UnicodeEncodeError:
            pass
    return cps


def main():
    if os.path.exists(OUT):
        print("already exists:", OUT)
        return 0
    os.makedirs("fonts", exist_ok=True)
    os.makedirs(".cache", exist_ok=True)
    if not os.path.exists(CACHE):
        print("downloading", SRC_URL)
        urllib.request.urlretrieve(SRC_URL, CACHE)
    opts = subset.Options()
    opts.layout_features = []
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.drop_tables += ["vhea", "vmtx", "VORG", "GSUB", "GPOS", "GDEF"]
    font = subset.load_font(CACHE, opts)
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=codepoints())
    sub.subset(font)
    subset.save_font(font, OUT, opts)
    print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
