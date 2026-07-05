# Arena Random Rewards Data

**Offset:** `0x335D2`

## Layout

| Offset | Content |
|---|---|
| `0x335D2` | Pointers to chance tables |
| `0x335DE` | Chance table (C-Class) |
| `0x335E7` | Chance table (B-Class) |
| `0x335F0` | Chance table (A-Class) |
| `0x335F9` | Chance table (S-Class) |
| `0x33602` | Pointers to reward tables |
| `0x3360E` | Rewards (C-Class) |
| `0x33616` | Rewards (B-Class) |
| `0x3361E` | Rewards (A-Class) |
| `0x33626` | Rewards (S-Class) |

## Chance Tables

Each class has 8 chance values (1 byte each), terminated by `0xFF`. Values are compared against a random number in range `0x00–0x63` (0–99). If the chance value is higher than the random value, the corresponding reward is given.

**Percentage calculation:** The actual probability for entry N is the difference between its value and the preceding value. Add 1 to the first entry's percentage, subtract 1 from the last.

### Example: S-Class (0x335F9)

| Value | Decimal | Actual chance |
|---|---|---|
| `0x0A` | 10 | 11% (10−0 +1) |
| `0x15` | 21 | 11% (21−10) |
| `0x20` | 32 | 11% (32−21) |
| `0x2B` | 43 | 11% (43−32) |
| `0x36` | 54 | 11% (54−43) |
| `0x41` | 65 | 11% (65−54) |
| `0x50` | 80 | 15% (80−65) |
| `0x64` | 100 | 19% (100−80 −1) |

## Reward Tables

One byte per entry, representing item IDs. Special values:
- `0xFD` = randomly selected accessory
- `0xFE` = Magic Key

### S-Class rewards (0x33626)

| Chance | Item ID | Item name |
|---|---|---|
| 11% | `0x17` | FriendStaff |
| 11% | `0x2C` | TinyMedal |
| 11% | `0x0D` | AtkSeed |
| 11% | `0x0E` | DefSeed |
| 11% | `0x15` | SmartBook |
| 11% | `0xFD` | Random accessory |
| 15% | `0x1E` | MeteOrb |
| 19% | `0xFE` | Magic Key |
