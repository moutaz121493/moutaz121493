#!/usr/bin/env python3
"""Homelab card: an isometric server rack + terminal + live numbers, drawn from data/live.json.

live.json is published hourly by the Raspberry Pi itself (aggregate numbers only) to the branch "live";
the homelab workflow copies it to data/live.json and runs this script. If the data is older than STALE_H,
the card says "last seen X h ago" in amber instead of ONLINE, so it never shows stale numbers as live.
"""
import datetime as dt
import json
import math
import os
import sys

from iso import box, iso
from svglib import Svg, THEMES, write, ROOT, E

STALE_H = 3


def spark(vals, x, y, w, h, lo, hi):
    if not vals:
        return "", ""
    span = (hi - lo) or 1
    xy = [(x + w * i / max(1, len(vals) - 1), y + h - h * (min(max(v, lo), hi) - lo) / span) for i, v in enumerate(vals)]
    line = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in xy)
    return line, line + f" L{x + w:.1f},{y + h:.1f} L{x:.1f},{y + h:.1f} Z"


def rack(t, ox, oy, online):
    """Isometric rack: 4 units, LEDs blink (green when online, amber when stale)."""
    out = [box(0, 0, 0, 92, 70, 170, ox, oy, 1, t["panel"], t["bg2"], t["line"], t["line2"])]
    led = t["live"] if online else t["accent"]
    for u in range(4):
        z = 20 + u * 38
        out.append(box(4, 70, z, 84, 4, 28, ox, oy, 1, t["bg2"], t["panel"], t["line"], t["line2"]))
        for k in range(3):
            p = iso(12 + k * 9, 74, z + 14, ox, oy)
            dur = 0.9 + ((u * 3 + k) % 5) * .37
            out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.6" fill="{led if k else t["ai"]}">'
                       f'<animate class="m" attributeName="opacity" values="1;.25;1" dur="{dur:.2f}s" repeatCount="indefinite"/></circle>')
        a, b = iso(48, 74, z + 18, ox, oy), iso(80, 74, z + 18, ox, oy)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{t["line2"]}" stroke-width="2"/>')
    return "".join(out)


def build(d, t, now):
    W, H = 1280, 452
    age_h = (now - d.get("updated_epoch", 0)) / 3600
    online = age_h <= STALE_H
    st_col = t["live"] if online else t["accent"]
    svg = Svg(W, H, f"Homelab live status, published by the Raspberry Pi: services {d.get('svc_up')}/{d.get('svc_total')}, "
                    f"availability {d.get('avail_30d')}% over 30 days" + ("" if online else f", last seen {age_h:.0f} h ago"), t)
    svg.defs.append(f'<radialGradient id="hg" cx="0%" cy="0%" r="65%"><stop offset="0" stop-color="{st_col}" stop-opacity="{t["glow"]}"/>'
                    f'<stop offset="1" stop-color="{st_col}" stop-opacity="0"/></radialGradient>'
                    f'<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="{t["line"]}" opacity=".35"/></pattern>'
                    f'<clipPath id="hc"><rect width="{W}" height="{H}" rx="20"/></clipPath>')
    svg.add(f'<g clip-path="url(#hc)"><rect width="{W}" height="{H}" fill="{t["panel"]}"/><rect width="{W}" height="{H}" fill="url(#hg)"/>')
    # header
    svg.add(svg.text(36, 44, "// HOMELAB · LIVE", "mono", 15, t["accentText"], ls=4))
    lab = "ONLINE" if online else f"LAST SEEN {age_h:.0f} H AGO"
    svg.add(f'<circle cx="300" cy="39" r="6" fill="{st_col}"><animate class="m" attributeName="r" values="6;9;6" dur="1.6s" repeatCount="indefinite"/></circle>')
    svg.add(svg.text(316, 44, lab, "mono", 13, t["liveText"] if online else t["accentText"], ls=2))
    when = dt.datetime.fromtimestamp(d.get("updated_epoch", now), dt.timezone(dt.timedelta(hours=d.get("utc_offset_h", 1))))
    svg.add(svg.text(W - 36, 44, f"Raspberry Pi 5 · self-hosted · data from {when:%d %b %H:%M} (Berlin)", "mono", 12, t["muted"], "end"))
    # rack
    svg.add(f'<ellipse cx="118" cy="330" rx="92" ry="17" fill="#000" opacity="{.3 if t["bg"] < "#8" else .1}"/>')
    svg.add(rack(t, 110, 236, online))
    svg.add(svg.text(118, 372, "pi5 · 4 GB", "mono", 11, t["muted"], "middle", 1.5))
    # terminal
    tx, ty, tw, th = 268, 70, 430, H - 104
    svg.add(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="{t["bg"]}" stroke="{t["line2"]}"/>'
            f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="url(#scan)"/>')
    svg.add(svg.text(tx + 18, ty + 24, "moutaz@homelab: ~", "mono", 12, t["muted"]))
    svc = f"{d.get('svc_up')}/{d.get('svc_total')}"
    lines = [("uptime", f"up {d.get('uptime_days')} days · load {d.get('load')}"),
             ("sensors", f"{d.get('temp_c')} °C · " + ("throttling!" if d.get("throttled") else "no throttling")),
             ("services", f"{svc} up · watched every minute"),
             ("backup", ("last night OK" if d.get("backup_ok") else "last night FAILED") + " · 3 encrypted copies"),
             ("diag-agent", f"{d.get('incidents_30d')} incidents auto-diagnosed (30 d)"),
             ("pihole", f"{d.get('blocked_pct')}% of DNS queries blocked today")]
    for i, (c, o) in enumerate(lines):
        y = ty + 62 + i * 52
        b = .3 + i * .45
        svg.add(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{b:.2f}s" dur=".25s" fill="freeze"/>'
                + svg.text(tx + 18, y, "$", "mono", 15, t["liveText"]) + svg.text(tx + 36, y, c, "mono", 15, t["fg"])
                + svg.text(tx + 36, y + 20, o, "mono", 13, t["muted"]) + "</g>")
    # tiles
    rx_ = 726
    tiles = [("UPTIME 30 D", f"{d.get('avail_30d')}%", "liveText"), ("SERVICES", svc, "aiText"),
             ("CPU TEMP", f"{d.get('temp_c')}°", "accentText"), ("RAM", f"{d.get('mem_pct', 0):.0f}%", "fg")]
    for i, (lab_, val, col) in enumerate(tiles):
        x = rx_ + i * 132
        svg.add(f'<rect x="{x + 5}" y="{75}" width="120" height="84" rx="12" fill="{t["line2"]}"/>'
                f'<rect x="{x}" y="70" width="120" height="84" rx="12" fill="{t["bg2"]}" stroke="{t["line2"]}"/>')
        svg.add(svg.text(x + 13, 93, lab_, "mono", 10.5, t["muted"], ls=1.5))
        svg.add(svg.text(x + 13, 136, val, "display", 28 if len(val) < 7 else 24, t[col]))
    # sparkline
    gx, gy, gw, gh = rx_, 214, 518, 84
    cpu, temp = d.get("cpu") or [], d.get("temp") or []
    cl, ca = spark(cpu, gx, gy, gw, gh, 0, max(25, max(cpu or [0])))
    tl, _ = spark(temp, gx, gy, gw, gh, 30, 80)
    svg.add(svg.text(gx, gy - 12, f"LAST 24 H · CPU avg {d.get('cpu_avg')}% · TEMP", "mono", 10.5, t["muted"], ls=1.5))
    svg.add(f'<line x1="{gx}" y1="{gy + gh}" x2="{gx + gw}" y2="{gy + gh}" stroke="{t["line2"]}"/>'
            f'<path d="{ca}" fill="{t["ai"]}" opacity=".16"/><path d="{cl}" fill="none" stroke="{t["ai"]}" stroke-width="1.6"/>'
            f'<path d="{tl}" fill="none" stroke="{t["accent"]}" stroke-width="1.8"/>')
    # 30-day strip
    sx, sy = rx_, 344
    svg.add(svg.text(sx, sy - 12, "LAST 30 DAYS", "mono", 10.5, t["muted"], ls=1.5))
    days = (d.get("days") or [])[-30:]
    bw = (518 - 29 * 3) / 30
    for i, v in enumerate(days):
        col = t["line2"] if v is None else (t["live"] if v >= 99.5 else t["accent"] if v >= 97 else t["bad"])
        svg.add(f'<rect x="{sx + i * (bw + 3):.1f}" y="{sy}" width="{bw:.1f}" height="30" rx="3" fill="{col}" opacity="{.35 if v is None else .9}"/>')
    svg.add(svg.text(W - 36, H - 18, "published hourly by the Pi itself · aggregate numbers only", "mono", 11, t["muted"], "end"))
    svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="19.5" fill="none" stroke="{t["line2"]}" stroke-width="1.5"/></g>')
    return svg.render()


def build_m(d, t, now):
    """Phone variant: 640 px, stacked (header, tiles 2x2, CPU graph, 30-day strip, terminal lines)."""
    W, H = 640, 980
    age_h = (now - d.get("updated_epoch", 0)) / 3600
    online = age_h <= STALE_H
    st_col = t["live"] if online else t["accent"]
    svg = Svg(W, H, f"Homelab live status: services {d.get('svc_up')}/{d.get('svc_total')}, availability {d.get('avail_30d')}% over 30 days"
                    + ("" if online else f", last seen {age_h:.0f} h ago"), t)
    svg.defs.append(f'<radialGradient id="hg" cx="0%" cy="0%" r="70%"><stop offset="0" stop-color="{st_col}" stop-opacity="{t["glow"]}"/>'
                    f'<stop offset="1" stop-color="{st_col}" stop-opacity="0"/></radialGradient><clipPath id="hc"><rect width="{W}" height="{H}" rx="20"/></clipPath>')
    svg.add(f'<g clip-path="url(#hc)"><rect width="{W}" height="{H}" fill="{t["panel"]}"/><rect width="{W}" height="{H}" fill="url(#hg)"/>')
    svg.add(svg.text(30, 50, "// HOMELAB · LIVE", "mono", 20, t["accentText"], ls=3))
    svg.add(f'<circle cx="38" cy="88" r="8" fill="{st_col}"><animate class="m" attributeName="r" values="8;11;8" dur="1.6s" repeatCount="indefinite"/></circle>')
    svg.add(svg.text(56, 95, "ONLINE" if online else f"LAST SEEN {age_h:.0f} H AGO", "mono", 20, t["liveText"] if online else t["accentText"], ls=2))
    svg.add(rack(t, W - 230, 196, online).replace('r="2.6"', 'r="3"'))
    svc = f"{d.get('svc_up')}/{d.get('svc_total')}"
    tiles = [("UPTIME 30 D", f"{d.get('avail_30d')}%", "liveText"), ("SERVICES", svc, "aiText"),
             ("CPU TEMP", f"{d.get('temp_c')}°", "accentText"), ("RAM", f"{d.get('mem_pct', 0):.0f}%", "fg")]
    for i, (lab_, val, col) in enumerate(tiles):
        x, y = 30 + (i % 2) * 292, 300 + (i // 2) * 122
        svg.add(f'<rect x="{x + 6}" y="{y + 6}" width="276" height="106" rx="14" fill="{t["line2"]}"/>'
                f'<rect x="{x}" y="{y}" width="276" height="106" rx="14" fill="{t["bg2"]}" stroke="{t["line2"]}"/>')
        svg.add(svg.text(x + 18, y + 32, lab_, "mono", 15, t["muted"], ls=1.5))
        svg.add(svg.text(x + 18, y + 84, val, "display", 42, t[col]))
    gx, gy, gw, gh = 30, 590, 580, 96
    cpu, temp = d.get("cpu") or [], d.get("temp") or []
    cl, ca = spark(cpu, gx, gy, gw, gh, 0, max(25, max(cpu or [0])))
    tl, _ = spark(temp, gx, gy, gw, gh, 30, 80)
    svg.add(svg.text(gx, gy - 16, f"LAST 24 H · CPU {d.get('cpu_avg')}% · TEMP", "mono", 15, t["muted"], ls=1))
    svg.add(f'<path d="{ca}" fill="{t["ai"]}" opacity=".16"/><path d="{cl}" fill="none" stroke="{t["ai"]}" stroke-width="2.2"/>'
            f'<path d="{tl}" fill="none" stroke="{t["accent"]}" stroke-width="2.4"/>')
    svg.add(svg.text(30, 740, "LAST 30 DAYS", "mono", 15, t["muted"], ls=1.5))
    days = (d.get("days") or [])[-30:]
    bw = (580 - 29 * 3) / 30
    for i, v in enumerate(days):
        col = t["line2"] if v is None else (t["live"] if v >= 99.5 else t["accent"] if v >= 97 else t["bad"])
        svg.add(f'<rect x="{30 + i * (bw + 3):.1f}" y="752" width="{bw:.1f}" height="40" rx="3" fill="{col}" opacity="{.35 if v is None else .9}"/>')
    lines = [f"backup: " + ("last night OK" if d.get("backup_ok") else "last night FAILED"),
             f"diag-agent: {d.get('incidents_30d')} incidents (30 d)", f"pihole: {d.get('blocked_pct')}% blocked today"]
    for i, l in enumerate(lines):
        svg.add(svg.text(30, 850 + i * 36, "$ " + l, "mono", 18, t["fg"] if i else t["liveText"]))
    svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="19.5" fill="none" stroke="{t["line2"]}" stroke-width="1.5"/></g>')
    return svg.render()


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "live.json")
    d = json.load(open(path))
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    for mode, t in THEMES.items():
        p, n = write("homelab", mode, build(d, t, now))
        write("homelab-m", mode, build_m(d, t, now))
        print(f"{p}: {n / 1024:.0f} KB")


if __name__ == "__main__":
    main()
