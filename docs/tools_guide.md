# Tools Guide

Detailed usage reference for the DWM2 hacking tools.

---

## `mod_data.py` — Data Table Editor

The primary tool for editing game data. Supports 20 tables covering items, skills, monsters, breeding, enemies, and more.

### Usage

```bash
python tools/mod_data.py <rom.gbc> [options]
```

### Commands

| Flag | Description |
|------|-------------|
| `--tables` | List all supported table names |
| `--table <name>` | Select a table to operate on |
| `--list` | Dump all entries as JSON to stdout |
| `--show <index>` | Show a single entry in human-readable form |
| `--edit '<json>'` | Apply edits from inline JSON string |
| `--edit-file <path>` | Apply edits from a JSON file |
| `--output <path>` | Write patched ROM to file |
| `--ips <path>` | Generate an IPS patch instead of full ROM |

### Edit JSON Format

Edits are a JSON object mapping entry indices to field changes:

```json
{
  "<entry_index>": {
    "field_name": new_value,
    "another_field": new_value
  }
}
```

Entry indices are **zero-based** and correspond to the table's natural ordering (e.g., species ID for `core_monster`, item ID for `items`).

### Examples

```bash
# View all items
python mod_data.py rom.gbc --table items --list

# Show item #5 details
python mod_data.py rom.gbc --table items --show 5

# Change item price
python mod_data.py rom.gbc \
    --table items \
    --edit '{"5": {"price": 999}}' \
    --output patched.gbc

# Bulk edit from file
python mod_data.py rom.gbc \
    --table core_monster \
    --edit-file edits/balance.json \
    --ips build/patch.ips
```

### Supported Tables

See the table in [README.md](../README.md#supported-data-tables) for a complete list. Key tables:

- **`core_monster`** — 324 species entries. Fields: `family`, `gender_ratio`, `join_rate`, `max_level`, `exp_growth`, `skill_1/2/3`, `hp/mp/atk/def/agi/int_growth`, `resistances`
- **`prebuilt_enemies`** — 600 entries. Fields: `species_id`, `level`, `hp/mp/atk/def/agi/int`, `exp`, `skill_1-4`, `aptitude_1-4`
- **`boss_battles`** — 40 entries. Fields: `count` (enemies-1), `enemy_1/2/3` (prebuilt IDs)
- **`stat_growth`** — 99 levels, 1 byte each
- **`exp_tables`** — 100 levels, 3-byte LE u24 cumulative XP

---

## `rom_region_diff.py` — Region Diff + IPS Generation

Diff specific ROM regions between two ROMs and generate an IPS patch. Useful for replicating changes from a known hack.

### Usage

```bash
python tools/rom_region_diff.py <clean_rom.gbc> <patched_rom.gbc> [options]
```

### Options

| Flag | Description |
|------|-------------|
| `--region <start:end>` | ROM region to diff (hex offsets). Can specify multiple regions |
| `--ips <path>` | Output IPS patch file |
| `--output <path>` | Output patched ROM (clean + changes) |
| `--summary` | Print summary only, no file output |

### Example

```bash
# Diff breeding region and generate IPS
python tools/rom_region_diff.py clean.gbc patched.gbc \
    --region 0x3A208:0x3BE99 \
    --ips build/breeding.ips

# Multiple regions at once
python tools/rom_region_diff.py clean.gbc patched.gbc \
    --region 0x3A208:0x3BE99 \
    --region 0xD433B:0xD7FFF \
    --ips build/combined.ips

# Summary only (no file output)
python tools/rom_region_diff.py clean.gbc patched.gbc \
    --region 0x3A208:0x3BE99 --summary
```

---

## `rom_diff.py` — Static Byte Diff

Compare two ROM files and report byte-level differences.

### Usage

```bash
python tools/rom_diff.py <rom1.gbc> <rom2.gbc>
```

Reports total differing bytes, first N differences with offsets, and whether ROMs are byte-identical.

---

## `tools/balancing/` — Bulk Edit Scripts

These scripts generate JSON configs that apply edits across many species at once. They are designed to be piped to a file and used with `mod_data.py --edit-file`.

### `generate_p2_pass[1-4].py` — Stat Growth Theme Correction

Boosts growth rates for weak monsters to match their family theme:
- **Pass 1:** Bottom 40 weakest monsters (critical fixes)
- **Pass 2:** Monsters below family median
- **Pass 3:** Gap-closing edits (stats >= 6 but below median)
- **Pass 4:** Final theme violations vs clean ROM medians

```bash
# Generate and apply pass 1 edits
python tools/balancing/generate_p2_pass1.py > pass1.json
python tools/mod_data.py rom.gbc \
    --table core_monster \
    --edit-file pass1.json \
    --output patched.gbc
```

### `generate_p2_pass3_skills.py` — Skill Swaps

Swaps skills for thematic abilities (e.g., Goopi: CallHelp → Ironize).

### `generate_p4_exp.py` — EXP Curve Adjustments

Reduces EXP requirement rank for rare/Lord monsters (-2 to -6 ranks) to offset increased difficulty.

---

## `tools/discovery/` — Runtime WRAM Tools

Advanced tools for reverse-engineering ROM data at runtime. Requires **PyBoy** and a working DWM2 ROM.

### `explore_wram.py` — Interactive WRAM Exploration

Probe live emulator memory, search for species IDs, find non-zero regions.

```bash
python tools/discovery/explore_wram.py <rom.gbc> [options]
```

| Flag | Description |
|------|-------------|
| `--search-species <id>` | Find where a species ID appears in WRAM |
| `--dump-range <start:end>` | Hex dump a WRAM range |
| `--snapshot <path>` | Save current WRAM state as JSON |

### `wram_inspector.py` — Snapshot Diffing

Compare two WRAM snapshots to find changed bytes.

```bash
python tools/discovery/wram_inspector.py \
    --diff-snapshots snapshot1.json snapshot2.json
```

### `map_party_struct.py` — Party Struct Mapping

Reverse-engineer party monster struct layout by navigating game menus and watching memory changes.

### `lib_pyboy.py` — Shared PyBoy Library

Not a standalone tool. Provides `make_pyboy()`, memory/register snapshots, save states for other discovery tools.

---

## Workflow: Making a Balanced ROM

Here's a typical workflow for creating a balancing mod:

1. **Start with a clean ROM** — unmodified US Cobi release
2. **Plan your edits** — decide which tables to modify and what changes to make
3. **Edit via `mod_data.py`** — apply changes, output patched ROM
4. **Verify with byte diff** — confirm only expected bytes changed
5. **Test in emulator** — boot patched ROM, verify gameplay

```bash
# Step 1: Plan edits (review existing examples)
cat edits/phase2_pass1.json

# Step 2: Apply edits
python tools/mod_data.py clean.gbc \
    --table core_monster \
    --edit-file my_edits.json \
    --output patched.gbc

# Step 3: Verify diff
python tools/rom_diff.py clean.gbc patched.gbc

# Step 4: Generate IPS for distribution
python tools/mod_data.py clean.gbc \
    --table core_monster \
    --edit-file my_edits.json \
    --ips build/my_balance.ips
```

## Tips

- **Always diff before testing** — `rom_diff.py` confirms you only changed what you intended
- **Use IPS patches for distribution** — smaller than full ROMs, easier to share
- **Test incrementally** — apply one table at a time, verify each works
- **Read the ROM map first** — `rom_maps/rom_map.txt` tells you where data lives
- **Check prebuilt ID usage** — `monster_data/prebuilt_id_usages.md` maps IDs to contexts
