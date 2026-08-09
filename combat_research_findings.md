# DWM2 Combat — Research Findings

**Date:** 2026-07-05
**Author:** Investigation agent (reimplementation reference)
**Scope:** INVESTIGATION AND FINDINGS ONLY. No design, no code, no recommendations.
**Predecessors:** [`personality_research_findings.md`](./personality_research_findings.md) and [`stat_growth_research_findings.md`](./stat_growth_research_findings.md) (established the 4-trait/27-personality model, that Charge/Mixed/Defend/Command are battle tactics, and that stat growth is species-driven not personality-driven).

**Confidence legend** (used on every claim below):
- **[ROM-verified]** — pointable address / table / byte offset in this repo's extracted data
- **[Wiki-documented]** — described on wiki/community guides; not confirmed in our ROM extraction
- **[Unknown]** — looked, could not determine

---

## Summary

The DWM2 combat-relevant **data tables** are substantially present in this extraction: the **skill table** (with MP cost, element, and per-side damage values), the **27-byte per-species resistance table** (with element IDs decoded), the **skill-unlock-requirements table**, the **prebuilt-enemy struct** (fully-resolved stats + skills + 4 tactic/aptitude bytes), the **item table**, **encounter/boss/arena tables**, and the **EXP tables**. What is **almost entirely absent** is the **runtime combat logic**: the damage *formula* (how ATK/DEF/skill-power combine), turn-order / initiative rules, status-effect application and durations, critical-hit handling, the recruitment ("join") formula, and the AI action-selection routine are all **in unmapped code**, not in any documented data table. The extraction is a ROM *data* extraction, not a *disassembly* — so anything that is a *routine* rather than a *table* is out of scope here.

**One-line verdict:** the static inputs to combat are here; the dynamic rules of combat are not. A faithful combat simulator cannot be built from this extraction alone — the damage formula, turn order, and status/AI logic would need the upstream [DWM2 disassembly](https://github.com/niyadev/dwm2_disassembly_github) or original design work.

---

## Q1: Skills

**A skill definition table exists in the extraction.** [ROM-verified]

### Location & shape

| Property | Value | Source |
|---|---|---|
| Table name | `skills` | `tools/mod_data.py:277-299` (`TABLE_SKILLS`) |
| ROM offset | `0x680D4` | `tools/mod_data.py:279`; `rom_maps/rom_map.txt:57` ("skill data") |
| Entry size | **17 bytes** | `tools/mod_data.py:280` |
| Entries mapped | **50** (comment: "first ~18 are well-structured, rest may differ") | `tools/mod_data.py:281` |

### Fields per skill [ROM-verified]

There are **two complementary** field interpretations. `mod_data.py` defines generic byte-named fields, while `rom_map.txt` provides a **richer semantic reading** of the damage bytes. Cross-referencing both:

| Byte offset | `mod_data.py` field | `rom_map.txt:60-66` interpretation |
|---|---|---|
| 0 | `mp_cost` | MP cost |
| 1 | `tier` | *(unlabeled — "1 byte")* |
| 2 | `type_flag` | *(part of the "7 bytes ?")* |
| 3 | `flag_3` | *(part of the "7 bytes ?")* |
| 4 | `element` | *(part of the "7 bytes ?" — but mod_data names byte 4 `element`)* |
| 5–8 | `marker_b5`…`marker_b8` | *(completes the "7 bytes ?")* |
| 9–10 | `dmg_1` (LE u16) | **Player base damage** |
| 11–12 | `dmg_2` (LE u16) | **Player random additional damage** |
| 13–14 | `dmg_3` (LE u16) | **Enemy base damage** |
| 15–16 | `dmg_4` (LE u16) | **Enemy random additional damage** |

**Key reconciliation:** `rom_map.txt:57-66` reads the 17-byte skill entry as `MP(1) + Element(1) + ?(7) + 4×damage(8)`. `mod_data.py` labels byte 1 as `tier` and byte 4 as `element`, with bytes 5–8 as opaque markers. The two sources agree on offsets 9–16 being four 2-byte damage values, and **`rom_map.txt` explicitly splits them into player-vs-enemy × base-vs-random** — the most combat-actionable detail in the whole extraction. [ROM-verified for offsets; `rom_map.txt`'s player/enemy split is the most authoritative field-level reading available here]

### What fields are PRESENT vs ABSENT

| Field (asked for) | Present? | Notes |
|---|---|---|
| MP cost | ✅ byte 0 | [ROM-verified] |
| Power / damage | ✅ bytes 9–16 | 4 values (player base/rand, enemy base/rand) [ROM-verified] |
| Element/type | ✅ byte 4 (`element`) | [ROM-verified] field exists; **enum NOT decoded** — see below |
| Tier | ✅ byte 1 | [ROM-verified] field exists; **meaning unknown** |
| Target (one/all/ally/self) | ❌ not a named field | Possibly encoded in the opaque bytes 2–8; **[Unknown]** |
| Effect/status inflicted | ❌ not a named field | Status skills (Sleep, Poison, Paralyze, etc.) exist by name but their *status-effect ID* is not a documented field here; **[Unknown]** |
| Accuracy / hit rate | ❌ not a named field | **[Unknown]** — likely in opaque bytes or the damage routine |

### Skill element is NOT decoded

`mod_data.py` defines a rich enum `RESISTANCE_ELEMENT_IDS` (lines 86–115) mapping 28 element/effect IDs (0x00–0x1B: `attack`, `blaze_family`, `firebal_family`, `bang_family`, `wind_family`, `lightning_family`, `ice_family`, `radiant_family`, `sleep_family`, `eerie_family`, `dance_family`, `stopspell`, `panic_family`, `sap_family`, `slow_family`, `sacrifice_family`, `megamagic`, `fire_air`, `ice_air`, `poison_air`, `paralyze`, `curse`, `legsweep_family`, `danceshut`, `mouthshut`, `rockthrow_family`, `gigaslash`, `water_family`). **However, the `skills` table's `enums` map is empty `{}`** (`mod_data.py:298`) — this enum is wired to the *resistance* table, not to the skills table's `element` byte. So while the element vocabulary exists, **the skill-table `element` byte values are not mapped to these labels** in the extraction. The element vocabulary is almost certainly shared (a skill's element indexes the same family a resistance byte resists), but that linkage is **inferred, not documented**. [ROM-verified that the enum exists; inferred that it applies to skills; Unknown re: confirming the skill-element→resistance-element mapping byte-for-byte]

### Is there a skill NAME table? — No.

**No skill-name string table is mapped anywhere in this extraction.** [ROM-verified absence] I searched `rom_maps/`, `docs/`, `tools/`, and `monster_data/` for "skill name", "skill string", "skill text", "name table" — zero matches. `rom_map.txt` documents a `0x20000 Strings` region and a `0x22061C strings - list of prebuilt enemies by name`, but **no equivalent for skill names**. The disassembly (`35:4001` etc. referenced in `core_monster_data.md:23-26`) handles skill *IDs*, not names.

**Where skill names actually come from in this repo** (two partial sources, neither authoritative as a complete ID→name map):
1. **`monster_data/monster_data_external.xml`** — each of the 315 species lists its skills **by display name** (e.g. slime-family entries list `CallHelp`, `LushLicks`, `Imitate`, `Blaze`, `Upper`, etc.). [ROM-derived via upstream `MetroWind/dwm2-tools`, per README:149] There are **145 distinct skill names** across **1,015 skill-slots** in the XML. This is the largest skill vocabulary in the repo, but it is **name-only, no IDs, no power/MP/element** — purely "species X knows skills named A, B, C."
2. **`tools/balancing/generate_p2_pass3_skills.py`** — comment annotations map a **subset** of skill IDs → names (from the skill_requirements/prebuilt context). Verified mappings: `Ironize=33`, `BladeD=113`, `Surge=161`, `MPass=16`, `SuckAll=114`, `HealUs=97`, `LifeSong=30`, `BigBang=143`, plus names referenced in edit comments (`CallHelp`, `StopSpell`, `HighJump`, `OddDance`, `Cover`, `Sacrifice`, `Beat`, `PoisonHit`, `Infernos`, `LegSweep`, `Radiant`, `TwinHits`, `FireAir`, `CleanCut`, `AquaCut`, `MapMagic`, `MagicWall`, `Curse`, `ZombieCut`, `Focus`, `SleepAir`, `Paralyze`, `PaniDance`, `LoveRain`, `Upper`, `Chance`). [ROM-derived IDs from `mod_data.py` table indices; names cross-referenced from XML]

**Net:** The complete authoritative skill-ID → skill-name table almost certainly lives in the ROM's string region (near `0x20000`), but **its offset is not documented here**. A full ID→name→power map would require either dumping the `skills` table from a ROM (`mod_data.py --table skills --list`, which needs a ROM file — none is in this repo per the legal posture) plus the unmapped name strings, or consulting the upstream disassembly. [Unknown — location not mapped; resolvable via ROM dump or disassembly]

---

## Q2: Damage / combat formula

**The damage *inputs* are extractable; the damage *formula* is NOT.** The formula lives in code (the battle routine), which is not disassembled in this extraction.

### What IS extractable (inputs) [ROM-verified]

1. **Per-skill damage values** — the skill table (`0x680D4`, 17-byte entries) carries four 2-byte damage fields per skill, and `rom_map.txt:63-66` labels them **player base, player random additional, enemy base, enemy random additional**. This is the single most combat-relevant extracted datum: each skill has a deterministic base plus a random add, **split by whether the caster is the player or the enemy**. [ROM-verified]
2. **ATK and DEF stats** — the prebuilt-enemy struct stores fully-resolved `Attack` (offset 14, LE u16) and `Defense` (offset 16, LE u16) per encounter (`ram_map.md:137-138`, `mod_data.py:342-343`). For *party* monsters, ATK/DEF/AGI/INT are computed at level-up from species growth bytes (`core_monster_data.md:50-55`, bytes 14–17) × the `0x6A616` level table. [ROM-verified — see `stat_growth_research_findings.md` for the growth model]
3. **Skill element** — byte 4 of each skill entry (enum not decoded; see Q1). [ROM-verified field, Unknown semantics]
4. **Per-species resistances** — 27 bytes that modify incoming typed damage (see Q4). [ROM-verified]

### What is NOT extractable (the formula)

The extraction contains **no damage-calculation routine**. Specifically, none of these are documented as a table or code path anywhere in this repo:

| Mechanic | Status | Evidence of absence |
|---|---|---|
| How ATK, DEF, and skill power combine (e.g. `(ATK×skillBase − DEF×k)` vs additive vs multiplicative) | **[Unknown — not in extraction]** | No `rom_map.txt` entry; no `mod_data.py` table; grep for "damage"/"formula" finds only the skill-table field labels |
| Level's contribution to damage (beyond its effect on the ATK stat itself) | **[Unknown]** | No table; not mentioned in `stat_growth_research_findings.md` |
| Random variance beyond the per-skill `random additional` byte | **[Unknown]** | The skill table exposes one random term; whether the routine adds more is unmapped |
| **Critical hits** | **[Unknown — confirmed to exist, location unmapped]** | `core_monster_data.md:61`: "Unknown bytes at offsets 5 and 11 are **NOT critical hit rates; those are stored elsewhere**." So crit data exists in the ROM, but **its address is not in `rom_map.txt` or `mod_data.py`**. Carried forward from `personality_research_findings.md` Gap (c). |
| Elemental/resistance interaction multiplier (e.g. "resist = half damage, weak = 1.5×") | **[Unknown]** | The 27 resistance bytes exist (Q4) but **how a resistance byte's value modifies damage is not documented** — see Q4 |
| Hit/miss (accuracy) resolution | **[Unknown]** | No accuracy field in skills table; no hit-rate table |

**Bottom line for Q2:** The damage *formula* is a code routine in the battle bank (near `0xC138C`, the personality/tactic region, or adjacent), and this extraction is data-only — it does not contain disassembled routines. The skill damage *bytes* are extractable and useful as inputs, but **how they combine with ATK/DEF/level/resistance/crit is not in this repo**. Resolving it requires the upstream [DWM2 disassembly](https://github.com/niyadev/dwm2_disassembly_github).

---

## Q3: Action economy & turn order

**Very little is extractable. Most of the turn engine is in unmapped code.**

### What IS known

1. **The tactic system (Charge/Mixed/Defend/Command) is present as four data tables** — established by `personality_research_findings.md` Q2. Each is 8 entries × 4 bytes (`stat_id` / `modifier_hi` / `modifier_lo` / `flag`) at `0xC138C`/`0xC13AC`/`0xC13CC`/`0xC13EC` (`mod_data.py:485-543`, `rom_map.txt:72-75`). These four are the player-selectable battle tactics. **However**, these tables encode the tactic's effect on the *hidden personality traits* (Bravery/Prudence/Caring/Motivation drift), **not** an immediate in-battle stat modifier or action. Their byte-level meaning is [Unknown] without a ROM dump. [ROM-verified addresses + Wiki-documented purpose]
2. **MP costs exist per skill** (skill table byte 0) and **tactic selection is a player action**, but **what action the monster actually performs under each tactic is AI-determined and not in a data table here.** [ROM-verified MP costs; Unknown re: tactic→action resolution]
3. **Agility is a stored stat** (prebuilt struct offset 18; party growth byte 16). [ROM-verified]

### What is NOT extractable

| Mechanic | Status | Notes |
|---|---|---|
| **Turn order / initiative** (does Agility sort the action queue?) | **[Unknown — not in extraction]** | No turn-order table, no initiative sort routine, no action-queue RAM structure documented. `ram_map.md:178-183` "Remaining Unknowns" explicitly lists "Battle state RAM region: Not yet probed (requires entering battle)." The party-struct field offsets for HP/MP/stats are also unmapped. |
| **Party size** (monsters per side) | **[Partially known, indirect]** | The prebuilt-enemy struct is per-individual; `boss_battles` (`0x2881C`, 8-byte entries) stores `count = enemies−1` + up to 3 enemy prebuilt IDs (`mod_data.py:665-678`, `rom_map.txt:7-12`), implying **up to 3 enemies per boss fight** (DWM2U bumps most to 3, per `dwm2u_analysis.md:18,65`). Player party count is tracked at WRAM `0xC563` (1 byte) (`ram_map.md:39`). The *max* party size in battle is not numerically stated in this repo. [Wiki-documented elsewhere as 3 per side for DWM2; not confirmed in our extraction] |
| **The "command" vs "tactic" action modes** | **[Wiki-documented, not in extraction]** | Per `personality_research_findings.md` Q2/Q3: "Command" = player picks the exact action (lowers Motivation); the three tactics (Charge/Mixed/Defend) = player sets a stance and the AI picks the action (raises Motivation). This is wiki-described; **no AI action-selection table or obedience/defiance threshold is mapped here.** |
| **Action selection / AI weights per personality** | **[Unknown — not in extraction]** | Carried from `personality_research_findings.md` Q4(a): "No AI-behavior table is present in this repo's ROM maps." |

**Bottom line for Q3:** The tactic *stance system* is present as data (4 tables), but the actual turn engine — initiative, action resolution, party-size enforcement, AI behavior — is entirely in unmapped code. The `ram_map.md` authors note the battle-state RAM region was never probed.

---

## Q4: Resistances & status effects

### The 27 resistance bytes — well documented as *which elements*, but *value encoding* is unknown.

**Location:** core monster species template, bytes 18–44 (27 bytes), at ROM `0xD433B` onward (324 species × 47 bytes). [ROM-verified] — `core_monster_data.md:56`, `mod_data.py:404-431`, mirrored in `ram_map.md:59` (working buffer offset `+0x12`).

**What each byte resists** — fully labeled via `RESISTANCE_ELEMENT_IDS` (`mod_data.py:86-115`). The 27 resist fields map to:

| Byte | Field (`mod_data.py`) | Resists |
|---|---|---|
| 18 | `resist_0_attack` | attack (normal/m physical) |
| 19 | `resist_1_blaze` | blaze_family |
| 20 | `resist_2_firebal` | firebal_family |
| 21 | `resist_3_bang` | bang_family |
| 22 | `resist_4_wind` | wind_family |
| 23 | `resist_5_lightning` | lightning_family |
| 24 | `resist_6_ice` | ice_family |
| 25 | `resist_7_radiant` | radiant_family |
| 26 | `resist_8_sleep` | sleep_family |
| 27 | `resist_9_eerie` | eerie_family |
| 28 | `resist_10_dance` | dance_family |
| 29 | `resist_11_stopspell` | stopspell |
| 30 | `resist_12_panic` | panic_family |
| 31 | `resist_13_sap` | sap_family |
| 32 | `resist_14_slow` | slow_family |
| 33 | `resist_15_sacrifice` | sacrifice_family |
| 34 | `resist_16_megamagic` | megamagic |
| 35 | `resist_17_fire_air` | fire_air |
| 36 | `resist_18_ice_air` | ice_air |
| 37 | `resist_19_poison_air` | poison_air |
| 38 | `resist_20_paralyze` | paralyze |
| 39 | `resist_21_curse` | curse |
| 40 | `resist_22_legsweep` | legsweep_family |
| 41 | `resist_23_danceshut` | danceshut |
| 42 | `resist_24_mouthshut` | mouthshut |
| 43 | `resist_25_rockthrow` | rockthrow_family |
| 44 | `resist_26_gigaslash` | gigaslash |

**So the 27 bytes resist a mix of:** damage *elements* (blaze, firebal, bang, wind, lightning, ice, radiant, megamagic, gigaslash, water — via the enum's 0x1B), *air/inhalation* attacks (fire_air, ice_air, poison_air), and **status/effect families** (sleep, eerie, dance, stopspell, panic, sap, slow, sacrifice, paralyze, curse, legsweep, danceshut, mouthshut, rockthrow). This is significant: **resistances double as the status-effect-affinity system** — sleep, paralyze, curse, etc. are resisted by the same 27-byte mechanism, not a separate status table. [ROM-verified element IDs; inferred that status resistances and elemental resistances share one mechanism]

**Numbering quirk:** the `RESISTANCE_ELEMENT_IDS` enum has **28 entries** (0x00–0x1B), but the struct has only **27 resist bytes** (offsets 18–44, mapping to enum IDs 0x00–0x1A). The enum's final entry `0x1B water_family` has **no corresponding `resist_27` field** in `mod_data.py`. Either byte 44 (`gigaslash`, enum 0x1A) is the last true resist and `water_family` is vestigial/used-elsewhere, or one resist byte is unexposed. [ROM-verified discrepancy — 28 enum labels vs 27 fields]

### Resistance byte VALUE encoding — [Unknown]

**How a resistance byte's value (0–255, or a smaller enum) modifies damage/status is not documented anywhere in this extraction.** Neither `rom_map.txt`, `mod_data.py`, `core_monster_data.md`, nor `ram_map.md` states what values mean (e.g. 0=immune, 1=resist-75%, 2=resist-50%, 3=normal, 4=weak-150%…). No enum is wired to the resist fields (`core_monster`'s `enums` only covers `join_rate`). The interpretation of these bytes requires reading the damage routine in the disassembly. [Unknown — value semantics not in extraction]

**Caveat:** Because no ROM file is in this repo (legal posture, `.gitignore`), the actual byte values across species can't be inspected here either — only the *layout* and *element labels* are mapped.

### Is there a separate status-effect system / table? — No dedicated table.

There is **no standalone status-effect definition table** (no "status effects" entry in `rom_map.txt` or the `TABLES` registry). What exists:

- **Status *affinities*** are folded into the 27-byte resistance table (sleep, paralyze, curse, poison_air, panic, slow, sap, etc. are all resistance slots — see above). [ROM-verified]
- **Status *infliction*** is implicit in skills: skills named `Sleep`, `SleepAir`, `PoisonHit`, `Paralyze`, `Curse`, `PaniDance`, `Slow`, `Beat`, `StopSpell` etc. appear in the XML (`monster_data_external.xml`) and the balancing-script comments. Their status-effect *ID* and *duration/tick mechanics* are **not** in any data table here. [ROM-verified that status-named skills exist; Unknown re: their mechanical resolution]
- **Cape resistances** (`0x64641`, 7 capes × up to 16 effect IDs, `0x80`-terminated, `mod_data.py:456-481`) — equipment that grants resistances; references the same effect-ID vocabulary. [ROM-verified]

**Bottom line for Q4:** The resistance *table layout and element vocabulary* are fully ROM-verified and combat-useful. The *value semantics* (what a resistance byte value means numerically) and any *status-duration / tick / cure* tables are **absent** — those are runtime logic, not data.

---

## Q5: Encounters

**Encounter data is substantially present and goes well beyond the prebuilt-enemy struct.**

### Encounter-related tables [all ROM-verified]

| Table | Offset | Shape | Source |
|---|---|---|---|
| **Prebuilt enemies** | `0xD0075` (IDs 0–299), `0x288056` (IDs 300–599) | 26 bytes × 600 entries | `mod_data.py:325-354`, `ram_map.md:120-144`, `battle_breeding_map.md:26-58` |
| **Random encounters** (per-world) | `0x29773` | 16 named world areas | `mod_data.py:600-609` (parser `parse_random_encounters`), `battle_breeding_map.md:10-24` |
| **Boss battles** | `0x2881C` | 8 bytes × 40 entries (`count`, 3× enemy prebuilt IDs) | `mod_data.py:665-678`, `rom_map.txt:6-12` |
| **Arena teams** | `0x3387F`–`0x33911` | per-class (Kiddie/C/B/A/S) team lists | `rom_map.txt:25-36` |
| **Arena rewards** | `0x335DE` | 4 classes × chance tables + reward item IDs | `mod_data.py:590-599` (parser `parse_arena_rewards`) |
| **Gift/event monsters** | `0x7098` | 9 LE16 prebuilt IDs | `mod_data.py:652-662` |
| **Wandering masters** | `0x286AE`/`0x286EE` | length + monster-set lists | `rom_map.txt:3-5` |

### Random encounter structure (per area) [ROM-verified]

`parse_random_encounters` (`mod_data.py:178-239`) documents each area's encounter structure as: `max_enemies(1) + max_chance(1) + chance_thresholds(5) + prebuilt_ids(variable, up to 5×2 bytes)`. The 16 areas are enumerated: `oasis_world` (`0x29773`), `well`, `pirate_world`, `hoodsquid_cave`, `harmirror_cave_1f/2f/3f`, `moonrock_tower_1f/2f`, `ghost_ship_1f`, `ice_world`, `gold_mine`, `spooky_forest`, `sky_world`, `limbo_world`, `elf_world`. So **spawn rates and per-region encounter tables ARE extractable** (max enemies, frequency band, and the prebuilt-ID pool per band). [ROM-verified]

### The "Join" / recruitment mechanic — byte present, formula NOT.

- **Join value byte:** present in two places. (a) Prebuilt-enemy struct offset `+0x08` (`join_value`, 1 byte) — `mod_data.py:338`, `ram_map.md:132`. (b) Core species template byte 4 (`join_rate`) — `mod_data.py:390`, `core_monster_data.md:42`. Both use the `JOIN_RATE` enum (`mod_data.py:118-127`): `0=always, 1=very_easy, 2=easy, 3=medium, 4=hard, 5=very_hard, 6=extreme, 7=never`. [ROM-verified]
- **The join *formula* (how join_value, meat items, monster HP, and randomness combine to produce a recruitment roll): [Unknown — not in extraction].** No recruitment routine, no meat-modifier table, no HP-threshold table is mapped. The byte encodes a *tier*, not a probability; the conversion is in code. The DWM2U ReadMe (`DWM2U ReadMe.txt:49`) mentions some bosses "require meat" to recruit — confirming a meat item interacts with the join roll — but no mechanic details are in our data. [ROM-verified tier byte; Wiki/ReadMe-documented that meat affects join; Unknown re: formula]

**Bottom line for Q5:** Encounters are a **strength** of this extraction — prebuilt enemies, per-world random-encounter tables, boss compositions, arena teams, and join-rate *tiers* are all present. The missing piece is the **join-roll formula** (runtime logic) and any shiny/recruitment-bonus interaction (the `battle_breeding_map.md` "Shiny System Integration" section is a *mod plan*, not extracted game data).

---

## Q6: Items

**An item definition table EXISTS and is well-structured.** [ROM-verified]

### Location & shape

| Property | Value | Source |
|---|---|---|
| Table name | `items` | `tools/mod_data.py:249-275` (`TABLE_ITEMS`) |
| ROM offset | `0x58CC2` | `mod_data.py:251`; `rom_map.txt:54` ("Item Data") |
| Entry size | **13 bytes** | `mod_data.py:252` |
| Entries | **47** (entry 0 = null placeholder) | `mod_data.py:253` |

### Fields per item [ROM-verified]

| Byte | Field | Decoded? |
|---|---|---|
| 0 | `effect_type` | ✅ enum `ITEM_EFFECT_TYPES`: healing / status_change / attribute_modifier / reduce_wild / cast_spell / teleport / unique_key_equip |
| 1–2 | `price` (LE u16) | ✅ |
| 3 | `unknown_0` | ❌ |
| 4 | `usability` | ✅ enum `ITEM_USABILITY`: always / out_of_battle / in_battle / never |
| 5 | `unknown_1` | ❌ |
| 6 | `targeting` | ✅ enum `ITEM_TARGETING`: one_ally / one_enemy / all_enemies / one_ally_or_enemy / all_allies / no_target (plus 2 unknown) |
| 7 | `world_map_icon` | ✅ enum `ITEM_WORLD_MAP_ICON`: leaf, bottle, bell, seed, meat, staff, warp_wing, tiny_medal, etc. |
| 8 | `unknown_2` | ❌ |
| 9 | `effect_byte_1` | ❌ (effect parameter) |
| 10 | `effect_byte_2` | ❌ (effect parameter) |
| 11 | `variable_1` | ❌ |
| 12 | `variable_2` | ❌ |

`effect_type=0x03 reduce_wild` is striking — that is the **meat/bait item category for wild-monster recruitment** (ties to Q5's join mechanic). `effect_type=0x04 cast_spell` means some items cast a skill effect. So items have a real combat-relevant structure: usability (in-battle flag), targeting, effect type, and two effect-parameter bytes. [ROM-verified]

### What is ABSENT for items

- **Item NAME table** — like skills, no item-name string table is mapped. Item names appear only indirectly (the `world_map_icon` enum and DWM2U ReadMe narrative name a few: Antidote, Laurel, WarpWing, WarpStaff, ExitBell, Herbs, Lovewater, Potion, Meats, Sirloin, Seeds, TinyMedal, MeteOrb). The authoritative ID→name strings live in the unmapped ROM string region. [ROM-verified absence in our maps]
- **Effect-parameter semantics** — bytes 9–12 (`effect_byte_1/2`, `variable_1/2`) are opaque. For a healing item these presumably encode heal amount; for `reduce_wild` (meat) they presumably encode join-roll modifier — but **the encoding is not documented**. [Unknown]
- **In-battle item-use routine** — code, not data. [Unknown]
- **Shop inventories** are separately mapped (`0x72188`, `mod_data.py:547-572`, 20 shops × up to 16 item IDs, `0xFF`-terminated) — so where items are sold is extractable, even though item *names* are not. [ROM-verified]

**Bottom line for Q6:** The item **table exists** with a rich, partially-decoded schema (effect type, usability, targeting, icon, price) — enough to know *which* items exist and *that* they have in-battle effects. The effect *parameters* and the item-name strings are not decoded. A future items data file has a real ROM table to map from.

---

## What's IN the extraction vs. NOT

This is the key decision input for whether a combat simulator can be faithfully built *now, from this extraction alone*.

### ✅ IN the extraction (ROM-verified data tables)

| Combat asset | Where | Usefulness |
|---|---|---|
| Skill table (MP, element byte, 4 damage values: player/enemy × base/random) | `0x680D4`, 17B×50 | High — skill power & cost |
| Skill-unlock-requirements table (level, 6 stat thresholds, prereq, 4 combine skills) | `0x6900A`, 18B×80 | Medium — skill progression |
| 27-byte resistance table per species + decoded element vocabulary (28 IDs) | `0xD433B` bytes 18–44 | High — damage typing |
| Prebuilt-enemy struct (species, 4 skills, EXP, join tier, level, full stats, 4 tactic/aptitude bytes) | `0xD0075`/`0x288056`, 26B×600 | High — enemy instantiation |
| Core species template (family, join rate, 3 skills, 6 growth bytes, 27 resistances) | `0xD433B`, 47B×324 | High — species base data |
| Item table (effect type, price, usability, targeting, icon, 4 effect params) | `0x58CC2`, 13B×47 | Medium — items & in-battle item use |
| Per-world random-encounter tables (max enemies, chance bands, prebuilt-ID pools) | `0x29773`, 16 areas | High — encounter spawning |
| Boss battles (count + up to 3 prebuilt IDs) | `0x2881C`, 8B×40 | High — boss composition |
| Arena teams & rewards (per-class C/B/A/S) | `0x3387F`/`0x335DE` | Medium — arena mode |
| Stat-growth & EXP tables | `0x6A616` / `0x64E60` | High — leveling (already ported) |
| 4 tactic tables (Charge/Mixed/Defend/Command → trait drift) | `0xC138C`–`0xC13EC` | Low for combat sim proper (drives personality drift, not immediate battle action) |
| Species skill-name lists (145 distinct names, 1015 slots) | `monster_data_external.xml` | Medium — naming only, no IDs/power |
| Partial skill-ID → name map (~30 skills) | `tools/balancing/generate_p2_pass3_skills.py` comments | Low — partial, anecdotal |

### ❌ NOT in the extraction (Unknown / in unmapped code)

| Missing combat mechanic | Needed for? | Resolvable via |
|---|---|---|
| **Damage formula** (ATK/DEF/skill-power/level combination) | Faithful damage calc | Upstream disassembly |
| **Critical-hit table/address** (confirmed to exist, location unmapped — `core_monster_data.md:61`) | Crit handling | Upstream disassembly |
| **Resistance byte value semantics** (what 0/1/2/3… means: immune/resist/normal/weak) | Applying resistances to damage | ROM dump + disassembly |
| **Turn order / initiative / action queue** | Turn engine | Upstream disassembly (battle-state RAM also unprobed — `ram_map.md:182`) |
| **AI action-selection per tactic/personality** | Enemy & tactic-driven ally behavior | Upstream disassembly |
| **Obedience/defiance thresholds** (Motivation→Command compliance) | Command tactic | Upstream disassembly |
| **Status-effect durations / tick rules / cure logic** | Status ailments | Upstream disassembly |
| **Hit/accuracy resolution** | Miss/crit rates | Upstream disassembly |
| **Join/recruitment roll formula** (join tier + meat + HP → probability) | Wild recruitment | Upstream disassembly |
| **Skill-ID → skill-name authoritative string table** | Skill display | ROM string region (~`0x20000`, unmapped) or disassembly |
| **Item-ID → item-name string table** | Item display | ROM string region (unmapped) |
| **Skill `element` byte decoding** (enum exists for resistances, not wired to skills) | Skill→element labeling | ROM dump (apply existing enum) |
| **Party-monster in-battle struct** (HP/MP/status field offsets in WRAM) | Runtime state | Live WRAM probing (`tools/discovery/map_party_struct.py`) or disassembly |
| **Max party size in battle** | Encounter scaling | Wiki says 3v3 for DWM2; not confirmed in our data |
| **27-personality definition table** (trait→personality lookup; personality→AI/growth/co-op) | Personality-driven AI/co-op | Upstream disassembly (carried from prior findings) |

**Verdict:** A combat simulator built strictly from this extraction would have **all the entity data** (species stats, skills with damage values, resistances, items, enemies, encounters) but **none of the resolution rules** (how damage is computed, who acts when, whether a hit lands, how status wears off, whether a monster joins). The data layer is sufficient to *represent* a battle; it is not sufficient to *resolve* one faithfully against DWM2. The gap is the battle-routine disassembly.

---

## Confidence Summary

| Claim | Confidence |
|---|---|
| Skill table exists at `0x680D4`, 17B×50, with MP/element/4 damage fields | **[ROM-verified]** (`mod_data.py:277-299`, `rom_map.txt:57-66`) |
| Skill damage bytes 9–16 = player base / player random / enemy base / enemy random | **[ROM-verified]** (`rom_map.txt:63-66` — most authoritative field reading) |
| Skill `element` byte (offset 4) exists but its enum is NOT decoded for skills | **[ROM-verified]** field + absence; **[inferred]** that resistance-element enum applies |
| No skill-name string table is mapped in this extraction | **[ROM-verified absence]** (exhaustive grep of maps/docs/tools) |
| 145 distinct skill names exist in the XML (name-only, no IDs/power) | **[ROM-derived via upstream MetroWind/dwm2-tools]** |
| Damage *formula* (ATK/DEF/level/power combination) is not in the extraction | **[ROM-verified absence]** (data-only extraction; no routine documented) |
| Crit data exists but its address is unmapped | **[ROM-verified]** that it exists (`core_monster_data.md:61`); **[Unknown]** location |
| 27 resistance bytes per species + 28-ID element vocabulary are decoded | **[ROM-verified]** (`mod_data.py:86-115, 404-431`) |
| Resistance byte *value* semantics (immune/resist/weak mapping) are undocumented | **[Unknown]** (no enum wired; no doc) |
| Status affinities fold into the 27-byte resistance table (no separate status table) | **[ROM-verified]** element labels include sleep/paralyze/curse/poison/panic/slow/sap |
| Tactic system (Charge/Mixed/Defend/Command) present as 4 trait-drift tables | **[ROM-verified]** addresses; **[Wiki-documented]** purpose; **[Unknown]** byte-level meaning |
| Turn order, initiative, action queue, AI selection are not in the extraction | **[ROM-verified absence]**; `ram_map.md:182` confirms battle-state RAM unprobed |
| Random encounter tables (16 areas) + prebuilt enemies (600) + bosses (40) are present | **[ROM-verified]** |
| Join-rate *tier* byte present (0–7 enum); join *formula* absent | **[ROM-verified]** tier; **[Unknown]** formula |
| Item table exists at `0x58CC2`, 13B×47, with effect-type/usability/targeting enums decoded | **[ROM-verified]** |
| Item-name and skill-name authoritative string tables are absent from our maps | **[ROM-verified absence]** |
| Party-monster in-battle struct field offsets (HP/MP/status) are unmapped | **[ROM-verified that it's unknown]** (`ram_map.md:178-183`) |
| Anything that is a code *routine* (damage calc, turn engine, AI, status tick, recruitment roll) lives in the upstream disassembly, not here | **[ROM-verified]** that this is a data-only extraction (README:5, README:106) |

---

## Sources

### Local extracted data (this repo)
- `README.md` — overview; lines 67-87 (20-table inventory); line 149 (XML sourced from MetroWind/dwm2-tools).
- `tools/mod_data.py` — the master table registry:
  - Lines 44-127: enums `ITEM_EFFECT_TYPES`, `ITEM_USABILITY`, `ITEM_TARGETING`, `ITEM_WORLD_MAP_ICON`, `RESISTANCE_ELEMENT_IDS`, `JOIN_RATE`.
  - Lines 249-275: `TABLE_ITEMS` (`0x58CC2`, 13B×47).
  - Lines 277-299: `TABLE_SKILLS` (`0x680D4`, 17B×50) — note `enums: {}` (element not decoded).
  - Lines 301-311: `TABLE_STAT_GROWTH` (`0x6A616`).
  - Lines 325-354: `TABLE_PREBUILT_ENEMIES` (`0xD0075`, 26B×600; join_value offset 8).
  - Lines 356-377: `TABLE_SKILL_REQUIREMENTS` (`0x6900A`, 18B×80; combine_skill_1-4 offsets 14-17).
  - Lines 379-437: `TABLE_CORE_MONSTER` (`0xD433B`, 47B×324; resist_0..26 offsets 18-44).
  - Lines 441-451: `TABLE_EXP_TABLES` (`0x64E60`).
  - Lines 456-481: `TABLE_CAPE_RESISTANCES` (`0x64641`).
  - Lines 485-543: four `TABLE_PERSONALITY_*` tactic tables (`0xC138C`-`0xC13EC`).
  - Lines 547-572: `TABLE_SHOP_INVENTORIES` (`0x72188`).
  - Lines 575-679: full `TABLES` registry (incl. `arena_rewards`, `random_encounters`, `magic_key_*`, `gift_monsters`, `boss_battles`).
  - Lines 178-239: `parse_random_encounters` (16-area encounter structure).
- `rom_maps/rom_map.txt`:
  - Lines 6-12: boss battle 8-byte struct.
  - Lines 13, 57-66: skill data region with the player/enemy base/random damage split (the authoritative field reading).
  - Lines 54-55: item data, cape resistances.
  - Lines 67-68: skill requirements, stat growth.
  - Lines 72-75: Charge/Mixed/Defend/Command personality-effect tables.
  - Lines 76-84: prebuilt enemies (part 1 + part 2), core monster data region.
- `rom_maps/ram_map.md`:
  - Lines 44-60: Monster Working Buffer (`0xC008`), 47-byte template fields incl. `+0x12` 27-byte resistances.
  - Lines 120-144: prebuilt-enemy struct (cross-confirm; agility offset 18, join offset 8).
  - Lines 178-183: **Remaining Unknowns** — party-struct size, HP/MP/stat offsets, **battle-state RAM region unprobed**, save-file integration.
- `rom_maps/battle_breeding_map.md`:
  - Lines 10-24: random encounter table structure.
  - Lines 26-58: prebuilt-enemy struct.
  - Lines 87-95: boss battle compositions.
  - Lines 98-107: encounter load path (26-byte ROM→WRAM memcpy).
  - Lines 130-176: "Shiny System Integration" — a *mod plan*, not extracted game data.
- `monster_data/core_monster_data.md` — 47-byte species template; **line 61: crit rates "stored elsewhere"** (confirms crit data exists, location unmapped).
- `monster_data/monster_data_external.xml` — 315 species; per-species skill lists by name (145 distinct names, 1015 slots), spawn locations, growth stats. **No resistance bytes, no skill IDs, no skill power.**
- `monster_data/breeding_data.md` — breeding pointers/lists; **no combat-relevant data** (confirmed: purely mate→result species resolution).
- `monster_data/prebuilt_id_usages.md` — prebuilt ID → in-game context (bosses, arenas, wandering masters, NPC breeding partners 174-178).
- `tools/balancing/generate_p2_pass3_skills.py` — partial skill-ID → name map (Ironize=33, BladeD=113, Surge=161, MPass=16, SuckAll=114, HealUs=97, LifeSong=30, BigBang=143, +~20 more named in comments).
- `dwm2u_reference/dwm2u_analysis.md` and `DWM2U ReadMe.txt` — DWM2 Ultimate hack analysis; reveals which *systems* exist (skill element changes line 108-118, boss counts, meat-required recruitment line 49 of ReadMe, EXP rank reductions) but is a mod changelog, not a mechanic specification.
- `docs/tools_guide.md` — confirms table inventory and that `core_monster` exposes `skill_1/2/3` + `resistances`.

### Predecessor findings (this repo)
- [`personality_research_findings.md`](./personality_research_findings.md) — established the 4-trait/27-personality model; Charge/Mixed/Defend/Command are battle *tactics* (4 tables at `0xC138C`); tactic→trait drift; all 5 personality downstream effects (AI, obedience, crit, healing, co-op) are **[Unknown]** in this repo.
- [`stat_growth_research_findings.md`](./stat_growth_research_findings.md) — stat growth is species-driven (growth bytes × `0x6A616` level table), not personality-driven; prebuilt/wild monster stats are hardcoded final values copied verbatim into WRAM.

### Upstream / external (referenced for gap resolution, not fetched)
- [niyadev/dwm2_disassembly_github](https://github.com/niyadev/dwm2_disassembly_github) — the DWM2 disassembly; referenced by this repo's README:106 as the source (0.002% byte-match at time of use). **This is where the damage formula, turn engine, AI, status logic, and crit/join tables would be resolved.** Not part of this extraction.
- [dragon-warrior-monsters-2-modding wikia — ROM Map](https://dragon-warrior-monsters-2-modding.wikia.com/wiki/ROM_Map) — community ROM map (credited in DWM2U ReadMe:142); may document additional combat addresses not in this repo.
