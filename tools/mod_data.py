#!/usr/bin/env python3
"""
mod_data.py — Unified data table editor for DWM2 ROMs.

Reads a DWM2 ROM, lets the user view and edit documented data tables
(items, skills, monsters, breeding, prebuilt enemies, stat growth),
and writes a patched ROM or IPS patch.

Usage:
    # List available tables
    python tools/mod_data.py roms/cobi_clean.gbc --tables

    # Show all entries in a table (JSON to stdout)
    python tools/mod_data.py roms/cobi_clean.gbc --table skills --list

    # Show a single entry
    python tools/mod_data.py roms/cobi_clean.gbc --table items --show 5

    # Edit and write patched ROM
    python tools/mod_data.py roms/cobi_clean.gbc \\
        --table items --edit '{"5": {"price": 999}}' \\
        --output build/cobi_modded.gbc

    # Edit from a JSON file, generate IPS patch
    python tools/mod_data.py roms/cobi_clean.gbc \\
        --table skills --edit-file edits/skill_changes.json \\
        --ips build/skill_edit.ips

Edit JSON format: {"<entry_index>": {"field_name": value, ...}, ...}
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any, Callable, Optional

# ---------------------------------------------------------------------------
# Enum definitions
# ---------------------------------------------------------------------------

ITEM_EFFECT_TYPES = {
    0x00: "healing",
    0x01: "status_change",
    0x02: "attribute_modifier",
    0x03: "reduce_wild",
    0x04: "cast_spell",
    0x05: "teleport",
    0x06: "unique_key_equip",
}

ITEM_USABILITY = {
    0x00: "always",
    0x01: "out_of_battle",
    0x02: "in_battle",
    0x03: "never",
}

ITEM_TARGETING = {
    0x00: "one_ally",
    0x01: "unknown_1",
    0x02: "one_enemy",
    0x03: "all_enemies",
    0x04: "one_ally_or_enemy",
    0x05: "all_allies",
    0x06: "unknown_6",
    0x07: "no_target",
}

ITEM_WORLD_MAP_ICON = {
    0x00: "none",
    0x01: "unknown_1",
    0x02: "leaf",
    0x03: "bottle",
    0x04: "bell",
    0x05: "seed",
    0x06: "meat",
    0x07: "staff",
    0x08: "warp_wing",
    0x09: "tiny_medal",
}

# Element IDs for resistances table (27 bytes per monster)
RESISTANCE_ELEMENT_IDS = {
    0x00: "attack",
    0x01: "blaze_family",
    0x02: "firebal_family",
    0x03: "bang_family",
    0x04: "wind_family",
    0x05: "lightning_family",
    0x06: "ice_family",
    0x07: "radiant_family",
    0x08: "sleep_family",
    0x09: "eerie_family",
    0x0A: "dance_family",
    0x0B: "stopspell",
    0x0C: "panic_family",
    0x0D: "sap_family",
    0x0E: "slow_family",
    0x0F: "sacrifice_family",
    0x10: "megamagic",
    0x11: "fire_air",
    0x12: "ice_air",
    0x13: "poison_air",
    0x14: "paralyze",
    0x15: "curse",
    0x16: "legsweep_family",
    0x17: "danceshut",
    0x18: "mouthshut",
    0x19: "rockthrow_family",
    0x1A: "gigaslash",
    0x1B: "water_family",
}

# Join rate values (0=always, 7=never)
JOIN_RATE = {
    0x00: "always",
    0x01: "very_easy",
    0x02: "easy",
    0x03: "medium",
    0x04: "hard",
    0x05: "very_hard",
    0x06: "extreme",
    0x07: "never",
}

# String pointer tables (bank 8): 2-byte LE offsets into the string-data region.
# Each pointer indexes into one of the corresponding string data tables.
# Pointer count = number of named entities in that category.

# Family string pointers at 0x20242. ~14 families documented (Slime, Dragon,
# Beast, Bird, Bug, Plant, Material, Water, Zombie, Devil, ?).
TABLE_FAMILY_NAME_POINTERS = {
    "name": "family_name_pointers",
    "offset": 0x20242,
    "entry_size": 2,
    "num_entries": 14,
    "description": "Family name string pointers (LE16 into string data at 0x213B5)",
    "fields": {
        "string_offset": (0, 2, "little"),
    },
    "enums": {},
}

# Monster species name pointers at 0x2025A.
TABLE_MONSTER_NAME_POINTERS = {
    "name": "monster_name_pointers",
    "offset": 0x2025A,
    "entry_size": 2,
    "num_entries": 324,
    "description": "Monster species name string pointers (LE16 into string data at 0x213F9)",
    "fields": {
        "string_offset": (0, 2, "little"),
    },
    "enums": {},
}

# Skill name string pointers at 0x2055A.
TABLE_SKILL_NAME_POINTERS = {
    "name": "skill_name_pointers",
    "offset": 0x2055A,
    "entry_size": 2,
    "num_entries": 50,
    "description": "Skill name string pointers (LE16 into string data at 0x21EF9)",
    "fields": {
        "string_offset": (0, 2, "little"),
    },
    "enums": {},
}

# Item name string pointers at 0x20718.
TABLE_ITEM_NAME_POINTERS = {
    "name": "item_name_pointers",
    "offset": 0x20718,
    "entry_size": 2,
    "num_entries": 47,
    "description": "Item name string pointers (LE16 into string data at 0x224E3)",
    "fields": {
        "string_offset": (0, 2, "little"),
    },
    "enums": {},
}

# Personality name string pointers at 0x208D6.
TABLE_PERSONALITY_NAME_POINTERS = {
    "name": "personality_name_pointers",
    "offset": 0x208D6,
    "entry_size": 2,
    "num_entries": 27,
    "description": "Personality name string pointers (LE16 into string data at 0x231F7)",
    "fields": {
        "string_offset": (0, 2, "little"),
    },
    "enums": {},
}


def parse_string_data(rom_data: bytes, table: dict) -> list[dict]:
    """Parse a null-terminated string table.

    Walks forward from the table's offset, splitting on 0x00 terminators,
    until a configurable stop condition (next null + safety margin, or
    fixed byte budget). Returns entries with index, rom_offset, text,
    and byte_length for each string.

    Variable-length tables are parsed lazily; editing is not supported
    here (changing string length would shift every subsequent pointer).
    """
    base = table["offset"]
    max_bytes = table.get("max_bytes", 1024)
    max_entries = table.get("max_entries", 256)

    entries = []
    pos = base
    end = min(base + max_bytes, len(rom_data))
    while pos < end and len(entries) < max_entries:
        # Find end of current string
        start = pos
        while pos < end and rom_data[pos] != 0x00:
            pos += 1
        if pos >= end:
            break
        # Decode printable ASCII (filter control bytes)
        raw = rom_data[start:pos]
        text = "".join(chr(b) if 0x20 <= b < 0x7F else "?" for b in raw)
        entries.append({
            "index": len(entries),
            "rom_offset": start,
            "byte_length": pos - start,
            "text": text,
        })
        pos += 1  # skip null terminator
    return entries


# Family string data at 0x213B5.
TABLE_FAMILY_NAMES = {
    "name": "family_names",
    "offset": 0x213B5,
    "entry_size": 1,
    "num_entries": 14,
    "max_bytes": 64,
    "description": "Family name strings (null-terminated, region up to 0x213F9)",
    "fields": {},
    "enums": {},
    "parser": parse_string_data,
}

# Monster species string data at 0x213F9.
TABLE_MONSTER_NAMES = {
    "name": "monster_names",
    "offset": 0x213F9,
    "entry_size": 1,
    "num_entries": 324,
    "max_bytes": 2816,
    "description": "Monster species name strings (null-terminated, region up to 0x21EF9)",
    "fields": {},
    "enums": {},
    "parser": parse_string_data,
}

# Skill string data at 0x21EF9.
TABLE_SKILL_NAMES = {
    "name": "skill_names",
    "offset": 0x21EF9,
    "entry_size": 1,
    "num_entries": 50,
    "max_bytes": 1500,
    "description": "Skill name strings (null-terminated, region up to 0x224E3)",
    "fields": {},
    "enums": {},
    "parser": parse_string_data,
}

# Item string data at 0x224E3.
TABLE_ITEM_NAMES = {
    "name": "item_names",
    "offset": 0x224E3,
    "entry_size": 1,
    "num_entries": 47,
    "max_bytes": 1500,
    "description": "Item name strings (null-terminated, region up to 0x231F7)",
    "fields": {},
    "enums": {},
    "parser": parse_string_data,
}

# Personality string data at 0x231F7.
TABLE_PERSONALITY_NAMES = {
    "name": "personality_names",
    "offset": 0x231F7,
    "entry_size": 1,
    "num_entries": 27,
    "max_bytes": 1024,
    "description": "Personality name strings (null-terminated, region up to ~0x23600)",
    "fields": {},
    "enums": {},
    "parser": parse_string_data,
}

# ---------------------------------------------------------------------------
# Custom parsers for variable-length tables
# Each parser: (rom_data: bytes, table: dict) -> list[dict]
# Returns entries with "index", "rom_offset", and field names.
# ---------------------------------------------------------------------------


def parse_arena_rewards(rom_data: bytes, table: dict) -> list[dict]:
    """Parse arena reward tables.

    Structure at 0x335DE:
    - 4 chance tables (C/B/A/S class), each ~9 bytes (8 ascending values + 0xFF terminator)
    - Reward tables follow at 0x3360E: item IDs per class

    Returns entries indexed by class (0=C, 1=B, 2=A, 3=S).
    Each entry has: chance_values[] and reward_items[].
    """
    classes = ["c_class", "b_class", "a_class", "s_class"]
    entries = []
    chance_offset = 0x335DE
    reward_offset = 0x3360E

    for i in range(4):
        entry = {"index": i, "class_name": classes[i]}
        # Parse chance table: read until 0xFF terminator
        pos = chance_offset
        chances = []
        while pos < len(rom_data) and rom_data[pos] != 0xFF:
            chances.append({"value": rom_data[pos], "rom_offset": pos})
            pos += 1
        pos += 1  # skip 0xFF terminator
        entry["chance_values"] = chances
        entry["chance_table_rom_offset"] = chance_offset

        # Parse reward table: read item IDs (8 per class)
        rpos = reward_offset + i * 8
        rewards = []
        for j in range(8):
            if rpos < len(rom_data):
                item_id = rom_data[rpos]
                rewards.append({"item_id": item_id, "rom_offset": rpos})
                rpos += 1
        entry["reward_items"] = rewards
        entry["reward_table_rom_offset"] = reward_offset + i * 8
        entries.append(entry)

    return entries


def parse_random_encounters(rom_data: bytes, table: dict) -> list[dict]:
    """Parse random encounter data.

    Structure at 0x29773+:
    - Each area has: pointer list (2-byte LE per screen) + encounter structures
    - Encounter structure: max_enemies(1), max_chance(1), chances(5 bytes),
      prebuilt_ids(variable, up to 5 entries × 2 bytes = 10 bytes)

    Returns entries for each known area. Each entry has area name and
    the first encounter structure's data.
    """
    # Known area offsets from rom_map + table_structure docs.
    # These point to the start of each area's data region (pointer list).
    # The encounter structures follow after the pointer list.
    areas = [
        ("oasis_world", 0x29773),
        ("well", 0x29856),
        ("pirate_world", 0x2989B),
        ("hoodsquid_cave", 0x29A4C),
        ("harmirror_cave_1f", 0x29A8A),
        ("harmirror_cave_2f", 0x29AB7),
        ("harmirror_cave_3f", 0x29ADE),
        ("moonrock_tower_1f", 0x29AFF),
        ("moonrock_tower_2f", 0x29B14),
        ("ghost_ship_1f", 0x29B29),
        ("ghost_ship_2f", 0x29B45),
        ("ghost_ship_cabin", 0x29B58),
        ("ice_world", 0x29B6B),
        ("gold_mine", 0x29D5D),
        ("spooky_forest", 0x29D9B),
        ("sleep_herb_mtn", 0x29DCA),
        ("ice_tower_1f", 0x29DE7),
        ("ice_tower_2f", 0x29E0C),
        ("sky_world", 0x29E2B),
        ("fhunt_tower_1f", 0x2A028),
        ("fhunt_tower_2f", 0x2A03D),
        ("fhunt_tower_3f", 0x2A052),
        ("fhunt_tower_4f", 0x2A06B),
        ("helm_cave_1f", 0x2A084),
        ("helm_cave_2f", 0x2A097),
        ("helm_cave_3f", 0x2A0BA),
        ("armor_tower_1f", 0x2A0DD),
        ("armor_tower_2f", 0x2A0F2),
        ("armor_tower_3f", 0x2A107),
        ("armor_tower_4f", 0x2A120),
        ("sword_castle_1f", 0x2A139),
        ("sword_castle_2f", 0x2A160),
        ("sword_castle_3f", 0x2A181),
        ("sword_castle_4f", 0x2A1A2),
        ("limbo_world", 0x2A1BD),
        ("darck_castle", 0x2A1FB),
        ("elf_world", 0x2A220),
        ("agdevil_lair", 0x2A2AB),
        ("lonely_world", 0x2A2D2),
        ("lonely_basement", 0x2A2EB),
        ("traveler_world", 0x2A300),
        ("dark_merchant_tower_1f", 0x2A382),
        ("dark_merchant_tower_2f", 0x2A393),
        ("dark_merchant_tower_3f", 0x2A3AA),
        ("dark_merchant_tower_4f", 0x2A3BF),
    ]

    entries = []
    for i, (name, area_offset) in enumerate(areas):
        entry = {
            "index": i,
            "area_name": name,
            "area_rom_offset": area_offset,
        }
        # Scan forward from area_offset to find the first encounter structure.
        # Pointer list entries are 2-byte LE values with high byte typically 0x29+.
        # Encounter structures start with small values (max_enemies <= 5).
        pos = area_offset
        while pos < len(rom_data) and pos < area_offset + 200:
            if rom_data[pos] <= 5 and rom_data[pos] > 0:
                # Likely an encounter structure start
                if pos + 13 <= len(rom_data):
                    data = rom_data[pos:pos + 13]
                    entry["max_enemies"] = data[0]
                    entry["max_chance"] = data[1]
                    entry["chance_thresholds"] = list(data[2:7])
                    if len(data) >= 9:
                        entry["prebuilt_id_1"] = struct.unpack_from("<H", data, 7)[0]
                    if len(data) >= 11:
                        entry["prebuilt_id_2"] = struct.unpack_from("<H", data, 9)[0]
                    entry["encounter_structure_offset"] = pos
                break
            pos += 1
        entries.append(entry)

    return entries


# ---------------------------------------------------------------------------
# Table definitions
# Each table: (offset, entry_size, num_entries, field_layout, enums, parser)
# field_layout: {name: (byte_offset, byte_count, endian_or_None)}
# enums: {field_name: {int_value: string_label}}
# ---------------------------------------------------------------------------

TABLE_ITEMS = {
    "name": "items",
    "offset": 0x58CC2,
    "entry_size": 13,
    "num_entries": 47,  # entry 0 is null placeholder
    "description": "Item data table (effect type, price, usability, targeting, healing range)",
    "fields": {
        "effect_type": (0, 1, None),
        "price": (1, 2, "little"),
        "unknown_0": (3, 1, None),
        "usability": (4, 1, None),
        "unknown_1": (5, 1, None),
        "targeting": (6, 1, None),
        "world_map_icon": (7, 1, None),
        "unknown_2": (8, 1, None),
        "effect_byte_1": (9, 1, None),
        "effect_byte_2": (10, 1, None),
        "variable_1": (11, 1, None),
        "variable_2": (12, 1, None),
    },
    "enums": {
        "effect_type": ITEM_EFFECT_TYPES,
        "usability": ITEM_USABILITY,
        "targeting": ITEM_TARGETING,
        "world_map_icon": ITEM_WORLD_MAP_ICON,
    },
}

TABLE_SKILLS = {
    "name": "skills",
    "offset": 0x680D4,
    "entry_size": 17,
    "num_entries": 50,  # first ~18 are well-structured, rest may differ
    "description": "Skill data table (MP cost, tier, element, damage values)",
    "fields": {
        "mp_cost": (0, 1, None),
        "tier": (1, 1, None),
        "type_flag": (2, 1, None),
        "flag_3": (3, 1, None),
        "element": (4, 1, None),
        "marker_b5": (5, 1, None),
        "marker_b6": (6, 1, None),
        "marker_b7": (7, 1, None),
        "marker_b8": (8, 1, None),
        "dmg_1": (9, 2, "little"),
        "dmg_2": (11, 2, "little"),
        "dmg_3": (13, 2, "little"),
        "dmg_4": (15, 2, "little"),
    },
    "enums": {},
}

TABLE_STAT_GROWTH = {
    "name": "stat_growth",
    "offset": 0x6A616,
    "entry_size": 1,
    "num_entries": 99,  # levels 1-99
    "description": "Stat growth tables (1 byte per level, 99 entries per table)",
    "fields": {
        "growth_value": (0, 1, None),
    },
    "enums": {},
}

TABLE_BREEDING = {
    "name": "breeding",
    "offset": 0x3A208,
    "entry_size": 2,
    "num_entries": 100,
    "description": "Breeding data (bank:offset pointers per species)",
    "fields": {
        "pointer": (0, 2, "little"),
    },
    "enums": {},
}

TABLE_PREBUILT_ENEMIES = {
    "name": "prebuilt_enemies",
    "offset": 0xD0075,
    "entry_size": 26,  # corrected from detailed schema docs
    "num_entries": 600,  # part 1 covers IDs 0-0x24F; NPC breeding at 174-178, post-game at 25A-25E
    "description": "Prebuilt enemy data (species ID, skills, stats, aptitudes)",
    "fields": {
        "species_id": (0, 2, "little"),
        "skill_1": (2, 1, None),
        "skill_2": (3, 1, None),
        "skill_3": (4, 1, None),
        "skill_4": (5, 1, None),
        "exp_yield": (6, 2, "little"),
        "join_value": (8, 1, None),
        "level": (9, 1, None),
        "hp": (10, 2, "little"),
        "mp": (12, 2, "little"),
        "attack": (14, 2, "little"),
        "defense": (16, 2, "little"),
        "agility": (18, 2, "little"),
        "intelligence": (20, 2, "little"),
        "charge_aptitude": (22, 1, None),
        "defense_aptitude": (23, 1, None),
        "motivation": (24, 1, None),
        "mixed_aptitude": (25, 1, None),
    },
    "enums": {
        "join_value": JOIN_RATE,
    },
}

TABLE_SKILL_REQUIREMENTS = {
    "name": "skill_requirements",
    "offset": 0x6900A,
    "entry_size": 18,  # level(1) + 6 stats×2 + prereq(1) + combine×4(4) = 18
    "num_entries": 80,
    "description": "Skill unlock requirements (level, stat thresholds, prerequisite, combine skills)",
    "fields": {
        "required_level": (0, 1, None),
        "required_hp": (1, 2, "little"),
        "required_mp": (3, 2, "little"),
        "required_attack": (5, 2, "little"),
        "required_defense": (7, 2, "little"),
        "required_agility": (9, 2, "little"),
        "required_intelligence": (11, 2, "little"),
        "prerequisite_skill": (13, 1, None),
        "combine_skill_1": (14, 1, None),
        "combine_skill_2": (15, 1, None),
        "combine_skill_3": (16, 1, None),
        "combine_skill_4": (17, 1, None),
    },
    "enums": {},
}

TABLE_CORE_MONSTER = {
    "name": "core_monster",
    "offset": 0xD433B,
    "entry_size": 47,
    "num_entries": 324,  # full table: species 0-323 (ID 0x017E), ends at 0xD7EB7
    "description": "Core monster data (family, join rate, skills, stat growth, resistances)",
    "fields": {
        "family": (0, 1, None),
        "gender_ratio": (1, 1, None),
        "flying": (2, 1, None),
        "metal": (3, 1, None),
        "join_rate": (4, 1, None),
        "unknown_5": (5, 1, None),
        "unbred_max_level": (6, 1, None),
        "exp_growth": (7, 1, None),
        "skill_1": (8, 1, None),
        "skill_2": (9, 1, None),
        "skill_3": (10, 1, None),
        "unknown_11": (11, 1, None),
        "hp_growth": (12, 1, None),
        "mp_growth": (13, 1, None),
        "atk_growth": (14, 1, None),
        "def_growth": (15, 1, None),
        "agi_growth": (16, 1, None),
        "int_growth": (17, 1, None),
        # resistances[0..26] at bytes 18-44
        "resist_0_attack": (18, 1, None),
        "resist_1_blaze": (19, 1, None),
        "resist_2_firebal": (20, 1, None),
        "resist_3_bang": (21, 1, None),
        "resist_4_wind": (22, 1, None),
        "resist_5_lightning": (23, 1, None),
        "resist_6_ice": (24, 1, None),
        "resist_7_radiant": (25, 1, None),
        "resist_8_sleep": (26, 1, None),
        "resist_9_eerie": (27, 1, None),
        "resist_10_dance": (28, 1, None),
        "resist_11_stopspell": (29, 1, None),
        "resist_12_panic": (30, 1, None),
        "resist_13_sap": (31, 1, None),
        "resist_14_slow": (32, 1, None),
        "resist_15_sacrifice": (33, 1, None),
        "resist_16_megamagic": (34, 1, None),
        "resist_17_fire_air": (35, 1, None),
        "resist_18_ice_air": (36, 1, None),
        "resist_19_poison_air": (37, 1, None),
        "resist_20_paralyze": (38, 1, None),
        "resist_21_curse": (39, 1, None),
        "resist_22_legsweep": (40, 1, None),
        "resist_23_danceshut": (41, 1, None),
        "resist_24_mouthshut": (42, 1, None),
        "resist_25_rockthrow": (43, 1, None),
        "resist_26_gigaslash": (44, 1, None),
        # bytes 45-46: base_exp_yield LE16 — not exposed for editing (DWM1 doesn't have it)
    },
    "enums": {
        "join_rate": JOIN_RATE,
    },
}

# Experience tables: 3-byte LE u24 values, one per level (0-99).
# Value = cumulative XP needed to reach that level.
TABLE_EXP_TABLES = {
    "name": "exp_tables",
    "offset": 0x64E60,
    "entry_size": 3,
    "num_entries": 100,  # levels 0-99; entry 0 = 0 XP (always)
    "description": "Experience to next level tables (3-byte LE u24 cumulative XP per level)",
    "fields": {
        "xp_required": (0, 3, "little"),
    },
    "enums": {},
}

# Cape resistances: each cape has a list of resisted effect IDs.
# Stored as variable-length rows (max 16 bytes) terminated by 0x80.
# ~7 capes documented. Model as fixed 16-byte entries for editing.
TABLE_CAPE_RESISTANCES = {
    "name": "cape_resistances",
    "offset": 0x64641,
    "entry_size": 16,
    "num_entries": 7,
    "description": "Cape resistance data (effect IDs per cape, 0x80-terminated, max 16 bytes/cape)",
    "fields": {
        "resist_0": (0, 1, None),
        "resist_1": (1, 1, None),
        "resist_2": (2, 1, None),
        "resist_3": (3, 1, None),
        "resist_4": (4, 1, None),
        "resist_5": (5, 1, None),
        "resist_6": (6, 1, None),
        "resist_7": (7, 1, None),
        "resist_8": (8, 1, None),
        "resist_9": (9, 1, None),
        "resist_10": (10, 1, None),
        "resist_11": (11, 1, None),
        "resist_12": (12, 1, None),
        "resist_13": (13, 1, None),
        "resist_14": (14, 1, None),
        "resist_15": (15, 1, None),
    },
    "enums": {},
}

# Personality effect tables: 4 tables (Charge, Mixed, Defend, Command).
# Each has 8 entries of 4 bytes = 32 bytes per table.
TABLE_PERSONALITY_CHARGE = {
    "name": "personality_charge",
    "offset": 0xC138C,
    "entry_size": 4,
    "num_entries": 8,
    "description": "Charge personality effect table (stat modifier entries, 4 bytes each)",
    "fields": {
        "stat_id": (0, 1, None),
        "modifier_hi": (1, 1, None),
        "modifier_lo": (2, 1, None),
        "flag": (3, 1, None),
    },
    "enums": {},
}

TABLE_PERSONALITY_MIXED = {
    "name": "personality_mixed",
    "offset": 0xC13AC,
    "entry_size": 4,
    "num_entries": 8,
    "description": "Mixed personality effect table (stat modifier entries, 4 bytes each)",
    "fields": {
        "stat_id": (0, 1, None),
        "modifier_hi": (1, 1, None),
        "modifier_lo": (2, 1, None),
        "flag": (3, 1, None),
    },
    "enums": {},
}

TABLE_PERSONALITY_DEFEND = {
    "name": "personality_defend",
    "offset": 0xC13CC,
    "entry_size": 4,
    "num_entries": 8,
    "description": "Defend personality effect table (stat modifier entries, 4 bytes each)",
    "fields": {
        "stat_id": (0, 1, None),
        "modifier_hi": (1, 1, None),
        "modifier_lo": (2, 1, None),
        "flag": (3, 1, None),
    },
    "enums": {},
}

TABLE_PERSONALITY_COMMAND = {
    "name": "personality_command",
    "offset": 0xC13EC,
    "entry_size": 4,
    "num_entries": 8,
    "description": "Command personality effect table (stat modifier entries, 4 bytes each)",
    "fields": {
        "stat_id": (0, 1, None),
        "modifier_hi": (1, 1, None),
        "modifier_lo": (2, 1, None),
        "flag": (3, 1, None),
    },
    "enums": {},
}

# Shop inventories: variable-length item ID lists terminated by 0xFF.
# Model as fixed-size entries for the first ~20 shops.
TABLE_SHOP_INVENTORIES = {
    "name": "shop_inventories",
    "offset": 0x72188,
    "entry_size": 16,  # max shop list size; actual lists are 0xFF-terminated
    "num_entries": 20,
    "description": "Shop inventory data (item ID lists, 0xFF-terminated, up to 16 items/shop)",
    "fields": {
        "item_0": (0, 1, None),
        "item_1": (1, 1, None),
        "item_2": (2, 1, None),
        "item_3": (3, 1, None),
        "item_4": (4, 1, None),
        "item_5": (5, 1, None),
        "item_6": (6, 1, None),
        "item_7": (7, 1, None),
        "item_8": (8, 1, None),
        "item_9": (9, 1, None),
        "item_10": (10, 1, None),
        "item_11": (11, 1, None),
        "item_12": (12, 1, None),
        "item_13": (13, 1, None),
        "item_14": (14, 1, None),
        "item_15": (15, 1, None),
    },
    "enums": {},
}

# Registry of all supported tables
TABLES: dict[str, dict[str, Any]] = {
    "items": TABLE_ITEMS,
    "skills": TABLE_SKILLS,
    "stat_growth": TABLE_STAT_GROWTH,
    "breeding": TABLE_BREEDING,
    "prebuilt_enemies": TABLE_PREBUILT_ENEMIES,
    "skill_requirements": TABLE_SKILL_REQUIREMENTS,
    "core_monster": TABLE_CORE_MONSTER,
    "exp_tables": TABLE_EXP_TABLES,
    "cape_resistances": TABLE_CAPE_RESISTANCES,
    "personality_charge": TABLE_PERSONALITY_CHARGE,
    "personality_mixed": TABLE_PERSONALITY_MIXED,
    "personality_defend": TABLE_PERSONALITY_DEFEND,
    "personality_command": TABLE_PERSONALITY_COMMAND,
    "shop_inventories": TABLE_SHOP_INVENTORIES,
    "family_name_pointers": TABLE_FAMILY_NAME_POINTERS,
    "monster_name_pointers": TABLE_MONSTER_NAME_POINTERS,
    "skill_name_pointers": TABLE_SKILL_NAME_POINTERS,
    "item_name_pointers": TABLE_ITEM_NAME_POINTERS,
    "personality_name_pointers": TABLE_PERSONALITY_NAME_POINTERS,
    "family_names": TABLE_FAMILY_NAMES,
    "monster_names": TABLE_MONSTER_NAMES,
    "skill_names": TABLE_SKILL_NAMES,
    "item_names": TABLE_ITEM_NAMES,
    "personality_names": TABLE_PERSONALITY_NAMES,
    "arena_rewards": {
        "name": "arena_rewards",
        "offset": 0x335DE,
        "entry_size": 1,
        "num_entries": 4,
        "description": "Arena random rewards (chance tables + reward item IDs per class C/B/A/S)",
        "fields": {},
        "enums": {},
        "parser": parse_arena_rewards,
    },
    "random_encounters": {
        "name": "random_encounters",
        "offset": 0x29773,
        "entry_size": 1,
        "num_entries": 45,
        "description": "Random encounter data per area (45 areas; max enemies, chance thresholds, prebuilt IDs)",
        "fields": {},
        "enums": {},
        "parser": parse_random_encounters,
    },
    # Magic key prefix probabilities: 15 prefixes × 10 level columns.
    # Each row is 16 bytes (10 values + 6 zero padding). Values are ascending
    # cumulative probabilities scaled to /100 (max = 0x64 = 100).
    "magic_key_prefixes": {
        "name": "magic_key_prefixes",
        "offset": 0x182969,
        "entry_size": 16,
        "num_entries": 15,
        "description": "Magic key prefix probability table (15 prefixes × 10 level columns, cumulative /100 scale)",
        "fields": {
            "lvl_1": (0, 1, None),
            "lvl_10": (1, 1, None),
            "lvl_20": (2, 1, None),
            "lvl_30": (3, 1, None),
            "lvl_40": (4, 1, None),
            "lvl_50": (5, 1, None),
            "lvl_60": (6, 1, None),
            "lvl_70": (7, 1, None),
            "lvl_80": (8, 1, None),
            "lvl_90": (9, 1, None),
        },
        "enums": {},
    },
    # Magic key suffix probabilities: 39 suffixes × 5 level columns.
    # Values are ascending cumulative probabilities scaled to /100.
    "magic_key_suffixes": {
        "name": "magic_key_suffixes",
        "offset": 0x182A09,
        "entry_size": 5,
        "num_entries": 39,
        "description": "Magic key suffix probability table (39 suffixes × 5 level columns, cumulative /100 scale)",
        "fields": {
            "lvl_1": (0, 1, None),
            "lvl_30": (1, 1, None),
            "lvl_50": (2, 1, None),
            "lvl_80": (3, 1, None),
            "lvl_90": (4, 1, None),
        },
        "enums": {},
    },
    # Gift/event monsters: LE16 prebuilt IDs at 0x7098.
    # ~9 documented entries before data transitions to a different structure.
    "gift_monsters": {
        "name": "gift_monsters",
        "offset": 0x7098,
        "entry_size": 2,
        "num_entries": 9,
        "description": "Gift/event monster prebuilt IDs (LE16, from TinyMedal eggs, story gifts, etc.)",
        "fields": {
            "prebuilt_id": (0, 2, "little"),
        },
        "enums": {},
    },
    # Boss battles: 8-byte entries at 0x2881C.
    # Structure: count(2B LE), boss_id(2B LE), field_a(2B LE), field_b(2B LE).
    "boss_battles": {
        "name": "boss_battles",
        "offset": 0x2881C,
        "entry_size": 8,
        "num_entries": 40,
        "description": "Boss battle data (count, boss prebuilt ID, field_a, field_b — all LE16)",
        "fields": {
            "count": (0, 2, "little"),
            "boss_id": (2, 2, "little"),
            "field_a": (4, 2, "little"),
            "field_b": (6, 2, "little"),
        },
        "enums": {},
    },
}

# ---------------------------------------------------------------------------
# Core parsing / serialization
# ---------------------------------------------------------------------------


def parse_entry(raw: bytes, fields: dict[str, tuple]) -> dict[str, int]:
    """Parse a raw entry into a dict of field names -> integer values."""
    result = {}
    for name, (offset, count, endian) in fields.items():
        if count == 1:
            result[name] = raw[offset]
        elif count == 2 and endian == "little":
            result[name] = struct.unpack_from("<H", raw, offset)[0]
        else:
            result[name] = int.from_bytes(raw[offset:offset + count], "little")
    return result


def entry_to_bytes(entry: dict[str, int], fields: dict[str, tuple]) -> bytes:
    """Serialize a parsed entry back to raw bytes."""
    entry_size = max(off + cnt for off, cnt, _ in fields.values())
    b = bytearray(entry_size)
    for name, (offset, count, endian) in fields.items():
        value = entry.get(name, 0)
        if count == 1:
            b[offset] = value & 0xFF
        elif count == 2 and endian == "little":
            struct.pack_into("<H", b, offset, value & 0xFFFF)
        else:
            masked = value & ((1 << (count * 8)) - 1)
            packed = masked.to_bytes(count, "little")
            for i in range(count):
                b[offset + i] = packed[i]
    return bytes(b)


def label_value(field: str, value: int, enums: dict[str, dict]) -> Optional[str]:
    """Return human-readable label for an enum field, or None."""
    enum_map = enums.get(field, {})
    return enum_map.get(value)


def human_readable(entry: dict[str, int], enums: dict[str, dict]) -> dict[str, Any]:
    """Add _name suffix fields for enum values."""
    result = dict(entry)
    for field, enum_map in enums.items():
        if field in result and result[field] in enum_map:
            result[f"{field}_name"] = enum_map[result[field]]
    return result


def build_reverse_enums(enums: dict[str, dict]) -> list[dict]:
    """Build reverse maps (name -> int) for all enum fields."""
    rev_maps = []
    for enum_map in enums.values():
        rev_maps.append({v: k for k, v in enum_map.items()})
    return rev_maps


def resolve_field_value(field: str, value: Any, enums: dict[str, dict]) -> int:
    """Convert a field value (int or enum name string) to an integer."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        for enum_map in enums.values():
            rev = {v: k for k, v in enum_map.items()}
            if value in rev:
                return rev[value]
            lower = value.lower().replace("-", "_")
            if lower in rev:
                return rev[lower]
    raise ValueError(f"Cannot resolve field value: {value!r} for {field}")


# ---------------------------------------------------------------------------
# Edit application
# ---------------------------------------------------------------------------


def apply_edits(
    rom_bytes: bytearray,
    table: dict[str, Any],
    edits: dict[str, Any],
    rom_data: bytes = None,
) -> list[dict]:
    """
    Apply edits to a ROM bytearray for the given table.

    edits format: {"<entry_index>": {"field_name": value, ...}, ...}
    Returns a list of change records.

    If table has a "parser" (variable-length), rom_data is used to build
    entry offsets dynamically. Otherwise uses fixed offset + entry_size.
    """
    changes = []
    offset = table["offset"]
    entry_size = table["entry_size"]
    fields = table["fields"]
    enums = table.get("enums", {})

    # Build entry list (use custom parser for variable-length tables)
    if "parser" in table and rom_data is not None:
        entry_list = table["parser"](rom_data, table)
    else:
        max_entries = table["num_entries"]
        entry_list = []
        for i in range(max_entries):
            base = offset + i * entry_size
            raw = bytes(rom_data[base:base + entry_size]) if rom_data else None
            parsed = parse_entry(raw, fields) if raw else {}
            parsed["index"] = i
            parsed["rom_offset"] = base
            entry_list.append(parsed)

    # Build a lookup from index to (entry_dict, rom_offset)
    entry_by_idx = {}
    for e in entry_list:
        entry_by_idx[e.get("index", 0)] = (e, e.get("rom_offset", 0))

    for idx_str, field_updates in edits.items():
        try:
            idx = int(idx_str)
        except (ValueError, TypeError):
            print(f"WARNING: skipping non-numeric index: {idx_str!r}",
                  file=sys.stderr)
            continue

        if idx not in entry_by_idx:
            print(f"WARNING: index {idx} not found in table {table['name']}",
                  file=sys.stderr)
            continue

        current, base = entry_by_idx[idx]

        for field, raw_value in field_updates.items():
            if field not in fields:
                print(f"WARNING: unknown field {field!r} for table {table['name']}",
                      file=sys.stderr)
                continue

            byte_offset, byte_count, endian = fields[field]
            new_value = resolve_field_value(field, raw_value, enums)

            # Clamp
            max_val = (1 << (byte_count * 8)) - 1
            new_value = new_value & max_val

            old_value = current.get(field, 0)
            if old_value == new_value:
                continue

            # Write to ROM
            if byte_count == 2 and endian == "little":
                struct.pack_into("<H", rom_bytes, base + byte_offset, new_value)
            elif byte_count == 1:
                rom_bytes[base + byte_offset] = new_value
            else:
                # Multi-byte (3+): write little-endian bytes
                packed = new_value.to_bytes(byte_count, "little")
                for i in range(byte_count):
                    rom_bytes[base + byte_offset + i] = packed[i]

            changes.append({
                "table": table["name"],
                "entry": idx,
                "field": field,
                "old": old_value,
                "new": new_value,
                "rom_offset": base + byte_offset,
            })

    return changes


# ---------------------------------------------------------------------------
# IPS generation (minimal)
# ---------------------------------------------------------------------------


def generate_ips(original: bytes, modified: bytes) -> bytes:
    """Generate a minimal IPS patch."""
    if len(original) != len(modified):
        raise ValueError("ROM size mismatch")

    diffs = []
    i = 0
    while i < len(original):
        if original[i] != modified[i]:
            start = i
            while i < len(original) and original[i] != modified[i]:
                i += 1
            length = i - start
            diffs.append(struct.pack(">H", start // 256) + bytes([start % 256]))
            diffs.append(struct.pack(">H", length))
            diffs.append(modified[start:i])
        else:
            i += 1
    return b"".join(diffs) + b"EOFS"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("rom", help="Path to the DWM2 ROM")
    p.add_argument("--tables", action="store_true",
                   help="List available tables and exit")
    p.add_argument("--table", type=str, default=None,
                   choices=list(TABLES.keys()),
                   help="Which table to operate on (required for --list/--show/--edit)")
    p.add_argument("--list", action="store_true",
                   help="List all entries in the table as JSON")
    p.add_argument("--show", type=int, default=None, metavar="INDEX",
                   help="Show a single entry by index")
    p.add_argument("--edit", type=str, default=None,
                   help='JSON string of edits: {"5": {"price": 999}}')
    p.add_argument("--edit-file", type=str, default=None, metavar="PATH",
                   help="Path to a JSON file of edits")
    p.add_argument("--output", type=str, default=None, metavar="PATH",
                   help="Write patched ROM to this path")
    p.add_argument("--ips", type=str, default=None, metavar="PATH",
                   help="Write IPS patch to this path")

    args = p.parse_args()
    rom_path = Path(args.rom)

    # --tables: list available tables and exit
    if args.tables:
        print("Available tables:")
        for key, tbl in TABLES.items():
            print(f"  {key:20s}  offset=0x{tbl['offset']:05X}  "
                  f"entry_size={tbl['entry_size']}  entries={tbl['num_entries']}  "
                  f"— {tbl['description']}")
        return 0

    # Read ROM
    if not rom_path.exists():
        print(f"ERROR: ROM not found: {rom_path}", file=sys.stderr)
        return 1
    rom_data = rom_path.read_bytes()

    # --list / --show need a table
    if args.list or args.show is not None:
        if not args.table:
            print("ERROR: --table required with --list/--show", file=sys.stderr)
            return 1
        tbl = TABLES[args.table]
        entries = []

        # Use custom parser if defined (for variable-length tables)
        if "parser" in tbl:
            entries = tbl["parser"](rom_data, tbl)
        else:
            for i in range(tbl["num_entries"]):
                base = tbl["offset"] + i * tbl["entry_size"]
                raw = rom_data[base:base + tbl["entry_size"]]
                parsed = parse_entry(raw, tbl["fields"])
                parsed["index"] = i
                parsed["rom_offset"] = base
                entries.append(parsed)

        if args.list:
            human = [human_readable(e, tbl.get("enums", {})) for e in entries]
            print(json.dumps(human, indent=2))
            return 0

        if args.show is not None:
            idx = args.show
            if 0 <= idx < len(entries):
                print(json.dumps(
                    human_readable(entries[idx], tbl.get("enums", {})),
                    indent=2
                ))
            else:
                print(f"ERROR: index {idx} out of range (0-{len(entries) - 1})",
                      file=sys.stderr)
                return 1
            return 0

    # Edit mode
    edits = None
    if args.edit:
        try:
            edits = json.loads(args.edit)
        except json.JSONDecodeError as e:
            print(f"ERROR: invalid JSON in --edit: {e}", file=sys.stderr)
            return 1
    elif args.edit_file:
        ef = Path(args.edit_file)
        if not ef.exists():
            print(f"ERROR: edit file not found: {ef}", file=sys.stderr)
            return 1
        edits = json.loads(ef.read_text())

    if edits is None:
        if not args.tables:
            p.print_help()
        return 0

    if not args.table:
        print("ERROR: --table required with --edit/--edit-file", file=sys.stderr)
        return 1
    tbl = TABLES[args.table]

    # Apply edits
    rom_modified = bytearray(rom_data)
    changes = apply_edits(rom_modified, tbl, edits, rom_data)

    if not changes:
        print("No changes applied (all values match original).", file=sys.stderr)
        return 0

    # Report changes
    print(f"Applied {len(changes)} change(s) to table '{tbl['name']}':")
    for c in changes:
        label = ""
        enum_map = tbl.get("enums", {}).get(c["field"], {})
        if c["new"] in enum_map:
            label = f" ({enum_map[c['new']]})"
        print(f"  Entry {c['entry']}: {c['field']} "
              f"0x{c['old']:04X} -> 0x{c['new']:04X}{label} "
              f"[ROM 0x{c['rom_offset']:X}]")

    # Write output
    if args.output:
        out = Path(args.output)
        out.write_bytes(bytes(rom_modified))
        print(f"Wrote patched ROM to {out} ({len(rom_modified)} bytes)")

    if args.ips:
        ips_data = generate_ips(rom_data, rom_modified)
        ips_path = Path(args.ips)
        ips_path.write_bytes(ips_data)
        print(f"Wrote IPS patch to {ips_path} ({len(ips_data)} bytes)")

    if not args.output and not args.ips:
        print("\nNo output specified. Use --output or --ips to write changes.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
