# DWM2 Personality System — Research Findings

**Date:** 2026-07-05
**Author:** Investigation agent (reimplementation reference)
**Scope:** INVESTIGATION AND FINDINGS ONLY. No design, no code, no recommendations.

**Confidence legend** (used on every claim below):
- **[ROM-verified]** — pointable address / table / byte offset in this repo's extracted data
- **[Wiki-documented]** — described on dragon-quest.org wiki or community guides; not confirmed in our ROM extraction
- **[Unknown]** — looked, could not determine

---

## Summary

DWM2's personality system is built on **four hidden integer traits** — Bravery, Prudence, Caring, and Motivation — that are invisible to the player, rise and fall based on in-battle behavior (which tactic/command the monster performs, whether it flees), and combine to select one of **27 personality types** (a 3×3×3 cube of Bravery×Prudence×Caring tiers, with Motivation acting as a separate modifier and enabler). A common misconception — modeling `Personality = { Charge, Mixed, Defend, Command }` — **mis-identifies the four battle commands as personality types**. In the ROM, Charge/Mixed/Defend/Command are the four available *battle tactics* whose effects are encoded in four dedicated stat-modifier tables at `0xC138C–0xC15FC`; the actual *personalities* (e.g. Lone Wolf, Nonchalant, Aggressive, Kindly) are a separate, larger set that drives AI, stat growth, and co-op skill eligibility.

A key structural finding: the local extraction contains the **tactic tables** and the **per-prebuilt-enemy aptitude/motivation storage**, but does **not** contain the **27-personality definition table** (the trait→personality mapping, or the personality→AI/growth/co-op tables). Those exist in the ROM but are not in this repo's documented maps; they are documented only on the wiki and in community guides.

---

## Q1: The 27 personalities

**Confirmed count: 27.** [Wiki-documented] The 27 arises as a 3×3×3 cube — each of the three traits (Bravery, Prudence, Caring) takes one of three tiers (Low / Average / High), and the tier-combination selects the personality. Motivation is a separate axis (see Q3).

**Source:** [dragon-quest.org wiki — List of personality types in Dragon Quest Monsters](https://dragon-quest.org/wiki/List_of_personality_types_in_Dragon_Quest_Monsters), cross-referenced with the [GameFAQs DWM Personalities guide](https://gamefaqs.gamespot.com/gbc/197155-dragon-warrior-monsters/faqs/80057/personalities) which gives the per-personality trait levels. Both agree on the 27-count and the tier groupings.

**Tier notation:** L = Low, A = Average, H = High, in order **Bravery / Prudence / Caring**.

### High Bravery tier (9)

| # | Personality | Bravery | Prudence | Caring | Notes |
|---|---|---|---|---|---|
| 1 | **Aggressive** | H | L | L | |
| 2 | **Quick Tempered** | H | L | A | |
| 3 | **Vain** | H | L | H | *self-clashing for co-op* |
| 4 | **Reckless** | H | A | L | |
| 5 | **Hot Blooded** | H | A | A | |
| 6 | **Snobby** | H | A | H | *self-clashing for co-op* |
| 7 | **Lucky** | H | H | L | |
| 8 | **Lone Wolf** | H | H | A | *self-clashing for co-op* |
| 9 | **Snob** (a.k.a. Proud) | H | H | H | |

### Average Bravery tier (9)

| # | Personality | Bravery | Prudence | Caring | Notes |
|---|---|---|---|---|---|
| 10 | **Solitary** | A | L | L | |
| 11 | **Stubborn** | A | L | A | *self-clashing for co-op* |
| 12 | **Naive** | A | L | H | |
| 13 | **Ordinary** | A | A | L | the "neutral" personality |
| 14 | **Easy Going** | A | A | A | |
| 15 | **Bigot** | A | A | H | |
| 16 | **Cool** | A | H | L | |
| 17 | **Rebel** | A | H | A | *self-clashing for co-op* |
| 18 | **Conceited** | A | H | H | |

### Low Bravery tier (9)

| # | Personality | Bravery | Prudence | Caring | Notes |
|---|---|---|---|---|---|
| 19 | **Cowardly** | L | L | L | |
| 20 | **Spoiled** | L | L | A | *self-clashing for co-op* |
| 21 | **Lazy** | L | L | H | *self-clashing for co-op* |
| 22 | **Wary** | L | A | L | |
| 23 | **Patient** | L | A | A | |
| 24 | **Smug** | L | A | H | *self-clashing for co-op* |
| 25 | **Timid** | L | H | L | |
| 26 | **Mellow** | L | H | A | |
| 27 | **Kindly** | L | H | H | |

**Notes on naming variants:**
- The wiki lists 27 entries. Some community guides use slightly different English names (e.g. "Snob" vs "Proud", "Snobby" vs "Stuck-up", "Bigot" vs "Egotist"). The *set* of 27 is stable; the exact label strings are not. [Wiki-documented]
- One wiki-table row appears to mis-paste "Easy Going" (row 14) with Lone Wolf's data — a likely copy-paste error on the wiki itself. The trait levels above for Easy Going (A/A/A) follow the GameFAQs guide, which is internally consistent with the cube structure. [Wiki-documented, with one noted discrepancy]
- **The 3×3×3 cube is bijective** — every (Bravery, Prudence, Caring) tier-triple maps to exactly one personality, and all 27 cells are filled. There are no "unused" or "overloaded" combinations among these three traits. [Wiki-documented]

**Where the 27-personality definition table lives in the ROM:** **[Unknown].** Not present in this repo's `rom_map.txt` or `mod_data.py`. It almost certainly exists as a lookup table in bank `0x30`–`0x3F` (where `0xC138C` lives — see Q2), but its address is not documented here. Resolving it would require disassembly work beyond what's in this repo.

---

## Q2: Charge / Mixed / Defend / Command's real role

**Headline: They are BATTLE TACTICS (commands), not personality types.** Their ROM tables encode **how each tactic modifies the four hidden traits** (and possibly stats) when a monster performs that tactic in battle.

### ROM evidence [ROM-verified]

`rom_maps/rom_map.txt:72-75`:
```
C138C    Charge's effect on personality
C13AC    Mixed's effect on personality
C13CC    Defend's effect on personality
C13EC    Command's effect on personality
```

`tools/mod_data.py:483-543` defines four parallel tables:

| Table | ROM offset | Entry size | Entries | Total bytes |
|---|---|---|---|---|
| `personality_charge`  | `0xC138C` | 4 | 8 | 32 |
| `personality_mixed`   | `0xC13AC` | 4 | 8 | 32 |
| `personality_defend`  | `0xC13CC` | 4 | 8 | 32 |
| `personality_command` | `0xC13EC` | 4 | 8 | 32 |

Range spans `0xC138C–0xC15FC` (8 entries × 4 bytes × 4 tables = 128 bytes; the last table ends at `0xC13EC + 0x20 = 0xC140C`, well within the range). Each 4-byte entry is:

| Byte offset | Field (per mod_data.py) |
|---|---|
| 0 | `stat_id` |
| 1 | `modifier_hi` |
| 2 | `modifier_lo` |
| 3 | `flag` |

The 8 entries per tactic correspond to the 8 things a tactic can modify. Given the four-trait model (Bravery/Prudence/Caring/Motivation) plus stat growth, the most likely interpretation is: **each entry is (target_id, signed/unsigned delta_hi, delta_lo, enable_flag)**, and the table lists which traits/stats a given tactic raises or lowers when used.

### What mechanically happens when a player uses the "Charge" tactic [Wiki-documented, partially inferred]

Cross-referencing the wiki and GameFAQs guide with the table structure:

- **Charge tactic** → raises **Bravery**, lowers **Prudence** and **Caring**. (Brave monsters charge.) [Wiki-documented]
- **Defend (Cautious) tactic** → raises **Prudence**, lowers **Bravery**, slightly raises **Caring**. [Wiki-documented]
- **Mixed tactic** → balances all three (small adjustments), raises **Motivation**. [Wiki-documented]
- **Command (direct order) tactic** → lowers **Motivation** (the monster resents being ordered around), small/mixed effect on the other three traits. [Wiki-documented]
- **Fleeing a battle** → sharply lowers **Bravery** and **Motivation**. [Wiki-documented]

So the four ROM tables map **directly** onto the four-tactic → four-trait-delta mechanic. The `stat_id` byte is most likely a **trait index** (0=Bravery, 1=Prudence, 2=Caring, 3=Motivation) or possibly includes stat-growth targets (HP/MP/ATK/DEF/AGI/INT) — that distinction is **[Unknown]** without reading the actual table bytes (no ROM file is in this repo; see Gaps).

### Are these tables applied at level-up, or do they drive Motivation/personality drift?

**Inferred answer: they drive personality drift (trait deltas), not direct level-up stat growth.** Reasoning:
- Level-up stat growth in DWM2 is governed by a *separate* documented table: `stat_growth` at `0x6A616` (`mod_data.py:301-311`, 99 entries, 1 byte per level), applied per-monster via the `core_monster` growth-rate bytes (`core_monster_data.md` bytes 12-17). [ROM-verified]
- The personality tables sit in a different bank (`0x30`-region: `0xC138C`) alongside other *battle* logic, not alongside stat growth (`0x6A616`) or monster data (`0xD4000`). [ROM-verified]
- The wiki explicitly describes tactics as shifting the *hidden traits* over time, which then re-evaluate the personality — a drift mechanism, not a one-shot level-up bonus. [Wiki-documented]

**Confidence on "drives trait drift, not level-up stats":** High but inferred. The byte-level meaning of `stat_id`/`modifier_hi`/`modifier_lo`/`flag` is **[Unknown]** without dumping the actual 128 bytes from a ROM.

---

## Q3: Motivation

### Where it is documented [mixed]

- **As a trait:** [Wiki-documented] Motivation is the **fourth hidden trait** alongside Bravery/Prudence/Caring. It does **not** participate in the 3×3×3 personality cube (that cube is only B×P×C). Instead, Motivation acts as a modifier/enabler: high Motivation unlocks a personality's "special effect" (e.g. a +50% damage bonus for very-brave personalities; wiki: "trait yields one of two possible special effects"). Low/zero Motivation suppresses these bonuses. [Wiki-documented]
- **As a stored byte in the prebuilt-enemy struct:** [ROM-verified] `motivation` is a 1-byte field at struct offset `+0x18` (decimal 24). See Q5.

### How it rises / falls [Wiki-documented]

- **Rises** when a monster acts *autonomously* under a **tactic** (Charge/Mixed/Defend) — i.e. the player sets a tactic and lets the monster choose its action. The fastest single source of Motivation gain is using the **Plan/Mixed** tactic. [Wiki-documented]
- **Falls** when a monster is given a **direct Command** (the player picks the exact action), or when it **flees** a battle. [Wiki-documented]
- Net: a player who micromanages (commands every turn) produces low-Motivation monsters; a player who sets tactics and lets the AI act produces high-Motivation monsters. [Wiki-documented]

### Level-dependent threshold for personality changes [Wiki-documented]

- **Lower-level monsters shift personality more easily; higher-level monsters shift more slowly.** [Wiki-documented] The wiki and GameFAQs guide both state this. The exact threshold curve (e.g. "trait delta required to flip a tier doubles every N levels") is **[Unknown]** — not in this repo's maps, and not numerically specified in the community sources I found.

### Where Motivation lives in RAM [partially ROM-verified, partially Unknown]

- In the **prebuilt-enemy struct** (loaded into WRAM on encounter): `+0x18`. [ROM-verified, `ram_map.md:142`, `mod_data.py:348`]
- In the **party-monster struct** (`0xDFC0+`, WRAM bank 1): **[Unknown]**. The party struct was probed via diffing (`tools/discovery/map_party_struct.py`) but only species ID + level + stat pointers were pinned down; the personality/attribute/motivation bytes for *party* monsters were **not** identified. The `ram_map.md` "Remaining Unknowns" section explicitly lists "HP/MP/stat field offsets within struct: Need before/after diff" — the trait/personality bytes are in the same undetermined region. [ROM-verified that it's unknown]

---

## Q4: Personality's downstream effects

For each claimed effect, the ROM-evidence status:

### (a) Battle AI behavior per personality — [Wiki-documented only]
The wiki describes personality-driven AI tendencies (e.g. Aggressive monsters favor attacks, Kindly monsters favor healing, Wary monsters favor defensive skills). **No AI-behavior table is present in this repo's ROM maps.** The AI logic is in code (bank `0x30`-region, near `0xC138C`), not in a documented data table. [Unknown — not in our extraction]

### (b) Obedience / defiance — [Wiki-documented only]
Low-Motivation monsters disobey direct Commands more often (the "defiance" mechanic). This is described on the wiki but **no obedience table or threshold is in this repo**. [Unknown — not in our extraction]

### (c) Critical-hit chance modifiers — [Wiki-documented, weakly]
Some community sources (Woodus forums) mention damage variability tied to personality, but I found **no specific crit-chance table** and **no ROM address** for it. Note: `core_monster_data.md:60` explicitly states the unknown bytes at offsets 5 and 11 are "NOT critical hit rates; those are stored elsewhere" — confirming crit data exists in the ROM but is not mapped in this repo. [Unknown — confirmed to exist, location unmapped]

### (d) MP-free healing triggers — [Wiki-documented only]
Caring-type personalities (Kindly, Patient, etc.) can trigger "MP-free" autonomous heals. Wiki-described; **no trigger table in this repo**. [Unknown — not in our extraction]

### (e) Co-op skill eligibility — [Wiki-documented, well-corroborated]
**Confirmed mechanic:** Eight personalities are **"self-clashing"** — if two monsters on the field *share* one of these personalities, their co-op skills will **fail to trigger**:

> Lone Wolf, Vain, Smug, Snobby, Stubborn, Rebel, Spoiled, Lazy

This is corroborated by **two independent community sources** (NeoSeeker co-op guide, GameFAQs boards). **Important nuance:** these personalities don't *prevent* co-op outright — they specifically prevent co-op between two monsters that *both* have the clashing personality. A Lone Wolf + an Ordinary monster can still co-op. [Wiki-documented, multiple sources agree]

**No co-op eligibility table is present in this repo's ROM maps.** [Unknown — location not mapped]

### Summary table for Q4

| Effect | Status in this repo | Status overall |
|---|---|---|
| (a) AI behavior per personality | Not mapped | Wiki-only |
| (b) Obedience/defiance | Not mapped | Wiki-only |
| (c) Crit chance modifiers | Confirmed exists (core_monster_data.md:60), location unmapped | Wiki + partial ROM |
| (d) MP-free healing | Not mapped | Wiki-only |
| (e) Co-op skill eligibility | Not mapped | Wiki-only, multi-source |

**Bottom line:** None of the five downstream effects have a pointable ROM address in this repo. The personality *definition* table (27 entries) and the personality→effect tables all exist in the DWM2 ROM but are **not part of this extraction**. They would need disassembly work to locate.

---

## Q5: Monster struct storage (byte offsets)

There are **two** relevant structs, and the personality/trait bytes live in different places in each:

### (1) Prebuilt Enemy Struct — 26 bytes [ROM-verified]

Source: `rom_maps/ram_map.md:121-144`, `rom_maps/battle_breeding_map.md:33-55`, `tools/mod_data.py:325-354`. ROM location: part 1 at `0xD0075` (IDs 0–299), part 2 at `0x288056` (IDs 300–599). This is the struct for **wild/encountered/boss/NPC** monsters; it's copied to WRAM on encounter.

| Offset (hex) | Offset (dec) | Size | Field |
|---|---|---|---|
| `+0x00` | 0 | 2 | Species ID (LE u16) |
| `+0x02` | 2 | 1 | Skill 1 |
| `+0x03` | 3 | 1 | Skill 2 |
| `+0x04` | 4 | 1 | Skill 3 |
| `+0x05` | 5 | 1 | Skill 4 |
| `+0x06` | 6 | 2 | EXP yield (LE u16) |
| `+0x08` | 8 | 1 | Join value (0=always … 7=never) |
| `+0x09` | 9 | 1 | Level |
| `+0x0A` | 10 | 2 | HP (LE u16) |
| `+0x0C` | 12 | 2 | MP (LE u16) |
| `+0x0E` | 14 | 2 | Attack (LE u16) |
| `+0x10` | 16 | 2 | Defense (LE u16) |
| `+0x12` | 18 | 2 | Agility (LE u16) |
| `+0x14` | 20 | 2 | Intelligence (LE u16) |
| **`+0x16`** | **22** | **1** | **Charge aptitude** |
| **`+0x17`** | **23** | **1** | **Defense aptitude** |
| **`+0x18`** | **24** | **1** | **Motivation** |
| **`+0x19`** | **25** | **1** | **Mixed aptitude** |

**Interpretation note on the four aptitude/motivation bytes [mixed confidence]:**
- The field *names* (`charge_aptitude`, `defense_aptitude`, `motivation`, `mixed_aptitude`) come from this repo's own struct documentation — so the **labels are ROM-derived**, not wiki-derived. [ROM-verified labels]
- `motivation` (`+0x18`) maps cleanly onto the wiki's fourth trait. [ROM-verified byte exists; wiki-verified it's the Motivation trait]
- `charge_aptitude` / `defense_aptitude` / `mixed_aptitude` (`+0x16`, `+0x17`, `+0x19`) are **most likely the three combat traits stored under their tactic-correlated names** — i.e. `charge_aptitude` = **Bravery**, `defense_aptitude` = **Prudence**, `mixed_aptitude` = **Caring**. This mapping is **inferred** from the tactic→trait correspondence in Q2 (Charge↔Bravery, Defend↔Prudence, Mixed↔Caring balance), not directly confirmed by a ROM comment. **Confidence: medium.** It's also possible these are starting *aptitude scores* (how good the monster is at each tactic) rather than the raw traits — the two could coincide. [Inferred — needs byte-level verification]
- Note there is **no `command_aptitude` byte** — consistent with "Command" being the player's direct-order action (not a monster aptitude). [ROM-verified absence]
- There is **no `personality` byte** in this struct. This means the personality is **computed** from the trait bytes at runtime (the 3×3×3 lookup), not stored. [ROM-verified absence → inferred computation]

### (2) Party Monster Struct (WRAM `0xDFC0+`) — [Unknown layout]

The party struct (~34–42 bytes per entry, exact size undetermined) holds the player's owned monsters. `ram_map.md:178-183` explicitly lists the undetermined fields. **From this repo:**
- Species ID (LE u16) and Level (1 byte) are confirmed at the start of each entry. [ROM-verified]
- HP/MP/Attack/Defense/Agility/Intelligence field offsets: **[Unknown]** (needs before/after diff of healing/leveling — `ram_map.md:182`).
- **Personality byte: [Unknown]** — not confirmed present.
- **Bravery/Prudence/Caring trait bytes: [Unknown]** — not confirmed present.
- **Motivation byte: [Unknown]** — not confirmed present (the prebuilt struct has it at `+0x18`, but the party struct layout differs and was not fully mapped).

**Implication for save/load modeling:** The prebuilt struct's 4 trait bytes (offsets 22–25) are the only personality-system bytes whose storage location is *confirmed* in this extraction, and they apply to *encountered* monsters. For *party* monsters (the ones that need save/load), the trait/personality byte offsets are **not determined by this repo** and would require either (a) further WRAM probing with a live ROM, or (b) consulting the upstream [DWM2 disassembly](https://github.com/niyadev/dwm2_disassembly_github).

### (3) Core Monster Species Template — 47 bytes [ROM-verified, but contains NO personality data]

Source: `monster_data/core_monster_data.md`, `tools/mod_data.py:379-437`. ROM: `0xD433B` (bank `0x35`), 324 species × 47 bytes. This is the **species template** (growth rates, resistances, skills, family) — it has **no personality, trait, or motivation bytes**. The 47 bytes are fully accounted for: family, gender ratio, flying, metal, join rate, 2 unknown bytes, max level, EXP growth, 3 skills, 1 unknown byte, 6 growth rates, 27 resistances, 2 base-EXP. **Personality is per-instance, not per-species** — confirmed by the absence of any such byte here. [ROM-verified]

---

## Gaps & unknowns

What this investigation could **not** determine from the local data + wiki:

1. **The 27-personality definition table's ROM address.** It exists (the game must look up personality from traits), but it's not in `rom_map.txt` or `mod_data.py`. Likely in bank `0x30`–`0x3F`. **To resolve:** disassembly work, or query the upstream `niyadev/dwm2_disassembly_github` repo for `personality` labels.

2. **The exact byte-level meaning of the four tactic tables (`0xC138C`–`0xC15FC`).** We know each is 8×4 bytes with fields `stat_id`/`modifier_hi`/`modifier_lo`/`flag`, but not which byte values map to which trait, whether modifiers are signed, or what the `flag` byte gates. **To resolve:** read the 128 raw bytes from a ROM (`mod_data.py --table personality_charge --list` etc., requires a ROM file — none is in this repo per `.gitignore`/legal posture), then cross-reference with disassembly of the routine that *reads* `0xC138C`.

3. **The party-monster struct's personality/trait/motivation byte offsets.** Prebuilt struct is mapped; party struct is not. **To resolve:** live WRAM probing with PyBoy (the repo's `tools/discovery/map_party_struct.py` is the intended tool but needs a ROM + gameplay to a known-personality state), or upstream disassembly.

4. **Whether `charge_aptitude`/`defense_aptitude`/`mixed_aptitude` (prebuilt offsets 22/23/25) ARE the Bravery/Prudence/Caring traits, or are something adjacent (e.g. tactic proficiency).** Inferred correspondence only. **To resolve:** byte-level inspection of a monster with a known personality, or disassembly labels.

5. **The exact level-dependent personality-shift threshold curve.** Wiki says "low level = fast shifts, high level = slow shifts" but gives no formula. **To resolve:** disassembly of the trait-recompute routine.

6. **ROM addresses for all five downstream effects (AI, obedience, crit, healing, co-op).** None mapped in this repo. **To resolve:** disassembly.

7. **Authoritative English name canonicalization for the 27 personalities.** Wiki and guides use slightly different labels (Snob/Proud, Snobby/Stuck-up, Bigot/Egotist). **To resolve:** pick a canonical source for display strings (a design decision, out of scope for this findings doc).

8. **The "two possible special effects per trait" mechanic.** The wiki Personality page mentions each trait yields one of two special effects (e.g. very-high Bravery → either crit-up or damage-up depending on Motivation), but the exact effect table and thresholds are not numerically documented. **To resolve:** disassembly or a more mechanics-focused community guide.

---

## Sources

### Local extracted data (this repo)
- `README.md` — overview; line 81 lists the 4 personality tables.
- `rom_maps/rom_map.txt` — lines 72-75: Charge/Mixed/Defend/Command effect-on-personality addresses (`0xC138C`–`0xC15FC` region).
- `rom_maps/ram_map.md` — lines 121-144: prebuilt enemy struct (Charge/Defense/Motivation/Mixed aptitudes at `+0x16`–`+0x19`); lines 178-183: party-struct unknowns.
- `rom_maps/battle_breeding_map.md` — lines 33-55: prebuilt enemy struct layout (cross-confirm).
- `monster_data/core_monster_data.md` — full 47-byte species template (no personality bytes; line 60: crit rates "stored elsewhere").
- `tools/mod_data.py` — lines 325-354 (prebuilt enemies, 4 trait bytes), lines 483-543 (4 personality tables, 8×4 bytes each), lines 585-588 (table registry).
- `dwm2u_reference/dwm2u_analysis.md` — DWM2 Ultimate hack analysis (does not modify personality system; confirms personality system is separate from stat-growth/breeding tables).

### Cross-referenced wiki & community sources (web)
- [List of personality types in Dragon Quest Monsters — Dragon Quest Wiki](https://dragon-quest.org/wiki/List_of_personality_types_in_Dragon_Quest_Monsters) — the 27-personality table with trait tiers.
- [Personality — Dragon Quest Wiki](https://dragon-quest.org/w/index.php?title=Personality&mobileaction=toggle_view_desktop) — the four-trait model (Bravery/Prudence/Caring/Motivation), special-effects mechanic.
- [Personalities — Dragon Warrior Monsters Walkthrough & Guide (GameFAQs, RSlickback)](https://gamefaqs.gamespot.com/gbc/197155-dragon-warrior-monsters/faqs/80057/personalities) — per-personality trait levels, tactic→trait deltas, Motivation mechanics.
- [Dragon Warrior Monsters 2: Cobi's Journey – Co-op Skill Guide (NeoSeeker)](https://www.neoseeker.com/dwm2/faqs/3072571-dragon-warrior-monsters-2-cobis-journey-coop-skills.html) — the 8 self-clashing personalities (Lone Wolf, Vain, Smug, Snobby, Stubborn, Rebel, Spoiled, Lazy).
- [GameFAQs boards — List of all Co-Op Skills](https://gamefaqs.gamespot.com/boards/525414-dragon-warrior-monsters-2-cobis-journey/77880249) — corroboration of the 8 self-clashing personalities.
- [Woodus.com Forums — Personalities](https://www.woodus.com/forums/topic/8611-personalities/) — gameplay-effect anecdotes (damage boosts, autonomous heals).
- Upstream (not fetched, referenced by this repo's README): [niyadev/dwm2_disassembly_github](https://github.com/niyadev/dwm2_disassembly_github) — the DWM2 disassembly; likely source for resolving gaps 1, 2, 3, 5, 6.
