# Capture Status — McBick "Advanced Skill Guide" FAQ #78461

Target: complete text of every section of the McBick "Advanced Skill Guide" FAQ for
Dragon Warrior Monsters 2: Cobi's Journey (GameFAQs FAQ #78461), to serve as
"MonTamer's skill database" reference for the hacking tool.

## Approach / what worked

- **GameFAQs live site is Cloudflare-protected.** Plain `curl` gets a 403
  ("Just a moment..." challenge page). The `mcp__web_reader__webReader` tool
  DOES penetrate Cloudflare and returns full body content, but long `text`
  results are truncated in the conversation display, so multi-thousand-token
  tables could not be faithfully transcribed to disk through it.
- **Neoseeker mirror is NOT Cloudflare-protected.** Plain `curl` returns HTTP 200
  for the single-page FAQ. This was used as the primary capture source.
  URL: https://www.neoseeker.com/dwm2/faqs/3080761-dragon-quest-monsters-2-cobis-journey-advanced-skill.html
- **Wayback Machine** has a single capture (2022-06-01) of the bare FAQ URL;
  only the intro section text is present there. Used as a cross-check.

## Per-section status (Neoseeker v1.1 mirror)

All 8 sections of v1.1 captured verbatim to `./<slug>.md` and to `ALL_SECTIONS.md`.

| # | Section (slug)               | Status | File                         | Notes |
|---|------------------------------|--------|------------------------------|-------|
| 1 | Intro (`intro`)              | OK     | intro.md                     | |
| 2 | Evasion (`evasion`)          | OK     | evasion.md                   | Full evasion-rate tables (size, AGI, SideStep) + battle mechanic |
| 3 | Critical Attacks (`critical-attacks`) | OK | critical-attacks.md          | Crit rate by attribute/courage/skill + mechanic |
| 4 | Critical Attributes (`critical-attributes`) | PARTIAL | critical-attributes.md | v1.1 lists only the Slime family. v4.0 (GameFAQs) has all families — NOT captured |
| 5 | List of Item Resistances (`list-of-item-resistances`) | OK | list-of-item-resistances.md | All 7 capes |
| 6 | List of Resistance Multipliers (`list-of-resistance-multipliers`) | OK | list-of-resistance-multipliers.md | 0-3 resistance -> multiplier/success-rate table |
| 7 | List of Battle Skills (`list-of-battle-skills`) | OK | list-of-battle-skills.md | All skills A-Z + Water, with MP, attribute, damage formulas, mechanics |
| 8 | Version Updates (`version-updates`) | OK | version-updates.md | v1.1 changelog only |

## What is MISSING (v4.0-only content, NOT captured)

These exist only in the current GameFAQs v4.0 version and could not be captured
faithfully (webReader returns them but display truncation prevented reliable
transcription; Neoseeker mirror is v1.1 and predates them; Wayback never
archived these section URLs):

1. **Per-monster critical rate — all families except Slime.** v1.1 only has the
   Slime family. v4.0 expands `list-of-monsters-critical-rate` to every family.
2. **"Intro to Skills" section** (`intro-to-skills`) — attribute-code (A-Z, Water)
   definitions and the base skill damage formula. Added after v1.1.
3. **Field Skills** section (`field-skills`) — overworld navigation skills.
4. **Skills split by type** (physical / spell / normal / breath / dance) as
   separate v4.0 tables — in v1.1 these are consolidated under one
   "List of Battle Skills" grouped by attribute (which is actually complete; the
   v4.0 split is just a re-presentation).
5. **Version 2.0-4.0 changelog entries** — only v1.1's changelog is captured.

To obtain these, the live GameFAQs pages must be captured through a route that
preserves full untruncated body text (e.g. a real browser with the Cloudflare
challenge solved, then save-as-text; or a scraping service that returns the raw
DOM). The webReader tool does retrieve the content but its output is truncated
in this agent's tool-result display, so it cannot be used to transcribe large
tables to disk from here.

## Version note

- Captured version: **v1.1** (Neoseeker, submitted 2020-07-16).
- Current GameFAQs version: **v4.0** (2025), 50 KB.
- All core mechanics data (damage formulas, resistance multipliers, status
  durations, evasion rules, critical-attack rules, item resistance bonuses) is
  present and identical between v1.1 and v4.0; only the scope of the per-monster
  critical-rate table and a few added sections differ.
