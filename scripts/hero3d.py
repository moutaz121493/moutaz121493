#!/usr/bin/env python3
"""Hero: "from CAN bits to RAG pipelines" told as one pipeline in five stages, with isometric depth.

  01 CAN FD bits  ->  02 decode (MCU)  ->  03 embed (tokens)  ->  04 reason (layered network)  ->  05 answer + sources

One 8 s story loop: the frame scrolls into the chip, the chip lights up, bytes become token cubes, an activation
wave sweeps through the network layer by layer, then the answer writes itself and the citations appear; everything
fades back and the loop restarts seamlessly. Reduced motion shows the finished state.
Desktop 1280 x 470 (stages left to right); phone 640 x 1130 (stages top to bottom). Deterministic.
"""
from iso import iso
from svglib import Svg, THEMES, write

LOOP = 8.0


def kt(*pairs):
    """[(time_s, value)] -> (values, keyTimes) for a looping SMIL animation."""
    pts = sorted(pairs)
    if pts[0][0] > 0:
        pts.insert(0, (0.0, pts[0][1]))
    if pts[-1][0] < LOOP:
        pts.append((LOOP, pts[0][1]))
    return ";".join(str(v) for _, v in pts), ";".join(f"{t / LOOP:.4f}" for t, _ in pts)


def anim(attr, *pairs):
    v, k = kt(*pairs)
    return f'<animate attributeName="{attr}" values="{v}" keyTimes="{k}" dur="{LOOP}s" repeatCount="indefinite"/>'


def poly(pts):
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)


def iso_box(x, y, z, w, d, h, ox, oy, s, top, left, right, stroke):
    P = lambda a, b, c: iso(a, b, c, ox, oy, s)   # noqa: E731
    t_ = [P(x, y, z + h), P(x + w, y, z + h), P(x + w, y + d, z + h), P(x, y + d, z + h)]
    l_ = [P(x, y + d, z + h), P(x + w, y + d, z + h), P(x + w, y + d, z), P(x, y + d, z)]
    r_ = [P(x + w, y, z + h), P(x + w, y + d, z + h), P(x + w, y + d, z), P(x + w, y, z)]
    sw = f'stroke="{stroke}" stroke-width="1.2" stroke-linejoin="round"'
    return (f'<polygon points="{poly(l_)}" fill="{left}" {sw}/><polygon points="{poly(r_)}" fill="{right}" {sw}/>'
            f'<polygon points="{poly(t_)}" fill="{top}" {sw}/>')


# ---------------- the five stages (each drawn around a centre point, at scale s) ----------------

BITS = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1]


def stage_bus(svg, t, cx, cy, s):
    """01: CAN_H / CAN_L on an isometric plate; the bit pattern scrolls towards the chip."""
    w = 184 * s
    plate = [(cx - w / 2, cy + 26 * s), (cx + w / 2 - 30 * s, cy + 26 * s), (cx + w / 2, cy + 46 * s), (cx - w / 2 + 30 * s, cy + 46 * s)]
    out = [f'<polygon points="{poly(plate)}" fill="{t["bg2"]}" stroke="{t["line2"]}"/>']
    bw = 16 * s

    def wave(rec, dom):
        d, x = [], 0.0
        for _ in range(3):
            for b in BITS:                               # 1 = recessive, 0 = dominant
                y = rec if b else dom
                d.append(f"L{x:.1f},{y:.1f} L{x + bw:.1f},{y:.1f}")
                x += bw
        return f"M0,{rec:.1f} " + " ".join(d), x / 3
    dh, per = wave(cy - 8 * s, cy - 28 * s)              # CAN_H rises when dominant
    dl, _ = wave(cy + 2 * s, cy + 20 * s)                # CAN_L falls when dominant
    cid = f"bus{int(cx)}{int(cy)}"
    svg.defs.append(f'<clipPath id="{cid}"><rect x="{cx - w / 2:.1f}" y="{cy - 40 * s:.1f}" width="{w:.1f}" height="{70 * s:.1f}"/></clipPath>')
    move = (f'<animateTransform attributeName="transform" type="translate" values="{cx - w / 2 - per:.1f},0;{cx - w / 2:.1f},0" '
            f'dur="{LOOP / 2}s" repeatCount="indefinite"/>')
    paths = (f'<path d="{dh}" fill="none" stroke="{t["accent"]}" stroke-width="{2.6 * s:.1f}" stroke-linejoin="round"/>'
             f'<path d="{dl}" fill="none" stroke="{t["ai"]}" stroke-width="{2.6 * s:.1f}" stroke-linejoin="round"/>')
    out.append(f'<g clip-path="url(#{cid})"><g class="m">{move}{paths}</g><g class="s" transform="translate({cx - w / 2:.1f},0)">{paths}</g></g>')
    out.append(svg.text(cx - w / 2, cy - 36 * s, "CAN_H", "mono", 11 * s, t["accentText"], ls=1))
    out.append(svg.text(cx - w / 2, cy + 40 * s, "CAN_L", "mono", 11 * s, t["aiText"], ls=1))
    out.append(svg.text(cx + 8 * s, cy + 66 * s, "1 0 1 1 0 1 0 0 …", "mono", 11.5 * s, t["muted"], ls=1.5))
    return "".join(out)


def stage_mcu(svg, t, cx, cy, s):
    """02: an isometric microcontroller; the die lights up when the frame arrives."""
    ox, oy = cx - 46 * s, cy - 16 * s
    out = []
    for i in range(6):                                   # pins on the two visible sides
        a = iso(8 + i * 13, 92, 0, ox, oy, s)
        b = iso(92, 8 + i * 13, 0, ox, oy, s)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{a[0] - 5 * s:.1f}" y2="{a[1] + 6 * s:.1f}" stroke="{t["muted"]}" stroke-width="{2.2 * s:.1f}"/>'
                   f'<line x1="{b[0]:.1f}" y1="{b[1]:.1f}" x2="{b[0] + 5 * s:.1f}" y2="{b[1] + 6 * s:.1f}" stroke="{t["muted"]}" stroke-width="{2.2 * s:.1f}"/>')
    out.append(iso_box(0, 0, 0, 92, 92, 16, ox, oy, s, t["panel"], t["bg2"], t["line"], t["line2"]))
    die = [iso(26, 26, 16, ox, oy, s), iso(66, 26, 16, ox, oy, s), iso(66, 66, 16, ox, oy, s), iso(26, 66, 16, ox, oy, s)]
    out.append(f'<polygon class="s" points="{poly(die)}" fill="{t["accent"]}" opacity=".3"/>')
    out.append(f'<polygon class="m" points="{poly(die)}" fill="{t["accent"]}" opacity=".12">'
               + anim("opacity", (0, .12), (1.5, .12), (1.8, .95), (2.6, .35), (7.4, .35), (7.8, .12)) + '</polygon>')
    c = iso(46, 46, 16, ox, oy, s)
    out.append(svg.text(c[0], c[1] + 4 * s, "MCU", "mono", 12 * s, t["fg"], "middle", 2))
    return "".join(out)


def stage_tokens(svg, t, cx, cy, s):
    """03: bytes -> tokens: 3 x 3 cubes appear one after another."""
    out = []
    cols = [t["ai"], t["accent"], t["live"]]
    ox, oy = cx - 4 * s, cy - 12 * s
    order = [(i, j) for j in range(3) for i in range(3)]
    for n, (i, j) in enumerate(order):
        col = cols[(i + j) % 3]
        box = iso_box(i * 24, j * 24, 0, 20, 20, 16 + ((i * 7 + j * 3) % 3) * 6, ox, oy, s * .9, col, t["line2"], t["bg2"], t["panel"])
        t0 = 2.0 + n * 0.11
        out.append(f'<g class="m" opacity="0">{box}' + anim("opacity", (0, 0), (t0, 0), (t0 + .15, 1), (7.4, 1), (7.8, 0)) + '</g>')
        out.append(f'<g class="s">{box}</g>')
    if s < 1.1:
        out.append(svg.text(cx, cy - 54 * s, "0x43 0x41 0x4E", "mono", 10.5 * s, t["muted"], "middle"))
    return "".join(out)


NET = [3, 4, 4, 2]


def stage_net(svg, t, cx, cy, s):
    """04: a layered network in columns with slight depth; an activation wave sweeps layer by layer."""
    pos = []
    for li, n in enumerate(NET):
        x = cx - 96 * s + li * 64 * s
        for k in range(n):
            y = cy - (n - 1) * 26 * s / 2 + k * 26 * s
            dz = (k - (n - 1) / 2) * 7 * s               # back nodes shift up-right and shrink a little
            pos.append((li, x + dz * .8, y - dz * .45, 1 - .08 * abs(k - (n - 1) / 2)))
    out = []
    for a in pos:
        for b in pos:
            if b[0] == a[0] + 1:
                ta = 3.0 + a[0] * .5
                v, k_ = kt((0, .22), (ta, .22), (ta + .25, .8), (ta + .7, .22))
                out.append(f'<line x1="{a[1]:.1f}" y1="{a[2]:.1f}" x2="{b[1]:.1f}" y2="{b[2]:.1f}" stroke="{t["ai"]}" stroke-width="{1.1 * s:.1f}" stroke-opacity=".22">'
                           f'<animate class="m" attributeName="stroke-opacity" values="{v}" keyTimes="{k_}" dur="{LOOP}s" repeatCount="indefinite"/></line>')
    for li, x, y, k in pos:
        ta = 3.0 + li * .5
        r = 8.5 * s * k
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{t["panel"]}" stroke="{t["ai"]}" stroke-width="{2.2 * s:.1f}"/>')
        out.append(f'<circle class="m" cx="{x:.1f}" cy="{y:.1f}" r="{r * .62:.1f}" fill="{t["accent"]}" opacity="0">'
                   + anim("opacity", (0, 0), (ta, 0), (ta + .2, 1), (ta + .9, .35), (7.4, .35), (7.8, 0)) + '</circle>')
        out.append(f'<circle class="s" cx="{x:.1f}" cy="{y:.1f}" r="{r * .62:.1f}" fill="{t["accent"]}" opacity=".35"/>')
    return "".join(out)


def stage_doc(svg, t, cx, cy, s):
    """05: an upright document with depth; the answer writes itself, then [1] [2] appear."""
    w, h, sk = 130 * s, 150 * s, 14 * s
    x0, y0 = cx - w / 2, cy - h / 2 - 6 * s
    side = [(x0 + w, y0), (x0 + w + sk, y0 - sk * .6), (x0 + w + sk, y0 + h - sk * .6), (x0 + w, y0 + h)]
    topf = [(x0, y0), (x0 + sk, y0 - sk * .6), (x0 + w + sk, y0 - sk * .6), (x0 + w, y0)]
    out = [f'<polygon points="{poly(side)}" fill="{t["line2"]}"/><polygon points="{poly(topf)}" fill="{t["line"]}"/>',
           f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{6 * s:.1f}" fill="{t["panel"]}" stroke="{t["line2"]}" stroke-width="1.4"/>',
           svg.text(x0 + 12 * s, y0 + 24 * s, "answer", "mono", 11 * s, t["liveText"], ls=1)]
    for i, f in enumerate([.82, .7, .78, .5]):
        ly, lw = y0 + (44 + i * 16) * s, round((w - 24 * s) * f, 1)
        t0 = 5.0 + i * .28
        out.append(f'<rect class="s" x="{x0 + 12 * s:.1f}" y="{ly:.1f}" width="{lw}" height="{5 * s:.1f}" rx="2" fill="{t["muted"]}" opacity=".6"/>')
        out.append(f'<rect class="m" x="{x0 + 12 * s:.1f}" y="{ly:.1f}" width="0" height="{5 * s:.1f}" rx="2" fill="{t["muted"]}" opacity=".6">'
                   + anim("width", (0, 0), (t0, 0), (t0 + .3, lw), (7.4, lw), (7.8, 0)) + '</rect>')
    for i, lab in enumerate(("[1]", "[2]")):
        px, py = x0 + 12 * s + i * 40 * s, y0 + h - 30 * s
        pill = (f'<rect x="{px:.1f}" y="{py:.1f}" width="{32 * s:.1f}" height="{18 * s:.1f}" rx="{9 * s:.1f}" fill="none" stroke="{t["accent"]}" stroke-width="1.4"/>'
                + svg.text(px + 6 * s, py + 13 * s, lab, "mono", 11 * s, t["accentText"]))
        t0 = 6.25 + i * .2
        out.append(f'<g class="s">{pill}</g><g class="m" opacity="0">{pill}' + anim("opacity", (0, 0), (t0, 0), (t0 + .15, 1), (7.4, 1), (7.8, 0)) + '</g>')
    return "".join(out)


def connector(t, a, b, t0, s, vertical=False):
    """Dashed link between two stages; a packet dot travels it at time t0."""
    (x1, y1), (x2, y2) = a, b
    out = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{t["line2"]}" stroke-width="{1.6 * s:.1f}" stroke-dasharray="4 5"/>'
    if vertical:
        hd = f"M{x2 - 6 * s:.1f},{y2 - 8 * s:.1f} L{x2:.1f},{y2:.1f} L{x2 + 6 * s:.1f},{y2 - 8 * s:.1f}"
    else:
        hd = f"M{x2 - 8 * s:.1f},{y2 - 6 * s:.1f} L{x2:.1f},{y2:.1f} L{x2 - 8 * s:.1f},{y2 + 6 * s:.1f}"
    out += f'<path d="{hd}" fill="none" stroke="{t["line2"]}" stroke-width="{1.8 * s:.1f}"/>'
    out += (f'<circle class="m" r="{4.2 * s:.1f}" cx="{x1:.1f}" cy="{y1:.1f}" fill="{t["accent"]}" opacity="0">'
            + anim("cx", (0, round(x1, 1)), (t0, round(x1, 1)), (t0 + .45, round(x2, 1)), (t0 + .46, round(x1, 1)))
            + anim("cy", (0, round(y1, 1)), (t0, round(y1, 1)), (t0 + .45, round(y2, 1)), (t0 + .46, round(y1, 1)))
            + anim("opacity", (0, 0), (t0, 0), (t0 + .05, 1), (t0 + .45, 1), (t0 + .46, 0)) + '</circle>')
    return out


STAGES = [("01", "CAN FD bits", stage_bus, "accentText"), ("02", "decode", stage_mcu, "accentText"), ("03", "embed", stage_tokens, "aiText"),
          ("04", "reason", stage_net, "aiText"), ("05", "answer + sources", stage_doc, "liveText")]
LINK_T = [1.25, 1.75, 2.75, 4.6]                 # when the packet crosses each link


def frame(svg, t, W, H):
    svg.defs.append(f'<radialGradient id="glow" cx="78%" cy="75%" r="60%"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"]}"/>'
                    f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>'
                    f'<pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{t["line"]}"/></pattern>'
                    f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    svg.add(f'<g clip-path="url(#clip)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/><rect width="{W}" height="{H}" fill="url(#dots)" opacity=".7"/>'
            f'<rect width="{W}" height="{H}" fill="url(#glow)"/>')


def build(mode, t):
    W, H = 1280, 470
    svg = Svg(W, H, "Moutaz Mohammad, embedded engineer building intelligent systems, from CAN bits to RAG pipelines. "
                    "Animation in five stages: a CAN FD frame is decoded by a microcontroller, its bytes become tokens, "
                    "a layered network reasons over them, and an answer with sources is written.", t)
    frame(svg, t, W, H)
    svg.add(svg.text(64, 70, "● WOLFENBÜTTEL, GERMANY", "mono", 13, t["accentText"], ls=3))
    svg.add(svg.text(60, 132, "Moutaz Mohammad", "display", 60, t["fg"]))
    svg.add(svg.text(64, 174, "Embedded engineer building intelligent systems", "body", 23, t["fg"]))
    svg.add(svg.text(64, 206, "from CAN bits to RAG pipelines.", "body", 23, t["accentText"]))
    svg.add(f'<line x1="64" y1="238" x2="{W - 64}" y2="238" stroke="{t["line"]}" stroke-width="1"/>')
    xs, cy = [150, 400, 600, 812, 1090], 330
    for i, (num, lab, fn, col) in enumerate(STAGES):
        svg.add(fn(svg, t, xs[i], cy, 1.0))
        svg.add(svg.text(xs[i], 446, f"{num}  {lab}", "mono", 13, t[col], "middle", 1.5))
    ends = [(250, cy), (334, cy), (474, cy), (540, cy), (668, cy), (704, cy), (922, cy), (1012, cy)]
    for i in range(4):
        svg.add(connector(t, ends[2 * i], ends[2 * i + 1], LINK_T[i], 1.0))
    svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="21.5" fill="none" stroke="{t["line2"]}" stroke-width="1.5"/></g>')
    return svg.render()


def build_m(mode, t):
    W, H = 640, 1130
    svg = Svg(W, H, "Moutaz Mohammad, embedded engineer building intelligent systems, from CAN bits to RAG pipelines, in five stages.", t)
    frame(svg, t, W, H)
    svg.add(svg.text(34, 58, "● WOLFENBÜTTEL, GERMANY", "mono", 18, t["accentText"], ls=2.5))
    svg.add(svg.text(30, 122, "Moutaz Mohammad", "display", 58, t["fg"]))
    svg.add(svg.text(34, 170, "Embedded engineer building", "body", 28, t["fg"]))
    svg.add(svg.text(34, 206, "intelligent systems", "body", 28, t["fg"]))
    svg.add(svg.text(34, 246, "from CAN bits to RAG pipelines.", "body", 28, t["accentText"]))
    svg.add(f'<line x1="34" y1="276" x2="{W - 34}" y2="276" stroke="{t["line"]}"/>')
    ys = [345, 505, 690, 855, 1025]
    for i, (num, lab, fn, col) in enumerate(STAGES):
        svg.add(fn(svg, t, 400, ys[i], 1.25 if i != 4 else 1.05))
        svg.add(svg.text(34, ys[i] - 30, num, "mono", 22, t[col], ls=2))
        svg.add(svg.text(34, ys[i], lab, "mono", 20, t[col], ls=1.5))
    links = [((400, 418), (400, 446)), ((400, 588), (400, 632)), ((400, 742), (400, 800)), ((400, 912), (400, 932))]
    for i, (a, b) in enumerate(links):
        svg.add(connector(t, a, b, LINK_T[i], 1.2, vertical=True))
    svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="21.5" fill="none" stroke="{t["line2"]}" stroke-width="1.5"/></g>')
    return svg.render()


def main():
    for mode, t in THEMES.items():
        p, n = write("hero", mode, build(mode, t))
        print(f"{p}: {n / 1024:.0f} KB")
        p, n = write("hero-m", mode, build_m(mode, t))
        print(f"{p}: {n / 1024:.0f} KB")


if __name__ == "__main__":
    main()
