#!/usr/bin/env python3
"""
explore_wram.py — Interactive WRAM explorer for DWM2 RAM mapping.

Advances the game past the title screen, lets it run to a state with
party data, then probes WRAM for monster-related structures.

Usage:
    python tools/explore_wram.py build/cobi_final.gbc
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from lib_pyboy import make_pyboy, snapshot_wram, tick


def press_start(pb):
    """Press and release Start button."""
    pb.button_press('start')
    pb.tick(3, render=False)
    pb.button_release('start')


def dump_region(pb, start: int, end: int, label: str = ""):
    """Hex dump a memory region."""
    buf = bytes(pb.memory[start:end])
    lines = [f"\n# {label} 0x{start:04X}-0x{end:04X}, {len(buf)} bytes"]
    width = 16
    for i in range(0, len(buf), width):
        chunk = buf[i:i+width]
        hexpart = " ".join(f"{b:02X}" for b in chunk)
        asciipart = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"0x{start+i:04X}  {hexpart:<{width*3}}  |{asciipart}|")
    return "\n".join(lines)


def find_nonzero_regions(pb, start: int, end: int, min_run: int = 4) -> list[tuple[int, int]]:
    """Find contiguous non-zero regions in a memory range."""
    wram = bytes(pb.memory[start:end])
    regions = []
    run_start = None
    for i, b in enumerate(wram):
        if b != 0:
            if run_start is None:
                run_start = start + i
        else:
            if run_start is not None and (start + i) - run_start >= min_run:
                regions.append((run_start, start + i))
            run_start = None
    # Handle run at end
    if run_start is not None and (end) - run_start >= min_run:
        regions.append((run_start, end))
    return regions


def search_le16(pb, value: int, start: int = 0xC000, end: int = 0xE000) -> list[int]:
    """Search for a little-endian 16-bit value in WRAM."""
    lo = value & 0xFF
    hi = (value >> 8) & 0xFF
    wram = bytes(pb.memory[start:end])
    matches = []
    for i in range(len(wram) - 1):
        if wram[i] == lo and wram[i + 1] == hi:
            matches.append(start + i)
    return matches


def main():
    rom_path = Path("build/cobi_final.gbc")
    if not rom_path.exists():
        print(f"ROM not found: {rom_path}")
        return

    pb = make_pyboy(rom_path)
    try:
        # Advance past title screen
        print("Booting... pressing Start to skip title screen")
        tick(pb, 60, render=False)  # Wait for title screen
        press_start(pb)
        
        # Let the game initialize (loading screen, etc.)
        print("Waiting for game to load...")
        tick(pb, 60 * 20, render=False)  # 20 seconds of gameplay
        
        print(f"After 20s: PC=0x{pb.register_file.PC:04X}, A=0x{pb.register_file.A:02X}")
        
        # Find non-zero regions in WRAM bank 0
        print("\n=== Non-zero WRAM regions (bank 0) ===")
        regions = find_nonzero_regions(pb, 0xC000, 0xD000)
        for start, end in regions:
            size = end - start
            print(f"  0x{start:04X}-0x{end:04X} ({size} bytes)")
        
        # Dump the first interesting region
        if regions:
            print(dump_region(pb, 0xC000, 0xC100, "WRAM Bank 0 (first 256 bytes)"))
        
        # Search for common species IDs
        # Species 1 = Slime (typically the first monster you get)
        print("\n=== Searching for species IDs ===")
        for species in [1, 2, 3]:  # Slime, etc.
            matches = search_le16(pb, species, 0xC000, 0xE000)
            if matches:
                print(f"  Species 0x{species:04X}: found at {len(matches)} locations")
                for addr in matches[:5]:
                    print(f"    0x{addr:04X}")
            else:
                print(f"  Species 0x{species:04X}: not found")
        
        # Also search in bank 1
        print("\n=== Searching WRAM bank 1 ===")
        pb.memory[0xFF70] = 1  # Switch to bank 1
        regions1 = find_nonzero_regions(pb, 0xD000, 0xE000)
        for start, end in regions1[:20]:
            size = end - start
            print(f"  0x{start:04X}-0x{end:04X} ({size} bytes)")
        
        # Save a snapshot for later diffing
        wram = snapshot_wram(pb, banks=[0])
        snap = {
            "label": "after_20s_gameplay",
            "timestamp": time.time(),
            "pc": pb.register_file.PC,
            "a": pb.register_file.A,
            "wram": {str(b): w.hex() for b, w in wram.items()},
        }
        Path("snapshots").mkdir(exist_ok=True)
        with open("snapshots/after_20s.json", 'w') as f:
            json.dump(snap, f, indent=2)
        print(f"\nSnapshot saved to snapshots/after_20s.json")
        
    finally:
        pb.stop()


if __name__ == "__main__":
    main()
