# Core Monster Data

**ROM region:** Bank 0x35 (`0xD4000–0xD7FFF`)

## Layout

| First Byte | Last Byte | Content |
|---|---|---|
| D4000 | D4000 | 0x35 bank code |
| D4001 | D403A | Functions (3 subroutines + 1 data-copy helper) |
| D403B | D433A | Pointer table (core ID → 2-byte offset into structure region) |
| D433B | D7EB6 | Monster structures (47 bytes × 324 entries) |
| D7EB7 | D7FFF | Empty padding |

## Core IDs

Monsters are enumerated `0x0000`–`0x017E` (little-endian). 324 monsters total, counting the empty entry for `0x0000`, with some holes in the enumeration. Not to be confused with prebuilt enemy IDs.

## Functions

| Address | Description |
|---|---|
| `35:4001` | `LD DE,D008; LD B,2F; CALL 401C; RET` — Copy full 47-byte structure to D008 |
| `35:400A` | `LD DE,D008; LD B,01; CALL 401C; RET` — Copy 1 byte to D008 |
| `35:4013` | `LD DE,D008; LD B,02; CALL 401C; RET` — Copy 2 bytes to D008 |
| `35:401C` | Given ID in D006/D007, address in DE, length in B: look up offset from pointer table, copy `length` bytes from structure to address |

## Pointer Table

**Offset:** `0xD403B`, **Size:** `0x300` bytes (324 entries × 2 bytes LE).

Maps core ID → offset into the structure region. Unused IDs point to `0xFF` (the first byte of the first structure, which is the null marker).

## Structure (47 bytes per monster)

| Bytes | Size | Field |
|---|---|---|
| 0 | 1 | Family ID |
| 1 | 1 | Gender ratio |
| 2 | 1 | Flying (LegSweep immune) |
| 3 | 1 | Metal type |
| 4 | 1 | Species-specific join rate |
| 5 | 1 | Unknown (1=flying, 2=Water family, 3=Starfish) |
| 6 | 1 | Unbred max level |
| 7 | 1 | Experience growth rate |
| 8 | 1 | Skill 1 ID |
| 9 | 1 | Skill 2 ID |
| 10 | 1 | Skill 3 ID |
| 11 | 1 | Unknown (related to random world selection?) |
| 12 | 1 | HP growth |
| 13 | 1 | MP growth |
| 14 | 1 | Attack growth |
| 15 | 1 | Defense growth |
| 16 | 1 | Agility growth |
| 17 | 1 | Intelligence growth |
| 18–44 | 27 | Resistances table |
| 45–46 | 2 | Base exp yield in random worlds (LE u16) |

**Notes:**
- First structure (ID 0) starts with `0xFF` — all pointers not pointing to a valid structure point there.
- Unknown bytes at offsets 5 and 11 are NOT critical hit rates; those are stored elsewhere. They may relate to how monsters are selected/created for random worlds.
- These fields do not all exist in the corresponding DWM1 species structure (notably the two unknown bytes and base exp yield).
