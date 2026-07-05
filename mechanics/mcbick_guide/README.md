# McBick Advanced Skill Guide — Captured Reference

Source: [McBick's "Advanced Skill Guide" FAQ #78461](https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461) for Dragon Warrior Monsters 2: Cobi's Journey.

Captured: 2026-07-05 from the [Neoseeker mirror](https://www.neoseeker.com/dwm2/faqs/3080761-dragon-quest-monsters-2-cobis-journey-advanced-skill.html) (single-page, not Cloudflare-protected). Version: **v1.1** (2020).

## Why this matters

This FAQ is the **combat-resolution spec** for DWM2. Where `dwm2-hacking-tools/` had data tables (skill MP costs, damage values, resistance bytes) but the *resolution rules* were [Unknown] (damage formula, crit rates, evasion, resistance value semantics, status durations), this guide closes those gaps with concrete formulas.

Per-section value for MonTamer:

| File | Closes which coverage_map gap |
|------|-------------------------------|
| `list-of-resistance-multipliers.md` | **Resistance value semantics** (0=weak×1.5, 1=normal×1, 2=resist×0.5, 3=immune×0) + success rates for status skills |
| `list-of-battle-skills.md` | **Skill database** — every skill with MP, type, damage multiplier, targeting, status durations, success rates, buff mechanics, priority rules |
| `critical-attacks.md` | **Critical-hit formula** (attribute 0-3 → 0/1/2/4 of 128, plus courage, plus skill-specific rates for EvilSlash/Massacre) |
| `evasion.md` | **Hit/evasion formula** (size tier + AGI-difference tier + skill, max 42/100, min 1/100) |
| `critical-attributes.md` | Per-species crit attribute (Slime family only in v1.1; v4.0 has all families — see STATUS.md) |
| `list-of-item-resistances.md` | The 7 capes and which resistances they grant |
| `intro.md` | Author's scope note |

## What's still missing (v4.0-only, behind Cloudflare)

Captured version is v1.1. The current GameFAQs version is v4.0, which adds:
1. Per-monster critical-rate table expanded to all families (v1.1 has only Slime)
2. "Intro to Skills" section with attribute-code definitions and the basic damage formula `[ATK/2 - DEF/4]`
3. Field Skills section
4. Skills split by type (physical/spell/normal/breath/dance) as separate tables (v1.1 consolidates these under one "List of Battle Skills" grouped by attribute — the data is complete, just re-presented in v4.0)
5. v2.0-4.0 changelog entries

See `STATUS.md` for the per-page capture log and notes on how to obtain v4.0-only content (real browser session through Cloudflare).

## Damage formula (basic attack)

From the v4.0 "Intro to Skills" section (visible in web reader but not captured verbatim — see STATUS.md):

> Basic attack damage = `[ATK/2 - DEF/4]`, then modified by skill multiplier, then by resistance multiplier (above).

## Files

- `ALL_SECTIONS.md` — combined doc, all 8 v1.1 sections
- `intro.md`, `evasion.md`, `critical-attacks.md`, `critical-attributes.md`, `list-of-item-resistances.md`, `list-of-resistance-multipliers.md`, `list-of-battle-skills.md`, `version-updates.md` — per-section
- `STATUS.md` — capture log + per-page status

## Provenance & licensing

McBick's FAQ is publicly hosted on GameFAQs and mirrored on Neoseeker. Captured here as reference for the MonTamer reimplementation project per the same "specification, not starting point" posture used for the rest of `dwm2-hacking-tools/`. Credit: McBick (author), 2020.
