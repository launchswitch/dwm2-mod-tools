# Prebuilt Enemies Data

**ROM regions:** Two banks — part 1 at `0xD0075` (up to prebuilt ID `0x024F`), part 2 at `0x288056` (remainder). Full name list at `0x22061C`.

## Usage

All prebuilt enemies in the game use **prebuilt IDs** (not species IDs) when referenced from:
- Random encounters in story worlds
- Boss battles
- Tournament monsters
- Wandering masters' teams
- Gift/event monsters (e.g., Slash the Slime, TinyMedal collector eggs)
- Summon spirits (Tatsu, Diago, Samsi, Bazoo)

## Functions

| Address | Description |
|---|---|
| `34:4001` | Sets `DE = CFEC`, calls `34:4040` — bank switch + delegate |
| `34:4008` | Copy `length` bytes at `offset` from structure for ID to destination. Expects `(CFE6:7)` = ID, `(FFC6)` = length, `C` = offset, `DE` = destination |
| `34:4040` | Copy entire structure for ID to destination. Expects `(CFE6:7)` = ID, `DE` = destination |

Bank 34 (`0xD0000`) functions compare the incoming ID with a threshold to decide if they are responsible or delegate to bank A2 (`0x288000`). The bank A2 functions subtract a base value to transform the incoming ID to a local index.

## Structure (23 bytes per entry)

| Bytes | Size | Field |
|---|---|---|
| 0–1 | 2 | Species ID (LE u16) |
| 2 | 1 | Skill 1 |
| 3 | 1 | Skill 2 |
| 4 | 1 | Skill 3 |
| 5 | 1 | Skill 4 |
| 6–7 | 2 | Exp yield (LE u16) |
| 8 | 1 | Join value (0=always, 7=never) |
| 9 | 1 | Level |
| 10–11 | 2 | HP (LE u16) |
| 12–13 | 2 | MP (LE u16) |
| 14–15 | 2 | Attack (LE u16) |
| 16–17 | 2 | Defense (LE u16) |
| 18–19 | 2 | Agility (LE u16) |
| 20–21 | 2 | Intelligence (LE u16) |
| 22 | 1 | Charge aptitude |
| 23 | 1 | Defense aptitude |
| 24 | 1 | Motivation |
| 25 | 1 | Mixed aptitude |

**Note:** Personality is determined by a combination of the aptitude values, not just the species ID. High values across all three strategy aptitudes = "Hot-Blooded". Low values across the board = "Lazy."

## Expanding the table

The free space directly after entry `0x024F` in part 1 cannot be used without patching the bank-switching threshold bytes at `0xD0013`, `0xD004B`, `0x28800D`, and `0x288038` (change from `0x50` to `0x71`). Side effects: all prebuilt IDs `0x0250+` would need to be remapped.
