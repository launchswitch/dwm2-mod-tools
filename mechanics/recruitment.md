# Recruitment (Monster Taming)

Two separate recruit rates exist for each monster:
1. **Unique/prebuilt join rate** — for the specific instance you're trying to recruit
2. **Species join rate** — for the species itself (used if you don't own that species yet)

Both are on a 0–7 scale: 0 = guaranteed success, 7 = forced failure (normally).

## Meat/Taming Modifier

Starts at 10 (one jerky's value). Capped at 1800.

| Meat | Taming Value |
|---|---|
| BeefJerky | 10 |
| PorkChop | 30 |
| Rib | 100 |
| Sirloin | 999 (255 in data, likely hardcoded) |
| BadMeat | 5 + poison |
| MeteOrb | 255 (guarantees join, taming value ignored) |

## Species Not Owned

Species join rate is checked first. Rate 7 = fail. Then a random 0–199 is compared against a threshold based on the species join rate:

| Rate | Threshold | Actual chance |
|---|---|---|
| 0 | 100 | 50% |
| 1 | 50 | 25% |
| 2 | 24 | 12% |
| 3 | 10 | 5% |
| 4 | 6 | 3% |
| 5 | 2 | 1% |
| 6 | 1 | 0.5% |
| 7 | 0 | 0% |

If that check passes, recruitment succeeds immediately (no meat needed). Otherwise, the unique/prebuilt join rate modifies the taming value:

| Unique rate | Modifier | Base success |
|---|---|---|
| 0 | Success | — |
| 1 | ×5 | 41% |
| 2 | ×2 | 11% |
| 3 | ×1 | 1% |
| 4 | ÷2 | needs meat |
| 5 | ÷5 | needs meat |
| 6 | ÷16 | needs meat |
| 7 | Fail | — |

## Species Already Owned

Skip the species-rate check. Unique/prebuilt join rate modifiers:

| Unique rate | Modifier | Base success |
|---|---|---|
| 0 | Success | — |
| 1 | ×1 | 1% |
| 2 | ÷4 | needs meat |
| 3 | ÷8 | needs meat |
| 4 | ÷8 | needs meat |
| 5 | ÷8 | needs meat |
| 6 | ÷20 | needs meat |
| 7 | Fail | — |

## Final Calculations (shared)

1. Random 10–100 is generated and subtracted from the taming modifier. If negative, fail.
2. Another random 1–100 is generated. Success if < 91 (90% chance). So even after passing step 1, there's a 10% fail chance unless MeteOrb was used.

**Conclusion:** You can never guarantee recruitment without MeteOrb for non-zero-rate monsters.
