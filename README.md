# DWM2 Hacking Tools

Python tools and data references for modding **Dragon Warrior Monsters 2** (Game Boy Color).

This repository contains everything you need to edit game data tables — monster stats, breeding formulas, boss compositions, items, skills, and more — without hand-editing hex values. It was built by disassembling the US Cobi ROM, cross-referencing a known ROM hack (DWM2 Ultimate), and verifying every change against the original via byte-diff testing.

## What's Inside

| Directory / File | Contents |
|-----------|----------|
| [`tools/`](tools/) | Python ROM hacking utilities |
| [`monster_data/`](monster_data/) | Complete species database (315 monsters, 554 breeding formulas) |
| [`mechanics/`](mechanics/) | Mechanic specs: recruitment formula, resistances, skill requirements, encounters, items, magic keys, strings |
| [`rom_maps/`](rom_maps/) | ROM and RAM memory maps |
| [`dwm2u_reference/`](dwm2u_reference/) | DWM2 Ultimate hack analysis (case study) |
| [`edits/`](edits/) | Example balancing edits (ready-to-apply JSON configs) |
| [`coverage_map.md`](coverage_map.md) | **One-stop verdict**: which subsystems are faithful-portable vs. need original design |
| [`disassembly_inventory.md`](disassembly_inventory.md) | What the vendored niyadev disassembly covers (and what it doesn't) |
| [`personality_research_findings.md`](personality_research_findings.md) | DWM2 personality system: 4 traits → 27 personalities, tactics vs. personalities |
| [`stat_growth_research_findings.md`](stat_growth_research_findings.md) | Stat growth is species+level only (personality does NOT affect it) |
| [`combat_research_findings.md`](combat_research_findings.md) | Combat data inventory (skills, resistances, items, encounters) |
| [`combat_reassessment_findings.md`](combat_reassessment_findings.md) | Re-assessment after string-table / WRAM additions |

### For MonTamer (the reimplementation project)

`dwm2-hacking-tools/` is the **single source of truth** that MonTamer's design specs reference. Before specing any DWM2-derived subsystem, read [`coverage_map.md`](coverage_map.md) — it says whether to implement faithfully (from a [ROM-verified] or [Mechanic-documented] source) or design originally (for an [Unknown]).

## Quick Start

### Prerequisites

- **Python 3.10+**
- A **DWM2 GBC ROM** (US Cobi version, 4 MB / 256 banks)
- Optional: **PyBoy 2.7.0** for runtime tools (`pip install pyboy pillow`)

### Edit a Data Table

```bash
# List available tables
python tools/mod_data.py your_rom.gbc --tables

# View all skills
python tools/mod_data.py your_rom.gbc --table skills --list

# Show a single monster entry
python tools/mod_data.py your_rom.gbc --table core_monster --show 25

# Edit and write a patched ROM
python tools/mod_data.py your_rom.gbc \
    --table items \
    --edit '{"5": {"price": 999}}' \
    --output patched_rom.gbc

# Apply edits from a JSON file, generate IPS patch
python tools/mod_data.py your_rom.gbc \
    --table core_monster \
    --edit-file edits/phase2_pass1.json \
    --ips build/balance_patch.ips
```

See [`docs/tools_guide.md`](docs/tools_guide.md) for detailed usage of each tool.

### Bulk Balancing Edits

The `tools/balancing/` scripts generate JSON configs that apply across 315 species:

```bash
# Generate stat growth edits, then apply via mod_data.py
python tools/balancing/generate_p2_pass1.py > my_edits.json
python tools/mod_data.py your_rom.gbc \
    --table core_monster \
    --edit-file my_edits.json \
    --output patched_rom.gbc
```

## Supported Data Tables

`mod_data.py` supports **20 data tables** covering all documented game data:

| Table | Entries | What It Controls |
|-------|---------|-----------------|
| `items` | 47 | Item effects, prices, usability, targeting |
| `skills` | 50 | MP cost, element, damage values |
| `core_monster` | 324 | Species stats, skills, growth rates, resistances |
| `stat_growth` | 99 | Per-level stat growth (1 byte per level) |
| `exp_tables` | 100 | XP required per level (3-byte LE u24) |
| `breeding` | 100 | Mate/result pointers for breeding formulas |
| `prebuilt_enemies` | 600 | Boss/NPC enemy compositions (species, skills, stats) |
| `boss_battles` | 40 | Enemy count, prebuilt IDs per boss fight |
| `skill_requirements` | 80 | Level/stat prerequisites, combine skills |
| `cape_resistances` | 7 | Effect IDs per cape type |
| `personality_*` | 4 tables | Charge/Mixed/Defend/Command stat modifiers |
| `shop_inventories` | 20 | Item ID lists (0xFF-terminated) |
| `arena_rewards` | variable | Chance tables + reward items per arena class |
| `random_encounters` | variable | Per-world encounter tables (prebuilt IDs) |
| `magic_key_*` | 54 | Key generation prefixes/suffixes |
| `gift_monsters` | 9 | Prebuilt IDs for gift/event monsters |

Variable-length tables (arena_rewards, random_encounters) use custom parsers. Fixed-size tables use direct offset math.

## Data References

### Species Database (`monster_data/`)

- **`monster_data_external.xml`** — 315 species with names, spawn locations, growth rates, skills
- **`breeding_data.md`** — 554 breeding formulas (species+species, species+family, family+family)
- **`core_monster_data.md`** — Full monster stats, skills, and resistances tables
- **`prebuilt_id_usages.md`** — Maps prebuilt enemy IDs to in-game contexts (bosses, trainers, arena)

### ROM Map (`rom_maps/`)

- **`rom_map.txt`** — Hand-curated data table offsets (where things live in the ROM)
- **`ram_map.md`** — WRAM memory map (party structs, runtime state)

## How It Was Built

1. **Disassembly** — The [DWM2 disassembly](https://github.com/niyadev/dwm2_disassembly_github) was used as the starting point (0.002% byte-match at time of use)
2. **Byte-diff testing** — Every patched ROM was compared against the original via static diff (no unexpected changes)
3. **DWM2 Ultimate cross-reference** — A known ROM hack with 441 patch locations was analyzed to validate table offsets and field semantics
4. **Runtime verification** — PyBoy (headless GBC emulator) was used to verify patched ROMs boot correctly and that memory state matches expectations
5. **Label generation** — 375/441 DWM2U patches were labeled with table/entry/field semantics

## Example: Nerf NPC Breeding Partners

This is a common first edit. NPC breeding partners (prebuilt IDs 174-178) have inflated stats that produce overpowered offspring.

```json
{
  "174": {"level": 3, "hp": 18, "mp": 14, "int": 32},
  "175": {"level": 3, "hp": 20, "mp": 12, "int": 35},
  "176": {"level": 3, "hp": 19, "agi": 33, "int": 32}
}
```

Apply with:
```bash
python tools/mod_data.py your_rom.gbc \
    --table prebuilt_enemies \
    --edit '{"174": {"level": 3, "hp": 18}, "175": {"level": 3, "int": 35}}' \
    --output patched.gbc
```

## Example: Strengthen Boss Battles

Change a boss fight from 1 enemy to 3 enemies:

```bash
python tools/mod_data.py your_rom.gbc \
    --table boss_battles \
    --edit '{"6": {"count": 2, "enemy_2": 45, "enemy_3": 67}}' \
    --output patched.gbc
```

(Count is enemies-1, so count=2 means 3 enemies.)

## License

The DWM2 ROM is © 1993 Ashura Corp / Nintendo. This repository contains no ROM files — only tools and data extracted from the game.

Species names and breeding formulas are from [MetroWind/dwm2-tools](https://github.com/MetroWind/dwm2-tools) and community guides.

All tools are released under the MIT License.
