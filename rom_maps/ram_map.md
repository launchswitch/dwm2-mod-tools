# DWM2 RAM Map

Runtime memory layout for DWM2 (Cobi, GBC). Addresses are GBC bus addresses.

Probed with `build/cobi_final.gbc` using PyBoy headless emulation.

## GBC Memory Map Refresher

| Region | Address Range | Size | Notes |
|---|---|---|---|
| WRAM Bank 0 | `0xC000-CFFF` | 4 KB | Always-mapped, main game state |
| WRAM Bank 1-7 | `0xD000-DFFF` | 4 KB | Banked via `0xFF70` |
| OAM | `0xFE00-FE9F` | 80 bytes | 40 sprites × 2 bytes each |
| IO Registers | `0xFF00-FF7F` | 128 bytes | Timers, palettes, joypad |
| HRAM | `0xFF80-FFFE` | 127 bytes | Fast byte-access RAM |

---

## WRAM Bank 0 (`0xC000-CFFF`) — Main Game State

### Species Registry: `0xC000-0xC080`

4-byte entries: `[species_id: LE u16][byte1][byte2]`. Maps species to internal indices/pointers. Confirmed species range: 0x0050–0x0073 (80–115).

### Encounter/Family Grouping: `0xC1F0-0xC2A0`

Groups of 5-8 sequential species IDs, zero-padded between groups. Used for random encounter tables or family classification.

### Party Monster Data: `0xC560-0xC570`

Confirmed by live probing. Raw bytes at game start (after opening cutscene):
```
0xC560: 00 00 00 03 00 00 00 14 00 00 00 00 07 1F D2
```

| Offset | Address | Size | Field | Evidence |
|---|---|---|---|---|
| +0x00 | `0xC560` | 3B | Unknown (padding/flags) | Always `00 00 00` at start |
| +0x03 | `0xC563` | 1B | **Party count** | Value = 3 at game start (initial party size) |
| +0x04 | `0xC564` | 3B | Unknown | `00 00 00` |
| +0x07 | `0xC567` | 1B | **Leader level** | Value = 0x14 = 20 at game start |
| +0x0A | `0xC56A` | 3B | Unknown (flags?) | `00 00 07` |

### Monster Working Buffer: `0xC008-0xC037`

Core functions at `35:4001` copy the 47-byte species template from ROM to this buffer for runtime processing. Fields:

| Offset | Size | Field |
|---|---|---|
| +0x00 | 1 | Family ID |
| +0x01 | 1 | Gender ratio |
| +0x02 | 1 | Flying flag |
| +0x03 | 1 | Metal type |
| +0x04 | 1 | Species join rate |
| +0x06 | 1 | Unbred max level |
| +0x07 | 1 | EXP growth rate |
| +0x08-0A | 3 | Skill 1/2/3 ID |
| +0x0C-0x11 | 6 | HP/MP/ATK/DEF/AGL/INT growth rates |
| +0x12 | 27 | Resistances table |
| +0x1B | 2 | Base EXP yield (LE u16) |

### Species Reference Area: `0xC520-0xC560`

Contains species ID references (LE u16) for active monsters. Species 0x0001 (Slime) confirmed at `0xC525`.

---

## WRAM Bank 1 (`0xD000-DFFF`, `0xFF70 = 1`) — Extended Monster Data

### Party Monster Entries: `0xDFC0-0xE010`

Confirmed by live probing. Each entry contains species ID, level, and associated stats/pointers.

Observed entries at game start:
| Address | Species | Level | Raw Pattern |
|---|---|---|---|
| `0xDFD6` | 0x0001 (Slime) | 20 | `01 00 14 C0 69 B1 ...` |
| `0xDFF8` | 0x0029 | 9 | `29 00 09 00 DE 2C ...` |

Entry structure (inferred, ~34-42 bytes per entry):
```
[species_id: 2B LE][level: 1B][unknown: 1B][stats/pointers: N bytes]
```

### How to detect new monster creation

Watch `0xC563` (party count) for increments. When it increases, a new species ID will appear in the `0xDFC0+` region. The new entry's species ID and level can be read from the struct.

---

## WRAM Bank 2 (`0xD000-DFFF`, `0xFF70 = 2`) — Additional Monster Data

Species 0x00A0 (160) Lv44 confirmed at `0xDFDB`. Same struct layout as bank 1.

---

## HRAM (`0xFF80-FFFE`)

| Address | Content | Evidence |
|---|---|---|
| `0xFF80-0xFF85` | Game state pointers/flags | Values `3E C0 E0 46 3E` at idle, change with screen |
| `0xFF98-0xFFA0` | Timers/counters | `10 00 18 00 00 01 00 04` pattern |

---

## IO Registers (`0xFF00-FF7F`)

### OBCP (Object Background Color Palette): `0xFF48-0xFF4B`

GBC palette entries for sprite rendering. Each entry is a 15-bit RGB color (5 bits per channel). Modifying these before render can tint sprites.

Confirmed values at idle: `D2 D2 E2` — neutral/gray palette.

### WRAM Bank Select: `0xFF70`

Write to switch WRAM bank 1-7. Bank 0 is always mapped at `0xC000-CFFF`.

---

## Prebuilt Enemy Struct (ROM → WRAM on load)

26 bytes per enemy, copied from ROM to WRAM when encountered:

| Offset | Size | Field |
|---|---|---|
| +0x00 | 2 | Species ID (LE u16) |
| +0x02 | 1 | Skill 1 |
| +0x03 | 1 | Skill 2 |
| +0x04 | 1 | Skill 3 |
| +0x05 | 1 | Skill 4 |
| +0x06 | 2 | EXP yield (LE u16) |
| +0x08 | 1 | Join value |
| +0x09 | 1 | Level |
| +0x0A | 2 | HP (LE u16) |
| +0x0C | 2 | MP (LE u16) |
| +0x0E | 2 | Attack (LE u16) |
| +0x10 | 2 | Defense (LE u16) |
| +0x12 | 2 | Agility (LE u16) |
| +0x14 | 2 | Intelligence (LE u16) |
| +0x16 | 1 | Charge aptitude |
| +0x17 | 1 | Defense aptitude |
| +0x18 | 1 | Motivation |
| +0x19 | 1 | Mixed aptitude |

---

## Strategy for Shiny Mod Integration

### Detecting new monster creation

1. Poll `0xC563` (party count) every frame
2. When count increases, scan `0xDFC0-0xE010` for the new species ID
3. Roll shiny dice, assign type, apply stat bonuses

### Applying stat bonuses

Two approaches:
- **A. Periodic overwrite:** Every N frames, read stats from monster struct, multiply by shiny bonus, write back
- **B. Lazy patch:** Watch for stat write patterns after level-up, re-apply bonuses

### Sprite tinting

- Modify OBCP entries at `0xFF48-0xFF4B` before render
- For per-sprite tinting: read OAM at `0xFE00-FE9F`, identify target sprite's palette index, modify only that palette

---

## Tools Built

| Tool | Purpose |
|---|---|
| `tools/wram_inspector.py` | Snapshot, diff, search species IDs, hex dump, watch addresses |
| `tools/explore_wram.py` | Navigate game, probe WRAM banks, find non-zero regions |
| `tools/map_party_struct.py` | Multi-state diffing for struct field identification |
| `tools/diff_wram.py` | Dual-ROM lockstep comparison (existing) |
| `tools/dump_memory.py` | Hex dump any memory region (existing) |

## Remaining Unknowns

- **Exact party monster struct size:** ~34-42 bytes inferred from entry spacing, not confirmed
- **HP/MP/stat field offsets within struct:** Need before/after diff of healing/leveling
- **Battle state RAM region:** Not yet probed (requires entering battle)
- **Save file integration:** How ext RAM maps to WRAM on load

## References

- [core_monster_data.md](../table_structure/core_monster_data.md) — ROM species templates
- [prebuilt_enemies_data.md](../table_structure/prebuilt_enemies_data.md) — prebuilt enemy structs
- [rom_map.txt](../roms/rom_map.txt) — full ROM data map
- binjgb API: `_emulator_read_mem(ptr, addr)`, `_emulator_write_mem(ptr, addr, val)`
