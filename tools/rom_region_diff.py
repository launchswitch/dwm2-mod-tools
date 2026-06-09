#!/usr/bin/env python3
"""
rom_region_diff.py — Diff a ROM region between two ROMs and generate an IPS patch.

Useful for replicating changes from reference ROMs (e.g., DWM2U) by comparing
specific memory regions and producing a minimal IPS patch of the differences.

Usage:
    # Diff breeding region and generate IPS
    python tools/rom_region_diff.py roms/cobi_clean.gbc roms/cobi_dwm2u.gbc \\
        --region 0x3A208:0x3BE99 \\
        --ips build/g5_breeding.ips

    # Diff and show summary without writing IPS
    python tools/rom_region_diff.py roms/cobi_clean.gbc roms/cobi_dwm2u.gbc \\
        --region 0x3A208:0x3BE99 --summary

    # Write patched ROM (clean + diff applied)
    python tools/rom_region_diff.py roms/cobi_clean.gbc roms/cobi_dwm2u.gbc \\
        --region 0x3A208:0x3BE99 \\
        --output build/cobi_breeding.gbc

    # Multiple regions at once
    python tools/rom_region_diff.py roms/cobi_clean.gbc roms/cobi_dwm2u.gbc \\
        --region 0x3A208:0x3BE99 \\
        --region 0xD433B:0xD7FFF \\
        --ips build/combined.ips

Known DWM2U regions (from breeding_data.md, core_monster_data.md):
    Breeding tables:       0x3A208:0x3BE99
    Core monster data:     0xD433B:0xD7FFF
    Prebuilt enemies:      0xD0075:0xD0A75
    Boss battles:          0x2881C:0x289DC
    Random encounters:     0x29773:0x2A3CE
    Item data:             0x58CC2:0x58E50
    Skill data:            0x680D4:0x683F4
    EXP tables:            0x64E60:0x6507C
"""

import struct
import argparse
import sys
import os


def parse_region(spec):
    """Parse region spec 'start:end' into (start, end) tuple."""
    parts = spec.split(':')
    start = int(parts[0], 16) if '0x' in parts[0] or '0X' in parts[0] else int(parts[0])
    end = int(parts[1], 16) if len(parts) > 1 and (parts[1] and ('0x' in parts[1] or '0X' in parts[1])) else int(parts[1]) if len(parts) > 1 and parts[1] else start + 0x100
    return start, end


def find_diffs(clean, patched, regions):
    """Find all differing bytes across specified regions."""
    diffs = []
    for start, end in regions:
        for i in range(start, min(end, len(clean))):
            if clean[i] != patched[i]:
                diffs.append((i, patched[i]))
    return diffs


def group_into_runs(diffs):
    """Group diffed bytes into contiguous runs for IPS patching."""
    if not diffs:
        return []
    runs = [[diffs[0]]]
    for i in range(1, len(diffs)):
        if diffs[i][0] <= runs[-1][-1][0] + 1:
            runs[-1].append(diffs[i])
        else:
            runs.append([diffs[i]])
    return runs


def generate_ips(diffs, patched):
    """Generate IPS binary data from diffed bytes."""
    runs = group_into_runs(diffs)
    ips = bytearray(b'PATCH\n')
    for run in runs:
        start = run[0][0]
        end = run[-1][0] + 1
        data_len = end - start
        # Offset (24-bit big-endian)
        ips.append((start >> 16) & 0xFF)
        ips.append((start >> 8) & 0xFF)
        ips.append(start & 0xFF)
        # Length (data + 2 for length field, big-endian)
        ips.append((data_len + 2) >> 8)
        ips.append((data_len + 2) & 0xFF)
        # Data from patched ROM
        ips.extend(patched[start:end])
    # EOF marker
    ips.extend(b'\x00\x00\x00\x00\x00\x00\n')
    return ips


def apply_ips(rom, ips_data):
    """Apply IPS patch data to a ROM bytearray."""
    rom = bytearray(rom)
    offset = 6  # skip 'PATCH\n'
    while offset + 4 < len(ips_data):
        poff = (ips_data[offset] << 16) | (ips_data[offset+1] << 8) | ips_data[offset+2]
        plen = (ips_data[offset+3] << 8) | ips_data[offset+4]
        dlen = plen - 2
        if poff == 0 and plen <= 2:
            break
        rom[poff:poff+dlen] = ips_data[offset+5:offset+5+dlen]
        offset += 3 + plen
    return bytes(rom)


def verify_ips(clean, patched, regions, ips_data):
    """Verify IPS produces identical output in target regions."""
    result = apply_ips(clean, ips_data)
    diffs = sum(1 for start, end in regions
                for i in range(start, min(end, len(result)))
                if result[i] != patched[i])
    return diffs


def main():
    parser = argparse.ArgumentParser(
        description='Diff ROM regions and generate IPS patches',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument('clean_rom', help='Base (clean) ROM file')
    parser.add_argument('patched_rom', help='Reference (patched) ROM file')
    parser.add_argument('--region', action='append', required=True,
                        help='ROM region to diff (hex start:end, e.g., 0x3A208:0x3BE99). '
                             'Can be specified multiple times.')
    parser.add_argument('--ips', help='Output IPS patch file path')
    parser.add_argument('--output', help='Output patched ROM (clean + diff applied)')
    parser.add_argument('--summary', action='store_true',
                        help='Show summary of differences without writing files')

    args = parser.parse_args()

    # Read ROMs
    with open(args.clean_rom, 'rb') as f:
        clean = f.read()
    with open(args.patched_rom, 'rb') as f:
        patched = f.read()

    if len(clean) != len(patched):
        print(f"Warning: ROM sizes differ ({len(clean)} vs {len(patched)})")

    # Parse regions
    regions = [parse_region(r) for r in args.region]

    # Find diffs
    diffs = find_diffs(clean, patched, regions)

    if not diffs:
        print("No differences found in specified regions.")
        return 0

    # Summary
    runs = group_into_runs(diffs)
    region_labels = {
        '0x3A208:0x3BE99': 'breeding tables',
        '0xD433B:0xD7FFF': 'core monster data',
        '0xD0075:0xD0A75': 'prebuilt enemies',
        '0x2881C:0x289DC': 'boss battles',
        '0x29773:0x2A3CE': 'random encounters',
        '0x58CC2:0x58E50': 'item data',
        '0x680D4:0x683F4': 'skill data',
        '0x64E60:0x6507C': 'EXP tables',
    }

    region_strs = [f'{start:#05x}:{end:#05x}' for start, end in regions]
    region_desc = ', '.join(region_labels.get(r, r) for r in region_strs)

    print(f"Region diff: {region_desc}")
    print(f"  {len(diffs)} differing bytes in {len(runs)} contiguous runs")
    print(f"  Regions: {' -> '.join(region_strs)}")

    if args.summary:
        # Show first 20 diff locations
        print(f"\nFirst {min(20, len(diffs))} differences:")
        for offset, new_val in diffs[:20]:
            old_val = clean[offset]
            bank = offset // 0x4000
            addr = offset & 0xFFFF
            print(f"  0x{offset:05X} (bank {bank}, 0x{addr:04X}): "
                  f"{old_val:02X} -> {new_val:02X}")
        if len(diffs) > 20:
            print(f"  ... and {len(diffs)-20} more")
        return 0

    # Generate IPS
    ips_data = generate_ips(diffs, patched)

    if args.ips:
        with open(args.ips, 'wb') as f:
            f.write(ips_data)
        print(f"IPS written: {args.ips} ({len(ips_data)} bytes)")

        # Verify
        mismatches = verify_ips(clean, patched, regions, ips_data)
        if mismatches:
            print(f"  Warning: {mismatches} bytes differ after applying IPS")
        else:
            print(f"  Verified: IPS produces identical output in target regions")

    if args.output:
        result = apply_ips(clean, ips_data)
        with open(args.output, 'wb') as f:
            f.write(result)
        print(f"Patched ROM written: {args.output}")

        # Final verification
        mismatches = sum(1 for start, end in regions
                        for i in range(start, min(end, len(result)))
                        if result[i] != patched[i])
        if mismatches:
            print(f"  Warning: {mismatches} bytes differ from reference ROM")
        else:
            print(f"  Verified: patched ROM matches reference in target regions")

    return 0


if __name__ == '__main__':
    sys.exit(main())
