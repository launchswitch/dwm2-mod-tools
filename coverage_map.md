# Coverage Map — What MonTamer Can Port Faithfully vs. Must Design

**Date:** 2026-07-05
**Purpose:** Single-paragraph-per-subsystem answer to "is this a faithful port or an original design?" Read this before specing any combat/personality/recruitment work. Cross-links the research findings and mechanic docs that back each verdict.

**Confidence legend (same as the research findings):**
- **[ROM-verified]** — pointable address / table / byte offset in our extracted data
- **[Mechanic-documented]** — concrete formula/rule written down (from a source table_structure doc), implementable as-is but not necessarily byte-verified against a routine
- **[Wiki-documented]** — described on the wiki/community guides but not in our ROM extraction
- **[Unknown]** — looked, could not determine; needs original design or deeper extraction

---

## Species & growth (Phase 1 — DONE, ported)

| Subsystem | Verdict | Source |
|-----------|---------|--------|
| Species definitions (315) | [ROM-verified] — ported | `monster_data/`, `monster_data_external.xml` |
| Stat growth (species × level) | [ROM-verified] — ported | `stat_growth_research_findings.md`; simplified v1 model in `MonTamer.Core/StatCalculator.cs` |
| Breeding (554 formulas, 4 structures) | [ROM-verified] — ported | `monster_data/breeding_data.md` |

---

## Personality (Phase 1 corrected — model done, effects deferred)

| Subsystem | Verdict | Source |
|-----------|---------|--------|
| 4 traits (Bravery/Prudence/Caring/Motivation) | [Wiki-documented] structure | `personality_research_findings.md` Q1–Q3 |
| 27 personalities (3×3×3 cube) | [Wiki-documented] table | `personality_research_findings.md` Q1; reference data in `data/personalities.yaml` |
| Personality does NOT affect stat growth | [ROM-verified absence + Wiki] | `stat_growth_research_findings.md` — corrected the v1 misnomer |
| Personality → AI/obedience/effects | **[Unknown — needs original design]** | All 5 downstream effects unmapped in our data; see "Deferred" in `2026-07-05-core-seams-design.md` |
| Trait drift via tactics (Charge/Mixed/Defend/Command tables) | [ROM-verified addresses, Unknown byte semantics] | 4 tables at `0xC138C`–`0xC15FC`; byte-level meaning needs ROM dump |
| Personality-name string table | [ROM-verified address] `0x208D6`/`0x231F6`, 27 entries | `mechanics/strings.md`; content unread (no ROM file) |

**Implication:** Personality is carried as inert v1 data. The drift/effects systems are future original design (or disassembly extraction — see `disassembly_inventory.md`).

---

## Combat

### Inputs (faithful-portable)

| Subsystem | Verdict | Source |
|-----------|---------|--------|
| Skill table (50 skills: MP, element, 4 damage values player/enemy × base/random) | [ROM-verified] `0x680D4`, 17B×50 | `combat_research_findings.md` Q1; element byte enum at `mod_data.py:86-115` |
| Skill name string table | [ROM-verified address] `0x20558`/`0x21EF9`, 50 entries | `mechanics/strings.md` |
| 27-byte resistance table per species + 28-ID element vocabulary | [ROM-verified] | `mechanics/resistances.md`; `mod_data.py:404-431` |
| Element → specific skill mappings (e.g. Blaze family = Blaze/BlazeMore/BlazeMost/BigBang/FireSlash) | [Mechanic-documented] | `mechanics/resistances.md` |
| Skill-unlock-requirements table | [ROM-verified] `0x6900A`, 18B×80 | `mechanics/skill_requirements_data.md` |
| Prebuilt-enemy struct (600 entries: stats + 4 skills + join tier + tactic/aptitude bytes) | [ROM-verified] | `mechanics/prebuilt_enemies_data.md`; `rom_maps/ram_map.md` |
| Per-world random encounter tables (45 areas: max enemies, chance bands, prebuilt-ID pools) | [ROM-verified] | `mechanics/random_encounter_data.md` |
| Boss battles (40: count + up to 3 prebuilt IDs) | [ROM-verified] | `mechanics/prebuilt_enemies_data.md` |
| Arena teams & rewards | [ROM-verified] | `mechanics/arena_random_rewards_data.md` |
| Item table (47 items: effect type, usability, targeting, price) | [ROM-verified] `0x58CC2`, 13B×47 | `combat_research_findings.md` Q6 |
| Item name string table | [ROM-verified address] `0x20716`/`0x224E3`, 47 entries | `mechanics/strings.md` |
| In-battle state buffer (6 slots: P1-3 + E1-3, lvl/HP/MP/ATK/DEF/AGL/INT/WLD/Icon) | [Wiki-documented] `$D8B7`–`$D964` | `rom_maps/ram_map.md`; **not ROM-probed** |

### Resolution rules (NOT portable from current data — original design or disassembly)

| Subsystem | Verdict | Notes |
|-----------|---------|-------|
| **Damage formula** (ATK/DEF/power/level combination) | **[Unknown]** | Highest-value gap; needs disassembly of the battle routine |
| **Critical hits** | **[Unknown]** | Confirmed to exist (`core_monster_data.md:61` "stored elsewhere"); address unmapped |
| **Resistance byte value semantics** (0/1/2/3 = immune/resist/normal/weak?) | **[Unknown]** | Element vocabulary is mapped; the *value* meaning is in code |
| **Turn order / initiative / action queue** | **[Unknown]** | Battle-state RAM is wiki-documented but resolution logic isn't |
| **AI action selection** per tactic/personality | **[Unknown]** | No AI-behavior table in our data |
| **Status-effect durations / tick / cure** | **[Unknown]** | Status *affinities* fold into the resistance table; resolution logic isn't |
| **Hit / accuracy resolution** | **[Unknown]** | No accuracy field in skills; no hit-rate table |
| **Skill execution routine** (what runs when a skill is used) | **[Unknown]** | In undisassembled bank |

**Implication:** Combat *representation* (instantiate a battle, populate stats/skills/resistances) is fully portable. Combat *resolution* (compute damage, decide turn order, apply status, roll hits/crits) requires either (a) deeper disassembly work — see `disassembly_inventory.md` — or (b) original MonTamer design informed by the maintainer's knowledge of DWM2's feel. **(b) is the planned path.**

---

## Recruitment (mechanic-documented — portable)

| Subsystem | Verdict | Source |
|-----------|---------|--------|
| Join formula (2-stage: species rate → unique rate, meat modifier, random thresholds, "already owned" path) | **[Mechanic-documented]** | `mechanics/recruitment.md` — closes the prior [Unknown] gap |
| Join-rate tier byte (0–7 enum) | [ROM-verified] prebuilt offset 8, species template byte 4 | `mod_data.py:118-127` (`JOIN_RATE` enum) |
| Meat/taming item modifier table (BeefJerky=10 … Sirloin=999 … MeteOrb=guaranteed) | [Mechanic-documented] | `mechanics/recruitment.md` |

**Implication:** Recruitment is implementable as a faithful port. The formula is concrete enough to spec.

---

## Items (data-faithful)

| Subsystem | Verdict | Source |
|-----------|---------|--------|
| Item table (47 items × 13 bytes: effect type, usability, targeting, icon, price, 4 effect params) | [ROM-verified] | `mechanics/` (none — covered by `combat_research_findings.md` Q6 + `mod_data.py:249-275`) |
| Item names | [ROM-verified address] | `mechanics/strings.md` |
| Effect-parameter byte semantics (heal amount? join-roll modifier?) | [Unknown] | Bytes 9–12 opaque |
| In-battle item-use routine | [Unknown] | Code, not data |

---

## Encounter spawning (data-faithful)

| Subsystem | Verdict | Source |
|-----------|---------|--------|
| 45 random-encounter areas (max enemies, chance bands, prebuilt-ID pools) | [ROM-verified] | `mechanics/random_encounter_data.md` |
| Boss battle compositions | [ROM-verified] | `mechanics/prebuilt_enemies_data.md` |
| Arena teams & rewards | [ROM-verified] | `mechanics/arena_random_rewards_data.md` |

**Implication:** Encounter *spawning* is faithful. Encounter *resolution* (running the battle) depends on the combat gaps above.

---

## How to use this doc

- **Designing a faithful subsystem** → the row's Verdict is [ROM-verified] or [Mechanic-documented]. Implement directly from the cited source.
- **Designing an original subsystem** → the row's Verdict is [Unknown]. The maintainer describes how it works in DWM2; we treat that as the spec.
- **Unblocking a faithful port via deeper work** → see `disassembly_inventory.md` for where the missing routines would be found.

## Pointers

- Research findings (this repo, root): `personality_research_findings.md`, `stat_growth_research_findings.md`, `combat_research_findings.md`, `combat_reassessment_findings.md`
- Mechanic specs: `mechanics/` (8 docs)
- Raw data tables: `tools/mod_data.py`, `monster_data/`, `rom_maps/`
- Disassembly: `disassembly_inventory.md` (this repo) → `/home/frank/repos/dwm2/dwm2_dissasembly_github/`
