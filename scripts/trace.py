#!/usr/bin/env python3
"""'Agent thinking' terminal: types out the thesis pipeline from data/trace.json, line by line, with a cursor.
Each line is revealed by a clip rectangle that grows (a typing effect without fonts tricks); the whole trace loops."""
import json
import os

from svglib import Svg, THEMES, write, ROOT

DATA = json.load(open(os.path.join(ROOT, "data", "trace.json")))
CH = 0.045          # seconds per character
GAP = 0.55          # pause after each line
HOLD = 3.5          # pause at the end before the loop restarts


def build(t):
    steps = DATA["steps"]
    query = DATA.get("example_query") or "«question in Arabic»"
    W = 1280
    top, lh = 92, 50
    H = top + lh * len(steps) + 34
    lines, tcur = [], 0.4
    for s in steps:
        arg = f' "{query}"' if s.get("arg") == "QUERY" else (f" {s['arg']}" if s.get("arg") else "")
        cmd = f"$ {s['cmd']}{arg}"
        out = f"  → {s['out']}"
        d1 = len(cmd) * CH
        d2 = len(out) * CH * .45
        lines.append((cmd, out, tcur, d1, d2))
        tcur += d1 + d2 + GAP
    total = tcur + HOLD
    svg = Svg(W, H, "Thesis trace, cross-lingual RAG: " + "; ".join(f"{s['cmd']}: {s['out']}" for s in steps), t)
    svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="{t["bg"]}" stroke="{t["line2"]}" stroke-width="1.5"/>')
    svg.add(f'<rect x="1.5" y="1.5" width="{W - 3}" height="46" rx="17" fill="{t["panel"]}"/>'
            f'<rect x="1.5" y="30" width="{W - 3}" height="18" fill="{t["panel"]}"/>'
            f'<line x1="1" y1="48" x2="{W - 1}" y2="48" stroke="{t["line2"]}"/>')
    for i, c in enumerate((t["bad"], t["accent"], t["live"])):
        svg.add(f'<circle cx="{26 + i * 18}" cy="25" r="5.5" fill="{c}" opacity=".75"/>')
    svg.add(svg.text(92, 30, f"{DATA['prompt']} · trace", "mono", 12.5, t["muted"]))
    svg.add(svg.text(W - 26, 30, DATA["title"], "mono", 12.5, t["accentText"], "end", 2))
    anim, static = [], []
    for i, (cmd, out, t0, d1, d2) in enumerate(lines):
        y = top + i * lh
        w1, w2 = len(cmd) * 10.2 + 40, len(out) * 8.9 + 40
        k = lambda a: f"{max(0.0, min(1.0, a / total)):.4f}"   # noqa: E731
        svg.defs.append(
            f'<clipPath id="c{i}a"><rect x="40" y="{y - 22}" width="0" height="30"><animate attributeName="width" '
            f'values="0;0;{w1:.0f};{w1:.0f};0" keyTimes="0;{k(t0)};{k(t0 + d1)};{k(total - .3)};1" dur="{total:.1f}s" repeatCount="indefinite"/></rect></clipPath>'
            f'<clipPath id="c{i}b"><rect x="40" y="{y + 2}" width="0" height="26"><animate attributeName="width" '
            f'values="0;0;{w2:.0f};{w2:.0f};0" keyTimes="0;{k(t0 + d1)};{k(t0 + d1 + d2)};{k(total - .3)};1" dur="{total:.1f}s" repeatCount="indefinite"/></rect></clipPath>')
        tc = svg.text(46, y, cmd, "mono", 16, t["fg"])
        to = svg.text(46, y + 22, out, "mono", 14, t["liveText"] if i == len(lines) - 1 else t["muted"])
        anim.append(f'<g clip-path="url(#c{i}a)">{tc}</g><g clip-path="url(#c{i}b)">{to}</g>')
        static.append(tc + to)
        # cursor follows the typing head of this line
        anim.append(f'<rect x="46" y="{y - 15}" width="9" height="18" fill="{t["accent"]}" opacity="0">'
                    f'<animate attributeName="x" values="46;46;{46 + w1 - 18:.0f};{46 + w1 - 18:.0f}" keyTimes="0;{k(t0)};{k(t0 + d1)};1" dur="{total:.1f}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{k(t0)};{k(t0 + .01)};{k(t0 + d1 + d2)};{k(t0 + d1 + d2 + .01)};1" '
                    f'dur="{total:.1f}s" repeatCount="indefinite"/></rect>')
    yl = top + lh * len(lines) - 16
    anim.append(f'<rect x="46" y="{yl - 15}" width="9" height="18" fill="{t["accent"]}" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;1;0;1;0;1;0" keyTimes="0;{(tcur - .1) / total:.4f};{(tcur + .5) / total:.4f};{(tcur + 1) / total:.4f};{(tcur + 1.5) / total:.4f};{(tcur + 2) / total:.4f};{(tcur + 2.5) / total:.4f};1" '
                f'dur="{total:.1f}s" repeatCount="indefinite"/></rect>')
    for i in range(len(lines)):
        svg.add(f'<circle cx="28" cy="{top + i * lh - 5}" r="3" fill="{t["line2"]}"/>')
    svg.add(f'<g class="m">{"".join(anim)}</g><g class="s">{"".join(static)}</g>')
    return svg.render()


def build_m(t):
    """Phone variant: static (no typing), larger type, outputs wrapped."""
    steps = DATA["steps"]
    query = DATA.get("example_query") or "«question in Arabic»"
    W, lines, y = 640, [], 92
    for s_ in steps:
        arg = f' "{query}"' if s_.get("arg") == "QUERY" else ""
        lines.append(("$ " + s_["cmd"] + arg, y, "cmd"))
        y += 30
        words, cur = s_["out"].split(), "→"
        for w_ in words:
            if len(cur) + len(w_) + 1 > 44:
                lines.append((cur, y, "out"))
                y += 26
                cur = "  " + w_
            else:
                cur += " " + w_
        lines.append((cur, y, "out"))
        y += 40
    H = y + 6
    svg = Svg(W, H, "Thesis trace, cross-lingual RAG: " + "; ".join(f"{s_['cmd']}: {s_['out']}" for s_ in steps), t)
    svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="{t["bg"]}" stroke="{t["line2"]}" stroke-width="1.5"/>'
            f'<line x1="1" y1="56" x2="{W - 1}" y2="56" stroke="{t["line2"]}"/>')
    for i, c in enumerate((t["bad"], t["accent"], t["live"])):
        svg.add(f'<circle cx="{28 + i * 22}" cy="29" r="7" fill="{c}" opacity=".75"/>')
    svg.add(svg.text(W - 26, 36, "// THESIS TRACE", "mono", 17, t["accentText"], "end", 2))
    for txt, yy, kind in lines:
        last = txt.startswith("→ Recall") or txt.startswith("  cost")
        svg.add(svg.text(30, yy, txt, "mono", 20 if kind == "cmd" else 17, t["fg"] if kind == "cmd" else (t["liveText"] if "Recall" in txt else t["muted"])))
    return svg.render()


def main():
    for mode, t in THEMES.items():
        p, n = write("trace", mode, build(t))
        write("trace-m", mode, build_m(t))
        print(f"{p}: {n / 1024:.0f} KB")


if __name__ == "__main__":
    main()
