#!/usr/bin/env python3
"""Generate Phase 3 edits — Skill Redistribution.

Swap one skill per monster to give rare/thematic abilities:
- Material (tanks): Ironize(33), BladeD(113), Surge(161)
- Bug (defensive): Ironize(33), BladeD(113)
- Devil (mages): MPass(16), SuckAll(114), HealUs(97)
- Plant (mages): MPass(16), LifeSong(30), HealUs(97)
- Water (magic tank): HealUs(97), SuckAll(114)
- Dragon (physical): Surge(161), BigBang(143)
- Beast (physical): Surge(161), BigBang(143)
- Slime (spellcaster): HealUs(97), LifeSong(30)
"""
import json

edits = {
    # Material family — tank skills
    "258": {"skill_1": 33},   # Goopi: CallHelp → Ironize
    "243": {"skill_2": 113}, # JewelBag: StopSpell → BladeD
    "236": {"skill_3": 33},  # SpikyBoy: HighJump → Ironize
    "251": {"skill_1": 113}, # MudDoll: OddDance → BladeD
    "252": {"skill_3": 33},  # LavaMan: Cover → Ironize
    "230": {"skill_2": 161}, # Facer: Sacrifice → Surge
    "234": {"skill_2": 113}, # Mimic: Beat → BladeD

    # Bug family — defensive skills
    "144": {"skill_2": 113}, # Catapila: PoisonHit → BladeD
    "158": {"skill_1": 33},  # Sickler: Infernos → Ironize
    "145": {"skill_3": 113}, # StagBug: LegSweep → BladeD
    "151": {"skill_3": 33},  # GiantMoth: Radiant → Ironize
    "148": {"skill_2": 113}, # MultiEyes: TwinHits → BladeD

    # Devil family — mage skills
    "170": {"skill_2": 16},  # EvilBeast: Ironize → MPass
    "171": {"skill_2": 114}, # Demonite: FireAir → SuckAll
    "179": {"skill_3": 97},  # Gremlin: StopSpell → HealUs
    "180": {"skill_2": 16},  # GateGuard: CleanCut → MPass
    "189": {"skill_3": 114}, # EvilArmor: AquaCut → SuckAll
    "194": {"skill_3": 16},  # BossTroll: Cover → MPass

    # Plant family — magic support
    "126": {"skill_3": 30},  # BeanMan: MapMagic → LifeSong
    "135": {"skill_3": 97},  # AmberWeed: MagicWall → HealUs
    "141": {"skill_2": 16},  # FaceTree: Curse → MPass
    "117": {"skill_2": 30},  # WingTree: ZombieCut → LifeSong

    # Water family — healing/drain
    "264": {"skill_2": 97},  # Scallopa: MagicWall → HealUs
    "268": {"skill_2": 114}, # Poseidon: Focus → SuckAll
    "272": {"skill_3": 97},  # Merman: SleepAir → HealUs

    # Dragon family — physical burst
    "28":  {"skill_2": 161}, # Chamelgon: Paralyze → Surge
    "35":  {"skill_3": 143}, # Rayburn: PoisonHit → BigBang

    # Beast family — physical burst
    "63":  {"skill_2": 161}, # Skullroo: PaniDance → Surge
    "89":  {"skill_3": 143}, # BigEye: LoveRain → BigBang

    # Slime family — healing
    "2":   {"skill_2": 97},  # BoxSlime: Upper → HealUs
    "6":   {"skill_3": 30},  # WonderEgg: Chance → LifeSong
}

print(json.dumps(edits, indent=2))
