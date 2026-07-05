# Stat Roles in Combat — INT & AGI

> Source: maintainer research (Google aggregator of DWM2 guides), 2026-07-05.
> Cross-referenced against `mechanics/mcbick_guide/evasion.md` (AGI→evasion half confirmed there).
> Confidence: **[Wiki-documented]** — consistent across community sources but not ROM-routine-verified.

This doc captures the combat roles of INT and AGI that are NOT in the McBick guide. The McBick guide covers AGI→evasion (the defender's side); it does not document AGI→turn-order or AGI→attacking-accuracy, and it does not document INT's combat roles at all (only the skill-unlock gateway, which is also in the skill-requirements tables).

---

## Intelligence (INT) — three roles, NOT spell damage

**Critical clarification:** INT does **not** increase spell damage or healing output in DWM2. A spell cast by a monster with 50 INT deals roughly the same damage as the same spell cast by a monster with 255 INT. Spell damage scales purely on the spell's base tier and the monster's level. (This is unusual for an RPG and easy to misremember.)

The three roles INT *does* play:

### 1. Skill-unlock gateway
[ROM-verified — see `mechanics/skill_requirements_data.md` and per-skill requirements in `mcbick_guide/skills-*.md`]

Monsters cannot learn new abilities or evolve existing spells into their ultimate versions (e.g. Firebal → Hellfire) unless INT meets the minimum required threshold. Same applies to ATK/HP/MP/AGL/DEF thresholds — all six stats gate skill unlocks. INT is the most common gate for Spell-type skills.

### 2. AI decision-making under tactics
[Wiki-documented — McBick does not cover this]

When monsters fight under automated orders (Charge, Mixed, Defense tactics), INT controls how smart their combat choices are:
- **Low INT:** Monsters are highly prone to wasting turns, missing physical strikes, or casting ineffective/wrong spells.
- **High INT:** The AI becomes actively aware of battle conditions. For example, a high-INT monster can identify when an enemy is preparing an anti-group counter (like Imitate) and will switch to single-target attacks to avoid triggering it.

**Implication for MonTamer:** This is the only concrete spec we have for the [Unknown] "AI action selection per tactic" gap. v1 can model this as: low-INT monsters under tactics pick actions randomly (or with naive heuristics); high-INT monsters pick contextually-optimal actions. The INT threshold tiers are not numerically documented — that's a design decision for MonTamer.

### 3. Status-effect evasion
[Wiki-documented — not in McBick]

A higher INT grants passive resistance to enemy status-debilitating magic (Sleep, Poison, etc.). It improves the monster's chance to dodge or shrug off these negative statuses. This stacks with (or modifies) the per-species resistance byte for the status element in question.

**Implication for MonTamer:** Status application has two checks — the skill's success rate (per `mcbick_guide/list-of-resistance-multipliers.md`: 3/3, 2/3, 1/3 by resistance tier) AND the defender's INT-based passive evasion. The interaction math is not documented; design decision.

---

## Agility (AGI) — two roles

### 1. Turn-order priority
[Wiki-documented — McBick does not cover this; the McBick evasion doc covers only the dodge half]

Monsters with higher AGI have a much greater chance of acting before slower allies or enemies each turn. Crucial for landing healing, applying buffs, or using crowd-control before the enemy strikes.

**Traits can bypass this:**
- **Last Word** trait → monster always acts last, regardless of AGI.
- **Early Bird** trait → monster always acts first, regardless of AGI.

**Implication for MonTamer:** Closes part of the [Unknown] "turn order" gap. v1 model: sort action queue by AGI descending, with trait overrides. Tie-breaking for equal AGI is not documented — design decision. (Random? Party-before-enemy? Input order?)

### 2. Accuracy and evasion
[Partial ROM-verified — the evasion half is in `mcbick_guide/evasion.md`; the accuracy-on-hit half is wiki-documented]

AGI directly affects physical hit/miss calculations:
- **On defense (evasion):** [Mechanic-documented in McBick] Evasion = size tier + AGI-difference tier + skill (SideStep). Max 42/100, min 1/100. See `mcbick_guide/evasion.md` for the full tier table.
- **On offense (accuracy):** [Wiki-documented] Having significantly higher AGI than your target helps guarantee your physical attacks land. (Same coin as evasion — the McBick doc frames it from the defender's side as "Defender's AGI − Attacker's AGI"; this is the attacker's-side framing of the same delta.)

Note: AGI affects **physical** accuracy/evasion. Spell and Breath skills use the resistance/success-rate mechanic instead (per `mcbick_guide/list-of-resistance-multipliers.md`).

---

## Implications for combat design (summary)

These findings resolve three [Unknown] gaps from `coverage_map.md`:

| Gap | Resolution |
|-----|------------|
| AI action selection per tactic | INT gates decision quality (low=random/naive, high=contextual). Specific tiers are a design call. |
| Turn order / initiative | AGI sorts the action queue; traits (Last Word, Early Bird) override. Tie-breaking is a design call. |
| INT's role in combat | NOT spell damage. Three roles: skill-unlock, AI quality, status evasion. |

Remaining [Unknown] for combat resolution: the **courage/motivation gain curve** (McBick documents that courage/motivation rises 1-3 points per Charge/Mixed/Defense command, level-dependent, but the level→gain-rate formula is not numerically specified).
