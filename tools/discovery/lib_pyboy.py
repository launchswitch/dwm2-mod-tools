"""
lib_pyboy.py — Common PyBoy setup and helpers for DWM2 mod tools.

Wraps the boilerplate of loading a ROM with the right flags, exposes
useful primitives (memory dumps, register snapshots, save states),
and provides headless defaults. Every tool in this directory imports
from this module.

Usage:
    from lib_pyboy import make_pyboy, snapshot_regs, snapshot_wram, diff_wram
    pb = make_pyboy("roms/cobi_clean.gbc")
    pb.tick(60 * 5, render=False)
    reg_state = snapshot_regs(pb)
    wram = snapshot_wram(pb)
    pb.stop()
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

# Locate the boot ROM stub (if shipped) and default ROM directory
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BOOT_ROM_STUB = REPO_ROOT / "roms" / "bootrom_cgb_stub.bin"
DEFAULT_ROM_DIR = REPO_ROOT / "roms"

# PyBoy is heavy; import lazily so CLI tools can fail fast on missing dep
try:
    from pyboy import PyBoy
except ImportError as e:
    print(
        "FATAL: pyboy not installed. Install it with:\n"
        "  pip install pyboy pillow",
        file=sys.stderr,
    )
    raise


def make_pyboy(
    rom_path: str | os.PathLike,
    *,
    cgb: bool = True,
    headless: bool = True,
    bootrom: Optional[str] = None,
    symbols: Optional[str] = None,
    log_level: str = "WARNING",
) -> "PyBoy":
    """Construct a PyBoy instance with sensible defaults.

    The bundled CGB boot ROM stub is used by default because the PyBoy-shipped
    stub is broken (mostly NOPs that loop forever at $07F1). Pass
    bootrom=None to use PyBoy's bundled stub (not recommended for DWM2).
    """
    kwargs = {
        "cgb": cgb,
        "window": "null" if headless else "SDL2",
        "log_level": log_level,
    }
    if bootrom is None:
        if BOOT_ROM_STUB.exists():
            kwargs["bootrom"] = str(BOOT_ROM_STUB)
        # else: PyBoy will fall back to its bundled stub
    else:
        kwargs["bootrom"] = bootrom
    if symbols is not None:
        kwargs["symbols"] = symbols
    return PyBoy(str(rom_path), **kwargs)


def snapshot_regs(pyboy) -> dict:
    """Read the full SM83 register file. Cheap, call as often as you like."""
    rf = pyboy.register_file
    return {
        "A": rf.A, "F": rf.F, "B": rf.B, "C": rf.C,
        "D": rf.D, "E": rf.E, "HL": rf.HL, "SP": rf.SP, "PC": rf.PC,
    }


def snapshot_wram(pyboy, banks: Optional[list[int]] = None) -> dict[int, bytes]:
    """Snapshot WRAM. By default reads bank 0 only ($C000-$DFFF). Pass a list
    of banks to also read bank 1..7 ($D000-$DFFF in each)."""
    out = {0: bytes(pyboy.memory[0xC000:0xE000])}
    if banks:
        for b in banks:
            if b == 0:
                continue
            out[b] = bytes(pyboy.memory[b, 0xD000:0xE000])
    return out


def snapshot_hram(pyboy) -> bytes:
    """HRAM is $FF80-$FFFE. Always 127 bytes."""
    return bytes(pyboy.memory[0xFF80:0xFFFF])


def snapshot_vram(pyboy, banks: Optional[list[int]] = None) -> dict[int, bytes]:
    """Snapshot VRAM. By default reads bank 0 ($8000-$9FFF)."""
    out = {0: bytes(pyboy.memory[0x8000:0xA000])}
    if banks:
        for b in banks:
            if b == 0:
                continue
            out[b] = bytes(pyboy.memory[b, 0x8000:0xA000])
    return out


def diff_wram(a: dict[int, bytes], b: dict[int, bytes]) -> list[tuple[int, int, int, int]]:
    """Diff two WRAM snapshots. Returns [(bank, addr, byte_a, byte_b), ...]
    where addr is the offset within the bank ($C000 base for bank 0,
    $D000 base for other banks — i.e. NOT the full GBA address)."""
    diffs = []
    banks = set(a.keys()) | set(b.keys())
    for bank in sorted(banks):
        ba = a.get(bank, b"")
        bb = b.get(bank, b"")
        # pad to equal length for safety
        n = min(len(ba), len(bb))
        for i in range(n):
            if ba[i] != bb[i]:
                diffs.append((bank, i, ba[i], bb[i]))
    return diffs


def save_state_to(pyboy, path: str | os.PathLike) -> None:
    """Save emulator state to a file. Includes CPU, memory, PPU, banking."""
    with open(path, "wb") as f:
        pyboy.save_state(f)


def load_state_from(pyboy, path: str | os.PathLike) -> None:
    """Load emulator state from a file."""
    with open(path, "rb") as f:
        pyboy.load_state(f)


def tick(pb, frames: int, render: bool = False) -> None:
    """Tick forward N frames. render=False is ~3x faster and we don't need
    pixels for diffs."""
    pb.tick(frames, render=render)
