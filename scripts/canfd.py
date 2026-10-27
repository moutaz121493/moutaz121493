#!/usr/bin/env python3
"""Animated CAN FD decoder strip: one real CAN FD base-format frame scrolls past, bit by bit, with every field labelled.

Bit layout (ISO 11898-1:2015, CAN FD base frame format, FBFF), in transmit order:
  SOF 1 (dominant) | ID 11 | RRS 1 (d) | IDE 1 (d) | FDF 1 (r) | res 1 (d) | BRS 1 (r) | ESI 1 (d, error active)
  | DLC 4 | DATA 0..64 bytes
  | stuff count: 3 bits Gray-coded (dynamic stuff bits mod 8) + 1 even-parity bit
  | CRC 17 (data <= 16 bytes; CRC 21 above) | CRC delimiter 1 (r) | ACK slot 1 | ACK delimiter 1 (r) | EOF 7 (r)
Stuffing:
  - dynamic: from SOF to the end of the data field, after 5 equal bits a complementary stuff bit is inserted;
  - fixed: in the CRC field (stuff count + CRC sequence) a fixed stuff bit (complement of the previous bit) is
    inserted before the first stuff-count bit and after every 4 bits; no dynamic stuffing there.
CRC-17: polynomial 0x3685B (x^17+x^16+x^14+x^13+x^11+x^6+x^4+x^3+x+1), register initialised with a 1 in the MSB
  (ISO 11898-1:2015). It covers SOF .. data field INCLUDING the dynamic stuff bits, plus the stuff count + parity;
  fixed stuff bits are not part of it.
Bit rate switch: nominal rate up to the sample point of BRS, data rate from there to the sample point of the CRC
  delimiter. Drawn here with nominal 500 kbit/s and data 2 Mbit/s (x4), sample points 80 % (nominal) / 75 % (data).
The ACK slot is drawn dominant: a receiver acknowledged the frame.
"""
from svglib import Svg, THEMES, write

FRAME_ID = 0x4D4
PAYLOAD = b"CAN FD > RAG"            # 12 bytes -> DLC 9
DLC_FOR = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 12: 9, 16: 10, 20: 11, 24: 12, 32: 13, 48: 14, 64: 15}
CRC17_POLY = 0x3685B
TN, TD = 24.0, 6.0                   # px per nominal / data bit
SPN, SPD = 0.80, 0.75                # sample points


def bits(v, n):
    return [(v >> (n - 1 - i)) & 1 for i in range(n)]


def crc17(stream):
    crc = 1 << 16
    for b in stream:
        top = (crc >> 16) & 1
        crc = (crc << 1) & 0x1FFFF
        if b ^ top:
            crc ^= CRC17_POLY & 0x1FFFF
    return crc


def build_frame():
    """-> list of (bit, field, kind) with kind in {'', 'stuff', 'fixed'}; plus facts for the labels."""
    dlc = DLC_FOR[len(PAYLOAD)]
    fields = [("SOF", [0]), ("ID", bits(FRAME_ID, 11)), ("RRS", [0]), ("IDE", [0]), ("FDF", [1]), ("res", [0]),
              ("BRS", [1]), ("ESI", [0]), ("DLC", bits(dlc, 4))]
    fields += [(f"D{i}", bits(b, 8)) for i, b in enumerate(PAYLOAD)]
    out, run_v, run_n, nstuff = [], None, 0, 0
    total = sum(len(bl) for _, bl in fields)
    k = 0
    for name, bl in fields:                       # dynamic stuffing SOF .. end of data
        for b in bl:
            k += 1
            out.append((b, name, ""))
            run_n = run_n + 1 if b == run_v else 1
            run_v = b
            if run_n == 5 and k < total:          # after the last data bit the fixed stuff bit takes this role
                out.append((1 - b, name, "stuff"))
                nstuff += 1
                run_v, run_n = 1 - b, 1
    gray = (nstuff % 8) ^ ((nstuff % 8) >> 1)
    sc = bits(gray, 3)
    sc.append(sum(sc) % 2)                        # even parity over the 4 bits
    crc = crc17([b for b, _, _ in out] + sc)      # dynamic stuff bits included, fixed ones not
    crc_bits = [("SBC", b) for b in sc] + [("CRC", b) for b in bits(crc, 17)]
    for i, (name, b) in enumerate(crc_bits):     # fixed stuff bits: before the first, then after every 4
        if i % 4 == 0:
            out.append((1 - out[-1][0], name, "fixed"))
        out.append((b, name, ""))
    out += [(1, "CRC del", ""), (0, "ACK", ""), (1, "ACK del", "")] + [(1, "EOF", "")] * 7
    return out, {"dlc": dlc, "stuff": nstuff, "gray": gray, "crc": crc}


def widths(frame):
    """Bit widths with the rate switch at the BRS / CRC-delimiter sample points."""
    ws, fast = [], False
    for b, name, kind in frame:
        if name == "BRS":
            ws.append(TN * SPN + TD * (1 - SPD))
            fast = True
        elif name == "CRC del":
            ws.append(TD * SPD + TN * (1 - SPN))
            fast = False
        else:
            ws.append(TD if fast else TN)
    return ws


FIELD_COL = {"SOF": "muted", "ID": "accent", "RRS": "muted", "IDE": "muted", "FDF": "ai", "res": "muted", "BRS": "ai",
             "ESI": "muted", "DLC": "live", "SBC": "muted", "CRC": "accent", "CRC del": "muted", "ACK": "live",
             "ACK del": "muted", "EOF": "muted"}


def group_fields(frame, xs, ws):
    """Consecutive bits of one field (data bytes merged into DATA) -> [(label, x0, x1, colour key)]."""
    out = []
    for (b, name, kind), x, w in zip(frame, xs, ws):
        key = "DATA" if name.startswith("D") and name not in ("DLC",) else name
        if out and out[-1][0] == key:
            out[-1][2] = x + w
        else:
            out.append([key, x, x + w])
    return out


def build(mode, t, frame, facts, W=1280, fs=1.0):
    H = int(236 + 60 * (fs - 1))
    ws = widths(frame)
    dy = 50 * (fs - 1)
    xs, x = [], 0.0
    for w in ws:
        xs.append(x)
        x += w
    total = x
    hi, lo = 112, 150                              # recessive (1) high, dominant (0) low
    d = [f"M0,{hi if frame[0][0] else lo}"]
    for (b, _, _), x0, w in zip(frame, xs, ws):
        y = hi if b else lo
        d.append(f"L{x0:.1f},{y} L{x0 + w:.1f},{y}")
    wave = "".join(d)
    fields = group_fields(frame, xs, ws)
    data_label = f'DATA · 12 bytes "{PAYLOAD.decode()}"'
    labels = {"ID": f"ID 0x{FRAME_ID:03X}", "DLC": f"DLC {facts['dlc']} (12 B)", "DATA": data_label,
              "SBC": f"stuff count {facts['stuff']} → {facts['gray']:03b}+P", "CRC": f"CRC-17 0x{facts['crc']:05X}",
              "BRS": "BRS", "FDF": "FDF", "EOF": "EOF", "ACK": "ACK", "SOF": "SOF"}
    svg = Svg(W, H, f"CAN FD frame decoder: base frame, ID 0x{FRAME_ID:03X}, {len(PAYLOAD)} data bytes \"{PAYLOAD.decode()}\", "
                    f"bit rate switch from 500 kbit/s to 2 Mbit/s, {facts['stuff']} dynamic stuff bits, CRC-17 0x{facts['crc']:05X}", t)
    g = []
    for key, a, b in fields:
        col = FIELD_COL.get(key, "live" if key == "DATA" else "muted")
        g.append(f'<rect x="{a:.1f}" y="92" width="{b - a - 1:.1f}" height="78" fill="{t[col]}" opacity=".07"/>'
                 f'<line x1="{a:.1f}" y1="84" x2="{a:.1f}" y2="178" stroke="{t["line2"]}" stroke-width="1"/>')
        lab = labels.get(key)
        if lab and (b - a) >= len(lab) * 6.6 * fs + 6 or key in (("BRS", "FDF", "ACK", "SOF") if W > 900 else ("BRS", "FDF", "ACK")):
            g.append(svg.text(a + 3, 80, lab or key, "mono", 11 * fs, t[col + "Text"] if col + "Text" in t else t[col]))
    for (b, name, kind), x0, w in zip(frame, xs, ws):
        if kind:
            col = t["bad"] if kind == "stuff" else t["ai"]
            g.append(f'<rect x="{x0 + .5:.1f}" y="184" width="{max(1.5, w - 1):.1f}" height="6" rx="1.5" fill="{col}"/>')
    # rate band under the wave
    brs_x = xs[[n for _, n, _ in frame].index("BRS")]
    del_x = xs[[n for _, n, _ in frame].index("CRC del")]
    g.append(f'<rect x="{brs_x + TN * SPN:.1f}" y="196" width="{del_x + TD * SPD - brs_x - TN * SPN:.1f}" height="4" fill="{t["ai"]}" opacity=".7"/>')
    g.append(svg.text(brs_x + TN * SPN + 4, 214, "data phase · 2 Mbit/s", "mono", 11 * fs, t["aiText"]))
    g.append(svg.text(4, 214, "arbitration · 500 kbit/s", "mono", 11 * fs, t["muted"]))
    g.append(svg.text(del_x + 30, 214, "nominal again", "mono", 11 * fs, t["muted"]))
    idle = 1300
    g.append(f'<path d="M{-idle},{hi} L0,{hi} M{total:.1f},{hi} L{total + idle:.1f},{hi}" fill="none" stroke="{t["accent"]}" stroke-width="2.2" opacity=".55"/>')
    g.append(svg.text(-idle + 900, hi - 10, "bus idle (recessive)", "mono", 11 * fs, t["muted"]))
    g.append(svg.text(total + 120, hi - 10, "bus idle · next frame…", "mono", 11 * fs, t["muted"]))
    g.append(f'<path d="{wave}" fill="none" stroke="{t["accent"]}" stroke-width="2.2" stroke-linejoin="round"/>')
    inner = "".join(g)
    dur = 13
    lead = 380
    anim = (f'<g class="m" transform="translate(0,{dy:.0f})"><g><animateTransform attributeName="transform" type="translate" '
            f'values="{W - lead},0;{W - lead - total - 60:.0f},0" dur="{dur}s" repeatCount="indefinite"/>{inner}</g></g>')
    sc = (W - 80) / total
    static = f'<g class="s" transform="translate(40,{dy:.0f}) scale({sc:.4f},1)"><g clip-path="url(#frm)">{inner}</g></g>'
    svg.defs.append(f'<clipPath id="frm"><rect x="0" y="0" width="{total:.0f}" height="{H}"/></clipPath>')
    svg.defs.append(f'<clipPath id="win"><rect x="24" y="{60 + dy * .6:.0f}" width="{W - 48}" height="{H - 66 - dy * .6:.0f}"/></clipPath>'
                    f'<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{t["bg"]}"/><stop offset=".06" stop-color="{t["bg"]}" stop-opacity="0"/>'
                    f'<stop offset=".94" stop-color="{t["bg"]}" stop-opacity="0"/><stop offset="1" stop-color="{t["bg"]}"/></linearGradient>')
    svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="{t["bg"]}" stroke="{t["line2"]}" stroke-width="1.5"/>')
    svg.add(svg.text(34, 40 * fs if fs > 1 else 40, "// CAN FD · LIVE DECODER", "mono", 13 * fs, t["accentText"], ls=3))
    legend = [("stuff bit", t["bad"]), ("fixed stuff bit", t["ai"])]
    lx = 360 if W > 900 else 34
    for lab, col in legend:
        ly = 40 if W > 900 else 40 + 30 * fs
        svg.add(f'<rect x="{lx}" y="{ly - 9}" width="{14 * fs:.0f}" height="{6 * fs:.0f}" rx="1.5" fill="{col}"/>' + svg.text(lx + 20 * fs, ly, lab, "mono", 11 * fs, t["muted"]))
        lx += 150 * fs

    svg.add(f'<g clip-path="url(#win)">{anim}{static}</g><rect x="24" y="{60 + dy * .6:.0f}" width="{W - 48}" height="{H - 66 - dy * .6:.0f}" fill="url(#edge)"/>')
    if W > 900:
        svg.add(svg.text(W - 34, 40, f"base frame · {len(frame)} bits on the wire · {facts['stuff']} dynamic + 6 fixed stuff bits",
                         "mono", 11 * fs, t["muted"], "end"))
    return svg.render()


def main():
    frame, facts = build_frame()
    for mode, t in THEMES.items():
        p, n = write("canfd", mode, build(mode, t, frame, facts))
        write("canfd-m", mode, build(mode, t, frame, facts, W=640, fs=1.7))
        print(f"{p}: {n / 1024:.0f} KB")
    print("facts:", facts, "bits:", len(frame))


if __name__ == "__main__":
    main()
