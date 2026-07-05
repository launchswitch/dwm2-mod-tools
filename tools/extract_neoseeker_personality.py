#!/usr/bin/env python3
"""
Extract clean markdown from two additional saved McBick/RSlickback FAQ pages:

  * co-op_skills.html      -> Neoseeker page   (FAQ body in <div id="faqtxt">)
  * personality_guide.html -> GameFAQs page    (FAQ body in <div id="faqwrap">,
                              with a <div class="ftoc"> table-of-contents to strip)

Unlike tools/extract_gamefaqs_faq.py (which is wired to the McBick #78461
skill-guide slugs), this script auto-detects the page type, locates the FAQ
body container, strips all site chrome (nav/ads/sidebar/JS/CSS/ToC), and
converts headings, paragraphs, lists and tables to clean markdown.

Tables are rendered as markdown pipe tables preserving EVERY row and column.
Rich cell formatting (<strong>/<b> -> **bold**, <em>/<i> -> *italic*, <br>
line breaks) is preserved so the personality matrix (High/Average/Low labels,
family-grouped arena text) is captured verbatim.
"""
import os
import re
import sys
from bs4 import BeautifulSoup, NavigableString, Tag


# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------
def clean_text(s):
    """Collapse whitespace, trim."""
    if s is None:
        return ""
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    return s.strip()


# ---------------------------------------------------------------------------
# inline rendering -> markdown (bold/italic), with <br> as a marker
# ---------------------------------------------------------------------------
def inline_md(node, parts=None):
    """Render an inline content tree to a string, preserving **bold**/*italic*
    and converting <br> into a literal <br> marker (kept for the table-cell
    path so we can collapse runs later)."""
    if parts is None:
        buf = []
        _inline_into(node, buf)
        return "".join(buf)
    _inline_into(node, parts)


def _strip_br(s):
    """Remove leading/trailing <br> markers and whitespace from a string."""
    s = re.sub(r"^(?:\s|<br>)+", "", s)
    s = re.sub(r"(?:\s|<br>)+$", "", s)
    return s


def _inline_into(node, parts):
    if isinstance(node, NavigableString):
        parts.append(str(node))
        return
    if not isinstance(node, Tag):
        return
    name = node.name
    if name in ("strong", "b"):
        inner = []
        for c in node.children:
            _inline_into(c, inner)
        txt = _strip_br("".join(inner))
        parts.append(f"**{txt}**" if txt else "")
        return
    if name in ("em", "i"):
        inner = []
        for c in node.children:
            _inline_into(c, inner)
        txt = _strip_br("".join(inner))
        parts.append(f"*{txt}*" if txt else "")
        return
    if name == "br":
        parts.append("<br>")
        return
    if name == "a":
        # keep anchor text only (drop nav hrefs); these FAQ bodies use <a> as
        # plain text or section anchors.
        for c in node.children:
            _inline_into(c, parts)
        return
    if name == "img":
        alt = node.get("alt", "")
        if alt:
            parts.append(alt)
        return
    if name == "p":
        # render children, then ensure a <br> boundary so adjacent <p> blocks
        # (e.g. inside a table cell) don't run together.
        before = len(parts)
        for c in node.children:
            _inline_into(c, parts)
        if len(parts) > before:
            parts.append("<br>")
        return
    # generic container / inline -> recurse
    for c in node.children:
        _inline_into(c, parts)


# ---------------------------------------------------------------------------
# table rendering
# ---------------------------------------------------------------------------
def cell_md(cell):
    """Render a <td>/<th> as a markdown cell string, with <br> line breaks
    and bold/italic preserved. Inline content only (nested tables flattened
    to text)."""
    parts = []
    for child in cell.children:
        _inline_into(child, parts)
    text = "".join(parts)
    # collapse whitespace runs but keep <br>
    text = re.sub(r"[ \t\r\n]+", " ", text)
    # collapse 3+ consecutive <br> into one
    text = re.sub(r"(<br> ?){2,}", "<br>", text)
    text = text.strip()
    text = re.sub(r"^(?:<br>| )+", "", text)
    text = re.sub(r"(?:<br>| )+$", "", text)
    # adjacent same-weight markers run together when the source splits a
    # phrase across two <strong>/<em> elements (e.g. "<b>Bravery<br></b>
    # <b>(Charge)</b>"). Normalize:
    #   **a****b** -> **a** **b**   (and the italic equivalent)
    text = re.sub(r"\*\*\*\*", "** **", text)
    text = re.sub(r"\*\*\s*\*\*", " ", text)   # empty bold -> drop
    text = re.sub(r"(?<!\*)\*(?!\*)\s*\*(?!\*)", " ", text)  # empty italic
    text = re.sub(r"\s{2,}", " ", text)
    # a markdown table cell cannot contain a literal pipe -> escape
    text = text.replace("|", "\\|")
    return text.strip()


def get_top_rows(tbl):
    """Return <tr> elements that are direct children of <table>/<tbody>/thead."""
    rows = tbl.find_all("tr", recursive=False)
    if not rows:
        for sub in ("thead", "tbody"):
            cont = getattr(tbl, sub, None)
            if cont is not None:
                rows = cont.find_all("tr", recursive=False)
                if rows:
                    break
    if not rows:
        # last resort: any tr anywhere
        rows = tbl.find_all("tr")
    return rows


def parse_row(tr):
    """Return list of (cell_text, colspan)."""
    out = []
    for c in tr.find_all(["th", "td"], recursive=False):
        colspan = int(c.get("colspan", "1") or "1")
        out.append((cell_md(c), colspan))
    return out


def expand_row(parsed):
    """Expand colspans into repeated empty cells so all rows share column
    count. (Rowspan is rare in these tables; if present, we leave a blank
    cell rather than carry state, which keeps every datum visible.)"""
    row = []
    for text, colspan in parsed:
        row.append(text)
        for _ in range(colspan - 1):
            row.append("")
    return row


def render_table(tbl):
    """Render a top-level table as a single markdown pipe table. A full-width
    single-cell row (colspan spanning all columns) is rendered as a bold
    section caption that flushes the current table."""
    rows = get_top_rows(tbl)
    if not rows:
        return ""
    parsed = [parse_row(r) for r in rows]
    parsed = [p for p in parsed if p]
    if not parsed:
        return ""
    ncol = max(sum(cs for _, cs in p) for p in parsed)

    out_lines = []
    body = []

    def flush():
        nonlocal body
        if body:
            out_lines.extend(emit_md_table(body))
            body = []

    for p in parsed:
        # caption row?  exactly one cell whose colspan >= ncol (or ==1 with
        # ncol==1)
        if len(p) == 1:
            txt, colspan = p[0]
            if not txt:
                continue
            if colspan >= ncol or ncol == 1:
                flush()
                out_lines.append(f"**{txt}**")
                out_lines.append("")
                continue
        row_md = expand_row(p)
        while len(row_md) < ncol:
            row_md.append("")
        body.append(row_md[:ncol])
    flush()
    return "\n".join(out_lines)


def emit_md_table(body):
    if not body:
        return []
    ncol = max(len(r) for r in body)
    out = []
    header = body[0] + [""] * (ncol - len(body[0]))
    out.append("| " + " | ".join(header) + " |")
    out.append("|" + "|".join(["---"] * ncol) + "|")
    for r in body[1:]:
        r = r + [""] * (ncol - len(r))
        out.append("| " + " | ".join(r) + " |")
    out.append("")
    return out


# ---------------------------------------------------------------------------
# block-level conversion of the FAQ body
# ---------------------------------------------------------------------------
def convert_node(node):
    """Convert a single child node of the FAQ body to markdown lines."""
    if isinstance(node, NavigableString):
        t = str(node).strip()
        return [t] if t else []
    if not isinstance(node, Tag):
        return []
    name = node.name
    if name in ("h1",):
        return ["# " + clean_text(node.get_text(" ", strip=True)), ""]
    if name in ("h2",):
        return ["## " + clean_text(node.get_text(" ", strip=True)), ""]
    if name in ("h3",):
        return ["### " + clean_text(node.get_text(" ", strip=True)), ""]
    if name in ("h4",):
        return ["#### " + clean_text(node.get_text(" ", strip=True)), ""]
    if name in ("p",):
        buf = []
        inline_md(node, buf)
        t = clean_text("".join(buf))
        # turn surviving <br> markers into real line breaks for prose
        t = t.replace("<br>", "  \n")
        t = clean_text(t)
        return [t, ""] if t else []
    if name == "table":
        return [render_table(node)]
    if name == "hr":
        return ["---", ""]
    if name == "ul":
        out = []
        for li in node.find_all("li", recursive=False):
            buf = []
            inline_md(li, buf)
            t = clean_text("".join(buf))
            if t:
                out.append("- " + t)
        if out:
            out.append("")
        return out
    if name == "ol":
        out = []
        for j, li in enumerate(node.find_all("li", recursive=False), 1):
            buf = []
            inline_md(li, buf)
            t = clean_text("".join(buf))
            if t:
                out.append(f"{j}. " + t)
        if out:
            out.append("")
        return out
    if name in ("div", "span", "section", "article"):
        out = []
        for child in node.children:
            out.extend(convert_node(child))
        return out
    # fallback: emit the text
    buf = []
    inline_md(node, buf)
    t = clean_text("".join(buf))
    return [t, ""] if t else []


def locate_body(soup):
    """Return the FAQ body element, or (None, reason).

    Order of preference:
      1. <div id="faqwrap">  (GameFAQs) -> also strip <div class="ftoc">
      2. <div id="faqtxt">   (Neoseeker)
      3. <div class="faqtext">
    """
    wrap = soup.find(id="faqwrap")
    if wrap is not None:
        kind = "gamefaqs"
        for toc in wrap.find_all("div", class_="ftoc"):
            toc.decompose()
        # also drop any copyright/pod/nav siblings that may have been wrapped
        for sel in ("copyright",):
            for el in wrap.find_all(class_=sel):
                el.decompose()
        return wrap, kind
    txt = soup.find(id="faqtxt")
    if txt is not None:
        return txt, "neoseeker"
    alt = soup.find("div", class_="faqtext")
    if alt is not None:
        return alt, "neoseeker"
    return None, "no FAQ body container found"


def html_to_md(html_path):
    with open(html_path, encoding="utf-8", errors="replace") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    body, kind = locate_body(soup)
    if body is None:
        return None, kind
    out = []
    for child in body.children:
        out.extend(convert_node(child))
    md = "\n".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return md, kind


# ---------------------------------------------------------------------------
# headers for the two known files
# ---------------------------------------------------------------------------
def make_header_coop():
    return (
        "# Co-op Skills\n\n"
        "> Source: McBick DWM2 FAQ (Neoseeker mirror, saved HTML)\n"
        "> Neoseeker URL: "
        "https://www.neoseeker.com/dwm2/faqs/"
        "3072571-dragon-warrior-monsters-2-cobis-journey-coop-skills.html\n"
        "> Captured: 2026-07-05 from browser-saved HTML\n\n"
        "---\n\n"
    )


def make_header_personality():
    return (
        "# Personalities\n\n"
        "> Source: RSlickback DWM1/DWM2 personality FAQ (GameFAQs #80057, "
        "saved HTML)\n"
        "> GameFAQs URL: "
        "https://gamefaqs.gamespot.com/gbc/197155-dragon-warrior-monsters/"
        "faqs/80057/personalities\n"
        "> Captured: 2026-07-05 from browser-saved HTML\n\n"
        "---\n\n"
    )


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    guide_dir = os.path.normpath(os.path.join(here, "..", "mechanics",
                                              "mcbick_guide"))
    jobs = [
        ("co-op_skills.html", "co-op-skills.md", make_header_coop()),
        ("personality_guide.html", "personality-guide.md",
         make_header_personality()),
    ]
    for src_name, dst_name, header in jobs:
        src = os.path.join(guide_dir, src_name)
        if not os.path.exists(src):
            # also try inside raw_html/
            src = os.path.join(guide_dir, "raw_html", src_name)
            if not os.path.exists(src):
                print(f"MISS: {src_name}", file=sys.stderr)
                continue
        md, kind = html_to_md(src)
        if isinstance(md, str) is False and md is None:
            print(f"ERR  {src_name}: {kind}", file=sys.stderr)
            continue
        full = header + md
        dst = os.path.join(guide_dir, dst_name)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(full)
        rows = md.count("\n| ")
        print(f"OK   {src_name} -> {dst_name}  [{kind}]  "
              f"({len(md)} body chars, ~{rows} table rows)")
