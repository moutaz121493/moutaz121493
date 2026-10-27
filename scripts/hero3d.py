#!/usr/bin/env python3
"""3D hero: CAN bits -> RAG pipelines.

A twisted pair (CAN_H / CAN_L) carries a CAN FD frame into a slowly rotating 3D neural network.
Everything is real 3D maths, precomputed: rotate -> perspective-project -> one SMIL keyframe per frame.
Loop: 36 s for one full turn of the network; the frame + pulse burst repeats every 6 s inside it,
so every animation loops seamlessly. Deterministic (fixed seed).
"""
import math
import random

from svglib import Svg, THEMES, vals, write

W, H = 1280, 400
LOOP = 36.0            # one full rotation
N = 72                 # rotation keyframes (0.5 s)
NP = 144               # pulse keyframes (0.25 s)
BURST = 6.0            # a frame arrives every 6 s
TRAVEL = 2.0           # seconds the frame takes along the bus
CX, CY, S, D = 1000, 186, 96, 5.6       # net centre on screen, scale, camera distance
YAW, TILT = 0.42, 0.20
HZ, BUS0, LABEL, NETLAB_Y = 205, (600, 318), 1.0, 360   # floor horizon, bus start, label scale, net caption y                   # fixed view angles (rad): look at the layers from the side and a bit above
LAYERS = [(4, 0.75), (6, 1.10), (6, 1.10), (3, 0.62)]   # (nodes, ring radius)


def net_nodes():
    pts = []
    for li, (n, r) in enumerate(LAYERS):
        x = -1.95 + li * 1.3
        for k in range(n):
            a = 2 * math.pi * k / n + li * 0.45
            pts.append((li, (x, r * math.cos(a), r * math.sin(a))))
    return pts


def project(p, ang):
    x, y, z = p
    # spin around the layer axis (x) like a drum, then a fixed yaw (y) and tilt (x) for the 3D view;
    # the layers stay ordered input -> output from left to right
    y, z = y * math.cos(ang) - z * math.sin(ang), y * math.sin(ang) + z * math.cos(ang)
    x, z = x * math.cos(YAW) + z * math.sin(YAW), -x * math.sin(YAW) + z * math.cos(YAW)
    y, z = y * math.cos(TILT) - z * math.sin(TILT), y * math.sin(TILT) + z * math.cos(TILT)
    k = D / (D + z)
    return CX + S * x * k, CY - S * y * k, k, z


def depth(z):
    """near = 1, far = 0"""
    return max(0.0, min(1.0, (1.6 - z) / 3.2))


def floor(svg, t):
    """Perspective grid floor + PCB traces fading into the distance (static camera)."""
    hz, fy = HZ, 1.9            # horizon y on screen, floor height below camera
    def fp(x, z):                # floor point (world x, depth z>0) -> screen
        return W / 2 + 330 * x / z, hz + 330 * fy / z / 3.4
    out = []
    for i in range(-14, 15):
        x = i * 0.9
        a, b = fp(x, 1.0), fp(x, 14)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{t["line"]}" stroke-width="1"/>')
    for j, z in enumerate([1.0, 1.25, 1.6, 2.1, 2.8, 3.8, 5.2, 7.4, 10.5, 14]):
        a, b = fp(-14, z), fp(14, z)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{t["line"]}" stroke-width="{1.1 - j * .07:.2f}"/>')
    rnd = random.Random(11)
    pulses = []
    for i in range(7):
        x, z = rnd.uniform(-4, 4), 1.1
        pts = [fp(x, z)]
        for _ in range(4):
            if rnd.random() < .55:
                z *= rnd.uniform(1.4, 1.9)
            else:
                x += rnd.choice([-1, 1]) * rnd.uniform(.6, 1.6)
            pts.append(fp(x, z))
        d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        out.append(f'<path d="{d}" fill="none" stroke="{t["trace"]}" stroke-width="1.4" opacity=".55"/>')
        out.append(f'<circle cx="{pts[0][0]:.1f}" cy="{pts[0][1]:.1f}" r="3" fill="none" stroke="{t["trace"]}" stroke-width="1.3" opacity=".7"/>')
        if i % 2 == 0:
            dur = 4 + i
            pulses.append(f'<circle r="2.2" fill="{t["accent"]}"><animateMotion dur="{dur}s" repeatCount="indefinite" path="{d}"/>'
                          f'<animate attributeName="opacity" values="0;1;1;0" dur="{dur}s" repeatCount="indefinite"/></circle>')
    svg.defs.append(f'<linearGradient id="fl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["bg"]}" stop-opacity="1"/>'
                    f'<stop offset=".35" stop-color="{t["bg"]}" stop-opacity=".2"/><stop offset="1" stop-color="{t["bg"]}" stop-opacity=".55"/></linearGradient>')
    svg.add(f'<g opacity=".9">{"".join(out)}<g class="m">{"".join(pulses)}</g></g>'
            f'<rect x="0" y="{hz}" width="{W}" height="{H - hz}" fill="url(#fl)"/>')


def bus(svg, t, entry):
    """Twisted pair from the lower left into the first network layer; the twist flows towards the net."""
    x0, y0 = BUS0
    x1, y1 = entry
    n, turns, amp = 70, 5.5, 9.0
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    nx, ny = -dy / ln, dx / ln
    def wire(phase, sign):
        pts = []
        for i in range(n + 1):
            s = i / n
            a = 2 * math.pi * turns * s - phase
            off = sign * amp * math.cos(a) * (0.35 + 0.65 * math.sin(math.pi * min(1, s * 1.15)))
            pts.append((x0 + dx * s + nx * off, y0 + dy * s + ny * off))
        return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    F = 24
    for sign, col, lab in ((1, t["accent"], "CAN_H"), (-1, t["ai"], "CAN_L")):
        frames = [wire(2 * math.pi * f / F, sign) for f in range(F)]
        svg.add(f'<path class="m" d="{frames[0]}" fill="none" stroke="{col}" stroke-width="2.4" stroke-linecap="round" opacity=".9">'
                f'<animate attributeName="d" values="{";".join(frames + frames[:1])}" dur="1.6s" repeatCount="indefinite"/></path>'
                f'<path class="s" d="{frames[0]}" fill="none" stroke="{col}" stroke-width="2.4" opacity=".9"/>')
    svg.add(svg.text(x0 - 8, y0 + 4, "CAN_H", "mono", 11 * LABEL, t["accentText"], "end", 1.5)
            + svg.text(x0 - 8, y0 + 4 + 16 * LABEL, "CAN_L", "mono", 11 * LABEL, t["aiText"], "end", 1.5))
    # the CAN FD frame: a glowing capsule with its bits, travelling along the bus every BURST seconds
    centre = f"M{x0},{y0} L{x1:.1f},{y1:.1f}"
    bits = "".join(f'<rect x="{-22 + i * 6}" y="-4" width="4" height="8" rx="1" fill="{t["bg"]}" opacity="{.9 if b else .35}"/>'
                   for i, b in enumerate([1, 0, 1, 1, 0, 1, 0, 0]))
    kt = f"0;{TRAVEL / BURST:.3f};1"
    svg.add(f'<g class="m" opacity="0"><rect x="-30" y="-9" width="60" height="18" rx="9" fill="{t["accent"]}"/>{bits}'
            f'<animateMotion dur="{BURST}s" repeatCount="indefinite" path="{centre}" keyPoints="0;1;1" keyTimes="{kt}" calcMode="linear"/>'
            f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.04;{TRAVEL / BURST - .03:.3f};{TRAVEL / BURST:.3f};1" dur="{BURST}s" repeatCount="indefinite"/></g>')
    svg.add(svg.text(x0 + 40, y0 + 34, "CAN FD frame → network input", "mono", 11 * LABEL, t["muted"], ls=1))


def network(svg, t):
    nodes = net_nodes()
    idx = {}
    for i, (li, _) in enumerate(nodes):
        idx.setdefault(li, []).append(i)
    edges = [(a, b) for li in range(len(LAYERS) - 1) for a in idx[li] for b in idx[li + 1]]
    angs = [2 * math.pi * f / N for f in range(N)]
    P = [[project(p, a) for a in angs] for _, p in nodes]     # P[node][frame] = (x, y, k, z)
    # edges (depth-shaded)
    eg, st = [], []
    for a, b in edges:
        xs1 = [P[a][f][0] for f in range(N)]
        ys1 = [P[a][f][1] for f in range(N)]
        xs2 = [P[b][f][0] for f in range(N)]
        ys2 = [P[b][f][1] for f in range(N)]
        op = [0.06 + 0.32 * depth((P[a][f][3] + P[b][f][3]) / 2) for f in range(N)]
        eg.append(f'<line x1="{xs1[0]:.1f}" y1="{ys1[0]:.1f}" x2="{xs2[0]:.1f}" y2="{ys2[0]:.1f}" stroke="{t["ai"]}" stroke-width="1" stroke-opacity="{op[0]:.2f}">'
                  f'<animate attributeName="x1" values="{vals(xs1)}" dur="{LOOP}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="y1" values="{vals(ys1)}" dur="{LOOP}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="x2" values="{vals(xs2)}" dur="{LOOP}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="y2" values="{vals(ys2)}" dur="{LOOP}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="stroke-opacity" values="{vals(op, 2)}" dur="{LOOP}s" repeatCount="indefinite"/></line>')
        st.append(f'<line x1="{xs1[0]:.1f}" y1="{ys1[0]:.1f}" x2="{xs2[0]:.1f}" y2="{ys2[0]:.1f}" stroke="{t["ai"]}" stroke-width="1" stroke-opacity="{op[0]:.2f}"/>')
    # pulses: in each burst, 5 signals run input -> output after the frame arrives
    rnd = random.Random(4)
    tp = [LOOP * f / NP for f in range(NP)]
    def pos(node, tt):                    # exact projection at time tt
        return project(nodes[node][1], 2 * math.pi * tt / LOOP)
    glow = {i: [0.0] * NP for i in range(len(nodes))}
    pulses = []
    for p in range(5):
        xs, ys, ops = [], [], []
        routes = [[rnd.choice(idx[li]) for li in range(len(LAYERS))] for _ in range(int(LOOP / BURST))]
        for f, tt in enumerate(tp):
            b = int(tt // BURST)
            u = (tt - b * BURST - TRAVEL - p * 0.12) / 2.4      # 0..1 across the 3 hops
            if 0 <= u <= 1:
                seg = min(2, int(u * 3))
                v = u * 3 - seg
                r = routes[b]
                a_, c_ = pos(r[seg], tt), pos(r[seg + 1], tt)
                xs.append(a_[0] + (c_[0] - a_[0]) * v)
                ys.append(a_[1] + (c_[1] - a_[1]) * v)
                ops.append(1.0)
                near = r[seg] if v < .5 else r[seg + 1]
                glow[near][f] = max(glow[near][f], 1 - abs(v - (0 if v < .5 else 1)) * 2)
            else:
                xs.append(CX)
                ys.append(CY)
                ops.append(0.0)
        pulses.append(f'<circle r="3.4" fill="{t["accent"]}" opacity="0">'
                      f'<animate attributeName="cx" values="{vals(xs)}" dur="{LOOP}s" repeatCount="indefinite"/>'
                      f'<animate attributeName="cy" values="{vals(ys)}" dur="{LOOP}s" repeatCount="indefinite"/>'
                      f'<animate attributeName="opacity" values="{vals(ops, 0)}" dur="{LOOP}s" repeatCount="indefinite" calcMode="discrete"/></circle>')
    # nodes: far = smaller and fainter; glow halo when a pulse passes
    nd, nst = [], []
    for i in range(len(nodes)):
        xs = [P[i][f][0] for f in range(N)]
        ys = [P[i][f][1] for f in range(N)]
        rs = [4.5 + 4.5 * P[i][f][2] ** 2 for f in range(N)]
        op = [0.35 + 0.65 * depth(P[i][f][3]) for f in range(N)]
        common = (f'<animate attributeName="cx" values="{vals(xs)}" dur="{LOOP}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="cy" values="{vals(ys)}" dur="{LOOP}s" repeatCount="indefinite"/>')
        g = [0.0] + [max(glow[i][f - 1], glow[i][f]) for f in range(1, NP)]
        nd.append(f'<circle cx="{xs[0]:.1f}" cy="{ys[0]:.1f}" r="16" fill="url(#halo)" opacity="0">{common}'
                  f'<animate attributeName="opacity" values="{vals(g, 2)}" dur="{LOOP}s" repeatCount="indefinite"/></circle>')
        nd.append(f'<circle cx="{xs[0]:.1f}" cy="{ys[0]:.1f}" r="{rs[0]:.1f}" fill="{t["panel"]}" stroke="{t["ai"]}" stroke-width="2" opacity="{op[0]:.2f}">{common}'
                  f'<animate attributeName="r" values="{vals(rs)}" dur="{LOOP}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="{vals(op, 2)}" dur="{LOOP}s" repeatCount="indefinite"/></circle>')
        nst.append(f'<circle cx="{xs[0]:.1f}" cy="{ys[0]:.1f}" r="{rs[0]:.1f}" fill="{t["panel"]}" stroke="{t["ai"]}" stroke-width="2" opacity="{op[0]:.2f}"/>')
    svg.defs.append(f'<radialGradient id="halo"><stop offset="0" stop-color="{t["accent"]}" stop-opacity=".9"/>'
                    f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>')
    svg.add(f'<g class="m">{"".join(eg)}{"".join(nd)}{"".join(pulses)}</g><g class="s">{"".join(st)}{"".join(nst)}</g>')
    first = [P[i][0] for i in idx[0]]
    entry = (sum(p[0] for p in first) / len(first) - 34, sum(p[1] for p in first) / len(first) + 22)
    svg.add(svg.text(CX - 30 * LABEL, NETLAB_Y, "NEURAL NETWORK · RAG", "mono", 11 * LABEL, t["muted"], ls=1.5))
    return entry


def build(mode, t):
    svg = Svg(W, H, "Moutaz Mohammad, embedded engineer building intelligent systems, from CAN bits to RAG pipelines. "
                    "Animation: a CAN FD frame travels along a twisted pair into a rotating 3D neural network.", t)
    svg.defs.append(f'<radialGradient id="glow" cx="80%" cy="42%" r="55%"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"]}"/>'
                    f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>'
                    f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{t["bg"]}" stop-opacity=".97"/>'
                    f'<stop offset=".42" stop-color="{t["bg"]}" stop-opacity=".75"/><stop offset=".6" stop-color="{t["bg"]}" stop-opacity="0"/></linearGradient>'
                    f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    svg.add(f'<g clip-path="url(#clip)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>')
    floor(svg, t)
    svg.add(f'<rect width="{W}" height="{H}" fill="url(#glow)"/>')
    # network first (to know where the bus enters), but drawn after the bus so it sits on top
    tmp = Svg(W, H, "", t)
    entry = network(tmp, t)
    bus(svg, t, entry)
    svg.parts += tmp.parts
    svg.defs += tmp.defs
    for k in svg.chars:
        svg.chars[k] |= tmp.chars[k]
    svg.add(f'<rect width="{W * .62:.0f}" height="{H}" fill="url(#fade)"/>')
    # crisp 2D text on top
    svg.add(svg.text(64, 92, "● WOLFENBÜTTEL, GERMANY", "mono", 13, t["accentText"], ls=3))
    svg.add(svg.text(60, 162, "Moutaz Mohammad", "display", 62, t["fg"]))
    svg.add(svg.text(64, 208, "Embedded engineer building intelligent systems", "body", 24, t["fg"]))
    svg.add(svg.text(64, 242, "from CAN bits to RAG pipelines.", "body", 24, t["accentText"]))
    x = 64
    for lab in ("AUTOMOTIVE NETWORKS", "LINUX & INFRASTRUCTURE", "APPLIED AI"):
        wch = len(lab) * 8.7 + 28
        svg.add(f'<rect x="{x}" y="272" width="{wch:.0f}" height="30" rx="15" fill="{t["panel"]}" stroke="{t["line2"]}"/>')
        svg.add(svg.text(x + 14, 292, lab, "mono", 12.5, t["muted"], ls=1))
        x += wch + 10
    svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="21.5" fill="none" stroke="{t["line2"]}" stroke-width="1.5"/></g>')
    return svg.render()


def build_m(mode, t):
    """Phone hero (640 x 600): text on top, the same 3D scene below it."""
    global W, H, CX, CY, S, HZ, BUS0, LABEL, NETLAB_Y
    saved = (W, H, CX, CY, S, HZ, BUS0, LABEL, NETLAB_Y)
    W, H, CX, CY, S, HZ, BUS0, LABEL, NETLAB_Y = 640, 600, 420, 410, 82, 380, (150, 520), 1.6, 578
    try:
        svg = Svg(W, H, "Moutaz Mohammad, embedded engineer building intelligent systems, from CAN bits to RAG pipelines.", t)
        svg.defs.append(f'<radialGradient id="glow" cx="65%" cy="68%" r="60%"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"]}"/>'
                        f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></radialGradient>'
                        f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["bg"]}" stop-opacity=".97"/>'
                        f'<stop offset=".38" stop-color="{t["bg"]}" stop-opacity=".8"/><stop offset=".5" stop-color="{t["bg"]}" stop-opacity="0"/></linearGradient>'
                        f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
        svg.add(f'<g clip-path="url(#clip)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>')
        floor(svg, t)
        svg.add(f'<rect width="{W}" height="{H}" fill="url(#glow)"/>')
        tmp = Svg(W, H, "", t)
        entry = network(tmp, t)
        bus(svg, t, entry)
        svg.parts += tmp.parts
        svg.defs += tmp.defs
        for k in svg.chars:
            svg.chars[k] |= tmp.chars[k]
        svg.add(f'<rect width="{W}" height="{H}" fill="url(#fade)"/>')
        svg.add(svg.text(34, 58, "● WOLFENBÜTTEL, GERMANY", "mono", 18, t["accentText"], ls=2.5))
        svg.add(svg.text(30, 122, "Moutaz Mohammad", "display", 58, t["fg"]))
        svg.add(svg.text(34, 170, "Embedded engineer building", "body", 28, t["fg"]))
        svg.add(svg.text(34, 206, "intelligent systems", "body", 28, t["fg"]))
        svg.add(svg.text(34, 246, "from CAN bits to RAG pipelines.", "body", 28, t["accentText"]))
        svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="21.5" fill="none" stroke="{t["line2"]}" stroke-width="1.5"/></g>')
        return svg.render()
    finally:
        W, H, CX, CY, S, HZ, BUS0, LABEL, NETLAB_Y = saved


def main():
    for mode, t in THEMES.items():
        p, n = write("hero", mode, build(mode, t))
        print(f"{p}: {n / 1024:.0f} KB")
        p, n = write("hero-m", mode, build_m(mode, t))
        print(f"{p}: {n / 1024:.0f} KB")


if __name__ == "__main__":
    main()
