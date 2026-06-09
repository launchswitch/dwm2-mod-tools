#!/usr/bin/env python3
"""
map_party_struct.py — Map DWM2 party monster struct layout via state diffing.

Strategy: Take WRAM snapshots at different game states and diff to find
which bytes correspond to which monster fields (HP, MP, stats, level).

Usage:
    python tools/map_party_struct.py build/cobi_final.gbc
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from lib_pyboy import make_pyboy, snapshot_wram


def boot_and_navigate(pb, new_game=True):
    """Boot game and navigate to main gameplay state."""
    # Press Start
    pb.button_press('start')
    pb.tick(30, render=False)
    pb.button_release('start')
    pb.tick(5 * 60, render=False)

    if new_game:
        # Press A for New Game (first option)
        pb.button_press('a')
        pb.tick(10, render=False)
        pb.button_release('a')
        # Wait for opening
        pb.tick(30 * 60, render=False)
    else:
        # Press Down + A for Continue
        pb.button_press('down')
        pb.tick(5, render=False)
        pb.button_release('down')
        pb.button_press('a')
        pb.tick(10, render=False)
        pb.button_release('a')
        pb.tick(15 * 60, render=False)

    # Move around a bit
    for _ in range(5):
        pb.button_press('right')
        pb.tick(5, render=False)
        pb.button_release('right')
        pb.tick(10, render=False)


def dump_all_wram(pb):
    """Dump all accessible WRAM banks."""
    # Bank 0 is always accessible at 0xC000-0xD000
    banks = {0: bytes(pb.memory[0xC000:0xD000])}

    # Banks 1-7 via bank switch
    for b in range(1, 8):
        pb.memory[0xFF70] = b
        banks[b] = bytes(pb.memory[0xD000:0xE000])

    return banks


def diff_bytes(a, b, label_a="A", label_b="B"):
    """Diff two byte arrays, return list of (offset, val_a, val_b)."""
    diffs = []
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            diffs.append((i, a[i], b[i]))
    return diffs


def find_species_entries(wram_bank, species_range=range(1, 200)):
    """Find all species ID (LE u16) occurrences in a WRAM bank."""
    entries = []
    for sp in species_range:
        lo = sp & 0xFF
        hi = (sp >> 8) & 0xFF
        for i in range(len(wram_bank) - 1):
            if wram_bank[i] == lo and wram_bank[i + 1] == hi:
                # Check surrounding bytes for level-like value (5-99)
                lvl = wram_bank[i + 2] if i + 2 < len(wram_bank) else 0
                entries.append({
                    'species': sp,
                    'offset': i,
                    'level_candidate': lvl,
                    'context_before': list(wram_bank[max(0, i-4):i]),
                    'context_after': list(wram_bank[i+3:min(len(wram_bank), i+15)]),
                })
    return entries


def main():
    rom_path = Path("build/cobi_final.gbc")
    if not rom_path.exists():
        print(f"ROM not found: {rom_path}")
        return

    pb = make_pyboy(rom_path)
    try:
        # === State A: After boot, before menu ===
        boot_and_navigate(pb, new_game=True)

        # Open party menu
        pb.button_press('start')
        pb.tick(10, render=False)
        pb.button_release('start')
        pb.tick(5 * 60, render=False)

        print("=== State A: Party menu open ===")
        print(f"PC=0x{pb.register_file.PC:04X}")

        wram_a = dump_all_wram(pb)

        # Find species entries in bank 1
        entries_a = find_species_entries(wram_a[1])
        print(f"\nSpecies entries in WRAM Bank 1 ({len(entries_a)} found):")
        for e in entries_a:
            if 5 <= e['level_candidate'] <= 99:
                print(f"  Sp 0x{e['species']:04X} @ offset 0x{e['offset']:04X}, "
                      f"Lv?={e['level_candidate']}, ctx={e['context_after'][:8]}")

        # === State B: Navigate to different menu screen ===
        pb.button_press('down')
        pb.tick(5, render=False)
        pb.button_release('down')
        pb.button_press('a')
        pb.tick(10, render=False)
        pb.button_release('a')
        pb.tick(5 * 60, render=False)

        print("\n=== State B: After menu navigation ===")
        print(f"PC=0x{pb.register_file.PC:04X}")

        wram_b = dump_all_wram(pb)

        # Diff bank 1
        diffs_b1 = diff_bytes(wram_a[1], wram_b[1])
        print(f"\nWRAM Bank 1 diffs: {len(diffs_b1)} bytes changed")
        for offset, va, vb in diffs_b1[:30]:
            addr = 0xD000 + offset
            print(f"  0x{addr:04X}: 0x{va:02X} -> 0x{vb:02X}")

        # === State C: Navigate to monster detail screen ===
        pb.button_press('a')
        pb.tick(10, render=False)
        pb.button_release('a')
        pb.tick(5 * 60, render=False)

        print("\n=== State C: Monster detail ===")
        print(f"PC=0x{pb.register_file.PC:04X}")

        wram_c = dump_all_wram(pb)

        # Diff bank 1: A vs C
        diffs_c1 = diff_bytes(wram_a[1], wram_c[1])
        print(f"\nWRAM Bank 1 diffs (A vs C): {len(diffs_c1)} bytes changed")
        for offset, va, vb in diffs_c1[:30]:
            addr = 0xD000 + offset
            print(f"  0x{addr:04X}: 0x{va:02X} -> 0x{vb:02X}")

        # === State D: Move to next monster in party ===
        for _ in range(3):
            pb.button_press('down')
            pb.tick(5, render=False)
            pb.button_release('down')
        pb.tick(3 * 60, render=False)

        print("\n=== State D: After scrolling party list ===")
        print(f"PC=0x{pb.register_file.PC:04X}")

        wram_d = dump_all_wram(pb)

        # Diff bank 1: C vs D
        diffs_d1 = diff_bytes(wram_c[1], wram_d[1])
        print(f"\nWRAM Bank 1 diffs (C vs D): {len(diffs_d1)} bytes changed")
        for offset, va, vb in diffs_d1[:30]:
            addr = 0xD000 + offset
            print(f"  0x{addr:04X}: 0x{va:02X} -> 0x{vb:02X}")

        # === Detailed analysis: find the active monster pointer ===
        # When scrolling through party, a pointer/index should change
        if diffs_d1:
            print("\n=== Analysis: Active monster pointer candidates ===")
            # Look for bytes that changed consistently when scrolling
            for offset, va, vb in diffs_d1:
                if abs(vb - va) <= 50:  # Likely an index or small counter
                    addr = 0xD000 + offset
                    print(f"  0x{addr:04X}: {va} -> {vb} (delta={vb-va}, likely index/counter)")

        # === Save snapshots for later analysis ===
        Path("snapshots").mkdir(exist_ok=True)

        for name, wram in [("state_a_party", wram_a),
                           ("state_b_menu", wram_b),
                           ("state_c_detail", wram_c),
                           ("state_d_scrolled", wram_d)]:
            snap = {
                "label": name,
                "timestamp": time.time(),
                "pc": pb.register_file.PC,
                "wram": {},
            }
            for bank, data in wram.items():
                snap["wram"][str(bank)] = data.hex()
            with open(f"snapshots/{name}.json", 'w') as f:
                json.dump(snap, f, indent=2)
            print(f"\nSaved snapshot: snapshots/{name}.json")

    finally:
        pb.stop()


if __name__ == "__main__":
    main()
