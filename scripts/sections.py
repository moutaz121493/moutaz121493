#!/usr/bin/env python3
"""Quiet sections of the profile README (dividers, toolbox, journey, CAN footer) in assets/ (dark = HUD, light = Retro-Tech paper, same palette as moutazm.com).
Run: python3 make_assets.py   (stdlib only; the README picks dark/light with <picture> + prefers-color-scheme)."""
import html
import os
import random

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

THEMES = {
    "dark": dict(bg="#060a0f", bg2="#0b1118", panel="#0f161d", line="#1f2c37", line2="#2b3c4a", fg="#e8eff3",
                 muted="#8d9ca8", accent="#f5b83f", ai="#4fd1ff", live="#45e08f", progress="#f5b83f",
                 trace="#1d6f8f", glow="0.22"),
    "light": dict(bg="#ebe2cc", bg2="#e2d6ba", panel="#f8f1e1", line="#cdbd98", line2="#b4a07a", fg="#231a11",
                  muted="#6a5842", accent="#d24f1b", ai="#16766f", live="#3d7a1f", progress="#b55a10",
                  trace="#b4a07a", glow="0.14"),
}
DISPLAY = "'Chakra Petch','Segoe UI',Helvetica,Arial,sans-serif"
BODY = "'IBM Plex Sans','Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
E = html.escape


def save(name, svg):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w") as f:
        f.write(svg)


STACK = [
    ("EMBEDDED & NETWORKS", ["CAN / CAN FD", "ISO 16845-1", "MCU drivers", "Bit timing & TDC", "LIN", "Auto Ethernet"]),
    ("PYTHON & TOOLING", ["Python", "Test automation", "Log analysis", "Reports", "CLI tools"]),
    ("LINUX & INFRA", ["Debian", "Docker Compose", "systemd", "Cloudflare", "Tailscale", "restic", "Uptime Kuma"]),
    ("APPLIED AI", ["RAG", "Claude", "Gemini", "Structured output", "Prompt-injection aware", "Evaluation"]),
]


def stack(t):
    w, rowh = 1280, 64
    h = 40 + rowh * len(STACK)
    rows = []
    for i, (head, items) in enumerate(STACK):
        y = 34 + i * rowh
        rows.append(f'<text x="34" y="{y + 22}" font-family="{MONO}" font-size="12.5" letter-spacing="2" fill="{t["accent"]}">{E(head)}</text>')
        x = 280
        for it in items:
            cw = int(len(it) * 8.6 + 32)
            rows.append(f'<rect x="{x}" y="{y}" width="{cw}" height="34" rx="9" fill="{t["bg2"]}" stroke="{t["line2"]}"/>'
                        f'<text x="{x + 15}" y="{y + 22}" font-family="{BODY}" font-size="15" fill="{t["fg"]}">{E(it)}</text>')
            x += cw + 10
        if i < len(STACK) - 1:
            rows.append(f'<line x1="34" y1="{y + rowh - 13}" x2="{w - 34}" y2="{y + rowh - 13}" stroke="{t["line"]}" stroke-dasharray="3 5"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Toolbox">
<rect x="8" y="8" width="{w - 9}" height="{h - 9}" rx="18" fill="{t["line2"]}"/>
<rect x=".75" y=".75" width="{w - 9}" height="{h - 9}" rx="18" fill="{t["panel"]}" stroke="{t["line2"]}" stroke-width="1.5"/>
{"".join(rows)}</svg>'''


def divider(t, label, w=1280, fs=15):
    h = int(fs * 3.1)
    x1 = len(label) * fs * .9 + fs * 4
    y = h * .55
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}">
<text x="0" y="{y + fs * .35:.1f}" font-family="{MONO}" font-size="{fs}" letter-spacing="{fs * .27:.1f}" fill="{t["accent"]}">// {E(label)}</text>
<line x1="{x1:.0f}" y1="{y:.1f}" x2="{w}" y2="{y:.1f}" stroke="{t["line2"]}" stroke-width="1.2"/>
<circle r="{fs / 5:.1f}" cy="{y:.1f}" fill="{t["accent"]}"><animate attributeName="cx" values="{x1:.0f};{w};{w}" keyTimes="0;.7;1" dur="4.5s" repeatCount="indefinite"/></circle>
</svg>'''


def footer(t):
    """A CAN data frame whose payload spells HELLO, with the bit stream scrolling underneath."""
    w, h = 1280, 150
    fields = [("SOF", 1, t["muted"]), ("ID 0x4D4", 11, t["accent"]), ("RTR", 1, t["muted"]), ("IDE r0", 2, t["muted"]),
              ("DLC 5", 4, t["ai"]), ('DATA 48 45 4C 4C 4F  "HELLO"', 40, t["live"]), ("CRC", 15, t["muted"]),
              ("ACK", 2, t["muted"]), ("EOF", 7, t["muted"])]
    total = sum(f[1] for f in fields)
    x, unit, boxes = 40, (w - 80) / total, []
    for lab, n, col in fields:
        bw = n * unit
        boxes.append(f'<rect x="{x:.1f}" y="30" width="{bw - 4:.1f}" height="40" rx="7" fill="{t["bg2"]}" stroke="{col}" stroke-width="1.3"/>'
                     + (f'<text x="{x + bw / 2 - 2:.1f}" y="55" text-anchor="middle" font-family="{MONO}" font-size="{12 if n > 3 else 9.5}" fill="{col}">{E(lab)}</text>' if bw > 9.5 * len(lab) * .62 + 6 else ""))
        x += bw
    bits = "0" + format(0x4D4, "011b") + "000" + "0101" + "".join(format(ord(c), "08b") for c in "HELLO") + "101100111010011" + "11" + "1111111"
    step, y1, y0 = 9, 96, 116
    d, px = [f"M0,{y1 if bits[0] == '1' else y0}"], 0
    for b in bits * 3:
        y = y1 if b == "1" else y0
        d += [f"L{px},{y}", f"L{px + step},{y}"]
        px += step
    period = len(bits) * step
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="A CAN frame whose data bytes spell HELLO. Thanks for visiting.">
<defs><clipPath id="c"><rect x="40" y="80" width="{w - 80}" height="50"/></clipPath>
<linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="{t["bg"]}" stop-opacity="1"/><stop offset=".08" stop-color="{t["bg"]}" stop-opacity="0"/><stop offset=".92" stop-color="{t["bg"]}" stop-opacity="0"/><stop offset="1" stop-color="{t["bg"]}" stop-opacity="1"/></linearGradient></defs>
<rect width="{w}" height="{h}" rx="18" fill="{t["bg"]}"/>
{"".join(boxes)}
<g clip-path="url(#c)"><path d="{" ".join(d)}" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-linejoin="round">
<animateTransform attributeName="transform" type="translate" from="0 0" to="-{period} 0" dur="9s" repeatCount="indefinite"/></path></g>
<rect x="40" y="80" width="{w - 80}" height="50" fill="url(#f)"/>
<text x="{w - 40}" y="{h - 4}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{t["muted"]}">0x48 0x45 0x4C 0x4C 0x4F = HELLO · thanks for visiting</text>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="17.5" fill="none" stroke="{t["line2"]}" stroke-width="1.5"/>
</svg>'''


JOURNEY = [("2014 – 2019", "B.Sc. Communications &", "Electronics Engineering", "muted", False),
           ("since 2022", "Test Engineer, automotive", "networks · CAN / CAN FD", "accent", False),
           ("today", "Self-hosted homelab +", "LLM automation on a Pi 5", "live", False),
           ("2027 · expected", "M.Sc. Web Technologies", "thesis: cross-lingual RAG", "ai", True)]


def journey(t):
    w, h = 1280, 190
    x0, x1, y = 175, w - 175, 70
    n = len(JOURNEY)
    xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]
    out = [f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="18" fill="{t["panel"]}" stroke="{t["line2"]}" stroke-width="1.5"/>',
           f'<line x1="{x0}" y1="{y}" x2="{xs[-2]:.0f}" y2="{y}" stroke="{t["line2"]}" stroke-width="3"/>',
           f'<line x1="{xs[-2]:.0f}" y1="{y}" x2="{x1}" y2="{y}" stroke="{t["line2"]}" stroke-width="3" stroke-dasharray="6 7"/>',
           f'<line x1="{x0}" y1="{y}" x2="{xs[-2]:.0f}" y2="{y}" stroke="{t["accent"]}" stroke-width="3" stroke-dasharray="{xs[-2] - x0:.0f}" stroke-dashoffset="{xs[-2] - x0:.0f}"><animate attributeName="stroke-dashoffset" from="{xs[-2] - x0:.0f}" to="0" dur="2.4s" fill="freeze"/></line>']
    for i, (when, a, b, col, future) in enumerate(JOURNEY):
        x = xs[i]
        out.append(f'<circle cx="{x:.0f}" cy="{y}" r="11" fill="{t["panel"]}" stroke="{t[col]}" stroke-width="4"'
                   + (' stroke-dasharray="4 4"' if future else "") + "/>"
                   + (f'<circle cx="{x:.0f}" cy="{y}" r="11" fill="none" stroke="{t[col]}" stroke-width="2"><animate attributeName="r" values="11;22" dur="1.8s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="1.8s" repeatCount="indefinite"/></circle>' if i == n - 2 else "")
                   + f'<text x="{x:.0f}" y="{y - 26}" text-anchor="middle" font-family="{MONO}" font-size="13" letter-spacing="1.5" fill="{t[col]}">{E(when)}</text>'
                   + f'<text x="{x:.0f}" y="{y + 46}" text-anchor="middle" font-family="{BODY}" font-size="17" font-weight="600" fill="{t["fg"]}">{E(a)}</text>'
                   + f'<text x="{x:.0f}" y="{y + 70}" text-anchor="middle" font-family="{BODY}" font-size="15" fill="{t["muted"]}">{E(b)}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Journey: B.Sc. 2014-2019, test engineer since 2022, homelab and LLM automation, M.Sc. 2027">{"".join(out)}</svg>'


def stack_m(t):
    """Phone toolbox: one group per block, chips wrap, larger type."""
    w, rows, y = 640, [], 30
    for gi, (head, items) in enumerate(STACK):
        rows.append(f'<text x="28" y="{y + 18}" font-family="{MONO}" font-size="17" letter-spacing="2" fill="{t["accent"]}">{E(head)}</text>')
        y += 34
        x = 28
        for it in items:
            cw = int(len(it) * 11.2 + 34)
            if x + cw > w - 30:
                x, y = 28, y + 52
            rows.append(f'<rect x="{x}" y="{y}" width="{cw}" height="42" rx="10" fill="{t["bg2"]}" stroke="{t["line2"]}"/>'
                        f'<text x="{x + 17}" y="{y + 28}" font-family="{BODY}" font-size="19" fill="{t["fg"]}">{E(it)}</text>')
            x += cw + 10
        y += 74
    h = y + 4
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Toolbox">
<rect x="8" y="8" width="{w - 9}" height="{h - 9}" rx="18" fill="{t["line2"]}"/>
<rect x=".75" y=".75" width="{w - 9}" height="{h - 9}" rx="18" fill="{t["panel"]}" stroke="{t["line2"]}" stroke-width="1.5"/>
{"".join(rows)}</svg>'''


def journey_m(t):
    """Phone journey: vertical timeline."""
    w, step = 640, 132
    h = 40 + step * len(JOURNEY)
    out = [f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="18" fill="{t["panel"]}" stroke="{t["line2"]}" stroke-width="1.5"/>',
           f'<line x1="60" y1="60" x2="60" y2="{40 + step * (len(JOURNEY) - 2) + 20}" stroke="{t["line2"]}" stroke-width="3"/>',
           f'<line x1="60" y1="{40 + step * (len(JOURNEY) - 2) + 20}" x2="60" y2="{40 + step * (len(JOURNEY) - 1) + 20}" stroke="{t["line2"]}" stroke-width="3" stroke-dasharray="6 7"/>']
    for i, (when, a, b, col, future) in enumerate(JOURNEY):
        y = 60 + i * step
        out.append(f'<circle cx="60" cy="{y}" r="13" fill="{t["panel"]}" stroke="{t[col]}" stroke-width="5"' + (' stroke-dasharray="4 4"' if future else "") + "/>")
        out.append(f'<text x="96" y="{y - 14}" font-family="{MONO}" font-size="17" letter-spacing="1.5" fill="{t[col]}">{E(when)}</text>'
                   f'<text x="96" y="{y + 16}" font-family="{BODY}" font-size="23" font-weight="600" fill="{t["fg"]}">{E(a)}</text>'
                   f'<text x="96" y="{y + 44}" font-family="{BODY}" font-size="19" fill="{t["muted"]}">{E(b)}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Journey">{"".join(out)}</svg>'


def main():
    for mode, t in THEMES.items():
        save(f"stack-{mode}.svg", stack(t))
        save(f"footer-{mode}.svg", footer(t))
        save(f"journey-{mode}.svg", journey(t))
        save(f"stack-m-{mode}.svg", stack_m(t))
        save(f"journey-m-{mode}.svg", journey_m(t))
        for lab in ("SELECTED WORK", "TOOLBOX", "ABOUT", "CONTACT", "HOMELAB", "NOW", "JOURNEY", "CONTRIBUTIONS", "CAN FD", "THESIS"):
            save(f"div-{lab.lower().replace(' ', '-')}-{mode}.svg", divider(t, lab))
            save(f"div-{lab.lower().replace(' ', '-')}-m-{mode}.svg", divider(t, lab, 640, 26))
    print("wrote", len(os.listdir(OUT)), "files to", OUT)


if __name__ == "__main__":
    main()
