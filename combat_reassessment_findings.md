# DWM2 Combat — Re-assessment of Maintainer's 4 Additions

**Date:** 2026-07-05
**Author:** Re-assessment investigation agent (MonTamer reference)
**Scope:** INVESTIGATION ONLY. Determine whether four maintainer additions change the prior "what's IN vs. NOT" combat/personality verdict. No design, no recommendations.
**Predecessors:**
- [`combat_research_findings.md`](./combat_research_findings.md) — established combat DATA is in extraction, combat RESOLUTION RULES are not.
- [`personality_research_findings.md`](./personality_research_findings.md) — established 4-trait/27-personality model; many gaps [Unknown].
- [`stat_growth_research_findings.md`](./stat_growth_research_findings.md) — stat growth is species-driven, not personality-driven.

**Confidence legend** (same as prior findings):
- **[ROM-verified]** — pointable address / table / byte offset in this repo's extracted data
- **[Wiki-documented]** — described on wiki/community guides; not confirmed by live ROM probing in this repo
- **[Unknown]** — looked, could not determine

---

## Summary

The four additions **materially close two prior gaps and partially address two more, but do NOT touch the combat-resolution blockers.** Specifically: the 10 string tables **close** the prior "no skill-name / no item-name string table" [ROM-verified absence] claims (Q1); the WRAM battle-state region **partially closes** the prior "battle-state RAM unprobed" gap by documenting 6 live combat slots with current HP/MP/stats — but it is [Wiki-documented] not [ROM-verified], and it is the *transient* battle buffer (bank 7), not the *persistent* party struct (bank 1) that the personality gaps concern (Q2). The "Useful Structures" section is **reorganization** with one clarified detail (Q3); the 29 new encounter areas are **more-of-the-same** structure, expanding coverage not mechanics (Q4). The personality-name string table **partially addresses** the canonical-name gap but content is unreadable without a ROM, and the 27-personality *definition* table remains [Unknown] (Q5). **The bottom-line combat verdict is unchanged: faithful combat still requires the upstream disassembly** — none of the four additions addresses damage formula, crit, resistance semantics, turn order, AI, status logic, or the join roll.

---

## Q1: The 10 string tables — closes skill-name & item-name gaps

### (a) Verification — the tables ARE there

The new `parse_string_data()` parser and 10 table definitions (5 pointer tables + 5 null-terminated string-data tables) are present in `tools/mod_data.py:129-301` and registered in the `TABLES` registry at `tools/mod_data.py:793-802`. [ROM-verified — the parser and registry entries exist]

| Category | Pointer table | Data table | Ptr offset | Data offset | Entries |
|---|---|---|---|---|---|
| Family names | `family_name_pointers` | `family_names` | `0x20242` | `0x213B5` | 14 |
| Monster species names | `monster_name_pointers` | `monster_names` | `0x2025A` | `0x213F9` | 324 |
| **Skill names** | `skill_name_pointers` | `skill_names` | `0x2055A` | `0x21EF9` | **50** |
| **Item names** | `item_name_pointers` | `item_names` | `0x20718` | `0x224E3` | **47** |
| **Personality names** | `personality_name_pointers` | `personality_names` | `0x208D6` | `0x231F7` | **27** |

Sources: `tools/mod_data.py:135-145` (family ptrs), `:148-158` (monster ptrs), `:161-171` (skill ptrs), `:174-184` (item ptrs), `:187-197` (personality ptrs); data tables at `:239-249`, `:252-262`, `:265-275`, `:278-288`, `:291-301`. `rom_map.txt:5-17` documents the same offsets as "String pointer tables (bank 8)" and "String data (bank 8)". [ROM-verified addresses]

The `parse_string_data` parser (`tools/mod_data.py:200-235`) walks from the table's `offset`, splitting on `0x00` null terminators, decoding printable ASCII (`0x20 ≤ b < 0x7F`, else `?`), with per-table `max_bytes`/`max_entries` budgets. [ROM-verified — parser logic inspected]

### (b) Which prior gaps CLOSE — skill-name and item-name [ROM-verified absence] → [ROM-verified present]

The prior combat findings (`combat_research_findings.md:73`, `:257`, `:301`, `:302`, `:319`, `:331`) stated:
- "No skill-name string table is mapped anywhere in this extraction. [ROM-verified absence]"
- "Item NAME table — like skills, no item-name string table is mapped. [ROM-verified absence in our maps]"
- In the NOT-IN table: "Skill-ID → skill-name authoritative string table — ROM string region (~`0x20000`, unmapped)"; "Item-ID → item-name string table — ROM string region (unmapped)".

**These two claims are now SUPERSEDED.** The prior estimate "near `0x20000`" was correct — the string region *is* bank 8 starting at `0x20000` (`rom_map.txt:3`), and the skill/item name pointers sit at `0x2055A`/`0x20718` with data at `0x21EF9`/`0x224E3`. The skill-name table matches the skill *data* table's count (50 entries each — `mod_data.py:165, 269` vs skill table `:484`), and the item-name table matches the item *data* table's count (47 each — `mod_data.py:178, 282` vs item table `:456`), so the ID→name mapping is index-aligned and authoritative. [ROM-verified addresses + count alignment; the actual string content is not readable here — see (c)]

The monster-name table (`0x2025A`/`0x213F9`, 324 entries) also now maps authoritative species names (vs the XML's display-name-only list), and the family-name table (`0x20242`/`0x213B5`, 14) maps family names. These were not flagged as gaps in the prior findings (the XML supplied species names), but they are new authoritative sources.

### (c) Can sample names be read? — NO (no ROM file in repo)

**Critical limitation:** The prior findings and AGENTS.md establish the legal posture (`.gitignore` excludes `*.gbc`/`*.gb`/`*.rom`), and I confirmed **no ROM file is present in this repo**. The `parse_string_data` parser is *implemented* but cannot be *executed* without a ROM image. Therefore:

- The table **layouts, addresses, and entry counts** are [ROM-verified] (they are static Python literals cross-referenced in `rom_map.txt`).
- The actual **string content** (e.g. "what is skill ID 0's name?") is **[Unknown — not readable without a ROM]** in this repo. No cached/extracted text dump of these regions exists (`grep` for the data offsets in `monster_data/`, `docs/`, and tool output caches found no extracted strings).

The prior finding's partial skill-ID→name map (~30 skills from `tools/balancing/generate_p2_pass3_skills.py` comments) and the XML's 145 distinct skill display-names remain the *only* readable name sources. The new tables make the authoritative source *addressable* but not yet *read*.

### (d) Personality-name table — bears on canonicalization gap, partially

The `personality_name_pointers` (`0x208D6`, 27 entries) + `personality_names` (`0x231F7`) tables directly address prior personality-research Gap 7 ("Authoritative English name canonicalization for the 27 personalities") — see Q5(c). The 27-entry count matches the wiki's 27-personality set exactly. But, as above, the content is **not readable here** (no ROM). So the gap moves from "no authoritative source mapped" to "authoritative source *addressed* but content *unread*". [ROM-verified address & count; Unknown content]

---

## Q2: WRAM battle-state region (0xD8B7–0xD964) — partially closes the prior battle-state gap

### (a) Verification — the region IS documented

The new "WRAM Bank 7 (`0xD000-DFFF`, `0xFF70 = 7`) — Battle State" section is present at `rom_maps/ram_map.md:95-229`. It documents 6 monster slots (Player 1-3 + Enemy 1-3) across 9 stat groups: Level (1B), Current HP, Max HP, Current MP, Max MP, ATK, DEF, AGL, INT (all 2B LE), WLD (2B LE), Icon (2B). [ROM-verified — the section exists with full per-slot address tables]

### (b) Does it give the runtime combat state needed to model a battle in progress?

**Yes, for the *state storage* layer — and it confirms 3v3.** The region provides, per slot:
- **Current and Max HP** (`0xD8BF-0xD8DB` / `0xD8CF-0xD8DB` range) — enough to track damage application and death. [Wiki-documented addresses]
- **Current and Max MP** (`0xD8DF-0xD8EB` / `0xD8EF-0xD8FB`) — enough to gate skill casting by MP cost. [Wiki-documented]
- **ATK / DEF / AGL / INT** (`0xD8FF-0xD90B` / `0xD90F-0xD91B` / `0xD91F-0xD92B` / `0xD92F-0xD93B`) — the four stats the damage formula would consume. [Wiki-documented]
- **Level** (`0xD8B7-0xD8BD`) — per-slot. [Wiki-documented]
- **Icon** (`0xD958-0xD964`) — display/sprite index. [Wiki-documented]

**3v3 confirmation:** The layout has exactly 3 player slots + 3 enemy slots per stat group, with a consistent interleave-and-pad pattern (Player triple, 1 byte pad, Enemy triple). This is the **first direct memory-layout evidence in this repo** for 3v3 battle size. The prior combat findings (`combat_research_findings.md:126`) could only say "[Partially known, indirect] ... Wiki says 3v3 for DWM2; not confirmed in our data." This region now documents it structurally — though still at [Wiki-documented] confidence, not [ROM-verified]. [Wiki-documented — stronger than prior's "indirect" but not ROM-confirmed]

**This partially closes the prior gap.** The prior findings (`combat_research_findings.md:125`, citing `ram_map.md:182` — now line 318: "Battle state RAM region: Not yet probed (requires entering battle)") flagged battle-state RAM as the blocker for "turn order, current HP/MP tracking, action queue, and the in-battle party struct." This new region resolves the **current HP/MP/stat-tracking** sub-question and the **in-battle struct layout** sub-question. It does **NOT** resolve turn order, action queue, or any resolution rule — those remain in unmapped code.

### (c) The [Wiki-documented] caveat — how much does it matter for a port spec?

**It matters meaningfully.** The section header itself states (`ram_map.md:101-103`): *"Address widths: level and stat bounds are documented as 1 byte and 2 bytes (LE u16) respectively. Width not yet independently confirmed via live probing; based on the wiki/community reference."* And the closing note (`ram_map.md:228`): *"Confidence: [Wiki-documented] — these addresses come from a community reference and have not been independently verified via live PyBoy probing in this repo."*

Implications for port fidelity:
- **Addresses could be off** (community maps occasionally lag the actual game, especially for banked WRAM). A faithful port spec ideally wants [ROM-verified] addresses confirmed by entering a battle and reading known HP values from these locations.
- **The interleave/pad pattern is plausible but unconfirmed** — the 1-byte gaps between player-triple and enemy-triple (e.g. `0xD8BA` pad between `0xD8B9` P3 and `0xD8BB` E1) are structurally odd and warrant verification.
- **The bank-select detail is solid** — `0xFF70 = 7` selects WRAM bank 7, consistent with the banked-WRAM model already [ROM-verified] for banks 0-2 elsewhere in `ram_map.md`.

**Net for porting:** Usable as a *draft* spec for an in-battle state model (the field set — HP/MP/ATK/DEF/AGL/INT/Level/WLD/Icon per of 6 slots — is almost certainly complete and right), but the exact byte addresses should be confirmed via live probing before being treated as authoritative. The repo's own `tools/discovery/map_party_struct.py` and the new `tools/discovery/probe_hram.py` (untracked) are the intended verification tools.

### (d) WLD stat — wildness/obedience implication

A **WLD (Wildness)** field is documented at `0xD93F-0xD94B` (2 bytes LE per slot, both player and enemy). [Wiki-documented] This is notable: it is the **first memory-mapped evidence of a wildness/obedience stat in this repo.** The prior personality findings described the obedience/defiance mechanic (low-Motivation monsters disobey Commands) as entirely [Wiki-documented, not mapped] (`personality_research_findings.md:169-170`). The WLD field's presence in the battle buffer is consistent with that mechanic — wild monsters resist commands, and a tamed monster's WLD would gate obedience.

**However:**
- The **value semantics are [Unknown]** — what WLD=0 vs WLD=100 means, how it changes (does it decay per turn? drop on Command use? drop on fleeing?), and the threshold at which a monster disobeys, are **not documented anywhere** in this extraction. The field exists; the rules that read it do not.
- It is **2 bytes** (unlike the 1-byte aptitude/motivation bytes in the prebuilt struct at `+0x16`-`+0x19`). This may indicate a different scale or a different quantity than the 1-byte Motivation trait — the relationship between WLD (battle buffer) and Motivation (prebuilt struct / personality trait) is **[Unknown]**. They could be the same value widened, or distinct.

**Implication:** WLD's existence *supports* the obedience mechanic's reality and gives a place to store it during battle, but the defiance *threshold and decay rules* remain [Unknown] — still in unmapped code. [Wiki-documented field present; Unknown semantics]

---

## Q3: "Useful Structures" section — reorganization + one clarified detail

### (a) Verification — the section IS there

The "Useful Structures" section is present at `rom_map.txt:94-139`. It documents three structs: boss battles (`:97-101`), random encounter data (`:103-117`), and core monster data (`:119-139`). [ROM-verified — section present]

### (b) New info vs. reorganization

**Predominantly reorganization.** All three structs were already documented in the prior findings and their source files:

| Struct | New location | Prior location(s) | New content? |
|---|---|---|---|
| Boss battles (8 bytes: count + 3× enemy prebuilt IDs) | `rom_map.txt:97-101` | `combat_research_findings.md:204`; `battle_breeding_map.md:89-94`; (previously also inline at the old `rom_map.txt:6-12`, now consolidated) | **No** — identical layout (2B count, 2B×3 IDs) |
| Random encounter data (variable-length) | `rom_map.txt:103-117` | `combat_research_findings.md:210-212`; `battle_breeding_map.md:10-24`; `mod_data.py:352-440` parser | **One clarified detail** — see below |
| Core monster data (47 bytes) | `rom_map.txt:119-139` | `combat_research_findings.md:278`; `core_monster_data.md:36-57`; `mod_data.py:379-437` | **No** — same 47-byte layout (family, gender, flying, metal, join, level, exp, 3 skills, 6 growth bytes, 27 resistances, base exp) |

**The one genuinely new detail** is in the encounter struct: the prior `battle_breeding_map.md:14-18` documented "Prebuilt enemy IDs (one per threshold band)" without a count cap; the new `rom_map.txt:106-117` explicitly enumerates **up to 5 enemy prebuilt-ID slots** (`0x7`-`0xf`, 5×2 bytes = 10 bytes, present only if the slot is used) and gives a **worked byte-level example** (Oasis overworld: `01 07 03 07 00 00 00 02 00 03 00` = max 1 enemy, range 7, 3/7 chance of prebuilt 0x02 else 0x03). This sharpens the prior "variable, up to 5×2 bytes" note in `combat_research_findings.md:212` into a concrete field map. [ROM-verified — the 5-slot cap and example are new; consistent with prior parser]

**Spot-check against prior findings:** The boss struct's `count = enemies−1` convention matches the prior `combat_research_findings.md:126` ("`count = enemies−1` ... implying up to 3 enemies"). The core monster struct's offsets (`0x12-0x2c` = 27 resistances, `0x2d-0x2e` = base exp) match `core_monster_data.md:56` and the resistance table in `combat_research_findings.md:138`. No contradictions found. The 47-byte total is unchanged.

**Net:** This addition is **housekeeping** — it consolidates three already-known struct layouts into a single referenceable section in `rom_map.txt`, with the encounter struct gaining a slightly sharper field map and a worked example. It reveals **no new combat mechanic** and closes **no prior [Unknown] gap**.

---

## Q4: 29 new encounter areas — more-of-the-same (coverage expansion, not mechanics)

### (a) Verification — the areas ARE added

`parse_random_encounters` (`tools/mod_data.py:352-412`) now lists 45 areas (was 16). The new 29 are: `ghost_ship_2f`, `ghost_ship_cabin`, `sleep_herb_mtn`, `ice_tower_1f`, `ice_tower_2f`, `fhunt_tower_1f-4f`, `helm_cave_1f-3f`, `armor_tower_1f-4f`, `sword_castle_1f-4f`, `darck_castle`, `agdevil_lair`, `lonely_world`, `lonely_basement`, `traveler_world`, `dark_merchant_tower_1f-4f` (`mod_data.py:377-411`). The registry `num_entries` is updated from 16 to 45 (`mod_data.py:817`, `:818` description). [ROM-verified — area list and count present]

### (b) Significance for combat design

**Coverage expansion, not mechanic revelation.** Every new area uses the **identical encounter structure** already documented in the prior findings and re-stated in the new "Useful Structures" section (Q3): `max_enemies(1) + range(1) + 5 chance thresholds + up to 5×2-byte prebuilt IDs` (`combat_research_findings.md:212`; `rom_map.txt:103-117`). The parser logic (`mod_data.py:414-440`) is unchanged — it scans forward from each area offset for the first byte ≤5 to find the encounter-structure start, then reads the same 13-byte window.

What this **does** improve:
- **Spawn-table completeness** — the prior 16 areas covered the early/mid game (Oasis through Limbo/Elf). The new 29 extend coverage to the late-game and post-game dungeons (Darck Castle, Agdevil Lair, Lonely/Traveler worlds, the four equipment-themed towers — Helm/Armor/Sword + the Fhunt tower). A port aiming at full game coverage now has encounter tables for substantially more of the world map.
- **Encounter-density signal** — more areas means more data points on how the original authors tuned `max_enemies` and chance bands per dungeon tier (e.g., do later towers allow 3-enemy encounters more often?). Useful for balance modeling, though the values themselves are only readable with a ROM.

What this **does not** change:
- **No new encounter mechanic** — no shiny tables, no recruitment-bonus-on-encounter, no weather/time modifiers surfaced. The prior finding's note that the "Shiny System Integration" in `battle_breeding_map.md` is a *mod plan, not extracted data* still holds.
- **The join-roll formula remains [Unknown]** — more encounter tables means more prebuilt IDs with `join_value` bytes, but the *formula* converting that tier to a recruitment probability is still in unmapped code (`combat_research_findings.md:217`).

**Net:** This is a breadth improvement (≈3× the encounter coverage) with no change to the combat-resolution verdict. More of the game's encounter *content* is mapped; the encounter *mechanics* were already as mapped as they're going to get from data alone.

---

## Q5: Personality gaps — cross-check against the four additions

The prior personality findings (`personality_research_findings.md:256-272`) listed 8 gaps. Cross-checking each against the four additions:

### (a) Gap 1 — "The 27-personality definition table's ROM address" — STILL UNKNOWN

**Not closed.** The new `personality_name_pointers` (`0x208D6`) / `personality_names` (`0x231F7`) tables are the **name strings** for the 27 personalities, **not** the trait→personality *definition* lookup (the 3×3×3 Bravery×Prudence×Caring tier cube that maps trait values to a personality index). The definition table — the routine/table the game consults to convert stored traits into a personality — is a separate, unmapped structure, still presumed to live in bank `0x30`-region near the tactic tables at `0xC138C`. **[Unknown — unchanged].** The name table gives us the *labels*; it does not give us the *computation*.

### (b) Gaps 3 & 4 — "Party-struct trait/personality/motivation byte offsets" & "are charge/defense/mixed aptitudes the traits?" — STILL UNKNOWN

**Not closed — and the WLD field does not resolve this.** Critical distinction: the new WRAM battle-state region (Q2) is in **WRAM bank 7** (`0xFF70 = 7`), which is the **transient in-battle buffer**. The personality gaps concern the **persistent party-monster struct** in **WRAM bank 1** (`0xDFC0+`, `ram_map.md:68-87`) — where owned monsters are stored across battles and saved to SRAM. These are **different banks** accessed via the `0xFF70` bank-select register; documenting one does not document the other.

- The WLD field in the battle buffer (bank 7) tells us wildness is tracked *during battle*, but says nothing about where Bravery/Prudence/Caring/Motivation are stored *persistently* per party monster (bank 1).
- The prior party-struct probing (`tools/discovery/map_party_struct.py`) confirmed only species ID + level at the start of each bank-1 entry; HP/MP/stat/trait/personality offsets remain undetermined (`ram_map.md:316-317`).
- So: **party-struct trait/personality/motivation byte offsets remain [Unknown].** The four additions do not touch bank 1. [Unknown — unchanged]

### (c) Gap 7 — "Authoritative English name canonicalization for the 27 personalities" — PARTIALLY ADDRESSED

**Partially closed.** The `personality_names` data table at `0x231F7` (27 entries, matching the wiki's 27-count) is precisely the authoritative in-ROM English name source the prior gap asked for — it would resolve the wiki/guide naming variants (Snob/Proud, Snobby/Stuck-up, Bigot/Egotist) by giving the game's own strings. **However**, as with all string tables (Q1c), the content is **not readable in this repo** (no ROM file). So the gap moves from "no authoritative source identified" to "authoritative source *addressed and count-confirmed*, content *not yet extracted*." [ROM-verified address + 27-entry count; Unknown content — readable only with a ROM]

### (d) Gaps 2, 5, 6, 8 — unchanged

- Gap 2 (byte-level meaning of the 4 tactic tables `0xC138C`-`0xC15FC`): **unchanged** — still needs a ROM dump to read the 128 raw bytes. [Unknown]
- Gap 5 (level-dependent personality-shift threshold curve): **unchanged** — no new table. [Unknown]
- Gap 6 (ROM addresses for AI/obedience/crit/healing/co-op effect tables): **unchanged** — none mapped. The WLD field (Q2d) is a *storage* location, not an *effect* table. [Unknown]
- Gap 8 ("two possible special effects per trait" mechanic): **unchanged**. [Unknown]

**Net for personality:** One of eight gaps partially addressed (canonical names — addressed but unread), seven unchanged. The most consequential gaps (definition table address, party-struct trait bytes, effect tables) are untouched.

---

## Updated "IN vs. NOT" verdict

### What moved from NOT → IN (or NOT → partially-IN)

| Prior status (combat findings) | New status | Driver |
|---|---|---|
| Skill-name string table: [ROM-verified absence] | **[ROM-verified present]** — `skill_name_pointers` `0x2055A` + `skill_names` `0x21EF9`, 50 entries (content unread, no ROM) | Addition #1 (string tables) |
| Item-name string table: [ROM-verified absence] | **[ROM-verified present]** — `item_name_pointers` `0x20718` + `item_names` `0x224E3`, 47 entries (content unread, no ROM) | Addition #1 (string tables) |
| Battle-state RAM: "Not yet probed" (`ram_map.md:318`) | **[Wiki-documented]** — 6 slots (3v3 confirmed structurally), current/max HP/MP, ATK/DEF/AGL/INT, Level, WLD, Icon at `0xD8B7`-`0xD964` (bank 7) | Addition #3 (WRAM battle-state) |
| Max party size in battle: [Wiki-documented, not in our data] | **[Wiki-documented, now in our maps]** — 3 player + 3 enemy slots structurally documented | Addition #3 (WRAM battle-state) |
| Encounter coverage: 16 areas | **45 areas** (29 added) — same structure | Addition #2 (encounters) |
| Personality-name canonical source: [Unknown] | **[ROM-verified address, 27 entries]** — `0x208D6`/`0x231F7` (content unread) | Addition #1 (string tables) |

### What is STILL MISSING (combat-resolution blockers — UNCHANGED)

**Every item on the prior "combat-resolution blockers" list remains [Unknown] / in unmapped code.** None of the four additions addresses any of these:

| Missing mechanic | Status | Why the additions don't help |
|---|---|---|
| **Damage formula** (ATK/DEF/skill-power/level combination) | **[Unknown — unchanged]** | String tables, encounter areas, battle-state RAM, and struct consolidation are all *data/state*, not the *routine*. |
| **Critical-hit routine/address** (confirmed exists, location unmapped) | **[Unknown — unchanged]** | No crit table mapped. The battle buffer has no crit field. |
| **Resistance byte value semantics** (0/1/2/3 = immune/resist/normal/weak) | **[Unknown — unchanged]** | The 27-byte resistance layout is mapped; the *value meaning* is not. No addition touches this. |
| **Turn order / initiative / action queue** | **[Unknown — unchanged]** | The battle-state region stores *per-slot stats* (incl. AGL), but the *sort/queue logic* that reads AGL is unmapped code. |
| **AI action-selection per tactic/personality** | **[Unknown — unchanged]** | WLD field exists but the AI routine that reads it (and the trait/aptitude bytes) is unmapped. |
| **Status-effect durations / tick rules / cure logic** | **[Unknown — unchanged]** | No status-duration table; status affinities remain folded into the 27-byte resistance table with unknown value semantics. |
| **Hit/accuracy resolution** | **[Unknown — unchanged]** | No accuracy field surfaced. |
| **Join/recruitment roll formula** | **[Unknown — unchanged]** | More encounter areas = more `join_value` bytes, but the tier→probability conversion is unmapped. |
| **Obedience/defiance threshold** | **[Unknown — unchanged]** | WLD field is *storage*; the threshold/decay rules are unmapped. |

### Verdict: faithful-portable, partially faithful, or needs upstream disassembly?

**Unchanged from prior findings: still requires the upstream disassembly for *faithful* combat.** The additions improve the extraction along two axes:

1. **Display/naming completeness** — skill, item, monster, family, and personality name tables are now addressable (though content needs a ROM read). A port can now point at authoritative name sources instead of relying on the XML's display-name list or the partial balancing-script ID→name map.
2. **Runtime state observability** — the battle-state region means a save-state inspector or debug overlay can now (once addresses are [ROM-verified]) read live HP/MP/stats per of 6 slots mid-battle, and the WLD field gives a handle on the obedience mechanic's *state*.

But neither axis touches the **resolution rules**. A combat simulator built strictly from this extraction (even with the additions) would still have all the entity data and now the live-state *layout*, but **none of the rules** that transform that state turn-to-turn: how ATK/DEF/skill-power combine into damage, who acts when, whether a hit lands, how status wears off, whether a monster joins, when it disobeys. Those are code routines in the battle bank, and this remains a **data-only extraction** (no disassembly). The gap is exactly where the prior findings left it: the [niyadev/dwm2_disassembly_github](https://github.com/niyadev/dwm2_disassembly_github) upstream.

**Honest tiering:**
- **Faithful combat (matches DWM2 damage/turn/AI/status/join outcomes):** NOT possible from this extraction alone — unchanged. Needs upstream disassembly.
- **Partially faithful combat (right entities, right state shape, original rules reverse-engineered or substituted):** Closer than before — the string tables and battle-state region reduce the *unknown-data* surface, so a port author substituting original rules has fewer gaps to paper over (e.g., they can now store WLD per slot, read authoritative names, model 3v3 confidently). But the *rules* are still the author's to design.
- **Data-faithful representation (right monsters, skills, stats, resistances, items, encounters, names):** Substantially improved — the extraction is now closer to "complete" for static combat data. The remaining static-data unknowns are: string *content* (needs ROM read), resistance *value* semantics, skill `element` byte decoding, and the personality *definition* table.

---

## Confidence Summary

| Claim | Confidence |
|---|---|
| 10 string tables (5 ptr + 5 data) exist at the documented bank-8 addresses, registered in `TABLES` | **[ROM-verified]** (`mod_data.py:129-301, 793-802`; `rom_map.txt:5-17`) |
| Skill-name and item-name string tables close the prior [ROM-verified absence] gaps (address + count) | **[ROM-verified]** addresses/counts; content **[Unknown]** (no ROM in repo) |
| Skill (50) / item (47) / personality (27) name-table entry counts match their respective data tables | **[ROM-verified]** count alignment (`mod_data.py:165/178/191` vs `:484/456` and wiki 27) |
| `parse_string_data` parser correctly walks null-terminated strings with ASCII filtering | **[ROM-verified]** logic inspected (`mod_data.py:200-235`); not executable here (no ROM) |
| Actual string content (sample names) is readable from this repo | **[Unknown — not readable]** no ROM file; no cached string dump found |
| WRAM bank-7 battle-state region (`0xD8B7`-`0xD964`) documents 6 slots × 9 stat groups | **[Wiki-documented]** (`ram_map.md:95-229`) — addresses from community ref, not live-probed |
| 3v3 party size is now structurally documented (3 player + 3 enemy slots) | **[Wiki-documented]** — stronger than prior "indirect" but still not [ROM-verified] |
| WLD (Wildness) field exists in the battle buffer at `0xD93F`-`0xD94B` | **[Wiki-documented]** field present; **[Unknown]** value semantics, decay, obedience threshold |
| Battle-state region resolves current HP/MP/stat *tracking*, NOT turn-order/action-queue/resolution rules | **[ROM-verified]** that the region stores state; **[ROM-verified absence]** of any resolution routine |
| "Useful Structures" section consolidates 3 already-known struct layouts (boss/encounter/core) | **[ROM-verified]** — predominantly reorganization; one new detail (5-slot encounter cap + worked example) |
| 29 new encounter areas use the identical already-documented encounter structure | **[ROM-verified]** (`mod_data.py:366-412`) — coverage expansion, no new mechanic |
| 27-personality *definition* table (trait→personality lookup) address remains unmapped | **[Unknown — unchanged]**; the name table (`0x231F7`) is labels, not the definition cube |
| Party-struct (bank 1, `0xDFC0+`) trait/personality/motivation byte offsets remain unmapped | **[Unknown — unchanged]**; battle-state region (bank 7) is a different, transient buffer |
| All 9 combat-resolution blockers (damage formula, crit, resistance semantics, turn order, AI, status, hit, join, obedience) remain [Unknown] | **[ROM-verified absence]** — none of the 4 additions is a routine or effect table |
| Faithful combat still requires the upstream disassembly | **[ROM-verified]** that this is a data-only extraction; verdict unchanged from prior findings |

---

## Sources

### Maintainer's additions (working-tree changes vs `HEAD` = `76fc334`)
- `tools/mod_data.py` (modified, +217 lines):
  - `:129-197` — 5 string pointer tables (`TABLE_FAMILY_NAME_POINTERS` … `TABLE_PERSONALITY_NAME_POINTERS`).
  - `:200-235` — `parse_string_data()` parser.
  - `:239-301` — 5 string data tables (`TABLE_FAMILY_NAMES` … `TABLE_PERSONALITY_NAMES`).
  - `:366-412` — `parse_random_encounters` area list expanded 16 → 45.
  - `:793-802` — 10 new entries registered in `TABLES`.
  - `:817-818` — `random_encounters` `num_entries` 16 → 45.
- `rom_maps/ram_map.md` (modified, +136 lines):
  - `:95-229` — "WRAM Bank 7 — Battle State" section (Level/HP/MP/ATK/DEF/AGL/INT/WLD/Icon × 6 slots).
  - `:101-103`, `:228` — [Wiki-documented] confidence caveats.
- `rom_maps/rom_map.txt` (modified, +73 lines):
  - `:3-17` — bank-8 string pointer/data region documented.
  - `:94-139` — "Useful Structures" section (boss / encounter / core monster structs).

### Prior findings (this repo, cross-referenced)
- [`combat_research_findings.md`](./combat_research_findings.md):
  - `:73, 257, 301, 302, 319, 331` — prior skill-name / item-name [ROM-verified absence] claims (now superseded by Q1).
  - `:125-126` (citing `ram_map.md:182`, now `:318`) — battle-state RAM unprobed; 3v3 indirect.
  - `:210-212` — random encounter structure (16 areas; now 45).
  - `:288-308` — the "NOT in extraction" / combat-resolution-blockers list (re-assessed as unchanged).
- [`personality_research_findings.md`](./personality_research_findings.md):
  - `:77, 256-272` — the 8 personality gaps (re-assessed in Q5; only Gap 7 partially addressed).
  - `:169-170, 197` — obedience/defiance [Wiki-documented, not mapped] (WLD field now gives storage, not rules).
  - `:237-246` — party-struct (bank 1) trait bytes [Unknown] (unchanged; bank 7 ≠ bank 1).
- [`stat_growth_research_findings.md`](./stat_growth_research_findings.md) — not directly affected by the 4 additions.

### Reference files (cited for cross-check)
- `rom_maps/battle_breeding_map.md:10-24, 89-94` — prior encounter/boss struct docs (confirmed consolidated, not contradicted, by "Useful Structures").
- `monster_data/core_monster_data.md:36-57` — 47-byte species template (matches `rom_map.txt:119-139`).
- `.gitignore` — confirms `*.gbc`/`*.gb`/`*.rom` excluded; no ROM in repo (limits string-content readability).
- `README.md:67` — "mod_data.py supports 20 data tables" (note: README table-count not yet updated for the 10 new string tables; actual registry now has 24 `TABLE_*` entries per `grep -c '": TABLE_'`).

### Upstream (referenced for the unchanged resolution-rule gap)
- [niyadev/dwm2_disassembly_github](https://github.com/niyadev/dwm2_disassembly_github) — where damage formula, turn engine, AI, status logic, crit/join tables, and the personality definition/effect tables would be resolved. Not part of this extraction.
