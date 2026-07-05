# Strings

Strings are organized as an array of lists. Each list is a category (family names, species names, skill names, etc.).

## String Categories (Bank 0x08)

Main array pointers at `0x20032–0x20043`.

| Offset | Category |
|---|---|
| 0x20044 | Unknown |
| 0x20242 | Family names |
| 0x20258 | Species names (core ID high byte = 0x00) |
| 0x20458 | Species names (core ID high byte = 0x01) |
| 0x20558 | Skill names |
| 0x20716 | Item names |
| 0x207F6 | Unknown |
| 0x208D6 | Personality names |
| 0x2090C | Unknown |

String data regions:

| First Byte | Last Byte | Content |
|---|---|---|
| 0x213B5 | — | Family name strings |
| 0x213F8 | — | Species name strings (00) |
| 0x21B36 | — | Species name strings (01) |
| 0x21EF9 | — | Skill name strings |
| 0x224E3 | — | Item name strings |
| 0x227EF | — | Item descriptions |
| 0x231F6 | 0x232B9 | Personality names |
| 0x232BA | 0x233E8 | Item use text |

## Bank 0x95

Additional string categories (not yet fully mapped).

## String Function

**`getString` at `0:2E81–0:2E97`:**
- Expects: `H` = index in first list, `L` = index in second list, `DE` = destination RAM address
- Calls `8:4016`, which checks if index >= 9 (bank 0x95) or < 9 (bank 0x08)

**Character encoding:** A–Z encoded as `0x10–0x36`. Digits and other characters have their own codes. Font tiles are in bank 19 at `0x7C000`.
