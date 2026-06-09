#!/usr/bin/env python3
"""
rom_diff.py — Static byte diff between two ROMs at file level.

Reports every offset that differs. For a 4MB ROM the diff is typically
small (the DWM2U patch is ~24KB). Use this to:
- Verify a patched ROM matches a known IPS log.
- See exactly which bytes a mod touches (no in-game behavior needed).

Usage:
    python tools/rom_diff.py roms/cobi_clean.gbc roms/cobi_dwm2u.gbc
    python tools/rom_diff.py roms/cobi_clean.gbc roms/cobi_dwm2u.gbc --json out.json
    python tools/rom_diff.py roms/cobi_clean.gbc roms/cobi_dwm2u.gbc --only-different
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("a", help="First ROM (cleaner / earlier state)")
    p.add_argument("b", help="Second ROM (modified / later state)")
    p.add_argument("--json", help="Output diff as JSON to this path")
    p.add_argument("--only-different", action="store_true",
                   help="Skip identical bytes (smaller output)")
    p.add_argument("--max", type=int, default=50,
                   help="Max diffs to print (default 50)")
    args = p.parse_args()

    a = Path(args.a).read_bytes()
    b = Path(args.b).read_bytes()
    if len(a) != len(b):
        print(f"WARNING: size mismatch {len(a)} vs {len(b)}", file=sys.stderr)

    diffs = []
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            diffs.append({
                "offset": i,
                "bank": i // 0x4000,
                "addr_in_bank": i % 0x4000,
                "from": a[i],
                "to": b[i],
            })

    summary = {
        "a": args.a,
        "b": args.b,
        "size_a": len(a),
        "size_b": len(b),
        "num_diffs": len(diffs),
        "diffs": diffs if not args.only_different else diffs,
    }

    if args.json:
        Path(args.json).write_text(json.dumps(summary, indent=2))
        print(f"Wrote {len(diffs)} diffs to {args.json}", file=sys.stderr)
    else:
        print(f"Comparing {args.a} ({len(a)} bytes) vs {args.b} ({len(b)} bytes)")
        print(f"Found {len(diffs)} differing bytes")
        print()
        print(f"{'offset':>8}  {'bank':>4}  {'addr':>6}  {'from':>4}  {'to':>4}")
        for d in diffs[:args.max]:
            print(
                f"0x{d['offset']:06X}  "
                f"{d['bank']:>4}  "
                f"0x{d['addr_in_bank']:04X}  "
                f"0x{d['from']:02X}  "
                f"0x{d['to']:02X}"
            )
        if len(diffs) > args.max:
            print(f"... and {len(diffs) - args.max} more (use --max to see more, or --json for all)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
