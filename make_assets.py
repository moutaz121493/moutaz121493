#!/usr/bin/env python3
"""Builds the profile README images in assets/ (dark = HUD, light = Retro-Tech paper, same palette as moutazm.com).
Run: python3 make_assets.py   (stdlib only; the README picks dark/light with <picture> + prefers-color-scheme)."""
import html
import os
import random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

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


def traces(t, w, h, seed, n=14, anim=True):
    """Circuit-board traces (right angles + pads); a few carry a moving pulse."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.randrange(0, w, 40), rnd.randrange(20, h, 20)
        pts = [(x, y)]
        for _ in range(rnd.randint(2, 4)):
            if rnd.random() < .5:
                x += rnd.choice([-1, 1]) * rnd.randrange(60, 220, 20)
            else:
                y += rnd.choice([-1, 1]) * rnd.randrange(20, 80, 20)
            x, y = max(0, min(w, x)), max(10, min(h - 10, y))
            pts.append((x, y))
        d = "M" + " L".join(f"{a},{b}" for a, b in pts)
        out.append(f'<path d="{d}" fill="none" stroke="{t["trace"]}" stroke-width="1.2" opacity=".55"/>')
        for a, b in (pts[0], pts[-1]):
            out.append(f'<circle cx="{a}" cy="{b}" r="2.6" fill="none" stroke="{t["trace"]}" stroke-width="1.2" opacity=".7"/>')
        if anim and i % 3 == 0:
            dur = rnd.uniform(3.5, 7)
            out.append(f'<circle r="2.4" fill="{t["accent"]}"><animateMotion dur="{dur:.1f}s" repeatCount="indefinite" '
                       f'path="{d}"/><animate attributeName="opacity" values="0;1;1;0" dur="{dur:.1f}s" repeatCount="indefinite"/></circle>')
    return "\n".join(out)


def banner(t, mode):
    w, h = 1280, 330
    # CAN differential pair: a bit pattern (SOF + ID bits) drawn as CAN_H / CAN_L
    bits = [1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0]
    x0, bw, yh, yl, yr = 800, 14, 112, 156, 134
    hp, lp, x = [f"M{x0},{yr}"], [f"M{x0},{yr}"], x0
    for b in bits:
        if b == 0:   # dominant: H up, L down
            hp += [f"L{x},{yh}", f"L{x + bw},{yh}", f"L{x + bw},{yr}"]
            lp += [f"L{x},{yl}", f"L{x + bw},{yl}", f"L{x + bw},{yr}"]
        else:
            hp.append(f"L{x + bw},{yr}")
            lp.append(f"L{x + bw},{yr}")
        x += bw
    can_end = x
    # neural net to the right of the signal
    layers = [[134], [84, 134, 184], [60, 108, 160, 208], [100, 168], [134]]
    lx = [can_end + 28 + i * 56 for i in range(len(layers))]
    edges, nodes = [], []
    for i in range(len(layers) - 1):
        for a in layers[i]:
            for b in layers[i + 1]:
                edges.append(f'<line x1="{lx[i]}" y1="{a}" x2="{lx[i + 1]}" y2="{b}" stroke="{t["ai"]}" stroke-width=".9" opacity=".35"/>')
    k = 0
    for i, col in enumerate(layers):
        for y in col:
            k += 1
            nodes.append(f'<circle cx="{lx[i]}" cy="{y}" r="6.5" fill="{t["panel"]}" stroke="{t["ai"]}" stroke-width="1.6">'
                         f'<animate attributeName="r" values="6.5;8;6.5" dur="2.4s" begin="{k * .17:.2f}s" repeatCount="indefinite"/></circle>')
    sig_len = (can_end - x0) * 3
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Moutaz Mohammad, embedded engineer building intelligent systems, from CAN bits to RAG pipelines">
<defs>
  <radialGradient id="g" cx="78%" cy="40%" r="55%"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"]}"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>
  <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{t["bg"]}" stop-opacity=".96"/><stop offset=".55" stop-color="{t["bg"]}" stop-opacity=".55"/><stop offset="1" stop-color="{t["bg"]}" stop-opacity=".1"/></linearGradient>
  <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{t["line"]}"/></pattern>
  <clipPath id="clip"><rect width="{w}" height="{h}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#clip)">
  <rect width="{w}" height="{h}" fill="{t["bg"]}"/>
  <rect width="{w}" height="{h}" fill="url(#dots)" opacity=".7"/>
  {traces(t, w, h, 7)}
  <rect width="{w}" height="{h}" fill="url(#g)"/>
  <rect width="{w}" height="{h}" fill="url(#fade)"/>
  <g font-family="{MONO}" font-size="11" fill="{t["muted"]}" letter-spacing="1.5">
    <text x="{x0}" y="92">CAN_H</text><text x="{x0}" y="184">CAN_L</text><text x="{lx[0] - 6}" y="250">NEURAL NET</text>
  </g>
  <path d="{" ".join(hp)}" fill="none" stroke="{t["accent"]}" stroke-width="2.4" stroke-linejoin="round" stroke-dasharray="{sig_len}" stroke-dashoffset="{sig_len}">
    <animate attributeName="stroke-dashoffset" values="{sig_len};0;0" keyTimes="0;.45;1" dur="5s" repeatCount="indefinite"/></path>
  <path d="{" ".join(lp)}" fill="none" stroke="{t["ai"]}" stroke-width="2.4" stroke-linejoin="round" stroke-dasharray="{sig_len}" stroke-dashoffset="{sig_len}">
    <animate attributeName="stroke-dashoffset" values="{sig_len};0;0" keyTimes="0;.45;1" dur="5s" repeatCount="indefinite"/></path>
  {"".join(edges)}
  {"".join(nodes)}
  <g font-family="{MONO}" font-size="13" fill="{t["accent"]}" letter-spacing="3">
    <text x="64" y="84">● WOLFENBÜTTEL, GERMANY</text>
  </g>
  <text x="62" y="152" font-family="{DISPLAY}" font-size="58" font-weight="700" fill="{t["fg"]}">Moutaz Mohammad</text>
  <text x="64" y="198" font-family="{BODY}" font-size="24" fill="{t["fg"]}">Embedded engineer building intelligent systems</text>
  <text x="64" y="232" font-family="{BODY}" font-size="24" fill="{t["accent"]}">from CAN bits to RAG pipelines.</text>
  <g font-family="{MONO}" font-size="12.5" letter-spacing="1">
    {chips(t, ["AUTOMOTIVE NETWORKS", "LINUX &amp; INFRASTRUCTURE", "APPLIED AI"], 64, 266)}
  </g>
  <rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="21.5" fill="none" stroke="{t["line2"]}" stroke-width="1.5"/>
</g>
</svg>'''


def chips(t, labels, x, y, pad=14, cw=8.9):
    out = []
    for lab in labels:
        width = int(len(html.unescape(lab)) * cw + pad * 2)
        out.append(f'<rect x="{x}" y="{y}" width="{width}" height="30" rx="15" fill="{t["panel"]}" stroke="{t["line2"]}"/>'
                   f'<text x="{x + pad}" y="{y + 20}" fill="{t["muted"]}">{lab}</text>')
        x += width + 10
    return "".join(out)


def wrap(text, n):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        if len(cur) + len(w_) + 1 > n:
            lines.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    return lines + [cur]


STATUS = {"live": ("LIVE", "live"), "web": ("RUNS IN THE BROWSER", "ai"), "progress": ("IN PROGRESS", "progress"),
          "code": ("OPEN SOURCE", "accent")}


def card(t, title, text, status, tags, icon, num=1):
    w, h = 600, 210
    lab, col = STATUS[status]
    lines = wrap(text, 62)[:3]
    body = "".join(f'<text x="28" y="{108 + i * 24}">{E(l)}</text>' for i, l in enumerate(lines))
    x, chip = 28, []
    for tg in tags:
        cw = int(len(tg) * 7.6 + 24)
        chip.append(f'<rect x="{x}" y="166" width="{cw}" height="24" rx="12" fill="none" stroke="{t["line2"]}"/>'
                    f'<text x="{x + 11}" y="182">{E(tg)}</text>')
        x += cw + 8
    sw = int(len(lab) * 8.0 + 36)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{E(title)}: {E(text)}">
<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="18"/></clipPath>
<radialGradient id="g" cx="100%" cy="0%" r="70%"><stop offset="0" stop-color="{t[col]}" stop-opacity="{t["glow"]}"/><stop offset="1" stop-color="{t[col]}" stop-opacity="0"/></radialGradient></defs>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="{t["panel"]}"/><rect width="{w}" height="{h}" fill="url(#g)"/>
  <rect x="0" y="0" width="4" height="{h}" fill="{t[col]}"/>
  <text x="28" y="40" font-family="{MONO}" font-size="13" letter-spacing="2" fill="{t[col]}">// {num:02d}</text>
  <rect x="{w - sw - 22}" y="22" width="{sw}" height="24" rx="12" fill="none" stroke="{t[col]}"/>
  <circle cx="{w - sw - 8}" cy="34" r="4" fill="{t[col]}"><animate attributeName="opacity" values="1;.25;1" dur="1.8s" repeatCount="indefinite"/></circle>
  <text x="{w - sw + 2}" y="38.5" font-family="{MONO}" font-size="11.5" letter-spacing="1" fill="{t[col]}">{lab}</text>
  <text x="28" y="78" font-family="{DISPLAY}" font-size="26" font-weight="700" fill="{t["fg"]}">{E(title)}</text>
  <g font-family="{BODY}" font-size="15.5" fill="{t["muted"]}">{body}</g>
  <g font-family="{MONO}" font-size="11.5" fill="{t["muted"]}">{"".join(chip)}</g>
  <rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="17.5" fill="none" stroke="{t["line2"]}" stroke-width="1.5"/>
</g></svg>'''


CARDS = [
    ("diag-agent", "diag-agent", "A server that diagnoses its own outages: redacted evidence, an LLM with no tools, one alert with cause and fix.",
     "code", ["Python", "systemd", "LLM", "Uptime Kuma"], "⚕"),
    ("can-tools", "CAN FD bit timing", "Finds valid nominal and data-phase bit timings for M_CAN-style controllers, entirely in the browser.",
     "web", ["CAN FD", "TDC", "JavaScript"], "⎍"),
    ("moutaz-home", "Moutaz Home", "Self-hosted homelab on a Raspberry Pi 5: zero-trust access, encrypted 3-2-1 backups with restore tests, monitoring.",
     "live", ["Docker", "Cloudflare", "restic"], "⌂"),
    ("paperless-ai", "Paperless AI", "German paperwork filed by an LLM: sender, type, amount, deadline and a short summary.",
     "live", ["Paperless-ngx", "Claude", "Python"], "✉"),
    ("home-rag", "Home RAG", "Master's thesis: ask in Arabic about German documents and get answers with sources, evaluated rather than guessed.",
     "progress", ["RAG", "Hybrid retrieval", "Eval"], "⌕"),
    ("moutazm-com", "moutazm.com", "My trilingual portfolio (EN / DE / AR with full RTL). Astro on Cloudflare Workers, no trackers.",
     "live", ["Astro", "i18n", "Workers"], "◈"),
]

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
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="18" fill="{t["panel"]}" stroke="{t["line2"]}" stroke-width="1.5"/>
{"".join(rows)}</svg>'''


def divider(t, label):
    w, h = 1280, 46
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}">
<text x="0" y="30" font-family="{MONO}" font-size="15" letter-spacing="4" fill="{t["accent"]}">// {E(label)}</text>
<line x1="{len(label) * 13.5 + 60}" y1="25" x2="{w}" y2="25" stroke="{t["line2"]}" stroke-width="1.2"/>
<circle r="3" cy="25" fill="{t["accent"]}"><animate attributeName="cx" values="{len(label) * 13.5 + 60};{w};{w}" keyTimes="0;.7;1" dur="4.5s" repeatCount="indefinite"/></circle>
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


def main():
    for mode, t in THEMES.items():
        save(f"banner-{mode}.svg", banner(t, mode))
        save(f"stack-{mode}.svg", stack(t))
        save(f"footer-{mode}.svg", footer(t))
        for n, (slug, title, text, status, tags, icon) in enumerate(CARDS, 1):
            save(f"card-{slug}-{mode}.svg", card(t, title, text, status, tags, icon, n))
        for lab in ("SELECTED WORK", "TOOLBOX", "ABOUT", "CONTACT", "HOMELAB"):
            save(f"div-{lab.lower().replace(' ', '-')}-{mode}.svg", divider(t, lab))
    print("wrote", len(os.listdir(OUT)), "files to", OUT)


if __name__ == "__main__":
    main()
