#!/usr/bin/env python3
"""Local GitHub-like preview of README.md, before anything is pushed.

- Markdown -> HTML (python-markdown), then the parts GitHub's sanitizer would remove are removed:
  <script>, <style>, <iframe>, style="" and on* attributes, and any tag outside a short allow-list.
- Rendered at GitHub's README widths (1012 px and 375 px) in dark and light colour schemes, so the
  <picture> sources switch exactly as on github.com. Writes .preview/<scheme>-<width>.png and .preview/index.html.
Needs: pip install markdown playwright && playwright install chromium (not needed by the workflows).
"""
import html.parser
import os
import re

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, ".preview")
ALLOWED = {"a", "b", "strong", "i", "em", "p", "br", "img", "picture", "source", "sub", "sup", "div", "span", "ul", "ol", "li",
           "table", "thead", "tbody", "tr", "td", "th", "details", "summary", "blockquote", "code", "pre", "h1", "h2", "h3", "h4", "hr"}
DROP_WITH_CONTENT = {"script", "style", "iframe"}
CSS = {  # GitHub's own page styling (approximation): the README itself cannot carry any of this
    "dark": "body{background:#0d1117;color:#e6edf3}a{color:#4493f8}blockquote{color:#9198a1;border-left:.25em solid #3d444d}",
    "light": "body{background:#ffffff;color:#1f2328}a{color:#0969da}blockquote{color:#59636e;border-left:.25em solid #d1d9e0}",
}


class Sanitizer(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out, self.skip, self.removed = [], 0, []

    def handle_starttag(self, tag, attrs):
        if tag in DROP_WITH_CONTENT:
            self.skip += 1
            self.removed.append(tag)
            return
        if self.skip:
            return
        if tag not in ALLOWED:
            self.removed.append(tag)
            return
        keep = []
        for k, v in attrs:
            if k == "style" or k.startswith("on"):
                self.removed.append(f"{tag}[{k}]")
                continue
            if k in ("src", "srcset", "href") and v and not re.match(r"^(https?:|mailto:|#)", v):
                v = "file://" + os.path.join(ROOT, v)
            keep.append(f' {k}="{html.escape(v or "", quote=True)}"' if v is not None else f" {k}")
        self.out.append(f"<{tag}{''.join(keep)}>")

    def handle_endtag(self, tag):
        if tag in DROP_WITH_CONTENT:
            self.skip = max(0, self.skip - 1)
            return
        if not self.skip and tag in ALLOWED:
            self.out.append(f"</{tag}>")

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)

    def handle_entityref(self, n):
        if not self.skip:
            self.out.append(f"&{n};")

    def handle_charref(self, n):
        if not self.skip:
            self.out.append(f"&#{n};")




def main():
    from playwright.sync_api import sync_playwright
    src = open(os.path.join(ROOT, "README.md")).read()
    body = markdown.markdown(src, extensions=["extra"])
    s = Sanitizer()
    s.feed(body)
    clean = "".join(s.out)
    missing = sorted({m for m in re.findall(r'file://([^"]+)', clean) if not os.path.exists(m)})
    os.makedirs(OUT, exist_ok=True)
    page = os.path.join(OUT, "index.html")
    with open(page, "w") as f:
        f.write('<!doctype html><meta charset="utf-8"><style>body{margin:0;font:16px/1.5 -apple-system,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif}'
                '.md{box-sizing:border-box;margin:24px auto;padding:0 16px}img{max-width:100%;box-sizing:content-box}'
                'blockquote{margin:0 0 16px;padding:0 1em}p{margin:0 0 16px}</style><style id="scheme"></style>'
                f'<div class="md">{clean}</div>')
    with sync_playwright() as p:
        b = p.chromium.launch()
        for scheme in ("dark", "light"):
            for width in (1012, 375):
                ctx = b.new_context(viewport={"width": width + 32, "height": 900}, color_scheme=scheme)
                pg = ctx.new_page()
                pg.goto("file://" + page)
                pg.evaluate(f"document.getElementById('scheme').textContent = {CSS[scheme]!r};"
                            f"document.querySelector('.md').style.maxWidth = '{width + 32}px'")
                pg.wait_for_timeout(2500)
                pg.screenshot(path=os.path.join(OUT, f"{scheme}-{width}.png"), full_page=True)
                ctx.close()
        b.close()
    print("removed by the sanitizer:", s.removed or "nothing")
    print("missing images:", [os.path.relpath(m, ROOT) for m in missing] or "none")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
