# DWM2 Ultimate - Analysis & Comparison

## Overview

**DWM2 Ultimate** is a ROM hack designed as a "DWM2 NG+" (New Game+) for players who have completed the base game multiple times. It makes the game significantly harder while adding convenience features to facilitate grinding.

**Total Changes:** 16,941 differing bytes across **441 patch locations**

---

## Key Difficulty Changes

### 1. Monster Level & Stat Increases

| Aspect | Base Game | DWM2 Ultimate | Impact |
|--------|-----------|---------------|--------|
| Starting level | Lv 1 | Lv 5 | Immediate challenge increase |
| Story key monsters | Original levels | Increased per region | Progressive difficulty scaling |
| Boss battles | 1-2 enemies | **3 enemies** | More complex combat |
| Random masters | Standard levels | "Extremely high level" | Post-game challenge |
| Post-game worlds | Standard | "Extremely difficult" | Elf/Traveler/Lonely worlds |

### 2. Stat Growth System

**Custom Level 1 Formula:** DWM2U uses a custom formula for base stats at level 1, then scales with regional difficulty. This means:
- Monsters start stronger in later regions
- Stat growth tables are still used, but the base is higher
- Promotes both challenge and breeding options

### 3. Experience System

**Custom EXP Formula** with rank reductions:
- Ultra rare monsters: **-2 ranks** (level up faster)
- Rare monsters: **-4 ranks**
- High EXP requirement monsters: **-6 ranks**

This balances the increased difficulty by making grinding more rewarding.

### 4. Encounter Variety Expansion

**Random encounters dramatically expanded:**
| World | Base | DWM2U | Increase |
|-------|------|-------|----------|
| Oasis | 11 species | 30 | **+173%** |
| Pirate | 36 | 53 | **+47%** |
| Ice | 39 | 52 | **+33%** |
| Sky | 48 | 59 | **+23%** |

**Regional grouping:** Monsters are now grouped by species in memory/encounters to improve habitat consistency.

---

## Prebuilt Enemy Changes

### Modified Enemy Tables (from IPS log)

The patch heavily modifies these regions:
- **0x0286FA**: Starting monster data (Gismo with Heal skill)
- **0x02881C-0x0288B3**: Boss battle compositions
- **0x029779-0x02A3CE**: All story key world encounters
- **0x0D008F-0x0D77BB**: Prebuilt enemy table (100+ entries)

### Specific Boss Changes

Most boss battles now have **3 enemies** instead of 1-2. Examples from patch analysis:
- CurseLamp fight expanded
- CaptDead, BombCrag, Niterich, Mudou, Darck all modified
- Arena monsters (Kiddie through S rank) replaced

### High XP Monsters in Random Keys

DWM2U creates a "Metaly hunting" experience with boosted base XP:

| Monster | Base XP | Notes |
|---------|---------|-------|
| MetalKing | 1800 | Still the king |
| Metabble | 1400 | Second highest |
| RoseVine | 1161 | Plant family |
| KingSlime | 927 | Slime family |
| GreatDrak | 900 | Dragon family |
| Phoenix/Blizzardy | 756 | Elemental birds |
| MetalDrak | 729 | Dragon |
| LavaMan | 666 | Thematic XP |

---

## Item & Economy Changes

### Item Quantity/Usage
- **Increased uses:** Antidote, Laurel, WarpWing, WarpStaff, ExitBell, Books
- **Improved effectiveness:** Herbs, Lovewater, Potion, Meats

### Shop Inventory Changes
- **Sirloin:** Fixed price at 1000G (no price gouging)
- **Seeds:** Now purchable post-game
- **Tiny Medals:** Purchasable AND sellable for 10000G (no loss)
- **Equipment:** Now available in some stores
- **Sell prices:** Increased for staves, seeds, equipment

### Modified Regions
- **0x5346B-0x538CB**: Item data tables (effectiveness changes)
- **0x7218F-0x723EC**: Shop inventories

---

## Skill Changes

| Skill | Base Game | DWM2 Ultimate | Effect |
|-------|-----------|---------------|--------|
| Family Cuts | 3 MP | **1 MP** | Cheaper to spam |
| Revive | 20 MP | **12 MP** | Less expensive recovery |
| Outside | 1 MP | **0 MP** | Free utility skill |
| Revive INT requirement | High | Reduced | Earlier access |
| Informer | Present | Replaced with Outside | More useful skill |
| FireSlash element | Physical | Fire | Consistent with FireBolt |
| MultiCut element | Physical | Magical | Consistent with MegaMagic |
| Gigaslash | INT req | HP/MP/Atk req instead | Different stat focus |

---

## Breeding Changes

### Added Formulas (from BCRobert's hack + custom)

**New breeding combinations:**
- Dragon (Monster) × DarkMate = Dimensaur
- Puppetor × Devil (Family) = Sabreman
- Kitehawk × Beast (Family) = Bigroost
- Foohero × Darck = Warubou
- Warubou × Slime (Monster) = Watabou
- Blizzardy/Phoenix/ZapBird × CloudKing = Lamia
- Beastnite × PomPomBom/FoxFire = Copycat

**Modified regions:** 0x3A526-0x3ACAA (breeding table)

---

## Random Key & Arena Changes

### Key System Overhaul

**Key types reduced** to improve odds (~6% per key):
- 11 Family keys
- Castle (Dragon+Slime), Land (Bug+Plant), Jungle (Beast+Bird), Star (Material+Water), Hell (Zombie+Devil)

**Level scaling:**
- Higher level keys more common
- Lord keys: 5% chance with Lv 80+ party leader

### Arena Rewards

**High-value rewards:** TinyMedals, MeteOrbs, Seeds, Magic Keys

### Post-Game Content

**New challenges:**
- Prince Kameha and Terry (difficult post-game fights)
- Elf, Traveler, Lonely worlds (extreme difficulty)
- **Milayou** (ultimate boss with max stats beyond 999)
- Brawn/Baffle/Soul keys: Boss challenges with promotional event monsters

---

## Uncatchable Monsters

Monsters that must be bred first (Lord types except Darck):
MetalKing, GoldSlime, GranSlime, Divinegon, Orligon, GigaDraco, KingLeo, Gorago, Azurile, RoseVine, EgDracil, Armorpion, Durran, Jamirus, Titanis, LazaManus, WhiteKing, Niterich, GoldGolem, DarkMate, Poseidon

This encourages breeding and adds progression gates.

---

## Lessons for Our Balancing Mod

### What DWM2U Does Well

1. **Progressive difficulty scaling** - later regions are harder
2. **More encounter variety** - exploration is rewarded
3. **Boss battle complexity** - 3 enemies forces strategic thinking
4. **Custom stat formula** - region-appropriate starting stats
5. **High XP targets** - grinding is meaningful
6. **Convenience features** - item improvements offset difficulty

### Ideas We Can Adapt

| Idea | Implementation | Priority |
|------|----------------|----------|
| Increase boss enemy count | Modify `boss_battles` table | High |
| Nerf NPC breeding partners | Lower levels in `prebuilt_enemies` | High (already planned) |
| Boost XP for elite monsters | Modify `core_monster` base_exp field | Medium |
| Adjust EXP requirements | Modify `exp_tables` to make rare monsters faster | Medium |
| Increase starting monster variety | Add more species to encounter tables | Low |
| Region-appropriate stat scaling | Custom growth rates per world | High (complex) |
| More arena opponents | Extend arena enemy pool | Medium |
| Item effectiveness tweaks | Modify item data at 0x5346B | Low |

### Data Regions to Focus On

Based on DWM2U's approach, these ROM regions are high-value targets:

1. **0x02881C** - Boss battle compositions (8 bytes × 40 entries)
2. **0x0D0075** - Prebuilt enemies (26 bytes × 600 entries)
3. **0x0D433B** - Core monster data (47 bytes × 324 species)
4. **0x29773-0x2A3CE** - Random encounter tables per world
5. **0x64E60** - EXP tables (3 bytes × 100 ranks)

---

## Recommended Next Steps

1. **Start with boss battles** - DWM2U shows 3-enemy bosses work well
2. **Nerf breeding partners** - Our G5 goal, already planned
3. **Adjust growth rates** - Target overpowered species (HornBeet, Balzak, Octoreach per recommendations)
4. **Tweak EXP curve** - Make late-game grinding more rewarding

The DWM2U hack proves that data-only changes can dramatically alter game feel without touching engine code or graphics.
