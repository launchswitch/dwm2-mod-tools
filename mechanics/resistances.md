# Elements / Resistances

The 27-byte resistances table in each monster's core data structure (offsets 18–44) maps element IDs to resistance values.

## Element ID Table

| ID | Hex | Skills affected |
|---|---|---|
| 0 | 0x00 | Attack (base damage) |
| 1 | 0x01 | Blaze, BlazeMore, BlazeMost, BigBang, FireSlash |
| 2 | 0x02 | Firebal, Firebane, Firebolt |
| 3 | 0x03 | Bang, Boom, Explodet |
| 4 | 0x04 | WindBeast, Vacuum, Infernos, Infermore, Infermost, MultiCut, VacuSlash |
| 5 | 0x05 | Lightning, Bolt, Zap, Thordain, Hellblast, BoltSlash |
| 6 | 0x06 | IceBolt, SnowStorm, Blizzard, IceSlash |
| 7 | 0x07 | Radiant, Surround, SandStorm |
| 8 | 0x08 | Sleep, NapAttack, SleepAir, SleepAll |
| 9 | 0x09 | EerieLite, UltraDown, Beat, Defeat, K.O.Dance |
| 10 | 0x0A | OddDance, RobDance, RobMagic |
| 11 | 0x0B | StopSpell |
| 12 | 0x0C | PaniDance, PanicAll |
| 13 | 0x0D | Sap, Defense, SickLick |
| 14 | 0x0E | Slow, SlowAll |
| 15 | 0x0F | Sacrifice, Kamikaze, Ramming |
| 16 | 0x10 | MegaMagic |
| 17 | 0x11 | FireAir, BlazeAir, Scorching, WhiteFire |
| 18 | 0x12 | FrigidAir, IceAir, IceStorm, WhiteAir |
| 19 | 0x13 | PoisonHit, PoisonGas, PoisonAir |
| 20 | 0x14 | Paralyze, PalsyAir |
| 21 | 0x15 | Curse |
| 22 | 0x16 | LegSweep, LushLicks, Ahhh, BigTrip, WarCry, LureDance |
| 23 | 0x17 | DanceShut |
| 24 | 0x18 | MouthShut |
| 25 | 0x19 | RockThrow, CallHelp, YellHelp |
| 26 | 0x1A | GigaSlash |
| 27 | 0x1B | Geyser, WaterShot, TidalWave |

Each byte in the resistances table corresponds to one element ID (index 0 = Attack, index 1 = Blaze-family, etc.). The value represents the monster's resistance/reduction against that element type.
