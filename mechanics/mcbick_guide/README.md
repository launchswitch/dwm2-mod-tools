# McBick Advanced Skill Guide — Captured Reference

Source: [McBick's "Advanced Skill Guide" FAQ #78461](https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461) for Dragon Warrior Monsters 2: Cobi's Journey.

**Captured: 2026-07-05 — v4.0 complete.** The current GameFAQs v4.0 (updated
2025-02-04) was captured from browser-saved HTML (Cloudflare challenge solved
in a real browser, pages saved as complete HTML, then parsed offline with
`extract.py`). All 11 in-FAQ sections present in the saved pages are
transcribed verbatim. See `STATUS.md` for the per-page log.

## Why this matters

This FAQ is the **combat-resolution spec** for DWM2. Where this repo's data tables (skill MP costs, damage values, resistance bytes) had
*resolution rules* were [Unknown] (damage formula, crit rates, evasion,
resistance value semantics, status durations), this guide closes those gaps
with concrete formulas.

Per-section value:

| File | Closes which coverage_map gap |
|---|---|
| `intro.md` | Skill-type taxonomy + the basic-attack damage formula `[ATK/2 - DEF/4]` |
| `list-of-attributes.md` | All 27 attribute codes (A–Z, Æ) decoded to their skill lists |
| `skills-physical.md` | **Skill database (physical)** — every skill with MP, attribute, damage modifiers, skill tree, stat requirements, description + mechanics |
| `skills-spell.md` | **Skill database (spell)** — attacks / support / healing |
| `skills-normal.md` | **Skill database (normal)** — attacks / support / healing, incl. level-scaling damage |
| `skills-breath.md` | **Skill database (breath)** — attacks / support |
| `skills-dance.md` | **Skill database (dance)** — attacks / support / healing |
| `field-skills.md` | The 8 overworld navigation skills |
| `critical-attributes.md` | **Critical-hit data (v4.0 full)** — attribute/courage/motivation rate tables + per-species crit rates for ALL 11 families + Secret Monsters |
| `evasion.md` | **Hit/evasion formula** — size tier + AGI-difference tier + DEF mechanic + SideStep (max 42/100, min 1/100) |
| `list-of-item-resistances.md` | The 7 capes and which resistances (full skill lists) they grant |
| `list-of-resistance-multipliers.md` | **Resistance value semantics** (0=weak×1.5, 1=normal×1, 2=resist×0.5, 3=immune×0) + success rates for status skills |
| `critical-attacks.md` | Per-skill crit rates (EvilSlash 64/128, Massacre 128/128) + max crit 11/128 — v1.1 detail not on v4.0 page |

## Files

### v4.0 capture (authoritative, from saved HTML)

- `intro.md`, `list-of-attributes.md`, `skills-physical.md`, `skills-spell.md`,
  `skills-normal.md`, `skills-breath.md`, `skills-dance.md`, `field-skills.md`,
  `critical-attributes.md`, `evasion.md`, `list-of-item-resistances.md`

### Retained v1.1 cross-references

- `critical-attacks.md` — per-skill crit rates + max crit (not on v4.0 page)
- `list-of-resistance-multipliers.md` — canonical resistance-value summary
- `list-of-battle-skills.md` — v1.1 consolidated skill list (superseded by the type-split tables above)
- `version-updates.md` — v1.1 changelog (v4.0 version-info page was not saved)

### Combined / status

- `ALL_SECTIONS.md` — combined v1.1 doc (predates the v4.0 capture)
- `STATUS.md` — capture log + per-page status

### Source / reproducibility

- `*.html` + `*_files/` — the original saved GameFAQs pages (source of truth)
- `extract.py` — BeautifulSoup converter that produced the v4.0 `.md` files

## Damage formula (basic attack)

From the v4.0 "Intro to Skills" section:

> Basic attack damage = `[ATK/2 - DEF/4]`, then modified by the skill's damage
> modifier (see each skill table), then by the target's resistance multiplier
> (0=×1.5, 1=×1, 2=×0.5, 3=×0).

## Provenance & licensing

McBick's FAQ is publicly hosted on GameFAQs. Captured here as reference for
the DWM2 modding community, per the same "specification, not starting
point" posture used for the rest of this repo. Credit: McBick
(author). v4.0 captured 2026-07-05 from browser-saved HTML; v1.1 cross-
references from the Neoseeker mirror (2020).
