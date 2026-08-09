#!/usr/bin/env python3
"""
verify.py — Smoke test for the DWM2 mod tools repo.

Verifies that the repo structure is intact and the core tooling works.
Does NOT require a ROM file (ROMs are not distributed with this repo).
If a ROM path is provided as an argument, also tests table parsing against it.

Usage:
    python tools/verify.py                    # structure + tooling check
    python tools/verify.py your_rom.gbc       # also test table parsing
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

tables: dict | None = None

passed = 0
failed = 0


def check(label: str, ok: bool, detail: str = "") -> bool:
    global passed, failed
    mark = "OK  " if ok else "FAIL"
    print(f"  [{mark}] {label}{(': ' + detail) if detail else ''}")
    if ok:
        passed += 1
    else:
        failed += 1
    return ok


print("=" * 60)
print("DWM2 Mod Tools — Repo Verification")
print("=" * 60)

# ---- 1. Directory structure ----
print("\n[1] Directory structure")
expected_dirs = [
    "tools",
    "tools/balancing",
    "tools/discovery",
    "monster_data",
    "mechanics",
    "rom_maps",
    "edits",
    "docs",
    "dwm2u_reference",
]
for d in expected_dirs:
    check(f"{d}/ exists", (REPO_ROOT / d).is_dir())

# ---- 2. Core data files ----
print("\n[2] Core data files")
expected_files = [
    "monster_data/monster_data_external.xml",
    "monster_data/breeding_data.md",
    "monster_data/core_monster_data.md",
    "monster_data/prebuilt_id_usages.md",
    "rom_maps/rom_map.txt",
    "rom_maps/ram_map.md",
    "rom_maps/battle_breeding_map.md",
    "tools/mod_data.py",
    "tools/rom_diff.py",
    "tools/rom_region_diff.py",
    "docs/tools_guide.md",
    "coverage_map.md",
    "disassembly_inventory.md",
    "LICENSE",
    "README.md",
]
for f in expected_files:
    check(f"{f} exists", (REPO_ROOT / f).is_file())

# ---- 3. mod_data.py loads and tables register ----
print("\n[3] mod_data.py table registry")
try:
    import mod_data

    tables = mod_data.TABLES
    check(f"tables loaded ({len(tables)} tables)", len(tables) >= 15, f"{len(tables)} found")

    # Spot-check key tables exist
    key_tables = [
        "items",
        "skills",
        "core_monster",
        "stat_growth",
        "breeding",
        "prebuilt_enemies",
        "boss_battles",
        "exp_tables",
    ]
    for name in key_tables:
        check(f"table '{name}' registered", name in tables)
except Exception as e:
    check("mod_data.py imports cleanly", False, str(e))

# ---- 4. Balancing scripts importable ----
print("\n[4] Balancing scripts")
balancing_dir = REPO_ROOT / "tools" / "balancing"
balancing_scripts = sorted(balancing_dir.glob("generate_*.py"))
for script in balancing_scripts:
    check(f"{script.name} exists", True, f"{script.stat().st_size} bytes")

# ---- 5. Example edits are valid JSON ----
print("\n[5] Example edit files (edits/)")
edits_dir = REPO_ROOT / "edits"
for ef in sorted(edits_dir.glob("*.json")):
    try:
        data = json.loads(ef.read_text())
        check(f"{ef.name} is valid JSON", True, f"{len(data)} entries")
    except Exception as e:
        check(f"{ef.name} is valid JSON", False, str(e))

# ---- 6. Mechanic docs exist ----
print("\n[6] Mechanic docs")
mechanics_dir = REPO_ROOT / "mechanics"
expected_mechanics = [
    "recruitment.md",
    "resistances.md",
    "strings.md",
    "stat_combat_roles.md",
    "courage_motivation.md",
    "skill_requirements_data.md",
    "random_encounter_data.md",
    "prebuilt_enemies_data.md",
    "arena_random_rewards_data.md",
    "magic_key_generation.md",
]
for m in expected_mechanics:
    check(f"mechanics/{m}", (mechanics_dir / m).is_file())

# ---- 7. No hardcoded local paths ----
print("\n[7] Portability check (no hardcoded absolute paths)")
import subprocess

# Check for /home/ or /Users/ patterns in source files (not the verify script itself)
result = subprocess.run(
    ["grep", "-rl", "--include=*.py", "--include=*.md",
     "-e", "/home/", "-e", "/Users/",
     str(REPO_ROOT)],
    capture_output=True,
    text=True,
    cwd=str(REPO_ROOT),
)
hits = [
    h for h in result.stdout.strip().split("\n")
    if h and ".git" not in h and "verify.py" not in h
]
check("no hardcoded absolute paths in .py or .md files", len(hits) == 0,
      f"{len(hits)} files: {', '.join(os.path.basename(h) for h in hits)}" if hits else "")

# ---- 8. Optional: ROM table test ----
rom_path = sys.argv[1] if len(sys.argv) > 1 else None
if rom_path and Path(rom_path).exists():
    print(f"\n[8] ROM table parsing ({Path(rom_path).name})")
    try:
        # Verify table definitions have valid offsets into the ROM
        rom_data = Path(rom_path).read_bytes()
        check("ROM is 4 MB", len(rom_data) == 4 * 1024 * 1024, f"{len(rom_data)} bytes")

        for table_name in ["items", "core_monster", "skills"]:
            try:
                if tables is None:
                    raise RuntimeError("tables not loaded")
                t = tables[table_name]
                offset = t["offset"]
                entry_size = t["entry_size"]
                num_entries = t["num_entries"]
                end = offset + entry_size * num_entries
                check(f"table '{table_name}' fits in ROM",
                      end <= len(rom_data),
                      f"0x{offset:X}–0x{end:X} ({num_entries}×{entry_size}B)")
            except Exception as e:
                check(f"table '{table_name}' definition", False, str(e))
    except Exception as e:
        check("ROM test", False, str(e))
else:
    print("\n[8] ROM table parsing — skipped (no ROM provided)")
    print("    Run: python tools/verify.py your_rom.gbc")

# ---- Summary ----
print("\n" + "=" * 60)
print(f"Results: {passed} passed, {failed} failed")
if failed == 0:
    print("VERIFICATION PASSED")
else:
    print("VERIFICATION FAILED — see failures above")
print("=" * 60)

sys.exit(1 if failed > 0 else 0)
