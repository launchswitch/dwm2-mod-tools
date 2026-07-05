# Skill Requirements Data

**Offset:** `0x6900A`, ordered by skill ID.

## Structure (15 bytes per skill)

| Bytes | Size | Field |
|---|---|---|
| 0 | 1 | Required level |
| 1–2 | 2 | Required HP (LE u16) |
| 3–4 | 2 | Required MP (LE u16) |
| 5–6 | 2 | Required Attack (LE u16) |
| 7–8 | 2 | Required Defense (LE u16) |
| 9–10 | 2 | Required Agility (LE u16) |
| 11–12 | 2 | Required Intelligence (LE u16) |
| 13 | 1 | Prerequisite skill ID |
| 14 | 1 | Combine skill 1 |
| 15 | 1 | Combine skill 2 |
| 16 | 1 | Combine skill 3 |
| 17 | 1 | Combine skill 4 |

## Mechanics

- **Prerequisite skill:** The skill that will be auto-replaced with the new skill once requirements are met. E.g., `BlazeMost` has `BlazeMore` as prerequisite.
- **Combine skills:** A list of up to 4 skills that, if a monster knows all of them, will allow it to learn the skill automatically on level-up. The game shows a message like "derived <skill> from the skills it already knew."
- **MegaMagic exception:** All 5 slots (prerequisite + 4 combine) are used as combine skills; the prerequisite slot is repurposed as a 5th combine skill.
