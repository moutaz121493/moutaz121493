"""Shared helpers for the profile generators: theme tokens, an SVG builder that embeds only the glyphs it uses,
and a reduced-motion switch.

Every generator writes <name>-dark.svg and <name>-light.svg into assets/. SVGs are loaded by GitHub as <img>,
so: no scripts, no external fonts/images, no links. Fonts are subset per file and embedded as base64 WOFF2.
Motion: animated layers carry class "m"; a static fallback layer carries class "s". With
prefers-reduced-motion the animated layer is hidden and the static one shown (CSS cannot pause SMIL).
"""
import base64
import html
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
FONTS = os.path.join(ROOT, "scripts", "fonts")
THEMES = json.load(open(os.path.join(ASSETS, "theme.json")))
E = html.escape

FAMILIES = {   # key -> (css family name, file, weight)
    "display": ("CP", "ChakraPetch-700.woff2", 700),
    "body": ("PS", "IBMPlexSans-400.woff2", 400),
    "bodyb": ("PSB", "IBMPlexSans-600.woff2", 600),
    "mono": ("JM", "JetBrainsMono-400.woff2", 400),
}
FALLBACK = {"display": "'Segoe UI',Helvetica,Arial,sans-serif", "body": "'Segoe UI',Helvetica,Arial,sans-serif",
            "bodyb": "'Segoe UI',Helvetica,Arial,sans-serif", "mono": "ui-monospace,Menlo,Consolas,monospace"}
_cache = {}


def subset_font(key, chars):
    """-> base64 WOFF2 holding only `chars` (fontTools, deterministic)."""
    from fontTools import subset
    from fontTools.ttLib import TTFont
    name, fn, _ = FAMILIES[key]
    ck = (key, "".join(sorted(chars)))
    if ck in _cache:
        return _cache[ck]
    font = TTFont(os.path.join(FONTS, fn), recalcTimestamp=False)   # no build time inside: rebuilds are byte-identical
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    opts.name_IDs = []
    opts.notdef_outline = True
    s = subset.Subsetter(opts)
    s.populate(text="".join(sorted(chars)) + " ")
    s.subset(font)
    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    _cache[ck] = base64.b64encode(buf.getvalue()).decode()
    return _cache[ck]


class Svg:
    def __init__(self, w, h, label, theme):
        self.w, self.h, self.label, self.t = w, h, label, theme
        self.parts, self.defs, self.css = [], [], []
        self.chars = {k: set() for k in FAMILIES}

    def add(self, s):
        self.parts.append(s)
        return self

    def text(self, x, y, s, font="body", size=16, fill=None, anchor=None, ls=None, extra=""):
        self.chars[font].update(s)
        name = FAMILIES[font][0]
        a = f' text-anchor="{anchor}"' if anchor else ""
        l_ = f' letter-spacing="{ls}"' if ls else ""
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{name},{FALLBACK[font]}" font-size="{size}"'
                f' fill="{fill or self.t["fg"]}"{a}{l_}{extra}>{E(s)}</text>')

    def render(self):
        faces = []
        for k, ch in self.chars.items():
            if ch:
                name, _, weight = FAMILIES[k]
                faces.append(f"@font-face{{font-family:{name};font-weight:{weight};"
                             f"src:url(data:font/woff2;base64,{subset_font(k, ch)}) format('woff2')}}")
        css = "".join(faces) + ".s{display:none}@media (prefers-reduced-motion:reduce){.m{display:none}.s{display:inline}}" + "".join(self.css)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" '
                f'role="img" aria-label="{E(self.label)}"><style>{css}</style><defs>{"".join(self.defs)}</defs>'
                + "".join(self.parts) + "</svg>")


def write(name, mode, svg):
    os.makedirs(ASSETS, exist_ok=True)
    p = os.path.join(ASSETS, f"{name}-{mode}.svg")
    with open(p, "w") as f:
        f.write(svg)
    return p, len(svg.encode())


def vals(seq, nd=1):
    """SMIL values list; repeats the first value at the end so the loop is seamless."""
    seq = list(seq) + [seq[0]]
    return ";".join(f"{v:.{nd}f}" if isinstance(v, float) else str(v) for v in seq)


def contrast(a, b):
    """WCAG contrast ratio of two #rrggbb colours."""
    def lum(c):
        c = c.lstrip("#")
        rgb = [int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        rgb = [v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
        return .2126 * rgb[0] + .7152 * rgb[1] + .0722 * rgb[2]
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)
