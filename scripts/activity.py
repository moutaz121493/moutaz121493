#!/usr/bin/env python3
"""Latest-activity card from the public GitHub API: commits pushed (30 days), recently active public repos,
language mix of the public repos. Plain stats only; nothing is generated or guessed.
Token: $GITHUB_TOKEN (in the Action) or ~/.config/github-token locally; public data only either way."""
import datetime as dt
import json
import os
import urllib.request

from svglib import Svg, THEMES, write

USER = "moutaz121493"
SKIP = {USER}                               # the profile repo itself is not "work"
LANG_COL = ["ai", "accent", "live", "muted", "bad"]


def api(path):
    tok = os.environ.get("GITHUB_TOKEN") or open(os.path.expanduser("~/.config/github-token")).read().strip()
    req = urllib.request.Request("https://api.github.com" + path, headers={
        "Authorization": "Bearer " + tok, "Accept": "application/vnd.github+json", "User-Agent": "profile-activity"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def ago(ts, now):
    s = (now - dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))).total_seconds()
    for unit, n in (("d", 86400), ("h", 3600), ("min", 60)):
        if s >= n:
            return f"{int(s // n)} {unit} ago"
    return "just now"


def collect():
    now = dt.datetime.now(dt.timezone.utc)
    repos = [r for r in api(f"/users/{USER}/repos?per_page=100&type=owner&sort=pushed") if not r["fork"] and not r["private"]]
    since = now - dt.timedelta(days=30)
    commits = 0                                  # commits on the default branch of each own public repo, bots excluded
    for r in repos:
        if dt.datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00")) < since:
            continue
        for c in api(f"/repos/{USER}/{r['name']}/commits?since={since:%Y-%m-%dT%H:%M:%SZ}&per_page=100"):
            if not ((c.get("author") or {}).get("login", "").endswith("[bot]")):
                commits += 1
    langs = {}
    for r in repos:
        if r["archived"]:
            continue
        for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
            langs[k] = langs.get(k, 0) + v
    recent = [{"name": r["name"], "lang": r["language"] or "–", "ago": ago(r["pushed_at"], now)}
              for r in repos if r["name"] not in SKIP and not r["archived"]][:4]
    active = sum(1 for r in repos if r["name"] not in SKIP and dt.datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00")) >= since)
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    return {"commits": commits, "active": active, "public": len([r for r in repos if r["name"] not in SKIP]),
            "recent": recent, "langs": [(k, v / total) for k, v in top], "date": now.strftime("%d %b %Y")}


def build(d, t):
    W, H = 1280, 250
    svg = Svg(W, H, f"GitHub activity: {d['commits']} commits pushed in 30 days, {d['active']} active repositories, "
                    f"languages: " + ", ".join(f"{k} {p:.0%}" for k, p in d["langs"]), t)
    svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="{t["panel"]}" stroke="{t["line2"]}" stroke-width="1.5"/>')
    svg.add(svg.text(34, 42, "// LATEST ACTIVITY", "mono", 13, t["accentText"], ls=3))
    svg.add(svg.text(W - 34, 42, f"public GitHub data · updated daily · {d['date']}", "mono", 11, t["muted"], "end"))
    for i, (lab, val, col) in enumerate((("COMMITS 30D", str(d["commits"]), "aiText"), ("ACTIVE REPOS", str(d["active"]), "liveText"),
                                          ("PUBLIC REPOS", str(d["public"]), "accentText"))):
        x = 34 + i * 128
        svg.add(f'<rect x="{x + 5}" y="73" width="116" height="92" rx="12" fill="{t["line2"]}"/>'
                f'<rect x="{x}" y="68" width="116" height="92" rx="12" fill="{t["bg2"]}" stroke="{t["line2"]}"/>')
        svg.add(svg.text(x + 13, 90, lab, "mono", 10, t["muted"], ls=1))
        svg.add(svg.text(x + 13, 140, val, "display", 36, t[col]))
    rx = 450
    svg.add(svg.text(rx, 82, "RECENTLY PUSHED", "mono", 10.5, t["muted"], ls=1.5))
    for i, r in enumerate(d["recent"]):
        y = 112 + i * 30
        svg.add(f'<circle cx="{rx + 5}" cy="{y - 5}" r="4" fill="{t["live"] if i == 0 else t["line2"]}"/>')
        svg.add(svg.text(rx + 20, y, r["name"], "bodyb", 16, t["fg"]))
        svg.add(svg.text(rx + 300, y, f'{r["lang"]} · {r["ago"]}', "mono", 12, t["muted"], "end"))
    lx, lw = 800, 446
    svg.add(svg.text(lx, 82, "LANGUAGES · PUBLIC REPOS", "mono", 10.5, t["muted"], ls=1.5))
    x = lx
    for i, (k, p) in enumerate(d["langs"]):
        w = max(3, lw * p)
        svg.add(f'<rect x="{x:.1f}" y="98" width="{w - 2:.1f}" height="16" rx="3" fill="{t[LANG_COL[i]]}"/>')
        x += w
    for i, (k, p) in enumerate(d["langs"]):
        cx, cy = lx + (i % 2) * 230, 146 + (i // 2) * 28
        svg.add(f'<rect x="{cx}" y="{cy - 10}" width="12" height="12" rx="3" fill="{t[LANG_COL[i]]}"/>')
        svg.add(svg.text(cx + 20, cy, k, "body", 15, t["fg"]) + svg.text(cx + 200, cy, f"{p:.0%}" if p >= .01 else "<1%", "mono", 13, t["muted"], "end"))
    svg.add(f'<line x1="34" y1="{H - 40}" x2="{W - 34}" y2="{H - 40}" stroke="{t["line"]}" stroke-dasharray="3 5"/>')
    svg.add(svg.text(34, H - 16, "Counts come straight from the GitHub API; private work is not shown.", "mono", 11, t["muted"]))
    return svg.render()


def build_m(d, t):
    W, H = 640, 660
    svg = Svg(W, H, f"GitHub activity: {d['commits']} commits in 30 days, {d['active']} active repositories", t)
    svg.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="{t["panel"]}" stroke="{t["line2"]}" stroke-width="1.5"/>')
    svg.add(svg.text(30, 52, "// LATEST ACTIVITY", "mono", 19, t["accentText"], ls=3))
    for i, (lab, val, col) in enumerate((("COMMITS 30D", str(d["commits"]), "aiText"), ("ACTIVE", str(d["active"]), "liveText"),
                                          ("PUBLIC", str(d["public"]), "accentText"))):
        x = 30 + i * 196
        svg.add(f'<rect x="{x + 6}" y="86" width="182" height="120" rx="14" fill="{t["line2"]}"/>'
                f'<rect x="{x}" y="80" width="182" height="120" rx="14" fill="{t["bg2"]}" stroke="{t["line2"]}"/>')
        svg.add(svg.text(x + 18, 112, lab, "mono", 15, t["muted"], ls=1))
        svg.add(svg.text(x + 18, 176, val, "display", 50, t[col]))
    svg.add(svg.text(30, 262, "RECENTLY PUSHED", "mono", 15, t["muted"], ls=1.5))
    for i, r in enumerate(d["recent"][:3]):
        y = 302 + i * 40
        svg.add(svg.text(30, y, r["name"], "bodyb", 22, t["fg"]) + svg.text(W - 30, y, f'{r["lang"]} · {r["ago"]}', "mono", 16, t["muted"], "end"))
    y0 = 302 + 3 * 40 + 20
    svg.add(svg.text(30, y0, "LANGUAGES", "mono", 15, t["muted"], ls=1.5))
    x = 30
    for i, (k, p) in enumerate(d["langs"]):
        w = max(4, 580 * p)
        svg.add(f'<rect x="{x:.1f}" y="{y0 + 16}" width="{w - 2:.1f}" height="20" rx="4" fill="{t[LANG_COL[i]]}"/>')
        x += w
    for i, (k, p) in enumerate(d["langs"][:4]):
        cx, cy = 30 + (i % 2) * 300, y0 + 76 + (i // 2) * 34
        svg.add(f'<rect x="{cx}" y="{cy - 14}" width="16" height="16" rx="4" fill="{t[LANG_COL[i]]}"/>'
                + svg.text(cx + 26, cy, f"{k} {p:.0%}" if p >= .01 else f"{k} <1%", "body", 19, t["fg"]))
    return svg.render()


def main():
    d = collect()
    for mode, t in THEMES.items():
        p, n = write("activity", mode, build(d, t))
        write("activity-m", mode, build_m(d, t))
        print(f"{p}: {n / 1024:.0f} KB")
    print(json.dumps({k: v for k, v in d.items() if k != "recent"}))


if __name__ == "__main__":
    main()
