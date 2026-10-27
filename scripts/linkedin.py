#!/usr/bin/env python3
"""LinkedIn banner (1584 x 396) in the profile style: tagline + the five pipeline stages, finished state.
The profile photo covers the lower left on LinkedIn, so everything sits right of x = 470.
Writes assets/linkedin-banner-<mode>.svg (render to PNG with a browser; not used in the README)."""
import hero3d as h
from svglib import Svg, THEMES, write


def build(t):
    W, H = 1584, 396
    svg = Svg(W, H, "Moutaz Mohammad: from CAN bits to RAG pipelines", t)
    svg.add(f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>')   # square corners: LinkedIn crops itself
    h.frame(svg, t, W, H)
    svg.add(svg.text(W - 60, 70, "Embedded engineer building intelligent systems", "body", 30, t["fg"], "end"))
    svg.add(svg.text(W - 60, 112, "from CAN bits to RAG pipelines.", "body", 30, t["accentText"], "end"))
    xs, cy = [600, 810, 980, 1170, 1440], 262
    for i, (num, lab, fn, col) in enumerate(h.STAGES):
        svg.add(fn(svg, t, xs[i], cy, .86 if i != 4 else .72))
        svg.add(svg.text(xs[i], 372, f"{num}  {lab}", "mono", 14, t[col], "middle", 1.5))
    for a, b in ((690, 742), (868, 925), (1035, 1072), (1268, 1375)):
        svg.add(f'<line x1="{a}" y1="{cy}" x2="{b}" y2="{cy}" stroke="{t["line2"]}" stroke-width="1.6" stroke-dasharray="4 5"/>'
                f'<path d="M{b - 8},{cy - 6} L{b},{cy} L{b - 8},{cy + 6}" fill="none" stroke="{t["line2"]}" stroke-width="1.8"/>')
    svg.add(svg.text(W - 60, 160, "moutazm.com  ·  github.com/moutaz121493", "mono", 15, t["muted"], "end", 1.5))
    svg.add("</g>")
    return svg.render()


if __name__ == "__main__":
    for mode, t in THEMES.items():
        write("linkedin-banner", mode, build(t))
    print("ok")
