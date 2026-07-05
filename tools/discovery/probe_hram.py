#!/usr/bin/env python3
"""
probe_hram.py — Probe HRAM (0xFF80-0xFFFE) for battle/breeding state flags.

Boots the ROM, navigates through different game states via button presses,
and records HRAM values at each state. Uses a wider HRAM range and includes
debug logging to verify the game is actually advancing.

Usage:
    python tools/discovery/probe_hram.py <rom.gbc>
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_pyboy import make_pyboy, tick, snapshot_hram, snapshot_regs

HRAM_START = 0xFF80
PROBE_LEN = 32   # Probe more of HRAM (0xFF80-0xFF9F)

def hram_hex(hram):
    return " ".join(f"{b:02X}" for b in hram)

def hram_diff(old, new):
    diffs = []
    for i, (a, b) in enumerate(zip(old, new)):
        if a != b:
            diffs.append((i, a, b))
    return diffs

def stable_hram(pb, frames=60):
    """Read HRAM after advancing; return the most stable reading."""
    tick(pb, frames, render=False)
    samples = [list(snapshot_hram(pb)[:PROBE_LEN]) for _ in range(5)]
    # Mode (most common value per position)
    return [max(set(col), key=col.count) for col in zip(*samples)]

def main():
    rom_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not rom_path or not rom_path.exists():
        for candidate in [
            Path("/home/frank/repos/dwm2-online/public/rom/cobi_final.gbc"),
        ]:
            if candidate.exists():
                rom_path = candidate
                break
        else:
            print("ERROR: No ROM found."); sys.exit(1)

    print(f"ROM: {rom_path}")
    print(f"Probing HRAM 0x{HRAM_START:04X}+{PROBE_LEN} bytes")
    print("=" * 70)

    pb = make_pyboy(rom_path)
    states = {}
    prev_hram = None

    # ---- State 1: Title Screen (skip intro) ----
    print("\n[1] Title Screen")
    tick(pb, 60 * 4, render=False)  # Wait for title screen music/animation
    hram = stable_hram(pb, frames=60)
    states["title"] = hram
    regs = snapshot_regs(pb)
    print(f"  PC=0x{regs['PC']:04X} HRAM: {hram_hex(hram)}")
    prev_hram = hram

    # ---- State 2: Press Start (skip to overworld) ----
    print("\n[2] Press Start → Overworld")
    pb.tick(1, b'p_start')
    tick(pb, 60 * 3, render=False)  # Wait for cutscene/transition
    hram = stable_hram(pb, frames=60)
    states["after_start"] = hram
    regs = snapshot_regs(pb)
    diffs = hram_diff(prev_hram, hram)
    print(f"  PC=0x{regs['PC']:04X} HRAM: {hram_hex(hram)}")
    if diffs:
        print(f"  Changes: {len(diffs)} bytes")
        for pos, old, new in diffs[:8]:
            print(f"    [0x{HRAM_START+pos:04X}] {old:02X} → {new:02X}")
    prev_hram = hram

    # ---- State 3: Walk around (trigger encounters) ----
    print("\n[3] Walking in multiple directions (looking for battle trigger)")
    
    # Try walking in each direction and check HRAM after each
    directions = [b'p_up', b'p_down', b'p_left', b'p_right']
    encounter_found = False
    
    for d_idx, direction in enumerate(directions):
        if encounter_found:
            break
            
        for step in range(20):  # Walk up to 20 steps
            pb.tick(15, direction)
            tick(pb, 5, render=False)
            
            current = list(snapshot_hram(pb)[:PROBE_LEN])
            diffs = hram_diff(prev_hram, current)
            
            if len(diffs) >= 3:  # Significant change = possible battle
                print(f"  Direction {d_idx} ({'UDLR'[d_idx]}), step {step+1}: {len(diffs)} HRAM bytes changed")
                print(f"    HRAM: {hram_hex(current)}")
                
                # Check if we're in a battle by looking at PC range
                regs = snapshot_regs(pb)
                print(f"    PC=0x{regs['PC']:04X}")
                
                states[f"walking_{d_idx}_step{step}"] = current
                
                # Try to end the battle (press A/B repeatedly)
                print(f"  Ending encounter...")
                for _ in range(10):
                    pb.tick(5, b'p_a')
                    tick(pb, 30, render=False)
                
                # Read HRAM after ending
                post = stable_hram(pb, frames=30)
                states[f"post_encounter_{d_idx}"] = post
                print(f"  Post-encounter HRAM: {hram_hex(post)}")
                encounter_found = True
                break
    
    if not encounter_found:
        print("  No significant HRAM changes detected during walking")

    # ---- State 4: Open party menu (Select button) ----
    print("\n[4] Pressing Select (party menu)")
    pb.tick(1, b'p_select')
    tick(pb, 30, render=False)
    hram = stable_hram(pb, frames=30)
    states["party_menu"] = hram
    diffs = hram_diff(prev_hram, hram)
    print(f"  HRAM: {hram_hex(hram)}")
    if diffs:
        print(f"  Changes: {len(diffs)} bytes")
    prev_hram = hram

    # ---- State 5: Walk more to trigger another encounter ----
    print("\n[5] Extended walking (60 seconds of random movement)")
    
    import random
    move_seq = [random.choice(directions) for _ in range(200)]
    baseline = list(snapshot_hram(pb)[:PROBE_LEN])
    
    transitions = []
    for i, direction in enumerate(move_seq):
        pb.tick(15, direction)
        tick(pb, 3, render=False)
        
        current = list(snapshot_hram(pb)[:PROBE_LEN])
        diffs = hram_diff(baseline, current)
        
        if len(diffs) >= 2:
            transitions.append({
                "step": i + 1,
                "direction": "UDLR"[directions.index(direction)] if direction in directions else "?",
                "changes": len(diffs),
                "hram": hram_hex(current),
                "pc": snapshot_regs(pb)['PC'],
            })
            baseline = current
    
    # ---- Summary ----
    print("\n" + "=" * 70)
    print("HRAM State Summary")
    print("=" * 70)
    
    for label, hram in states.items():
        print(f"\n{label}:")
        print(f"  {hram_hex(hram)}")
    
    if transitions:
        print(f"\n--- Movement transitions ({len(transitions)} detected) ---")
        for t in transitions[:20]:  # Limit output
            print(f"  step {t['step']:3d} dir={t['direction']} "
                  f"changes={t['changes']} PC=0x{t['pc']:04X}")
            print(f"    {t['hram'][:60]}")
    
    # ---- Save results ----
    output = Path(__file__).resolve().parent.parent / "hram_probe_results.json"
    results = {
        "states": {k: hram_hex(v) for k, v in states.items()},
        "transitions": transitions,
        "probe_len": PROBE_LEN,
        "hram_start": f"0x{HRAM_START:04X}",
    }
    output.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {output}")
    
    pb.stop()

if __name__ == "__main__":
    main()
