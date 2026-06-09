#!/usr/bin/env python3
"""
verify.py — End-to-end smoke test of the workbench.

Boots both ROMs, runs them briefly, takes screenshots, runs the
static ROM diff, and reports status of every component. Use this
to confirm the workbench is healthy before handing off to agnt.

Usage:
    python tools/verify.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

WORKBENCH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKBENCH / "tools"))

from lib_pyboy import make_pyboy, tick


def check(label: str, ok: bool, detail: str = "") -> bool:
    mark = "OK  " if ok else "FAIL"
    print(f"  [{mark}] {label}{(': ' + detail) if detail else ''}")
    return ok


def main() -> int:
    print("=" * 60)
    print("DWM2 Workbench Verification")
    print("=" * 60)

    all_ok = True
    roms = {
        "cobi_clean": WORKBENCH / "roms" / "cobi_clean.gbc",
        "cobi_dwm2u": WORKBENCH / "roms" / "cobi_dwm2u.gbc",
    }
    labels = WORKBENCH / "labels" / "labels.json"
    build_dir = WORKBENCH / "build"
    build_dir.mkdir(exist_ok=True)

    # ---- 1. ROMs exist and are correct size
    print("\n[1] ROM files")
    for name, path in roms.items():
        if not path.exists():
            all_ok &= check(f"{name} exists", False, str(path))
            continue
        size = path.stat().st_size
        ok = size == 4 * 1024 * 1024
        all_ok &= check(f"{name} is 4 MB", ok, f"size={size}")

    # ---- 2. Boot ROM stub
    print("\n[2] Boot ROM stub")
    stub = WORKBENCH / "roms" / "bootrom_cgb_stub.bin"
    if stub.exists():
        size = stub.stat().st_size
        ok = size == 2304
        all_ok &= check("stub is 2304 bytes", ok, f"size={size}")
        first = stub.read_bytes()[:8]
        ok = first == bytes([0x3E, 0x11, 0xE0, 0x50, 0xC3, 0x00, 0x01, 0x00])
        all_ok &= check("stub starts with CGB signature jump", ok, first.hex())
    else:
        all_ok &= check("stub exists", False, str(stub))

    # ---- 3. Labels file
    print("\n[3] Labels file")
    if labels.exists():
        data = json.loads(labels.read_text())
        n = data.get("summary", {}).get("num_patches", 0)
        all_ok &= check("labels.json parses", True, f"{n} patch labels")
    else:
        all_ok &= check("labels.json exists", False, str(labels))

    # ---- 4. Both ROMs boot to title screen
    print("\n[4] ROM boot in PyBoy")
    for name, path in roms.items():
        try:
            pb = make_pyboy(path)
            tick(pb, 60 * 5, render=False)
            pc = pb.register_file.PC
            lcdc = pb.memory[0xFF40]
            ok = pc != 0x0000  # PC in ROM, not stuck at reset
            all_ok &= check(
                f"{name} advances past reset", ok,
                f"PC=0x{pc:04X}, LCDC=0x{lcdc:02X}",
            )
            # Save screenshot
            out = build_dir / f"boot_{name}_5s.png"
            pb.screen.image.save(out)
            check(f"{name} screenshot saved", True, str(out))
            pb.stop()
        except Exception as e:
            all_ok &= check(f"{name} boots", False, str(e))

    # ---- 5. Static ROM diff finds differences
    print("\n[5] Static ROM diff")
    a = roms["cobi_clean"].read_bytes()
    b = roms["cobi_dwm2u"].read_bytes()
    n_diffs = sum(1 for i in range(len(a)) if a[i] != b[i])
    ok = n_diffs > 1000  # DWM2U touches ~16,941 bytes
    all_ok &= check(
        "patched differs from clean", ok,
        f"{n_diffs} bytes differ (expected ~16,941)",
    )

    # ---- 6. Runtime WRAM diff works
    print("\n[6] Runtime WRAM diff")
    try:
        pa = make_pyboy(roms["cobi_clean"])
        pb2 = make_pyboy(roms["cobi_dwm2u"])
        tick(pa, 60 * 3, render=False)
        tick(pb2, 60 * 3, render=False)
        from lib_pyboy import snapshot_wram, diff_wram
        sa = snapshot_wram(pa)
        sb = snapshot_wram(pb2)
        diffs = diff_wram(sa, sb)
        # After 3s with LCD off, diffs may be 0 (game is idle) — that's fine
        check(
            "diff_wram runs without error", True,
            f"{len(diffs)} diffs after 3s (0 is OK if LCD off)",
        )
        pa.stop()
        pb2.stop()
    except Exception as e:
        all_ok &= check("diff_wram runs", False, str(e))

    # ---- 7. Makefile targets
    print("\n[7] Makefile")
    makefile = WORKBENCH / "Makefile"
    all_ok &= check("Makefile exists", makefile.exists(), str(makefile))

    # ---- Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("VERIFICATION PASSED — workbench is ready for handoff")
        return 0
    else:
        print("VERIFICATION FAILED — see failures above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
