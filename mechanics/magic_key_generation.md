# Magic Key Generation

**Offsets:** `0x182969` (prefix chances), `0x182A09` (suffix chances)

## Mechanics

- Level of the first monster on your team is used: `level // 10` determines which column of the probability table applies.
- If you already have a key with the same suffix, a new key is regenerated up to 20 times before giving up. Full duplicates (prefix + suffix) are never allowed.
- Prefixes/suffixes are compared in order against a random number `0x00–0x63`. If the assigned value is higher than the random number, it continues; otherwise that prefix/suffix is selected.
- Values must be ascending, and the last entry must be `0x64` for proper operation.

## Probability Calculation

The actual chance = difference between a value and the preceding value. First entry gets +1%, last entry gets −1%.

Example: `0x14, 0x28, 0x37` → 21% (20−0+1), 20% (40−20), 15% (55−40)

## Prefix Table (0x182969)

15 prefixes × 10 level columns (Lvl÷10, floored: 1, 10, 20, ..., 90). Values are percentages.

| Prefix | Lvl 1 | Lvl 10 | Lvl 20 | Lvl 30 | Lvl 40 | Lvl 50 | Lvl 60 | Lvl 70 | Lvl 80 | Lvl 90 |
|---|---|---|---|---|---|---|---|---|---|---|
| Ylw | 21 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Plain | 20 | 15 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Green | 15 | 15 | 15 | 16 | 6 | 4 | 4 | 0 | 0 | 0 |
| Blue | 15 | 15 | 15 | 15 | 10 | 5 | 5 | 3 | 0 | 0 |
| First | 10 | 15 | 15 | 15 | 10 | 10 | 10 | 3 | 4 | 0 |
| Red | 10 | 10 | 15 | 15 | 15 | 15 | 10 | 10 | 5 | 6 |
| White | 10 | 5 | 10 | 15 | 15 | 15 | 10 | 10 | 5 | 5 |
| Quiet | 4 | 5 | 10 | 10 | 15 | 20 | 15 | 15 | 5 | 5 |
| Black | 0 | 4 | 5 | 5 | 10 | 10 | 15 | 15 | 15 | 10 |
| Gaudy | 0 | 0 | 4 | 5 | 10 | 10 | 15 | 15 | 15 | 10 |
| Silvr | 0 | 0 | 0 | 4 | 5 | 5 | 15 | 10 | 15 | 10 |
| Dream | 0 | 0 | 0 | 0 | 4 | 5 | 5 | 10 | 10 | 10 |
| Misty | 0 | 0 | 0 | 0 | 0 | 1 | 5 | 5 | 10 | 15 |
| Secrt | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 3 | 10 | 15 |
| Shiny | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 5 | 10 |
| Last | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 4 |

## Suffix Table (0x182A09)

39 suffixes × 5 level columns (Lvl÷10, floored: 1, 30, 50, 80, 90). Values are percentages.

| Suffix | Lvl 1 | Lvl 30 | Lvl 50 | Lvl 80 | Lvl 90 |
|---|---|---|---|---|---|
| Slime | 2 | 2 | 7 | 7 | 7 |
| Draco | 0 | 1 | 6 | 6 | 6 |
| Beast | 1 | 1 | 6 | 6 | 6 |
| Bird | 1 | 1 | 6 | 6 | 5 |
| Tree | 1 | 1 | 6 | 6 | 5 |
| Bug | 1 | 1 | 5 | 5 | 5 |
| Devil | 0 | 1 | 5 | 5 | 5 |
| Death | 0 | 1 | 5 | 5 | 5 |
| Thing | 1 | 1 | 5 | 5 | 5 |
| Water | 1 | 1 | 5 | 5 | 5 |
| Lord | 0 | 0 | 0 | 3 | 5 |
| Cave | 2 | 2 | 1 | 1 | 1 |
| Isle | 3 | 2 | 1 | 0 | 0 |
| Torch | 3 | 2 | 1 | 1 | 1 |
| Gardn | 3 | 2 | 1 | 1 | 1 |
| Pit | 0 | 2 | 1 | 2 | 2 |
| Bsmt | 0 | 2 | 1 | 2 | 1 |
| Jail | 0 | 2 | 1 | 1 | 1 |
| Magma | 3 | 2 | 1 | 0 | 0 |
| Sea | 3 | 2 | 1 | 0 | 0 |
| Field | 3 | 2 | 1 | 0 | 0 |
| Tower | 3 | 2 | 1 | 0 | 0 |
| Mine | 3 | 2 | 1 | 1 | 1 |
| Hill | 3 | 2 | 1 | 0 | 0 |
| Cstle | 0 | 2 | 1 | 3 | 3 |
| Mound | 2 | 2 | 1 | 1 | 1 |
| Desrt | 3 | 2 | 1 | 0 | 0 |
| Lake | 3 | 2 | 1 | 0 | 0 |
| Jungl | 3 | 2 | 1 | 1 | 1 |
| Haven | 0 | 2 | 1 | 3 | 3 |
| Grass | 3 | 2 | 1 | 0 | 0 |
| Forst | 3 | 2 | 1 | 0 | 0 |
| Grave | 0 | 2 | 1 | 2 | 2 |
| Crag | 3 | 2 | 1 | 0 | 0 |
| Shore | 3 | 2 | 1 | 1 | 1 |
| Log | 3 | 2 | 1 | 1 | 1 |
| Sky | 3 | 2 | 1 | 1 | 1 |
| Mtn | 3 | 2 | 1 | 0 | 0 |
| View | 0 | 2 | 1 | 1 | 1 |
| Cliff | 3 | 2 | 1 | 1 | 1 |
| Islet | 3 | 2 | 1 | 1 | 1 |
| Land | 3 | 2 | 1 | 0 | 0 |
| Grove | 3 | 2 | 1 | 1 | 1 |
| Swamp | 3 | 2 | 1 | 0 | 0 |
| Manor | 0 | 2 | 1 | 1 | 1 |
| Depth | 0 | 2 | 1 | 2 | 2 |
| Hole | 0 | 2 | 1 | 1 | 1 |
| Tomb | 2 | 2 | 1 | 2 | 2 |
| Soil | 2 | 2 | 1 | 1 | 1 |
| Pond | 3 | 2 | 1 | 0 | 0 |
| Hell | 0 | 2 | 1 | 3 | 3 |
| Moon | 2 | 2 | 1 | 2 | 2 |
| Ocean | 2 | 2 | 1 | 2 | 2 |
| Gulch | 3 | 2 | 1 | 0 | 0 |
| River | 2 | 2 | 1 | 0 | 0 |
| Star | 0 | 1 | 0 | 1 | 1 |
