# Breeding Data

**Note:** Editing breeding data is tedious because it's split across multiple pointer + list pairs.

## Important Locations

| Offset | Content |
|---|---|
| `0x3A208` | Species+Species: Mate pointers |
| `0x3A508` | Species+Species: Lists of mates |
| `0x3AE14` | Species+Species: Results pointers |
| `0x3B114` | Species+Species: Lists of results |
| `0x3B34E` | Species+Family: Mate pointers |
| `0x3B64E` | Species+Family: Lists of mates |
| `0x3B74F` | Species+Family: Results pointers |
| `0x3BA4F` | Species+Family: Lists of results |
| `0x3BB83` | Family+Species: Mate pointers |
| `0x3BB99` | Family+Species: Lists of mates |
| `0x3BDBF` | Family+Species: Results pointers |
| `0x3BDD5` | Family+Species: Lists of results |
| `0x3BE99` | Family+Family data |

All pointers are 2-byte LE, based on address `0x34000`. Tables are ordered by species ID (or family ID for Family+ tables).

## Accessing mate data

For species ID `N`, the mate pointer is at `0x3A208 + (N × 2)`. The pointer value `P` gives the mate list at `0x34000 + P`.

### Mate list delimiters

| Bytes | Meaning |
|---|---|
| `FD FD` | End of set (one group of mates for a specific result) |
| `FB FB` | End of set; all following sets require link cable |
| `FF FF` | End of monster's mate lists |
| `04 FE 04 FC` | +5 breed marker |

### Example: Slime (species ID `0x0A`)

Pointer at `0x3A212` = `[18 65]` → address `0x3A518`. Mate list decodes as:
- `04 FE 04 FC` — Slime+5 + Slime+5 → result a
- `FD FD` — end of set
- `4A 00 53 00` — Pillowrat OR Mommonja → result b
- `FD FD` — end of set
- `0D 01` — CopyCat → result c
- `FB FB` — end of set; following sets require link cable
- `75 00` — BigRoost → result d (link cable)
- `FF FF` — end of lists

### Results

Result pointer at `0x3AE14 + (N × 2)`. For Slime: `0x3AE28` = `[1C 71]` → address `0x3B11C`. Read as many LE16 species IDs as there were mate sets.

| ID | Result | From which pairing? |
|---|---|---|
| `0x0010` | KingSlime | Slime(+5) + Slime(+5) |
| `0x0014` | TropicGel | Slime + Pillowrat/Mommonja |
| `0x0016` | HaloSlime | Slime + CopyCat |
| `0x001A` | WonderEgg | Slime + BigRoost (link cable) |

## Family+Family breeding

Different structure: pointers increment by `0x16`, followed by a table of result IDs. First entry is `FFFF` (returns base monster, e.g., Slime+Slime), then ordered by family ID.
