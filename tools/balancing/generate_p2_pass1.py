#!/usr/bin/env python3
"""Generate Phase 2 Pass 1 edits for bottom 40 weakest monsters.

Each monster gets its family theme stat boosted to be viable.
Growth rates are single bytes (1-31 scale) at core_monster bytes 12-17.
"""
import json

# Format: {index: {field: new_value, ...}}
# Based on analysis of bottom 40 monsters by total growth score.
# Family themes: Material=DEF, Plant=INT, Zombie=HP, Bug=DEF, Bird=AGI,
#               Dragon=ATK, Water=INT/HP, Beast=ATK, Devil=INT

edits = {
    # --- Tier 1: Critical (total ≤ 40) ---
    "258": {"def_growth": 18},           # Goopi (material) DEF 3→18 Tank wall
    "126": {"int_growth": 14},           # BeanMan (plant) INT 2→14 Nature mage
    "215": {"hp_growth": 22},            # Niterich (zombie) HP 7→22 Tank
    "135": {"int_growth": 13},           # AmberWeed (plant) INT 3→13 Early mage
    "243": {"def_growth": 18},           # JewelBag (material) DEF 4→18 Wall
    "144": {"def_growth": 16},           # Catapila (bug) DEF 4→16 Defensive bug
    "131": {"int_growth": 15},           # TreeBoy (plant) INT 3→15 Magic focus

    # --- Tier 2: Weak (total 41-48) ---
    "268": {"int_growth": 15, "hp_growth": 14},  # Poseidon (water) INT+HP Magic tank
    "28":  {"hp_growth": 16},              # Chamelgon (dragon) HP Physical striker
    "151": {"def_growth": 19},             # GiantMoth (bug) DEF 9→19 Defensive bug
    "101": {"agi_growth": 21},             # DuckKite (bird) AGI 9→21 Swift striker
    "35":  {"agi_growth": 5},              # Rayburn (dragon) AGI 1→5 Power hitter
    "89":  {"atk_growth": 16},             # BigEye (beast) ATK 10→16 Physical attacker
    "158": {"def_growth": 15},             # Sickler (bug) DEF 3→15 Defensive tank
    # Exaucers (241) already thematic, GateGuard (180) INT=17 already good
    "180": {"mp_growth": 10},              # GateGuard (devil) MP 1→10 Give spell resources
    "236": {"def_growth": 18},             # SpikyBoy (material) DEF 4→18 Wall

    # --- Tier 3: Below average (total 52-60) ---
    # Grendal, EvilWell, SkyDragon, ArmyAnt, ArmyCrab, Unicorn, Drygon,
    # MadPlant, MetalDrak, Eggplaton, Reaper already have decent theme stats
    "148": {"def_growth": 17},             # MultiEyes (bug) DEF 7→17 Defensive bug
    "202": {"hp_growth": 18},              # DeadNite (zombie) HP 6→18 Tank
    "216": {"hp_growth": 16},              # RotRaven (zombie) HP 9→16 Support tank
    "93":  {"agi_growth": 18},             # AquaHawk (bird) AGI 6→18 Fast striker
    "117": {"int_growth": 14},             # WingTree (plant) INT 11→14 Swift mage
    "252": {"agi_growth": 6},              # LavaMan (material) AGI 1→6 Fast wall
    "264": {"int_growth": 14, "hp_growth": 14},  # Scallopa (water) INT+HP Magic tank
    "272": {"int_growth": 13},             # Merman (water) INT 6→13 Swift mage
    "63":  {"atk_growth": 18, "agi_growth": 5},  # Skullroo (beast) ATK+AGI Physical striker
    "145": {"def_growth": 17},             # StagBug (bug) DEF 9→17 Defensive bug
    "171": {"int_growth": 16},             # Demonite (devil) INT 4→16 Magic fairy
}

print(json.dumps(edits, indent=2))
