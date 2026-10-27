#!/usr/bin/env python3
"""Thesis results card from data/thesis.json. Writes nothing (and removes an old card) while 'results' is empty,
so the profile never shows placeholder numbers. Each result: metric, value, optional baseline and note."""
import json
import os

from svglib import Svg, THEMES, write, ROOT, ASSETS

D = json.load(open(os.path.join(ROOT, "data", "thesis.json")))


def build(t):
    res = D["results"][:6]
    W, H = 1280, 82 + 92 * ((len(res) + 2) // 3)
    svg = Svg(W, H, "Thesis results: " + "; ".join(f"{r['metric']} {r['value']}" for r in res), t)
    svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="{t["panel"]}" stroke="{t["line2"]}" stroke-width="1.5"/>')
    svg.add(svg.text(34, 44, D.get("title", "// THESIS RESULTS"), "mono", 13, t["accentText"], ls=3))
    if D.get("eval_set"):
        svg.add(svg.text(W - 34, 44, D["eval_set"], "mono", 11, t["muted"], "end"))
    for i, r in enumerate(res):
        x, y = 34 + (i % 3) * 408, 72 + (i // 3) * 92
        svg.add(f'<rect x="{x + 5}" y="{y + 5}" width="390" height="78" rx="12" fill="{t["line2"]}"/>'
                f'<rect x="{x}" y="{y}" width="390" height="78" rx="12" fill="{t["bg2"]}" stroke="{t["line2"]}"/>')
        svg.add(svg.text(x + 16, y + 26, r["metric"], "mono", 12, t["muted"], ls=1))
        svg.add(svg.text(x + 16, y + 62, str(r["value"]), "display", 30, t["liveText"]))
        sub = " · ".join(v for v in (r.get("baseline"), r.get("note")) if v)
        if sub:
            svg.add(svg.text(x + 374, y + 62, sub, "mono", 11, t["muted"], "end"))
    return svg.render()


def main():
    if not D.get("results"):
        for m in THEMES:
            p = os.path.join(ASSETS, f"thesis-{m}.svg")
            if os.path.exists(p):
                os.remove(p)
        print("thesis: no results yet, card hidden")
        return
    for mode, t in THEMES.items():
        p, n = write("thesis", mode, build(t))
        print(f"{p}: {n / 1024:.0f} KB")


if __name__ == "__main__":
    main()
