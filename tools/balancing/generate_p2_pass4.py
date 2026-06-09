#!/usr/bin/env python3
"""Generate Phase 2 Pass 4 edits — final theme violations vs original medians.

Targets remaining monsters still below original clean ROM family median - 3.
"""
import json

# Original clean ROM medians (stable baseline, not affected by our patches)
CLEAN_MEDIAN = {
    'beast': 17, 'bird': 18, 'bug': 13, 'devil': 13,
    'dragon': 19, 'material': 18, 'plant': 14, 'slime': 11,
    'water': 10, 'zombie': 14,
}

edits = {
    # --- Plant (INT median=14) ---
    "134": {"int_growth": 14},   # FireWeed     INT 9→14  gap=5
    "125": {"int_growth": 14},   # Warubou      INT 10→14 gap=4
    "129": {"int_growth": 14},   # Voodoll      INT 11→14 gap=3

    # --- Slime (MP median=11) ---
    "7":   {"mp_growth": 11},    # SlimeNite    MP 7→11   gap=4
    "15":  {"mp_growth": 11},    # KingSlime    MP 7→11   gap=4

    # --- Dragon (ATK median=19) ---
    "34":  {"atk_growth": 19},   # Vampirus     ATK 15→19 gap=4
    "49":  {"atk_growth": 19},   # Orligon      ATK 15→19 gap=4
    "44":  {"atk_growth": 19},   # Dragon       ATK 16→19 gap=3

    # --- Beast (ATK median=17) ---
    "61":  {"atk_growth": 17},   # Grizzly      ATK 13→17 gap=4
    "66":  {"atk_growth": 17},   # HyaWarrior   ATK 13→17 gap=4
    "69":  {"atk_growth": 17},   # Wolfon       ATK 13→17 gap=4
    "79":  {"atk_growth": 17},   # SabreTooth   ATK 13→17 gap=4
    "60":  {"atk_growth": 17},   # Bristle      ATK 14→17 gap=3
    "80":  {"atk_growth": 17},   # ThunderPup   ATK 14→17 gap=3
    "87":  {"atk_growth": 17},   # BigEye       ATK 14→17 gap=3

    # --- Bird (AGI median=18) ---
    "90":  {"agi_growth": 18},   # KiteHawk     AGI 14→18 gap=4
    "99":  {"agi_growth": 18},   # BullBird     AGI 14→18 gap=4
    "103": {"agi_growth": 18},   # PuffRobin    AGI 14→18 gap=4

    # --- Material (DEF median=18) ---
    "231": {"def_growth": 18},   # Golem        DEF 14→18 gap=3.5
    "237": {"def_growth": 18},   # MetalDrak    DEF 14→18 gap=3.5
    "247": {"def_growth": 18},   # GoldGolem    DEF 14→18 gap=3.5
    "252": {"def_growth": 18},   # LavaMan      DEF 14→18 gap=3.5

    # --- Zombie (HP median=14) ---
    "201": {"hp_growth": 14},    # Spooky       HP 11→14  gap=3
    "224": {"hp_growth": 14},    # DarkCrab     HP 11→14  gap=3
}

print(json.dumps(edits, indent=2))
