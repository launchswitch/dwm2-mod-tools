#!/usr/bin/env python3
"""
wram_inspector.py — WRAM inspection tool for DWM2 RAM mapping.

Takes a snapshot of WRAM at the current game state, searches for known
species IDs, and diffs snapshots to identify runtime data structures.

This is the primary tool for Phase 1: mapping where DWM2 stores party
monster data, battle state, and other runtime structures in WRAM.

Usage:
    # Take a labeled snapshot of WRAM
    python tools/wram_inspector.py roms/cobi_clean.gbc --snapshot --label "title_screen" --seconds 5

    # Search WRAM for a known species ID (helps locate party array)
    python tools/wram_inspector.py roms/cobi_clean.gbc --search-species 0x0001 --seconds 30

    # Diff two snapshots to find what changed
    python tools/wram_inspector.py roms/cobi_clean.gbc --diff-snapshots snapshot_a.json snapshot_b.json

    # Dump a specific WRAM range as hex
    python tools/wram_inspector.py roms/cobi_clean.gbc --dump-range 0xC0C0-0xC200 --seconds 30

    # Watch an address over time (log changes)
    python tools/wram_inspector.py roms/cobi_clean.gbc --watch 0xC0C0 --seconds 60 --poll-interval 60
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

from lib_pyboy import make_pyboy, snapshot_wram, diff_wram, tick


def search_species_id(pb, species_id: int, region_start: int = 0xC000, region_end: int = 0xE000) -> list[int]:
    """Search WRAM for a little-endian species ID. Returns list of offsets."""
    lo = species_id & 0xFF
    hi = (species_id >> 8) & 0xFF
    wram = bytes(pb.memory[region_start:region_end])
    matches = []
    pattern = bytes([lo, hi])
    for i in range(len(wram) - 1):
        if wram[i] == lo and wram[i + 1] == hi:
            matches.append(region_start + i)
    return matches


def dump_range(pb, start: int, end: int) -> str:
    """Hex dump a memory range."""
    buf = bytes(pb.memory[start:end])
    lines = [f"# WRAM dump 0x{start:04X}-0x{end:04X}, {len(buf)} bytes\n"]
    width = 16
    for i in range(0, len(buf), width):
        chunk = buf[i:i+width]
        hexpart = " ".join(f"{b:02X}" for b in chunk)
        asciipart = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"0x{start+i:04X}  {hexpart:<{width*3}}  |{asciipart}|")
    return "\n".join(lines)


def take_snapshot(pb, label: str, banks: list[int]) -> dict:
    """Take a labeled WRAM snapshot and return as serializable dict."""
    wram = snapshot_wram(pb, banks=banks if banks else None)
    # Convert bytes to hex strings for JSON serialization
    serialized = {
        "label": label,
        "timestamp": time.time(),
        "pc": pb.register_file.PC,
        "a": pb.register_file.A,
        "wram": {str(b): w.hex() for b, w in wram.items()},
    }
    return serialized


def load_snapshot(path: Path) -> dict:
    """Load a previously saved snapshot from JSON."""
    with open(path) as f:
        return json.load(f)


def diff_snapshots(snap_a: dict, snap_b: dict) -> list[dict]:
    """Diff two snapshots and return list of changed addresses."""
    # Reconstruct bytes dicts
    wa = {int(b): bytes.fromhex(w) for b, w in snap_a.get("wram", {}).items()}
    wb = {int(b): bytes.fromhex(w) for b, w in snap_b.get("wram", {}).items()}
    raw_diffs = diff_wram(wa, wb)

    results = []
    for bank, offset, val_a, val_b in raw_diffs:
        # Compute actual address
        base = 0xC000 if bank == 0 else 0xD000
        addr = base + offset
        results.append({
            "addr": f"0x{addr:04X}",
            "bank": bank,
            "offset": offset,
            "from": f"0x{val_a:02X}",
            "to": f"0x{val_b:02X}",
        })
    return results


def watch_address(pb, addr: int, total_frames: int, poll_interval: int = 60) -> list[dict]:
    """Watch a memory address and log every change."""
    changes = []
    prev_val = pb.memory[addr]
    frame = 0

    for _ in range(total_frames // 60):
        tick(pb, 60, render=False)
        frame += 60

        for i in range(0, 60, poll_interval if poll_interval <= 60 else 60):
            tick(pb, min(poll_interval, 60 - i), render=False)
            frame += min(poll_interval, 60 - i)
            curr_val = pb.memory[addr]
            if curr_val != prev_val:
                changes.append({
                    "frame": frame,
                    "seconds": round(frame / 60, 2),
                    "addr": f"0x{addr:04X}",
                    "from": f"0x{prev_val:02X}",
                    "to": f"0x{curr_val:02X}",
                })
                prev_val = curr_val

    return changes


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("rom", help="Path to .gbc ROM")

    # Modes (mutually exclusive)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--snapshot", action="store_true",
                      help="Take a labeled WRAM snapshot and save to file")
    mode.add_argument("--search-species", type=int,
                      help="Search WRAM for a species ID (decimal or hex with 0x prefix)")
    mode.add_argument("--diff-snapshots", nargs=2, metavar="SNAPSHOT",
                      help="Diff two previously saved snapshots")
    mode.add_argument("--dump-range", help="Hex dump a WRAM range (e.g. 0xC0C0-0xC200)")
    mode.add_argument("--watch", type=int, help="Watch an address and log changes over time")

    # Common options
    p.add_argument("--seconds", type=int, default=10,
                   help="Seconds to run before operation (default 10)")
    p.add_argument("--label", default="snapshot",
                   help="Label for snapshot (default: snapshot)")
    p.add_argument("--out", help="Output file for snapshot/diff results")
    p.add_argument("--banks", default="0",
                   help="Comma-separated WRAM banks to include (default: 0)")
    p.add_argument("--poll-interval", type=int, default=60,
                   help="For --watch: poll every N frames (default 60)")

    args = p.parse_args()
    banks = [int(x) for x in args.banks.split(",")]

    # Handle --diff-snapshots (no ROM needed)
    if args.diff_snapshots:
        snap_a = load_snapshot(Path(args.diff_snapshots[0]))
        snap_b = load_snapshot(Path(args.diff_snapshots[1]))
        diffs = diff_snapshots(snap_a, snap_b)

        print(f"# Diff: {snap_a.get('label', 'A')} vs {snap_b.get('label', 'B')}")
        print(f"# {len(diffs)} byte(s) changed\n")
        print(f"{'Address':>8}  {'Bank':>4}  {'From':>6}  {'To':>6}")
        for d in diffs:
            print(f"{d['addr']:>8}  {d['bank']:>4}  {d['from']:>6}  {d['to']:>6}")

        if args.out:
            Path(args.out).write_text(json.dumps(diffs, indent=2))
            print(f"\nWrote diff to {args.out}")
        return 0

    # All other modes need the ROM
    rom_path = Path(args.rom)
    if not rom_path.exists():
        print(f"ROM not found: {rom_path}", file=sys.stderr)
        return 2

    pb = make_pyboy(rom_path)
    try:
        tick(pb, 60 * args.seconds, render=False)

        if args.snapshot:
            snap = take_snapshot(pb, args.label, banks)
            out_path = Path(args.out) if args.out else Path(f"snapshots/{args.label}.json")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, 'w') as f:
                json.dump(snap, f, indent=2)
            print(f"Snapshot '{args.label}' saved to {out_path}")
            print(f"  PC=0x{snap['pc']:04X}, A=0x{snap['a']:02X}")

        elif args.search_species:
            species_id = args.search_species
            matches = search_species_id(pb, species_id)
            print(f"Species ID 0x{species_id:04X} found at {len(matches)} location(s):")
            for addr in matches:
                print(f"  0x{addr:04X}")
            if not matches:
                print("  (not found in WRAM bank 0)")

        elif args.dump_range:
            start_s, end_s = args.dump_range.split("-")
            start = int(start_s, 0)
            end = int(end_s, 0)
            print(dump_range(pb, start, end))

        elif args.watch:
            addr = args.watch
            total_frames = 60 * args.seconds
            changes = watch_address(pb, addr, total_frames, args.poll_interval)
            print(f"# Watched 0x{addr:04X} for {args.seconds}s ({total_frames} frames)")
            print(f"# {len(changes)} change(s)\n")
            for c in changes:
                print(f"Frame {c['frame']:>5} ({c['seconds']:>6.2f}s): "
                      f"[{c['addr']}] {c['from']} -> {c['to']}")

    finally:
        pb.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
