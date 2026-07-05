#!/usr/bin/env python3
"""
Extract clean markdown from saved GameFAQs HTML pages of McBick's
"Advanced Skill Guide" FAQ #78461 (v4.0).

Each input HTML is a complete saved page; the FAQ body lives inside
<div id="faqwrap">. We strip the .ftoc (table of contents) and convert
the remaining body (headings, paragraphs, tables) to markdown.
"""
import re
import sys
from bs4 import BeautifulSoup, NavigableString, Tag

FAFAQ_SLUG = {
    "intro_to_skills.html":      "intro-to-skills",
    "list_of_attributes.html":   "list-of-attributes",
    "skills_physical.html":      "skills-physical",
    "skills_spell.html":         "skills-spell",
    "skills_normal.html":        "skills-normal",
    "skills_breath.html":        "skills-breath",
    "skills_dance.html":         "skills-dance",
    "field_skills.html":         "field-skills",
    "per_species_crit_rates.html": "critical-rates",
    "evation_rates.html":        "evasion-rates",
    "item_resistances.html":     "item-resistances",
}

FAFAQ_TITLE = {
    "intro_to_skills.html":      "Intro to Skills",
    "list_of_attributes.html":   "List of Attributes",
    "skills_physical.html":      "Skills - Physical",
    "skills_spell.html":         "Skills - Spell",
    "skills_normal.html":        "Skills - Normal",
    "skills_breath.html":        "Skills - Breath",
    "skills_dance.html":         "Skills - Dance",
    "field_skills.html":         "Field Skills",
    "per_species_crit_rates.html": "Critical Rates",
    "evation_rates.html":        "Evasion Rates",
    "item_resistances.html":     "Item Resistances",
}


def clean_text(s):
    """Collapse whitespace, trim."""
    if s is None:
        return ""
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    return s.strip()


def _walk_cell(node, parts):
    """Recursive descent: emit text and <br> markers, handling nested tables."""
    if isinstance(node, NavigableString):
        parts.append(str(node))
        return
    if not isinstance(node, Tag):
        return
    name = node.name
    if name == "br":
        parts.append("<br>")
        return
    if name == "table":
        parts.append(render_nested_stat_table(node))
        return
    if name in ("ol", "ul"):
        items = node.find_all("li", recursive=False)
        for k, li in enumerate(items):
            if k > 0:
                parts.append("<br>")
            parts.append(li.get_text(" ", strip=True))
        return
    if name == "p":
        # render children, then ensure a <br> boundary after the paragraph
        # (only if there is actual trailing non-whitespace)
        before = len(parts)
        for child in node.children:
            _walk_cell(child, parts)
        # add a trailing <br> if the paragraph produced content
        if len(parts) > before:
            parts.append("<br>")
        return
    # generic container / inline (strong, span, a, etc.) -> recurse
    for child in node.children:
        _walk_cell(child, parts)


def cell_md(cell):
    """Render a <td>/<th> as markdown cell text (line breaks as <br>)."""
    parts = []
    for child in cell.children:
        _walk_cell(child, parts)
    text = "".join(parts)
    # collapse runs of whitespace (but keep <br>)
    text = re.sub(r"[ \t\r\n]+", " ", text)
    # collapse 3+ consecutive <br> into a single <br>
    text = re.sub(r"(<br> ?){2,}", "<br>", text)
    # trim leading/trailing <br> and whitespace
    text = text.strip()
    text = re.sub(r"^(?:<br>| )+", "", text)
    text = re.sub(r"(?:<br>| )+$", "", text)
    return text.strip()


def render_nested_stat_table(tbl):
    """
    Render a table nested inside a skill cell.

    The common case is the per-skill stat requirements table:
      header: Lv | HP | MP | ATK | DEF | AGL | INT
      data:   values
    rendered compactly as `Lv X | HP a | MP b | ...`.

    For any other nested table (e.g. BeDragon's transform-form stat block),
    render each row as `Label value` pairs joined by <br>, preserving all
    content (handles colspan label + value cells).
    """
    rows = tbl.find_all("tr")
    if len(rows) < 1:
        return ""

    def row_cells(r):
        return [c.get_text(" ", strip=True) for c in r.find_all(["th", "td"])]

    hdr = row_cells(rows[0])

    # Detect the standard requirements table: header is exactly
    # Lv HP MP ATK DEF AGL INT (7 cols) with a single data row.
    req_signature = ["Lv", "HP", "MP", "ATK", "DEF", "AGL", "INT"]
    if [h.strip() for h in hdr] == req_signature and len(rows) >= 2:
        data = row_cells(rows[1])
        pairs = list(zip(hdr, data))
        return "<br>".join(f"{h} {v}" for h, v in pairs)

    # Generic nested table: render each row as "label(s): value(s)".
    parts = []
    for r in rows:
        cells = row_cells(r)
        if not cells:
            continue
        # If first cell looks like a label and there's a single value cell
        # (possibly merged via colspan), render as "Label value".
        nonempty = [c for c in cells if c]
        if not nonempty:
            continue
        parts.append(" ".join(nonempty))
    return "<br>".join(parts)


def get_top_rows(tbl):
    """Return <tr> elements that are direct children of <table> or <tbody>."""
    rows = tbl.find_all("tr", recursive=False)
    if not rows and tbl.tbody is not None:
        rows = tbl.tbody.find_all("tr", recursive=False)
    return rows


def is_caption_row(cells, ncol):
    """A row that is a single full-width section title: exactly one cell
    (whose colspan may span all columns)."""
    if len(cells) != 1:
        return False
    colspan = int(cells[0].get("colspan", "1") or "1")
    return colspan >= ncol or colspan == 1


def render_simple_table(tbl):
    """
    Render a *top-level* table as one or more markdown pipe tables.
    A row that is a single full-width cell (colspan across all columns) is
    treated as a section caption: it flushes the current table (if any) and
    is emitted as a bold heading, starting a new table for the rows that
    follow.
    """
    rows = get_top_rows(tbl)
    if not rows:
        return ""

    parsed = []
    for r in rows:
        parsed.append(r.find_all(["th", "td"], recursive=False))
    if not parsed:
        return ""
    ncol = max(len(c) for c in parsed)

    out_lines = []
    body = []        # accumulated rows for the current table
    have_table = False  # whether a header row has been emitted for current body

    def flush():
        nonlocal body, have_table
        if body:
            out_lines.extend(emit_md_table(body))
            body = []
            have_table = False

    for cells in parsed:
        if is_caption_row(cells, ncol):
            txt = clean_text(cells[0].get_text(" ", strip=True))
            if not txt:
                continue
            flush()
            out_lines.append(f"**{txt}**")
            out_lines.append("")
            continue
        row_md = expand_row(cells)
        while len(row_md) < ncol:
            row_md.append("")
        body.append(row_md)
    flush()
    return "\n".join(out_lines)


def expand_row(cells):
    """Convert a row's <td>/<th> cells into a markdown-cell list, expanding
    colspan attributes into repeated empty cells."""
    row = []
    for c in cells:
        colspan = int(c.get("colspan", "1") or "1")
        text = cell_md(c)
        row.append(text)
        for _ in range(colspan - 1):
            row.append("")
    return row


def emit_md_table(body):
    """Given a list of row-lists, emit a markdown table (first row = header)."""
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


def render_skill_table(tbl):
    """
    Skill category tables have a specific structure:
      Row: full-width caption (e.g. "Elemental Attacks")
      Row: header (Skill | MP | Attribute | Damage | Skill Tree | Requirements)
      Repeated per skill:
        Row: skill data, with the Requirements cell containing a nested
             stat-requirements table.
        Row: full-width "Description:" / "Mechanics:" text row.
    We flatten to: one markdown table per category, where the Requirements
    column carries the compact stat string, and the description becomes its
    own line under the table (or an extra column).
    """
    rows = get_top_rows(tbl)
    if not rows:
        return ""

    # Identify header row (the row whose cells contain the column labels).
    caption = None
    header = None
    header_idx = None
    ncol = 0
    parsed_rows = []
    for i, r in enumerate(rows):
        cells = r.find_all(["th", "td"], recursive=False)
        parsed_rows.append(cells)
        ncol = max(ncol, len(cells))

    # First non-empty single-cell full-width row is caption.
    out_lines = []
    body = []

    # find header: a row with >1 cell whose text matches known labels
    for i, cells in enumerate(parsed_rows):
        texts = [clean_text(c.get_text(" ", strip=True)) for c in cells]
        joined = " ".join(texts).lower()
        if any(k in joined for k in ("skill", "mp", "attribute", "damage",
                                     "resistance", "requirements")) and len(cells) > 1:
            header = texts
            header_idx = i
            break

    # caption: a full-width single-cell row before the header
    for i in range(header_idx if header_idx is not None else len(parsed_rows)):
        cells = parsed_rows[i]
        if len(cells) == 1:
            t = clean_text(cells[0].get_text(" ", strip=True))
            if t:
                caption = t
                break

    if caption:
        out_lines.append(f"**{caption}**")
        out_lines.append("")

    # Walk rows after header, pairing skill rows with following description rows.
    if header_idx is None:
        # no header found -> fall back to simple rendering
        return render_simple_table(tbl)

    descriptions = []  # parallel to body rows: description text or ""
    i = header_idx + 1
    skill_rows_text = []
    skill_descs = []
    while i < len(parsed_rows):
        cells = parsed_rows[i]
        if len(cells) == 1:
            # description row (full width) -> attach to previous skill
            t = clean_text(cells[0].get_text(" ", strip=True))
            if skill_rows_text:
                skill_descs[-1] = (skill_descs[-1] + ("; " if skill_descs[-1] else "") + t).strip("; ").strip()
            i += 1
            continue
        # skill data row
        row_md = []
        for c in cells:
            row_md.append(cell_md(c))
        while len(row_md) < len(header):
            row_md.append("")
        skill_rows_text.append(row_md[:len(header)])
        skill_descs.append("")
        i += 1

    # Decide whether to include a Description column.
    has_desc = any(d for d in skill_descs)
    table_header = list(header)
    if has_desc:
        table_header.append("Description")

    out_lines.append("| " + " | ".join(table_header) + " |")
    out_lines.append("|" + "|".join(["---"] * len(table_header)) + "|")
    for row, desc in zip(skill_rows_text, skill_descs):
        row_full = row + [""] * (len(header) - len(row))
        if has_desc:
            row_full.append(desc)
        out_lines.append("| " + " | ".join(row_full) + " |")
    out_lines.append("")
    return "\n".join(out_lines)


def is_skill_table(tbl):
    """Heuristic: skill tables contain a header row mentioning 'Skill'."""
    for r in get_top_rows(tbl):
        cells = r.find_all(["th", "td"], recursive=False)
        texts = [clean_text(c.get_text(" ", strip=True)).lower() for c in cells]
        joined = " ".join(texts)
        if "skill" in joined and ("mp" in joined or "requirements" in joined or "damage" in joined or "attribute" in joined):
            return True
    return False


def convert_table(tbl):
    if is_skill_table(tbl):
        rendered = render_skill_table(tbl)
        if rendered.strip():
            return rendered
    return render_simple_table(tbl)


def convert_node(node):
    """Convert a single child node of faqwrap to markdown lines."""
def inline_md(node):
    """Render inline content preserving <strong>/<b> as **bold** and
    <em>/<i> as *italic*. Returns a string."""
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ""
    name = node.name
    if name in ("strong", "b"):
        inner = "".join(inline_md(c) for c in node.children).strip()
        return f"**{inner}**" if inner else ""
    if name in ("em", "i"):
        inner = "".join(inline_md(c) for c in node.children).strip()
        return f"*{inner}*" if inner else ""
    if name == "br":
        return " "
    # container or unknown inline -> recurse
    return "".join(inline_md(c) for c in node.children)


def convert_node(node):
    """Convert a single child node of faqwrap to markdown lines."""
    if isinstance(node, NavigableString):
        t = str(node).strip()
        return [t] if t else []
    if not isinstance(node, Tag):
        return []
    name = node.name
    if name in ("h2",):
        return ["## " + clean_text(node.get_text(" ", strip=True)), ""]
    if name in ("h3",):
        return ["### " + clean_text(node.get_text(" ", strip=True)), ""]
    if name in ("h4",):
        return ["#### " + clean_text(node.get_text(" ", strip=True)), ""]
    if name in ("p",):
        t = clean_text(inline_md(node))
        return [t, ""] if t else []
    if name == "table":
        return [convert_table(node)]
    if name == "hr":
        return ["---", ""]
    if name == "ul":
        out = []
        for li in node.find_all("li", recursive=False):
            out.append("- " + clean_text(li.get_text(" ", strip=True)))
        if out:
            out.append("")
        return out
    if name == "ol":
        out = []
        for j, li in enumerate(node.find_all("li", recursive=False), 1):
            out.append(f"{j}. " + clean_text(li.get_text(" ", strip=True)))
        if out:
            out.append("")
        return out
    if name in ("div",):
        out = []
        for child in node.children:
            out.extend(convert_node(child))
        return out
    # fallback
    t = clean_text(node.get_text(" ", strip=True))
    return [t, ""] if t else []


def html_to_md(html_path):
    with open(html_path, encoding="utf-8", errors="replace") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    wrap = soup.find(id="faqwrap")
    if wrap is None:
        return None, "no #faqwrap found"
    # strip TOC
    ftoc = wrap.find("div", class_="ftoc")
    if ftoc is not None:
        ftoc.decompose()

    out = []
    for child in wrap.children:
        out.extend(convert_node(child))

    # collapse 3+ blank lines, trim
    md = "\n".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return md, None


def make_header(title, slug):
    return (
        f"# {title}\n\n"
        f"> Source: McBick \"Advanced Skill Guide\" FAQ #78461, v4.0 (GameFAQs, saved HTML)\n"
        f"> GameFAQs URL: https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461/{slug}\n"
        f"> Captured: 2026-07-05 from browser-saved HTML\n\n"
        f"---\n\n"
    )


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1:
        targets = sys.argv[1:]
    else:
        targets = list(FAFAQ_SLUG.keys())
    for fn in targets:
        path = os.path.join(here, fn)
        if not os.path.exists(path):
            print(f"MISS: {fn}", file=sys.stderr)
            continue
        md, err = html_to_md(path)
        if err:
            print(f"ERR  {fn}: {err}", file=sys.stderr)
            continue
        slug = FAFAQ_SLUG[fn]
        title = FAFAQ_TITLE[fn]
        full = make_header(title, slug) + md
        out_path = os.path.join(here, "__preview__" + slug.replace("-", "_") + ".md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full)
        print(f"OK   {fn} -> {out_path} ({len(md)} body chars)")
