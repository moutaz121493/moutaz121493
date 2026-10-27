#!/usr/bin/env python3
"""Isometric depth for the quiet sections: the NOW tiles and the six project cards.

Cards are raised tiles (flat, readable front face + extruded side faces + soft shadow); each has a small
isometric illustration with one slow micro-animation. Text stays flat and crisp (embedded fonts).
"""
import math

from svglib import Svg, THEMES, write, E

C30, S30 = math.cos(math.radians(30)), 0.5


def iso(x, y, z, ox, oy, s=1.0):
    return ox + (x - y) * C30 * s, oy + (x + y) * S30 * s - z * s


def box(x, y, z, w, d, h, ox, oy, s, top, left, right, stroke, extra=""):
    """Isometric box -> 3 faces (top, left = +y side, right = +x side)."""
    P = lambda a, b, c: iso(a, b, c, ox, oy, s)   # noqa: E731
    f = lambda pts: " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)   # noqa: E731
    t_ = [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    l_ = [P(x, y + d, z + h), P(x + w, y + d, z + h), P(x + w, y + d, z), P(x, y + d, z)]
    r_ = [P(x + w, y, z + h), P(x + w, y + d, z + h), P(x + w, y + d, z), P(x + w, y, z)]
    sw = f' stroke="{stroke}" stroke-width="1.2" stroke-linejoin="round"'
    return (f'<g{extra}><polygon points="{f(l_)}" fill="{left}"{sw}/><polygon points="{f(r_)}" fill="{right}"{sw}/>'
            f'<polygon points="{f(t_)}" fill="{top}"{sw}/></g>')


def tile(t, x, y, w, h, col, depth=10):
    """Raised card: shadow, extruded bottom/right faces, front face with a coloured edge."""
    d = depth
    return (f'<rect x="{x + d + 6}" y="{y + d + 10}" width="{w}" height="{h}" rx="16" fill="#000" opacity="{.35 if t["bg"] < "#8" else .12}" filter="url(#blur)"/>'
            f'<path d="M{x + 16},{y + h} L{x + w},{y + h} L{x + w},{y + 16} L{x + w + d},{y + 16 + d} L{x + w + d},{y + h + d - 10} '
            f'Q{x + w + d},{y + h + d} {x + w + d - 10},{y + h + d} L{x + 16 + d},{y + h + d} Z" fill="{t["line2"]}"/>'
            f'<path d="M{x + 16},{y + h} L{x + 16 + d},{y + h + d} L{x + w + d - 10},{y + h + d}" fill="none" stroke="{t[col]}" stroke-width="1.2" opacity=".6"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{t["panel"]}" stroke="{t["line2"]}" stroke-width="1.5"/>'
            f'<rect x="{x}" y="{y + 18}" width="4" height="{h - 36}" fill="{t[col]}"/>')


def wrap(text, n):
    out, cur = [], ""
    for w_ in text.split():
        if len(cur) + len(w_) + 1 > n:
            out.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    return out + [cur]


# ---------- micro illustrations (isometric, one slow animation each) ----------

def ill_book(t, ox, oy):
    s = 1.0
    out = box(0, 0, 0, 56, 40, 8, ox, oy, s, t["panel"], t["line2"], t["line"], t["accent"])
    a0, a1 = iso(28, 0, 8, ox, oy), iso(28, 40, 8, ox, oy)
    # page that flips: its free edge swings from the right half to the left half
    def page(angle):
        r = 26
        ex = 28 + r * math.cos(angle)
        ez = 8 + r * math.sin(angle) * .9
        p1, p2 = iso(ex, 0, ez, ox, oy), iso(ex, 40, ez, ox, oy)
        return f"M{a0[0]:.1f},{a0[1]:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} L{a1[0]:.1f},{a1[1]:.1f} Z"
    frames = [page(math.radians(a)) for a in (8, 40, 90, 140, 172, 172, 172, 8)]
    out += (f'<path class="m" d="{frames[0]}" fill="{t["bg2"]}" stroke="{t["ai"]}" stroke-width="1.4">'
            f'<animate attributeName="d" values="{";".join(frames + frames[:1])}" dur="4.5s" repeatCount="indefinite"/></path>'
            f'<path class="s" d="{frames[2]}" fill="{t["bg2"]}" stroke="{t["ai"]}" stroke-width="1.4"/>')
    return out


def ill_ring(t, ox, oy):
    # a progress ring lying in the isometric floor plane (ellipse), slowly filling
    rx, ry = 34, 20
    circ = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
    return (f'<ellipse cx="{ox}" cy="{oy}" rx="{rx}" ry="{ry}" fill="none" stroke="{t["line2"]}" stroke-width="7"/>'
            f'<ellipse cx="{ox}" cy="{oy}" rx="{rx}" ry="{ry}" fill="none" stroke="{t["accent"]}" stroke-width="7" stroke-linecap="round" '
            f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ * .62:.1f}">'
            f'<animate class="m" attributeName="stroke-dashoffset" values="{circ * .9:.1f};{circ * .38:.1f};{circ * .38:.1f};{circ * .9:.1f}" '
            f'keyTimes="0;.6;.9;1" dur="6s" repeatCount="indefinite"/></ellipse>'
            + box(-8, -8, 0, 16, 16, 18, ox, oy - 4, 1, t["panel"], t["line2"], t["line"], t["accent"]))


def ill_blocks(t, ox, oy):
    # three cubes drop in one after another and stack
    out = []
    cols = [t["live"], t["ai"], t["accent"]]
    pos = [(0, 0, 0), (22, 0, 0), (11, 0, 18)]
    for i, (x, y, z) in enumerate(pos):
        b = box(x, y, z, 20, 20, 18, ox, oy, 1, cols[i], t["line2"], t["line"], t["panel"])
        k0, k1 = .1 + i * .2, .25 + i * .2
        out.append(f'<g class="m" opacity="0">{b}<animateTransform attributeName="transform" type="translate" values="0,-40;0,-40;0,0;0,0;0,0" '
                   f'keyTimes="0;{k0:.2f};{k1:.2f};.92;1" dur="5s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{k0:.2f};{k1:.2f};.92;1" dur="5s" repeatCount="indefinite"/></g>')
        out.append(f'<g class="s">{b}</g>')
    return "".join(out)


def ill_monitor(t, ox, oy):   # diag-agent: a server box with a heartbeat on its front
    out = box(0, 0, 0, 60, 34, 34, ox, oy, 1, t["panel"], t["line2"], t["bg2"], t["accent"])
    pts = [(0, 20), (14, 20), (18, 10), (22, 28), (26, 20), (34, 20), (38, 6), (42, 30), (46, 20), (60, 20)]
    d = "M" + " L".join(f"{iso(a, 34, 34 - b * .9, ox, oy)[0]:.1f},{iso(a, 34, 34 - b * .9, ox, oy)[1]:.1f}" for a, b in pts)
    return out + (f'<path d="{d}" fill="none" stroke="{t["live"]}" stroke-width="2" stroke-dasharray="120" stroke-dashoffset="120">'
                  f'<animate class="m" attributeName="stroke-dashoffset" values="120;0;0" keyTimes="0;.5;1" dur="2.8s" repeatCount="indefinite"/></path>')


def ill_scope(t, ox, oy):     # CAN tools: oscilloscope screen with a CAN wave
    out = box(0, 0, 0, 64, 10, 40, ox, oy, 1, t["bg2"], t["line2"], t["panel"], t["ai"])
    bits = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1]
    d, x = [], 4
    for b in bits:
        z = 12 if b else 28
        a = iso(x, 10, z, ox, oy)
        c = iso(x + 5.6, 10, z, ox, oy)
        d.append(f"L{a[0]:.1f},{a[1]:.1f} L{c[0]:.1f},{c[1]:.1f}")
        x += 5.6
    st = iso(4, 10, 12, ox, oy)
    return out + (f'<path d="M{st[0]:.1f},{st[1]:.1f} {" ".join(d)}" fill="none" stroke="{t["ai"]}" stroke-width="1.8" opacity=".95">'
                  f'<animate class="m" attributeName="opacity" values=".25;1;.25" dur="2.4s" repeatCount="indefinite"/></path>')


def ill_pi(t, ox, oy):        # Moutaz Home: a little board with blinking LEDs
    out = box(0, 0, 0, 64, 44, 6, ox, oy, 1, t["live"] if False else t["panel"], t["line2"], t["line"], t["live"])
    out += box(8, 8, 6, 18, 18, 8, ox, oy, 1, t["bg2"], t["line2"], t["line"], t["muted"])
    out += box(34, 6, 6, 22, 12, 10, ox, oy, 1, t["bg2"], t["line2"], t["line"], t["muted"])
    leds = []
    for i, col in enumerate((t["live"], t["accent"])):
        p = iso(52, 34 + i * 6, 6, ox, oy)
        leds.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.6" fill="{col}">'
                    f'<animate class="m" attributeName="opacity" values="1;.2;1" dur="{1.1 + i * .7:.1f}s" repeatCount="indefinite"/></circle>')
    return out + "".join(leds)


def ill_docs(t, ox, oy):      # Paperless AI: a stack of documents, the top one gets a tag
    out = ""
    for i in range(3):
        out += box(0, 0, i * 5, 46, 58, 3, ox, oy, 1, t["panel"], t["line2"], t["line"], t["muted"])
    for k in range(3):
        a, b = iso(8, 10 + k * 9, 18, ox, oy), iso(36, 10 + k * 9, 18, ox, oy)
        out += f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{t["line2"]}" stroke-width="2"/>'
    tag = iso(30, 44, 18, ox, oy)
    return out + (f'<g transform="translate({tag[0]:.1f},{tag[1]:.1f})"><rect x="-4" y="-9" width="34" height="14" rx="7" fill="{t["accent"]}">'
                  f'<animate class="m" attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.3;.4;.9;1" dur="4s" repeatCount="indefinite"/></rect></g>')


def ill_rag(t, ox, oy):       # Home RAG: a database cylinder with a scanning ring
    rx, ry, hh = 30, 15, 40
    out = (f'<path d="M{ox - rx},{oy} L{ox - rx},{oy + hh} A{rx},{ry} 0 0 0 {ox + rx},{oy + hh} L{ox + rx},{oy} Z" fill="{t["bg2"]}" stroke="{t["ai"]}" stroke-width="1.3"/>'
           f'<ellipse cx="{ox}" cy="{oy}" rx="{rx}" ry="{ry}" fill="{t["panel"]}" stroke="{t["ai"]}" stroke-width="1.3"/>')
    for k in (1, 2):
        out += f'<path d="M{ox - rx},{oy + k * 13} A{rx},{ry} 0 0 0 {ox + rx},{oy + k * 13}" fill="none" stroke="{t["line2"]}" stroke-width="1.2"/>'
    return out + (f'<ellipse cx="{ox}" cy="{oy}" rx="{rx + 4}" ry="{ry + 2}" fill="none" stroke="{t["accent"]}" stroke-width="2">'
                  f'<animate class="m" attributeName="cy" values="{oy};{oy + hh};{oy}" dur="3.6s" repeatCount="indefinite"/>'
                  f'<animate class="m" attributeName="opacity" values=".9;.3;.9" dur="3.6s" repeatCount="indefinite"/></ellipse>')


def ill_web(t, ox, oy):       # moutazm.com: a browser window with 3 language tabs
    out = box(0, 0, 0, 70, 6, 46, ox, oy, 1, t["bg2"], t["line2"], t["panel"], t["live"])
    for i, col in enumerate((t["live"], t["accent"], t["ai"])):
        pts = [iso(6 + i * 20 + dx, 6, z, ox, oy) for dx, z in ((0, 42), (16, 42), (16, 34), (0, 34))]
        out += (f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{col}" opacity=".35">'
                f'<animate class="m" attributeName="opacity" values=".25;.95;.25" begin="{i * .9:.1f}s" dur="2.7s" repeatCount="indefinite"/></polygon>')
    return out


def defs(svg):
    svg.defs.append('<filter id="blur" x="-10%" y="-10%" width="120%" height="140%"><feGaussianBlur stdDeviation="9"/></filter>')


NOW = [("STUDYING", "M.Sc. Web Technologies: thesis on cross-lingual RAG (Arabic ↔ German).", "ai", ill_book),
       ("LEARNING", "Structured AI-engineering path: IBM AI Engineering, then Google Cloud ML Engineer.", "accent", ill_ring),
       ("BUILDING", "A measurable RAG system over my own documents, with an evaluation set and experiments.", "live", ill_blocks)]


def now(t):
    W, H = 1280, 250
    svg = Svg(W, H, "Now: studying an M.Sc. with a thesis on cross-lingual RAG; learning a structured AI-engineering path; "
                    "building a measurable RAG system over my own documents", t)
    defs(svg)
    cw, gap = 396, 22
    for i, (k, v, col, ill) in enumerate(NOW):
        x, y = 8 + i * (cw + gap), 8
        svg.add(tile(t, x, y, cw, 210, col))
        svg.add(ill(t, x + cw - 92, y + 150))
        svg.add(svg.text(x + 26, y + 40, k, "mono", 13, t[col + "Text"], ls=3))
        for j, line in enumerate(wrap(v, 27)[:4]):
            svg.add(svg.text(x + 26, y + 84 + j * 27, line, "body", 18, t["fg"]))
    return svg.render()


CARDS = [
    ("diag-agent", "diag-agent", "A server that diagnoses its own outages: redacted evidence, an LLM with no tools, one alert with cause and fix.",
     "OPEN SOURCE", "accent", ["Python", "systemd", "LLM", "Uptime Kuma"], ill_monitor),
    ("can-tools", "canfd-bittiming", "C99 library: exact CAN FD bit timings for M_CAN, NBTP/DBTP/TDCR + TDC. No heap, sanitizer-tested; also runs in the browser.",
     "OPEN SOURCE", "ai", ["C99", "CAN FD", "M_CAN", "CI"], ill_scope),
    ("moutaz-home", "Moutaz Home", "Self-hosted homelab on a Raspberry Pi 5: zero-trust access, encrypted 3-2-1 backups with restore tests, monitoring.",
     "LIVE", "live", ["Docker", "Cloudflare", "restic"], ill_pi),
    ("paperless-ai", "Paperless AI", "German paperwork filed by an LLM: sender, type, amount, deadline and a short summary.",
     "LIVE", "live", ["Paperless-ngx", "Claude", "Python"], ill_docs),
    ("home-rag", "Home RAG", "Master's thesis: ask in Arabic about German documents and get answers with sources, evaluated rather than guessed.",
     "IN PROGRESS", "accent", ["RAG", "Hybrid retrieval", "Eval"], ill_rag),
    ("moutazm-com", "moutazm.com", "My trilingual portfolio (EN / DE / AR with full RTL). Astro on Cloudflare Workers, no trackers.",
     "LIVE", "live", ["Astro", "i18n", "Workers"], ill_web),
]


def card(t, n, title, text, status, col, tags, ill):
    W, H = 620, 262
    svg = Svg(W, H, f"{title}: {text}", t)
    defs(svg)
    x, y, w, h = 6, 6, 590, 226
    svg.add(tile(t, x, y, w, h, col))
    svg.add(ill(t, x + w - 96, y + 86))
    svg.add(svg.text(x + 26, y + 38, f"// {n:02d}", "mono", 13, t[col + "Text"], ls=2))
    sw = len(status) * 8.4 + 34
    sx = x + 26 + 70
    svg.add(f'<rect x="{sx}" y="{y + 22}" width="{sw:.0f}" height="24" rx="12" fill="none" stroke="{t[col]}"/>'
            f'<circle cx="{sx + 14}" cy="{y + 34}" r="4" fill="{t[col]}"><animate class="m" attributeName="opacity" values="1;.25;1" dur="1.8s" repeatCount="indefinite"/></circle>')
    svg.add(svg.text(sx + 24, y + 38.5, status, "mono", 11.5, t[col + "Text"], ls=1))
    svg.add(svg.text(x + 26, y + 82, title, "display", 28, t["fg"]))
    for j, line in enumerate(wrap(text, 46)[:3]):
        svg.add(svg.text(x + 26, y + 114 + j * 23, line, "body", 15.5, t["muted"]))
    tx = x + 26
    for tg in tags:
        cw = len(tg) * 7.9 + 24
        svg.add(f'<rect x="{tx:.0f}" y="{y + h - 42}" width="{cw:.0f}" height="24" rx="12" fill="none" stroke="{t["line2"]}"/>')
        svg.add(svg.text(tx + 12, y + h - 25.5, tg, "mono", 11.5, t["muted"]))
        tx += cw + 8
    return svg.render()


def main():
    for mode, t in THEMES.items():
        p, n_ = write("now3d", mode, now(t))
        print(f"{p}: {n_ / 1024:.0f} KB")
        for i, (slug, title, text, status, col, tags, ill) in enumerate(CARDS, 1):
            p, n_ = write(f"card3d-{slug}", mode, card(t, i, title, text, status, col, tags, ill))
        print(f"6 cards ({mode}) ok")



# ---------- phone variants (640 px wide, stacked, larger type) ----------

def now_m(t):
    W, th, gap = 640, 196, 22
    H = 8 + 3 * th + 2 * gap + 22
    svg = Svg(W, H, "Now: studying an M.Sc. with a thesis on cross-lingual RAG; learning a structured AI-engineering path; "
                    "building a measurable RAG system over my own documents", t)
    defs(svg)
    for i, (k, v, col, ill) in enumerate(NOW):
        x, y = 6, 6 + i * (th + gap)
        svg.add(tile(t, x, y, W - 30, th, col))
        svg.add(ill(t, x + W - 140, y + 112))
        svg.add(svg.text(x + 26, y + 42, k, "mono", 18, t[col + "Text"], ls=3))
        for j, line in enumerate(wrap(v, 30)[:4]):
            svg.add(svg.text(x + 26, y + 86 + j * 30, line, "body", 22, t["fg"]))
    return svg.render()


def card_m(t, n, title, text, status, col, tags, ill):
    W, H = 380, 300
    svg = Svg(W, H, f"{title}: {text}", t)
    defs(svg)
    x, y, w, h = 6, 6, 356, 270
    svg.add(tile(t, x, y, w, h, col))
    svg.add(ill(t, x + w - 110, y + 150))
    svg.add(svg.text(x + 24, y + 46, f"{n:02d}", "mono", 22, t[col + "Text"], ls=2))
    svg.add(f'<circle cx="{x + 80}" cy="{y + 39}" r="7" fill="{t[col]}"><animate class="m" attributeName="opacity" values="1;.25;1" dur="1.8s" repeatCount="indefinite"/></circle>')
    words = title.split()
    lines = [title] if len(title) <= 13 else [" ".join(words[:len(words) // 2 or 1]), " ".join(words[len(words) // 2 or 1:])]
    for j, line in enumerate(lines):
        svg.add(svg.text(x + 24, y + 104 + j * 40, line, "display", 36, t["fg"]))
    svg.add(svg.text(x + 24, y + h - 26, status, "mono", 18, t[col + "Text"], ls=1.5))
    return svg.render()


def main_m():
    for mode, t in THEMES.items():
        write("now3d-m", mode, now_m(t))
        for i, (slug, title, text, status, col, tags, ill) in enumerate(CARDS, 1):
            write(f"card3d-{slug}-m", mode, card_m(t, i, title, text, status, col, tags, ill))
    print("phone variants: now3d-m + 6 cards")


if __name__ == "__main__":
    main()
    main_m()
