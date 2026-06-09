#!/usr/bin/env python3
"""Generate Phase 2 Pass 2 edits — Theme Corrections.

Bring monsters with theme stat well below their family median up to median level.
Excludes monsters already edited in Pass 1.
"""
import json

edits = {
    # --- Devil family (should be smart, INT >= ~14) ---
    "194": {"int_growth": 14},   # BossTroll      INT 0→14  (was literally 0!)
    "189": {"int_growth": 14},   # EvilArmor      INT 1→14
    "170": {"int_growth": 12},   # EvilBeast      INT 3→12
    "179": {"int_growth": 12},   # Gremlin        INT 4→12

    # --- Material family (should be walls, DEF >= ~18) ---
    "230": {"def_growth": 18},   # Facer          DEF 6→18
    "234": {"def_growth": 18},   # Mimic          DEF 6→18
    "251": {"def_growth": 18},   # MudDoll        DEF 6→18

    # --- Slime family (should be magical, MP >= ~12) ---
    "2":   {"mp_growth": 12},    # BoxSlime       MP 1→12
    "6":   {"mp_growth": 12},    # WonderEgg      MP 1→12
    "12":  {"mp_growth": 12},    # TreeSlime      MP 1→12
    "3":   {"mp_growth": 11},    # MetalKing      MP 2→11

    # --- Zombie family (should be tanky, HP >= ~16) ---
    "226": {"hp_growth": 16},    # DeadNoble      HP 5→16
    "211": {"hp_growth": 18},    # Inverzon       HP 6→18

    # --- Plant family (should use magic, INT >= ~14) ---
    "141": {"int_growth": 14},   # FaceTree       INT 4→14
    "122": {"int_growth": 14},   # CactiBall      INT 5→14

    # --- Dragon family (should be strong, ATK >= ~19) ---
    "45":  {"atk_growth": 19},   # FairyDrak      ATK 10→19

    # --- Beast family (should be physical, ATK >= ~17) ---
    "62":  {"atk_growth": 17},   # Tonguella      ATK 8→17
    "67":  {"atk_growth": 17},   # BeastNite      ATK 8→17

    # --- Bug family (should be defensive, DEF >= ~16) ---
    "163": {"def_growth": 16},   # MadHornet      DEF 7→16
    "166": {"def_growth": 16},   # Lipsy          DEF 7→16
}

print(json.dumps(edits, indent=2))
