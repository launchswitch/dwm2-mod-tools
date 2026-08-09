# Capture Status — McBick "Advanced Skill Guide" FAQ #78461

Target: complete text of every section of the McBick "Advanced Skill Guide" FAQ for
Dragon Warrior Monsters 2: Cobi's Journey (GameFAQs FAQ #78461), to serve as
the skill database reference for the hacking tool.

## Current state: v4.0 capture COMPLETE

All 12 sections of the current GameFAQs **v4.0** (2025-02-04) FAQ are captured
verbatim from browser-saved HTML pages. The earlier v1.1 (Neoseeker mirror)
capture is retained only where it documents details the v4.0 pages omit; those
files carry a note explaining their status.

## Capture route

- **GameFAQs live site is Cloudflare-protected.** Plain `curl` gets a 403.
  The `mcp__web_reader__webReader` tool penetrates Cloudflare but truncates
  long results, so large skill tables could not be transcribed through it.
- **Browser save-as-complete + offline parse (THIS capture, 2026-07-05).**
  Each of the 10 v4.0 section pages was saved from a real browser session
  (Cloudflare challenge solved) as `<section>.html` (+ a `*_files/` asset dir,
  ignored). The FAQ body lives in `<div id="faqwrap">`; chrome (nav, ads,
  related-games sidebar, JS, the in-page Table of Contents) was stripped.
  Conversion was done with `extract.py` (BeautifulSoup) — it handles prose,
  headings, pipe tables, the per-skill nested stat-requirements tables, and
  colspan/rowspan. Source HTML and the script are kept in this dir for
  reproducibility.
- **Neoseeker mirror** (v1.1, single-page, not Cloudflare-protected) was the
  source for the first capture. URL:
  https://www.neoseeker.com/dwm2/faqs/3080761-dragon-quest-monsters-2-cobis-journey-advanced-skill.html

## Per-section status

| # | v4.0 Section (slug) | Status | File | Source | Notes |
|---|---|---|---|---|---|
| 1 | Intro to Skills (`intro-to-skills`) | OK | intro.md | v4.0 HTML | Replaces v1.1 author-note-only intro. Has the 6 skill-type descriptions + `[ATK/2 - DEF/4]` formula |
| 2 | List of Attributes (`list-of-attributes`) | OK | list-of-attributes.md | v4.0 HTML | All 27 attribute codes (A–Z, Æ) decoded to their skill lists |
| 3 | Skills - Physical (`skills-physical`) | OK | skills-physical.md | v4.0 HTML | Elemental / Debilitating / Physical / Monster / Defensive tables, every skill with MP, attribute, damage modifiers, skill tree, stat requirements, description+mechanics |
| 4 | Skills - Spell (`skills-spell`) | OK | skills-spell.md | v4.0 HTML | Attacks / Support / Healing tables (incl. BeDragon transform block, Chance effect table) |
| 5 | Skills - Normal (`skills-normal`) | OK | skills-normal.md | v4.0 HTML | Attacks / Support / Healing tables, incl. level-scaling damage (WindBeast/Vacuum/Lightning/CallHelp/YellHelp) |
| 6 | Skills - Breath (`skills-breath`) | OK | skills-breath.md | v4.0 HTML | Attacks (FireAir/IceAir trees) + Support (status breaths) |
| 7 | Skills - Dance (`skills-dance`) | OK | skills-dance.md | v4.0 HTML | Attacks / Support / Healing |
| 8 | Field Skills (`field-skills`) | OK | field-skills.md | v4.0 HTML | All 8 overworld skills (Whistle, Pheromone, StepGuard, Outside, Informer, Erand, EagleEye, MapMagic) |
| 9 | Critical Rates (`critical-rates`) | OK | critical-attributes.md | v4.0 HTML | Replaces v1.1 Slime-only table. Has the revised mechanics prose, attribute/courage/motivation rate tables, and per-species crit rates for ALL 11 families + Secret Monsters |
| 10 | Evasion Rates (`evasion-rates`) | OK | evasion.md | v4.0 HTML + v1.1 | v4.0 size/AGI tables + Secret Monsters + DEF mechanic; v1.1 SideStep/max-42 mechanic appended (v4.0 page omits SideStep) |
| 11 | Item Resistances (`item-resistances`) | OK | list-of-item-resistances.md | v4.0 HTML | All 7 capes, every resistance type with full skill lists |
| 12 | Version Info (`version-info`) | n/a | — | — | NOT in the 10 saved HTML files. v1.1 changelog only is in version-updates.md (see below) |

## Retained v1.1-only files (cross-references; v4.0 has no direct equivalent)

These came from the v1.1 Neoseeker mirror and document details the v4.0 pages
either omit or distribute across other sections. Each carries a header note
explaining its status.

| File | Why retained |
|---|---|
| critical-attacks.md | Per-skill crit rates for EvilSlash (64/128) and Massacre (128/128), and the max crit rate (11/128) — not restated on the v4.0 Critical Rates page |
| list-of-resistance-multipliers.md | Canonical summary of resistance 0–3 → damage multiplier / success rate. v4.0 embeds these per-skill but has no standalone summary |
| list-of-battle-skills.md | v1.1 consolidated skill list grouped by attribute. Superseded by the v4.0 type-split tables but kept as a cross-reference |
| version-updates.md | v1.1 changelog. The v4.0 version-info page was not among the saved HTML files |

## Reproducibility

- `extract.py` — BeautifulSoup converter that produced all the v4.0 `.md`
  files from the saved `*.html`. Run `python3 extract.py` to regenerate the
  `__preview__*.md` files; the final files were copied/edited from those.
- `*.html` + `*_files/` — the original saved GameFAQs pages (kept as the
  source of truth).

## Version note

- Captured version: **v4.0** (GameFAQs, updated 2025-02-04), via browser-saved HTML.
- Previous capture: v1.1 (Neoseeker, 2020-07-16) — retained files noted above.
- All core mechanics data (damage formulas, resistance multipliers, status
  durations, evasion rules, critical-attack rules, item resistance bonuses)
  is present in v4.0; the v4.0 capture is the authoritative source.
