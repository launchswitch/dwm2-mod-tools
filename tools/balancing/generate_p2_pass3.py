#!/usr/bin/env python3
"""Generate Phase 2 Pass 3 edits — remaining theme violations (gap >= 6).

Brings monsters with theme stat >= 6 below family median up to median level.
"""
import json

edits = {
    # --- Water family (INT, median=13) ---
    "265": {"int_growth": 13},   # Gamanian     INT 4→13  gap=9
    "263": {"int_growth": 13},   # Octokid      INT 7→13  gap=6
    "271": {"int_growth": 13},   # Starfish     INT 7→13  gap=6

    # --- Dragon family (ATK, median=19) ---
    "41":  {"atk_growth": 19},   # Dragon       ATK 11→19 gap=8
    "31":  {"atk_growth": 19},   # DragonKid    ATK 13→19 gap=6

    # --- Plant family (INT, median=14) ---
    "136": {"int_growth": 14},   # Devipine     INT 6→14  gap=8
    "121": {"int_growth": 14},   # DanceVegi    INT 7→14  gap=7

    # --- Bug family (DEF, median=16) ---
    "150": {"def_growth": 16},   # Pyuro        DEF 8→16  gap=8
    "164": {"def_growth": 16},   # Digster      DEF 9→16  gap=7

    # --- Bird family (AGI, median=18) ---
    "104": {"agi_growth": 18},   # FunkyBird    AGI 11→18 gap=7

    # --- Zombie family (HP, median=16) ---
    "208": {"hp_growth": 16},    # Skullgon     HP 9→16   gap=7
    "217": {"hp_growth": 16},    # Hork         HP 9→16   gap=7
    "200": {"hp_growth": 16},    # Copycat      HP 10→16  gap=6

    # --- Material family (DEF, median=18) ---
    "241": {"def_growth": 18},   # Exaucers     DEF 11→18 gap=7
    "229": {"def_growth": 18},   # BombCrag     DEF 12→18 gap=6
    "232": {"def_growth": 18},   # Roboster1    DEF 12→18 gap=6
    "238": {"def_growth": 18},   # SabreMan     DEF 12→18 gap=6
    "250": {"def_growth": 18},   # CurseLamp    DEF 12→18 gap=6

    # --- Beast family (ATK, median=17) ---
    "65":  {"atk_growth": 17},   # Mommonja     ATK 11→17 gap=6

    # --- Devil family (INT, median=14) ---
    "176": {"int_growth": 14},   # MadKnight    INT 8→14  gap=6
    "193": {"int_growth": 14},   # Bubblemon    INT 8→14  gap=6
}

print(json.dumps(edits, indent=2))
