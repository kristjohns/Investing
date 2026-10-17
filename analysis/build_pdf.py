"""Render visa_report.md to an A4 PDF (visa_report.pdf) with the charts embedded.

Markdown is parsed as CommonMark + tables (the same dialect GitHub renders), turned
into a styled HTML page and printed by headless Chromium via Playwright, which gives
page-numbered footers, a linked contents page and PDF bookmarks.

Requires:  pip install markdown-it-py mdit-py-plugins linkify-it-py playwright
           plus a Chromium: either `playwright install chromium`, or set CHROMIUM_PATH.
Usage:     python analysis/build_pdf.py
"""
import base64
import os
import re
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "visa_report.md"
OUT = ROOT / "visa_report.pdf"
CHROMIUM = os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium")

CSS = """
@page { size: A4; }
html { font-family: Inter, "DejaVu Sans", sans-serif; color: #0b0b0b; font-size: 9.4pt; line-height: 1.45;
       font-feature-settings: "calt" 0, "case" 0; }  /* alternates break copy/search of "-" and "()" in the PDF text layer */
body { margin: 0; }
h1 { font-size: 23pt; line-height: 1.15; margin: 0 0 10pt; letter-spacing: -0.01em; }
h2 { font-size: 15pt; margin: 0 0 8pt; padding-bottom: 4pt; border-bottom: 2px solid #2a78d6; break-before: page; break-after: avoid; }
h3 { font-size: 11pt; margin: 14pt 0 5pt; break-after: avoid; }
h3[id^="recommendation"], h3[id^="confidence"] { background: #eef5fd; border-left: 4px solid #2a78d6; padding: 6pt 9pt; margin: 6pt 0; font-size: 11.5pt; }
h3[id^="final-recommendation"] { background: #eef5fd; border-left: 4px solid #2a78d6; padding: 6pt 9pt; }
p { margin: 0 0 6pt; orphans: 3; widows: 3; }
ul, ol { margin: 0 0 6pt; padding-left: 16pt; }
li { margin: 0 0 2.5pt; }
li::marker { font-variant-numeric: normal; font-feature-settings: "tnum" 0, "calt" 0, "case" 0; }
li > ul, li > ol { margin-top: 2.5pt; }
a { color: #1c5cab; text-decoration: none; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 85%; background: #f3f2ee; padding: 0 2pt; border-radius: 2pt; }
blockquote { margin: 8pt 0; padding: 7pt 10pt; background: #fbf3e6; border-left: 4px solid #eda100; }
blockquote p { margin: 0; }
hr { display: none; }  /* section dividers are redundant: every h2 starts a page */
p:has(+ ul), p:has(+ ol), p:has(+ table) { break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 6pt; font-size: 7.9pt; line-height: 1.32; }
thead { display: table-header-group; }
th { background: #f0efec; color: #0b0b0b; font-weight: 600; text-align: left; vertical-align: bottom; }
th, td { border-bottom: 1px solid #e1e0d9; padding: 3pt 5pt; }
td { vertical-align: top; }
tr { break-inside: avoid; }
tbody tr:nth-child(even) td { background: #fbfbf9; }
img { width: 88%; display: block; margin: 6pt auto 8pt; break-inside: avoid; }
p:has(> img) { break-inside: avoid; margin: 0; }
p:has(> em:only-child) em, td em { color: #52514e; }
.cite { font-size: 82%; color: #52514e; white-space: nowrap; }
.cite a { color: #1c5cab; }
.tag { display: inline-block; font-size: 6.6pt; font-weight: 700; line-height: 1; padding: 1.5pt 3pt; border-radius: 3pt; vertical-align: 1pt; color: #fff; }
.tag-F { background: #256abf; }
.tag-E { background: #199e70; }
.tag-J { background: #c98500; }
.toc { columns: 1; font-size: 9.2pt; }
.toc a { color: #0b0b0b; }
.toc .l2 { font-weight: 600; margin: 5pt 0 1pt; }
.toc .l3 { margin: 0 0 0 14pt; color: #52514e; font-size: 8.6pt; }
.toc .l3 a { color: #52514e; }
.sources li, .sources p { font-size: 7.6pt; line-height: 1.35; overflow-wrap: anywhere; }
.sources ul { padding-left: 12pt; }
.sources li { margin-bottom: 1.5pt; }
"""

FOOTER = """<div style="font-family: Inter, 'DejaVu Sans', sans-serif; font-size: 7px; color: #898781;
 font-feature-settings: 'calt' 0, 'case' 0, 'tnum' 0;
 width: 100%; margin: 0 15mm; display: flex; justify-content: space-between;">
 <span>Visa Inc. (NYSE: V) · Investment report · Analysis date {date} · Not personal financial advice</span>
 <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>"""


def render_body(text: str) -> str:
    md = (MarkdownIt("commonmark", {"linkify": True})
          .enable(["table", "linkify"])
          .use(anchors_plugin, min_level=2, max_level=3))
    body = md.render(text)
    defs = dict(re.findall(r"^\[([A-Z][A-Z0-9\-]+)\]:\s*(\S+)", text, flags=re.M))

    # single citations rendered by the parser as <a>CODE</a>: restore brackets, style them
    def single(m):
        code = m.group(2)
        if code not in defs:
            return m.group(0)
        return f'<span class="cite">[<a href="{m.group(1)}">{code}</a>]</span>'
    body = re.sub(r'<a href="([^"]+)">([A-Z][A-Z0-9\-]+)</a>', single, body)

    # grouped citations like [V10K25, V10K22] (and codes only listed in the source list, which
    # have no link definition) stay literal text: style them, linking every code that has a URL
    listed = set(re.findall(r"^- \[([A-Z][A-Z0-9\-]+)\]", text, flags=re.M))
    known = set(defs) | listed

    def group(m):
        codes = [c.strip() for c in m.group(1).split(",")]
        if not all(c in known for c in codes):
            return m.group(0)
        links = ", ".join(f'<a href="{defs[c]}">{c}</a>' if c in defs else c for c in codes)
        return f'<span class="cite">[{links}]</span>'
    body = re.sub(r"\[((?:[A-Z][A-Z0-9\-]+)(?:,\s*[A-Z][A-Z0-9\-]+)*)\]", group, body)
    leftover = sorted(set(re.findall(r"\[([A-Z][A-Z0-9\-]{2,})\]", re.sub(r"<[^>]+>", "", body))) - known)
    if leftover:
        print("warning: unrecognised citation codes:", leftover)

    # fact / estimate / judgement tags
    body = re.sub(r"\[(F|E|J)\]", r'<span class="tag tag-\1">\1</span>', body)

    # embed charts so the PDF is self-contained
    def embed(m):
        p = ROOT / m.group(1)
        if not p.exists():
            return m.group(0)
        return 'src="data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode() + '"'
    body = re.sub(r'src="([^"]+\.png)"', embed, body)

    # contents page from h2/h3, inserted before the first numbered section
    heads = re.findall(r'<h([23]) id="([^"]+)">(.*?)</h\1>', body)
    items = []
    for lvl, hid, title in heads:
        if hid.startswith(("recommendation", "confidence")):
            continue
        plain = re.sub(r"<[^>]+>", "", title)
        items.append(f'<div class="l{lvl}"><a href="#{hid}">{plain}</a></div>')
    toc = '<h2 id="contents">Contents</h2><div class="toc">' + "".join(items) + "</div>"
    first_h2 = body.find("<h2")
    body = body[:first_h2] + toc + body[first_h2:]

    # smaller type for the source list
    i = body.find('<h2 id="sources">')
    if i != -1:
        body = body[:i] + '<div class="sources">' + body[i:] + "</div>"
    return body


def main():
    text = SRC.read_text(encoding="utf-8")
    date = re.search(r"\*\*Analysis date: ([^*]+?)\.\*\*", text)
    date = date.group(1) if date else ""
    title = re.search(r"^# (.+)$", text, flags=re.M).group(1)
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>'
            f"<style>{CSS}</style></head><body>{render_body(text)}</body></html>")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        kwargs = {"executable_path": CHROMIUM} if Path(CHROMIUM).exists() else {}
        browser = p.chromium.launch(**kwargs)
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        page.pdf(path=str(OUT), format="A4", print_background=True, display_header_footer=True,
                 header_template="<div></div>", footer_template=FOOTER.format(date=date),
                 margin={"top": "15mm", "bottom": "17mm", "left": "15mm", "right": "15mm"},
                 outline=True, tagged=True)
        browser.close()
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
