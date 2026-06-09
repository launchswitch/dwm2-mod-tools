#!/usr/bin/env python3
"""Generate Phase 4 edits — EXP curve adjustments for rare/Lord monsters.

Reduce exp_growth rank to make investing in rare species less punishing:
- Rare (maxLvl 50-54): -2 ranks  (~20% less grinding)
- Lord (maxLvl 55+):    -3 ranks (~25% less grinding)
- Common (maxLvl < 50): unchanged

exp_growth is byte 7 of core_monster entries (1-31 scale, lower = faster).
"""
import json
import xml.etree.ElementTree as ET
import subprocess

# Get current ROM data
result = subprocess.run(['python3', 'tools/mod_data.py', 'build/cobi_p3.gbc',
                         '--table', 'core_monster', '--list'],
                        capture_output=True, text=True)
rom_data = json.loads(result.stdout)

# Get max level from XML
tree = ET.parse('table_structure/monster_data_external.xml')
root = tree.getroot()
maxlvl_map = {}
idx = 1
for family in root.find('families').findall('family'):
    for m in family.find('monsters').findall('monster'):
        growth = m.find('growth')
        if growth is not None:
            maxlvl_map[idx] = int(growth.get('maxlvl', 50))
        idx += 1

edits = {}
for entry in rom_data[1:]:
    i = entry['index']
    total = sum(entry[f'{s}_growth'] for s in ['hp','mp','atk','def','agi','int'])
    if total == 0:
        continue  # skip null placeholders

    maxlvl = maxlvl_map.get(i, 50)
    if maxlvl < 50:
        continue  # only touch rare/lord types

    old_exp = entry['exp_growth']
    reduction = 3 if maxlvl >= 55 else 2
    new_exp = max(1, old_exp - reduction)  # floor at 1

    if new_exp != old_exp:
        edits[str(i)] = {"exp_growth": new_exp}

print(json.dumps(edits, indent=2))
