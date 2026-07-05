# Battle & Breeding Data Map

ROM and RAM locations for battle encounters and breeding system in DWM2 (Cobi GBC).

Purpose: source of truth for linking the shiny system to wild encounters (3% chance)
and breeding inheritance calculations.

## ROM Data Tables

### Random Encounter Tables

**Offset:** `0x29773` — **Size:** ~4 KB — **16 world areas**

Each area entry contains:
- Max enemies per encounter (1–3)
- Max chance value (determines encounter frequency)
- 5 chance thresholds (probability bands for enemy count)
- Prebuilt enemy IDs (one per threshold band)

When the game triggers a random encounter, it reads this table for the current area,
rolls against the chance thresholds, and selects a prebuilt enemy ID.

**Verified:** 16 areas (oasis_world through elf_world). Parser in `tools/mod_data.py`
supports `--table random_encounters --list`.

### Prebuilt Enemy Structs (26 bytes each)

| Part | ROM Offset | Entry Range | Notes |
|------|-----------|-------------|-------|
| Part 1 | `0xD0075` | IDs 0–299 | Bosses, overworld encounters, trainers |
| Part 2 | `0x288056` | IDs 300–599 | Later areas, rare encounters, post-game |

**Struct layout (26 bytes):**

```
Offset  Size  Field
+0x00   2     Species ID (LE u16)
+0x02   1     Skill 1 ID
+0x03   1     Skill 2 ID
+0x04   1     Skill 3 ID
+0x05   1     Skill 4 ID
+0x06   2     EXP yield (LE u16)
+0x08   1     Join value (0=always, 7=never)
+0x09   1     Level
+0x0A   2     HP (LE u16)
+0x0C   2     MP (LE u16)
+0x0E   2     Attack (LE u16)
+0x10   2     Defense (LE u16)
+0x12   2     Agility (LE u16)
+0x14   2     Intelligence (LE u16)
+0x16   1     Charge aptitude
+0x17   1     Defense aptitude
+0x18   1     Motivation
+0x19   1     Mixed aptitude
```

**Verified:** Entry 0 = species 0x0000 (null), Entry 1 = species 0x000A (Slime, Lv1).
Parser in `tools/mod_data.py` supports `--table prebuilt_enemies --show <id>`.

### Core Monster Data (Species Templates)

**Offset:** `0xD4000–D7FFF` (Bank 0x35) — **Size:** 16 KB — **324 species × 47 bytes**

Pointer table at `0xD403B` maps species ID → offset into structure region (`0xD433B+`).

Functions at `35:4001` copy the full 47-byte template to WRAM when needed. This is how
the game loads species data during battle, breeding, and party operations.

### Breeding Data Tables

| Table | ROM Offset | Content |
|-------|-----------|---------|
| Mate pointers (Species+Species) | `0x3A208` | 2-byte LE pointer per species |
| Mate lists (Species+Species) | `0x3A508` | Species IDs that produce each result |
| Result pointers (Species+Species) | `0x3AE14` | 2-byte LE pointer per species |
| Result lists (Species+Species) | `0x3B114` | Result species IDs (one per mate set) |
| Mate pointers (Species+Family) | `0x3B34E` | Same structure, family-based matching |
| Mate pointers (Family+Species) | `0x3BB83` | Same structure, reversed parent order |
| Family+Family data | `0x3BE99` | Family-level breeding results |

**Pointer convention:** All pointers are 2-byte LE, based on address `0x34000`.
For species ID N, mate pointer at `0x3A208 + (N × 2)`, result pointer at `0x3AE14 + (N × 2)`.

**Verified:** Species 0 pointer = 0x6508 → list at 0xE9D8. Parser supports
`--table breeding --show <species_id>`.

### Boss Battle Compositions

**Offset:** `0x2881C` — **Size:** ~1 KB — **40 boss fights**

Each entry (8 bytes): `[count: 2B LE][enemy_1: 2B][enemy_2: 2B][enemy_3: 2B]`
Count = number of enemies minus 1 (so count=2 means 3 enemies).

**Verified:** Boss 0 has 1 enemy (ID 7), Boss 2 has 3 enemies (IDs 399, 28, 399).

## RAM Data Flow

### Battle Encounter Path (ROM → RAM)

```
Player walks in world
  → Game reads random_encounters table (ROM 0x29773+) for current area
  → Selects prebuilt enemy ID from chance thresholds
  → Copies 26-byte prebuilt struct from ROM (0xD0075+ or 0x288056+) into WRAM
  → Data lands in Monster Working Buffer at 0xC008 (WRAM Bank 0)
  → Battle UI renders, battle logic runs using data at 0xC008
```

### Breeding Path (ROM → RAM)

```
Player enters breeding with NPC or wild monster
  → Game reads breeding_mate pointers from ROM (0x3A208+)
  → Looks up result species ID based on parent combination
  → Copies core monster template from ROM (0xD4000+) to buffer at 0xC008
  → New monster created with inherited/modified stats
  → Monster joins party → 0xC563 (party count) increases
  → New entry appears at 0xDFC0+ in WRAM Bank 1
```

### Key RAM Addresses

| Address | Bank | Content | Access Pattern |
|---------|------|---------|----------------|
| `0xC008` | 0 (always) | Monster Working Buffer | Species ID at +0x00, full template during battle/breeding |
| `0xC563` | 0 (always) | Party count (1 byte) | Poll every frame to detect party changes |
| `0xDFC0+` | 1 (`0xFF70=1`) | Party monster entries (~34 bytes each) | Read species ID, level, stat pointers |
| `0xFF80-0xFF85` | HRAM | Game state flags | Change on screen transitions (overworld/menu/battle) |

## Shiny System Integration Points

### Wild Encounter Detection (Battle Start)

**Current approach:** Poll `0xC008` for non-zero species ID. Works but has false positives
(title screen, menus also populate this buffer).

**Recommended approach — 3-signal confirmation:**

1. **Signal A:** `0xC008` has a non-zero species ID (enemy template loaded)
2. **Signal B:** Party count `> 0` (player has a party — filters title screen)
3. **Signal C:** HRAM at `0xFF80-0xFF85` shows battle-state values (filters menus)

**Action needed:** Probe HRAM values during actual battles to catalog "battle state" flag
values. Current RAM map shows these bytes change on screen transitions but doesn't
document what each value means.

### Breeding Detection

**Current approach:** Can't distinguish breeding from recruitment/gifts. All trigger the
same signal: party count increases + new species ID at `0xDFC0+`.

**Recommended approach — NPC breeder tracking:**

NPC breeding partners use prebuilt IDs 174–178. When these IDs appear in the Monster
Working Buffer (`0xC008`), breeding is happening.

Alternative: Track HRAM flags for "breeding menu" state (requires probing).

### Wild Shiny → Party Join Persistence

When a wild monster is determined shiny during battle, the shiny type must persist when
the monster joins the party after recruitment. Currently `rollWildShiny` sets
`battleShinyType` but this isn't transferred to the new party member.

**Fix:** When party count increases within N frames of battle ending, check if
`battleShinyType` is set and transfer it to the new slot instead of re-rolling.

### Shiny Chance Configuration

| Context | Base Chance | Notes |
|---------|-----------|-------|
| Wild encounter | 3% (0.03) | Flat roll, no parent inheritance |
| Breeding (1 shiny parent) | 50% (0.50) | Inherited from party shiny count |
| Breeding (2+ shiny parents) | 100% | Guaranteed shiny offspring |
| Gift/event monster | 3% (0.03) | Same as wild, no special handling |

## Probing Plan (Next Steps)

### Step 1: HRAM Battle-State Values

Boot ROM, probe `0xFF80–0xFF85` during:
- Overworld (walking)
- Wild battle (enemy engaged)
- Boss battle
- Breeding menu (NPC conversation)
- Party menu

Compare values to identify unique "battle" and "breeding" signatures.

### Step 2: Prebuilt ID → Species Mapping

Build a lookup table of prebuilt enemy ID → species ID for all 600 entries.
This lets the shiny system know which species is being encountered before the
game resolves it to a party member.

Use `tools/mod_data.py --table prebuilt_enemies --list` to generate this data.

### Step 3: Encounter Area → Shiny Rate Mapping

Optionally boost shiny rates in rare areas (limbo world, elf world) based on
the encounter area index from the random encounters table.
