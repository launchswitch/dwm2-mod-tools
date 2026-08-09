# Disassembly Inventory — niyadev/dwm2_disassembly_github

**Date:** 2026-07-05
**Purpose:** Honest accounting of what the vendored DWM2 disassembly contains, so modders know what's recoverable from it vs. what needs original design. This is reference material; the canonical source-of-truth docs live in this repo (`mechanics/`, `monster_data/`, `rom_maps/`, the research findings).

**Location:** Clone the [niyadev/dwm2_disassembly_github](https://github.com/niyadev/dwm2_disassembly_github) repo locally.
**Status per its own README:** 0.0021% byte-match, dormant since 2022. A build-workbench wrapper around it verified it builds byte-identical to the clean Cobi ROM (`make build` + `make diff`).

## Coverage summary

**The disassembly is PARTIAL.** Only 5 of ~128 ROM banks have any source, and only one (Bank0) has substantial content. Combat, AI, status effects, damage calculation, and the personality/skill/item tables are NOT in the disassembled banks — they live in higher banks (skill table `0x680D4` ≈ bank `0x1A`; personality/tactic tables `0xC138C` ≈ bank `0x30`).

| Bank | Source lines | Function docs | What's there |
|------|-------------|---------------|--------------|
| **Bank0** | 2,393 | 27 | Boot, reset vectors, main event loop, memory init, the bank-dispatch switch (`FUN_0355`), wait/event helpers |
| **Bank1** | 36 | 1 | `FUN_4001` — initializes `C5F6`–`C5FF` to 0, calls `FUN_4045`, sets `C5EC=3`, jumps to `FUN_077A(1)`. Likely a scene/mode entry point. |
| **Bank2** | 31 | 1 | `FUN_42FA` — minimal |
| **Bank27** | 586 | 1 | `FUN_4001` — larger routine (likely a scene/mode bank) |
| **Bank31** | 135 | 1 | `FUN_5040` — references `C47C`/`C47F` (ROM pointer calc) |

**Total:** ~3,181 lines of source, 31 function docs, 20 documented software variables.

## What's useful for modding

### 1. The bank-dispatch switch (`FUN_0355`)

`documentation/bank0/FUN_0355.md` reveals the bank layout for mode/scene dispatch:

```
[$C5DB] == 0 → ROM bank 1   (FUN_ROM1_4001)
[$C5DB] == 1 → ROM bank 2   (FUN_ROM2_45C6)
[$C5DB] == 2 → ROM bank 3
[$C5DB] == 3 → (no-op, return)
[$C5DB] == 4 → ROM bank 49
[$C5DB] == 5 → ROM bank 7
[$C5DB] == 6 → ROM bank 36
[$C5DB] == 7 → ROM bank 160
[$C5DB] == 8 → ROM bank 242
```

This tells us which banks hold scene/mode entry points but **none of these banks (1, 2, 3, 7, 36, 49, 160, 242) are disassembled** except the stubs of 1, 2, 27, 31. The combat scene's bank is not identified here.

### 2. RAM variable roles (`documentation/variables/software/`)

20 addresses documented. Most are unknown graphics/event flags. The useful ones:

| Address | Role (per docs) | Relevance |
|---------|-----------------|-----------|
| `$C5DB` | Bank-dispatch selector (0–8) | Mode/scene switch — see above |
| `$C524` | `SkipWait?` bool | Event-loop control |
| `$C000`–`$C0A0` | Cleared via memset on init | Memory init boundary |
| `$C5F6`–`$C5FF` | Initialized to 0 by `FUN_ROM1_4001` | Unknown purpose; cleared on scene entry |

**None of these are battle-state addresses.** The battle-state RAM region (`$D8B7`–`$D964`, per `rom_maps/ram_map.md`) is documented separately in this repo from wiki sources, not from the disassembly.

### 3. Function-index pointers (where deeper work would start)

If someone wanted to chase combat routines in the disassembly, the entry points are:
- `FUN_0355`'s dispatch targets (banks 1/2/3/49/7/36/160/242) — none disassembled beyond stubs
- `FUN_077A` (called by `FUN_ROM1_4001` with arg 1) — likely the next-level dispatch
- The `rst $10` long-call targets (G4 goal: "chase the rst $10 long-call targets visible from bank 0")

None of this work has been done. Combat routines remain undisassembled.

## What's NOT in the disassembly (the gaps)

Confirmed absent (in banks not covered by the disassembly):
- **Damage formula** — how ATK/DEF/skill-power/level combine
- **Critical-hit routine** — `core_monster_data.md:61` says crit data is "stored elsewhere" but the address is unmapped in any source we have
- **Turn order / initiative / action queue** — battle-state RAM (`$D8B7`+) is wiki-documented in `rom_maps/ram_map.md` but not from disassembly
- **AI action selection** per tactic/personality
- **Status-effect tick / duration / cure** logic
- **Hit/accuracy resolution**
- **Skill execution routine** — what runs when a monster uses a skill
- **Resistance value semantics** — the byte meaning (immune/resist/normal/weak) is in code, not data, and not in any disassembled bank

For these, modders will use **original design informed by DWM2's data tables and knowledge of how the game plays.** See `coverage_map.md`.

## `notes.txt`

122 lines of raw pseudo-Pascal snippets at the disassembly root. Sample content is graphics-related (references `$C0C0`/`$C0D8`, `rVBK` = video bank register, bit-masking for tile attributes). Appears to be scratch notes on sprite/tile routines, not combat. Not spec-grade.

## How to extend this

If deeper extraction is wanted later, the path is:
1. Use the runtime discovery tools in `tools/discovery/` (`explore_wram.py`, `wram_inspector.py`) to observe what runs during a battle — this identifies the executing bank empirically without disassembling it.
2. Once the combat bank is identified, disassemble it with the same pseudo-Pascal style as the existing `documentation/` tree.
3. The highest-value target is the **damage routine** — finding it would lift combat from "original design" to "faithful port."

Until that work happens, this disassembly is **not** a usable source for combat resolution rules. It's a boot/init layer wrapping the gameplay code we can't see.
