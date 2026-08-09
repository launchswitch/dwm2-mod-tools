# DWM2 Stat Growth & Personality — Research Findings

**Date:** 2026-07-05
**Author:** Investigation agent (reimplementation reference)
**Scope:** INVESTIGATION AND FINDINGS ONLY. No design, no code, no recommendations.
**Predecessor:** [`personality_research_findings.md`](./personality_research_findings.md) (read first — established the 4-trait / 27-personality model and that Charge/Mixed/Defend/Command are battle tactics, not personalities).

**Keystone question:** *Does personality (or the 4 traits) affect level-up STAT GROWTH in DWM2, or is stat growth purely species-driven?*

**Confidence legend** (used on every claim below):
- **[ROM-verified]** — pointable address / table / byte offset in this repo's extracted data
- **[Wiki-documented]** — described on dragon-quest.org wiki or community guides; not confirmed in our ROM extraction
- **[Unknown]** — looked, could not determine

---

## Direct Answer

**In DWM2 specifically, personality/traits do NOT appear to feed level-up stat growth — stat growth is species-driven (per-species growth bytes combined with a shared per-level table), and the personality/trait system governs AI behavior, obedience/wildness, and in-battle "special actions" instead.** This is **[Wiki-documented, strongly supported by negative ROM evidence]** — see Q2 for the evidentiary basis. The personality→stat-growth mechanic *does* exist in the Dragon Quest franchise (notably the DQIII remakes), but the DWM2-specific section of the wiki's Personality page describes personality's effects as AI/obedience/special-action only, with no mention of stat growth. Our local ROM extraction contains no code path or table reference connecting personality/traits to the stat-growth routine (Q2).

**Confidence in the direct answer:** Medium-high. The wiki's DWM2 section omits stat growth, the wiki's DQIII section explicitly includes it, and our ROM data has zero personality→growth linkage — three convergent signals. The only residual uncertainty is that the stat-growth *routine's disassembly* is not in this repo (no code, only data tables), so the negative is "no evidence of linkage in mapped data + wiki describes no linkage," not "we read the routine and confirmed personality is absent."

---

## Q1: The 0x6A616 stat-growth table

### What the local extraction documents [ROM-verified]

- **Address & shape:** `rom_maps/rom_map.txt:68` — `6A616  stat growth tables (1 byte entries, 99 entries per table)`. The plural "tables" and the parenthetical "99 entries per table" indicate this is **a region of multiple stacked 99-byte tables**, not a single 99-byte table. `tools/mod_data.py:301-311` (`TABLE_STAT_GROWTH`) defines only the *first* 99 entries as an editable table — `"num_entries": 99`, one `growth_value` byte each — so the editor exposes one tier; the surrounding tiers (one per stat, or one per growth-rate-class) are in the same ROM region but not separately mapped.

- **Function (inferred from structure + neighbors):** It is a **per-level lookup** indexed by level (1–99). Each byte is a multiplier/accumulator contribution applied during level-up stat computation. It is **NOT indexed by species** (species growth lives separately at `0xD433B` — see below) and **NOT indexed by personality/trait** (no personality table is near this address; the personality/tactic tables are at `0xC138C`, ~95 KB away in a different bank — `rom_map.txt:72-75`).

- **How it combines with species growth bytes [ROM-verified, mechanism inferred]:** The per-species growth rates live in the **core monster species template** — `monster_data/core_monster_data.md:50-55` (bytes 12–17: `HP growth`, `MP growth`, `Attack growth`, `Defense growth`, `Agility growth`, `Intelligence growth`, one byte each), mirrored in `tools/mod_data.py:398-403` (`hp_growth` … `int_growth`). The DWM2U ReadMe (`dwm2u_reference/DWM2U ReadMe.txt:40`) states monsters' "stats are built using **in-game stat growth tables** and a **custom lv 1 formula**," and `dwm2u_analysis.md:23-28` confirms "stat growth tables are still used, but the base is higher." So the model is: **species growth byte (rate) × per-level table value (curve) + base** — species provides the per-stat rate, the `0x6A616` region provides the shared level curve. Neither input is personality-derived.

### What is NOT documented locally [Unknown / out of scope]

- The exact number of stacked 99-byte tables in the `0x6A616` region (could be 6, one per stat, or could be growth-rate-tier tables). The region between `0x6A616` and the next mapped table (`0x6D1B6` censored names) is ~11 KB — far larger than 6×99=594 bytes — so other unmapped data is interleaved. Resolving the precise table count and the multiplication/addition formula requires disassembly of the level-up routine, which is not in this repo. [Unknown]

---

## Q2: Does any personality/trait byte feed the stat-growth routine?

### Negative evidence (no linkage found) [ROM-verified absence]

A full search of the local extraction for any code path, table reference, or doc note connecting personality/traits to stat growth found **none**:

- `rom_maps/rom_map.txt` lists `stat growth tables` at `0x6A616` (line 68) and the four `…'s effect on personality` tactic tables at `0xC138C–0xC13EC` (lines 72-75). These are **~95 KB apart in different ROM banks** (bank `0x1A`-ish vs bank `0x30`). No entry in `rom_map.txt` references personality in the stat-growth region, and no entry references stat growth in the personality region.
- `tools/mod_data.py` — the table registry (lines 575-679) places `stat_growth` (lines 301-311) and the four `personality_*` tables (lines 485-543) in fully separate table definitions with no shared field, index, or cross-reference. The `stat_growth` table has a single field `growth_value`; the personality tables have `stat_id`/`modifier_hi`/`modifier_lo`/`flag`. There is no field naming a personality or trait index in any growth table.
- `monster_data/core_monster_data.md` — the 47-byte species template (lines 36-57) has **no personality, trait, or motivation byte at all** (confirmed in prior findings, Q5(3)). All 47 bytes are accounted for by family/gender/flying/metal/join/level/exp/skills/6 growth bytes/27 resistances/base-exp. Personality is per-instance, not per-species. [ROM-verified]
- The prebuilt-enemy struct (`ram_map.md:120-144`, `mod_data.py:325-354`) stores both stats (offsets 10–20) and the 4 trait/aptitude bytes (offsets 22–25) **adjacently**, but the trait bytes come *after* the fully-resolved stat block — i.e. stats are stored as final values, not computed-from-traits at read time (see Q4).
- No file in the repo (`*.md`, `*.py`, `*.txt`) contains a sentence asserting or depicting personality influencing the level-up stat computation. The only co-occurrences of "personality" + "growth"/"stat" are (a) the table *descriptions* in `mod_data.py` ("stat modifier entries" describing the tactic tables' 4-byte layout — a field-naming comment, not a stat-growth claim) and (b) the predecessor `personality_research_findings.md` itself.

### The tactic tables at 0xC138C do NOT feed stat growth [ROM-verified address + Wiki-documented purpose]

Per the predecessor findings (Q2 of that doc), the four tables at `0xC138C–0xC15FC` are **tactic→trait-DELTA tables**: they describe how performing a tactic (Charge/Mixed/Defend/Command) shifts the hidden traits (Bravery/Prudence/Caring/Motivation), driving **personality drift** over time. They are not consulted at level-up. They sit in the battle-logic bank, not the stat-growth region. The byte-level meaning of their `stat_id`/`modifier_*` fields is still [Unknown] without a ROM dump, but their *placement* and the wiki's description of tactics-as-trait-drifters both indicate they mutate traits, not stats.

### Convergent wiki signal [Wiki-documented]

The dragon-quest.org wiki **Personality** page has a **DWM/DWM2-specific section** that enumerates personality's mechanical effects: AI action selection, obedience/wildness, and "special actions" (autonomous healing, etc.). **Stat growth is NOT among the listed DWM2 effects.** The same page's *Dragon Quest III remakes* section explicitly *does* list "modifies stat growth on level up" as a personality effect there. The presence of the stat-growth effect under DQIII and its **absence under DWM2** on the same page is strong evidence the mechanic was dropped (or never present) for the Monsters sub-series. (Cross-checked via web fetch of the page; the DWM2 section's effect list does not contain a growth/stat entry.)

---

## Q3: What does personality mechanically affect (per our ROM data)?

**Honest answer: per our extracted ROM data, personality has NO mapped mechanical effect at all.** Every downstream effect listed in the prior findings (AI behavior, obedience/defiance, crit modifiers, MP-free heals, co-op eligibility) is **[Wiki-documented only]** — none has a pointable ROM address in this repo. The prior findings doc already established this (its Q4 summary table: all five effects = "Not mapped" in this repo).

What our ROM data *does* contain for the personality system is just **two storage artifacts**, neither of which is an *effect* table:

1. **The four tactic→trait-delta tables** (`0xC138C–0xC15FC`, `mod_data.py:485-543`) — these describe how tactics *change* traits, i.e. the *input* side of personality drift, not what personality *does*. [ROM-verified]
2. **The 4 trait/aptitude bytes in the prebuilt-enemy struct** (offsets 22–25: `charge_aptitude`, `defense_aptitude`, `motivation`, `mixed_aptitude`) — these are *stored per-encounter*, alongside but mechanically downstream of the stats (see Q4). [ROM-verified]

So within the four corners of this repo, personality is **stored and drifted, but its effects are entirely in unmapped code** (the AI/obedience/special-action routines in the battle bank near `0xC138C`, none of which are disassembled here). The personality→effect mappings (27-personality definition table, AI weights, obedience thresholds, crit/heal trigger tables, co-op eligibility) all exist in the DWM2 ROM but are **not part of this extraction** — locating them needs disassembly work (e.g. via the upstream `niyadev/dwm2_disassembly_github`).

---

## Q4: Wild/encountered monster stat computation — species+level, or species+level+traits?

**Answer: species + level (+ prebuilt overrides). The 4 trait bytes are stored alongside stats but are NOT inputs to the stat values in the struct.** [ROM-verified struct layout; inferred data flow]

### Evidence

The prebuilt-enemy struct (`ram_map.md:120-144`, `battle_breeding_map.md:33-55`, `mod_data.py:325-354`) stores, per encounter:

| Offsets | Content |
|---|---|
| `+0x00` | species ID |
| `+0x09` | level |
| `+0x0A`–`+0x14` | **fully-resolved final stats**: HP, MP, Attack, Defense, Agility, Intelligence (each LE u16) |
| `+0x16`–`+0x19` | the 4 trait/aptitude bytes (charge/defense/motivation/mixed) |

Three observations that jointly answer Q4:

1. **The stats are stored as final 2-byte values, not as growth-rates-to-be-applied.** For *party* monsters, the game computes stats at level-up from species growth × level curve (Q1). But for *prebuilt/wild* monsters, the encounter struct **bakes the final numbers in** — the designer hardcoded HP/MP/ATK/DEF/AGI/INT per prebuilt entry. So when a wild encounter is built, the game does **not** compute stats from species+level at encounter time; it **copies the prebuilt struct's final stats** into WRAM (`battle_breeding_map.md:98-107`: "Copies 26-byte prebuilt struct from ROM … into WRAM"). The species ID and level in the struct are used for *other* purposes (breeding eligibility, EXP yield, display), and the growth bytes at `0xD433B` are used *after* recruitment when the monster levels up in the player's party. [ROM-verified]

2. **The trait bytes (`+0x16`–`+0x19`) sit AFTER the stat block**, and there is no field in the struct linking them to the stats. If traits fed the stat numbers, you'd expect either (a) the stats to be stored as growth rates + a trait modifier recomputed at load, or (b) a documented pointer/formula tying the two. Neither exists. The layout is "stats (final), then traits (for AI/personality)" — two logically independent blocks within one struct. [ROM-verified layout; inferred independence]

3. **No routine in this repo reads the trait bytes to compute stats.** The encounter-load path (`battle_breeding_map.md:98-107`) is a straight 26-byte memcpy from ROM to the WRAM working buffer; no transformation involving traits is documented. The level-up stat routine (which *would* consult growth bytes + the `0x6A616` table) is not disassembled here, but its inputs are the species template (`0xD433B`, which has no trait bytes — Q2) and the level table — again, no traits. [ROM-verified that no linkage is mapped; Unknown re: the unmapped routine]

**Net:** For a *wild* encounter, the monster's stats are the prebuilt struct's hardcoded values (which the original game authors derived from species+level when they authored the table, but which are not recomputed at runtime from traits). The 4 trait bytes ride along in the same struct to drive the monster's **AI behavior and obedience** during the battle and to seed its starting personality if recruited — not to compute its HP/ATK/etc. For a *party* monster leveling up, stats come from species growth × level curve, again with no trait input. In neither path do the trait bytes participate in stat computation.

---

## Implication for stat calculators

**Factual implication only (not a design recommendation):** A `Compute(growth, level, personality, modifiers)` stat model — which multiplies each stat by a per-personality modifier — encodes a mechanic (personality→stat-growth) that, per the evidence above, **does not correspond to anything in DWM2's stat-growth path**. In DWM2:

- Stat growth inputs = **species growth bytes + per-level table** (no personality). [ROM-verified inputs]
- Personality's mechanical effects = **AI, obedience, special actions** — none of which are stat-multipliers anyway. [Wiki-documented effects; none mapped in ROM]

So the `personality` parameter in `StatCalculator` is carrying a mechanic that the source game applies elsewhere (battle behavior), not at stat-computation time. Whether to drop it, repurpose it, or keep it as an original-design choice is a **design decision** and out of scope for this findings doc. The factual point is: **a faithful DWM2 stat-growth model takes species growth + level only; personality is not an input.**

---

## Confidence Summary

| Claim | Confidence |
|---|---|
| `0x6A616` is a per-level stat-growth table region (≥1 table of 99 bytes); not indexed by species or personality | **[ROM-verified]** (address, "99 entries per table" plural note, single exposed table) |
| Per-species growth bytes (core template offsets 12–17) combine with the level table to drive growth | **[ROM-verified]** that both inputs exist and are the documented growth fields; **[inferred]** that they combine by multiplication/addition (formula not disassembled) |
| The species template (`0xD433B`) contains NO personality/trait/motivation byte | **[ROM-verified]** (all 47 bytes accounted for — `core_monster_data.md:36-57`) |
| The tactic tables (`0xC138C`) drive trait drift, not level-up stat growth | **[ROM-verified]** addresses/bank placement + **[Wiki-documented]** tactic→trait behavior; byte-level table meaning **[Unknown]** without a ROM dump |
| No personality/trait→stat-growth code path or table reference exists in this repo | **[ROM-verified absence]** (exhaustive grep of `*.md`/`*.py`/`*.txt`; no co-occurrence in growth region) |
| DWM2's personality affects AI/obedience/special-actions, NOT stat growth | **[Wiki-documented]** (DWM2 section of wiki Personality page omits growth; DQIII section includes it — strong differential signal) |
| Wild/prebuilt monster stats are hardcoded final values copied verbatim into WRAM, not recomputed from traits at encounter | **[ROM-verified]** struct layout + memcpy load path; **[inferred]** that traits are not also consulted (no mapped linkage) |
| The exact level-up stat formula (how growth byte × level-table value combines, randomness, "+breed" bonuses) | **[Unknown]** — routine not disassembled in this repo; community sources mention partial randomness and `+`-breed HP/ATK bonuses (`woodus.com` forums) but no personality involvement |
| The 27-personality definition table's ROM address and personality→effect tables | **[Unknown]** — not in this extraction (carried over from prior findings, Gaps 1 & 6) |

---

## Sources

### Local extracted data (`/home/frank/repos/dwm2-hacking-tools/`)
- `rom_maps/rom_map.txt:68` — `stat growth tables` at `0x6A616` ("1 byte entries, 99 entries per table").
- `rom_maps/rom_map.txt:72-75` — four tactic/personality effect tables at `0xC138C–0xC13EC` (different bank from stat growth).
- `rom_maps/ram_map.md:120-144` — prebuilt enemy struct: stats at `+0x0A`–`+0x14`, trait/aptitude bytes at `+0x16`–`+0x19`.
- `rom_maps/battle_breeding_map.md:33-55` — prebuilt struct layout (cross-confirm); `:98-107` — encounter load path (26-byte ROM→WRAM memcpy, no trait-based recomputation).
- `monster_data/core_monster_data.md:36-57` — 47-byte species template; bytes 12–17 = the 6 growth bytes; **no personality/trait/motivation byte present**.
- `tools/mod_data.py:301-311` — `TABLE_STAT_GROWTH` (offset `0x6A616`, 99 entries, 1 `growth_value` byte each).
- `tools/mod_data.py:325-354` — `TABLE_PREBUILT_ENEMIES` (stats offsets 10–20; trait bytes offsets 22–25).
- `tools/mod_data.py:379-437` — `TABLE_CORE_MONSTER` (growth bytes at offsets 12–17; no personality field).
- `tools/mod_data.py:485-543` — four `TABLE_PERSONALITY_*` tactic tables (8×4 bytes each; `stat_id`/`modifier_hi`/`modifier_lo`/`flag`).
- `dwm2u_reference/DWM2U ReadMe.txt:40` — "Monster stats are built using in-game stat growth tables and a custom lv 1 formula."
- `dwm2u_reference/dwm2u_analysis.md:23-28` — "Stat Growth System": stat growth tables used, base adjusted; no personality mention.

### Cross-referenced wiki & community sources (web)
- [Personality — Dragon Quest Wiki](https://dragon-quest.org/wiki/Personality) — DWM2-specific section lists AI/obedience/special-action effects; **stat growth absent**. DQIII-remakes section on the same page **does** list stat-growth modification — the differential is the key signal.
- [List of personality types in Dragon Quest Monsters — Dragon Quest Wiki](https://dragon-quest.org/wiki/List_of_personality_types_in_Dragon_Quest_Monsters) — the 4-trait / 27-personality model (Bravery/Prudence/Caring + Motivation).
- [Personalities — Dragon Warrior Monsters Walkthrough & Guide (GameFAQs, RSlickback)](https://gamefaqs.gamespot.com/gbc/197155-dragon-warrior-monsters/faqs/80057/personalities) — per-personality trait tiers, tactic→trait deltas, Motivation mechanics (no stat-growth-per-personality table).
- [Plusses and Stat Growth — Woodus.com Forums](https://www.woodus.com/forums/topic/9087-pluses-and-stat-growth/) — DWM2 stat growth is partly random; `+`-breed bonuses boost HP/ATK growth (a breeding mechanic, not a personality mechanic).
- [How important is personality? — Dragon Warrior Monsters (GameFAQs board)](https://gamefaqs.gamespot.com/boards/197155-dragon-warrior-monsters/78852504) — community discussion of the 4 traits' gameplay effects (AI/obedience framing).
- Predecessor doc: [`personality_research_findings.md`](./personality_research_findings.md) — established the 4-trait/27-personality model and the tactic-vs-personality distinction (this doc builds on its Q2/Q4/Q5).
- Upstream (not fetched, referenced for gap resolution): [niyadev/dwm2_disassembly_github](https://github.com/niyadev/dwm2_disassembly_github) — would resolve the level-up routine disassembly and confirm/deny personality absence in code.
