# Random Encounter Data

**Start offset:** `0x29773`

## Structure

Each area has two parts:
1. A list of 2-byte pointers, one per screen of the map
2. A list of encounter structures

### Encounter Structure (13 bytes)

| Bytes | Size | Field |
|---|---|---|
| 0 | 1 | Maximum number of enemies |
| 1 | 1 | Max chance value |
| 2–6 | 5 | Chance thresholds (LE u16 × ? — actually compared as single bytes) |
| 7+ | variable | Prebuilt enemy IDs (LE u16, up to 5 entries = 10 bytes) |

**Mechanics:** A random value is computed in range `0..max_chance`. It's compared against each threshold in order. If the random value is below a threshold, the corresponding prebuilt enemy appears.

### Example: Oasis World (0x29773)

First screen pointer → `0x297F3`:
```
01 07 03 07 00 00 00 02 00 03 00
 ^^ ^^ = max_chance=7, thresholds=[3, 7]
         rand < 3 → Spotslime (prebuilt ID 0x0002), chance 3/7
         rand >= 3 and < 7 → CactiBall (prebuilt ID 0x0003), chance 4/7
```

Note: last threshold equals max_chance, otherwise the game reads into the ID values.

## Exceptions

Randomly generated maps (LastLord, YlwPlain, RedLake, etc.) do NOT use this structure — encounters are generated at runtime instead.

## Area Map

| Offset | Area |
|---|---|
| `0x29773` | Oasis World |
| `0x29856` | Well |
| `0x2989B` | Pirate World |
| `0x29A4C` | HoodSquid's Cave |
| `0x29A8A` | Harmirror Cave 1F |
| `0x29AB7` | Harmirror Cave 2F |
| `0x29ADE` | Harmirror Cave 3F |
| `0x29AFF` | Moonrock Tower 1F |
| `0x29B14` | Moonrock Tower 2F |
| `0x29B29` | Ghost Ship 1F |
| `0x29B45` | Ghost Ship 2F |
| `0x29B58` | Ghost Ship Cabin |
| `0x29B6B` | Ice World |
| `0x29D5D` | Gold Mine |
| `0x29D9B` | Spooky Forest |
| `0x29DCA` | Sleep Herb Mountain |
| `0x29DE7` | Ice Tower 1F |
| `0x29E0C` | Ice Tower 2F |
| `0x29E2B` | Sky World |
| `0x2A028` | Fhunt Tower 1F |
| `0x2A03D` | Fhunt Tower 2F |
| `0x2A052` | Fhunt Tower 3F |
| `0x2A06B` | Fhunt Tower 4F |
| `0x2A084` | Heaven Helm Cave 1F |
| `0x2A097` | Heaven Helm Cave 2F |
| `0x2A0BA` | Heaven Helm Cave 3F |
| `0x2A0DD` | Heaven Armor Tower 1F |
| `0x2A0F2` | Heaven Armor Tower 2F |
| `0x2A107` | Heaven Armor Tower 3F |
| `0x2A120` | Heaven Armor Tower 4F |
| `0x2A139` | Heaven Sword Castle 1F |
| `0x2A160` | Heaven Sword Castle 2F |
| `0x2A181` | Heaven Sword Castle 3F |
| `0x2A1A2` | Heaven Sword Castle 4F |
| `0x2A1BD` | Limbo World |
| `0x2A1FB` | Darck's Castle |
| `0x2A220` | Elf World |
| `0x2A2AB` | AgDevil's Lair |
| `0x2A2D2` | Lonely World |
| `0x2A2EB` | Basement |
| `0x2A300` | Traveler World |
| `0x2A382` | Dark Merchant's Tower 1F |
| `0x2A393` | Dark Merchant's Tower 2F |
| `0x2A3AA` | Dark Merchant's Tower 3F |
| `0x2A3BF` | Dark Merchant's Tower 4F |
