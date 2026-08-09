# Courage (Bravery) and Motivation — Hidden Personality Stats

> Source: maintainer research (Google aggregator of DWM2 guides), 2026-07-05.
> Cross-referenced against `mechanics/mcbick_guide/personality-guide.md` and `critical-attributes.md`.
> Confidence: **[Wiki-documented]** — consistent across community sources but not ROM-routine-verified.

---

## Overview

In DWM2, "Courage" (also called **Bravery**) and **Motivation** are two distinct
internal personality mechanics governed by specific growth caps and execution
metrics. Because these are hidden stats, they do not scale linearly with the
standard Level EXP curves. They function on a flat numeric threshold system
driven strictly by battle commands.

Bravery is one of the four personality traits (alongside Caring, Prudence, and
Motivation) documented in `mechanics/mcbick_guide/personality-guide.md`. The
trait model there confirms:

- Four traits affect personality: **Bravery, Caring, Prudence, Motivation**.
- Using **PLAN** in combat is the fastest way to affect personality; **FIGHT**
  and **ITEM** have no direct effect.
- Lower-level monsters change personalities more easily; high-level monsters
  more slowly — so conditioning early matters.
- Each trait has bonus effects that are more likely to proc when high, and
  negative effects when low.

## Motivation gain curve

- Every captured or bred monster starts with baseline **Motivation = 0**,
  scaling up to a hard max cap of **255**.
- The curve speed is **flat and action-dependent** (not level-dependent). It is
  a fast-growing stat, maxable in a few dozen standard battles.
- **Level-up multiplier:** level-ups don't directly grant Motivation points,
  BUT lower-level monsters gain and lose personality traits *faster* than
  high-level monsters. Conditioning monsters early ensures quicker personality
  shifts.

> The personality-guide trait table corroborates the action mapping: Motivation
> is **Boosted** by "any action other than Command and Run" and **Lowered** by
> "Command, Run" — matching the per-command deltas below.

## Action-based calculations

The gain table (the per-command deltas):

| Battle Command | Courage Change | Motivation Change |
|----------------|----------------|-------------------|
| PLAN > Charge | Large Increase (+++) | Small Increase |
| PLAN > Mixed | No Change | Small Increase |
| PLAN > Cautious/Defensive | Large Decrease (---) | Small Increase |
| FIGHT (Direct Move Command) | No Change | Small Decrease |
| RUN (Fleeing) | Massive Decrease (---) | Massive Decrease (---) |
| Using an Item | No Change | No Change |

> Note: The personality-guide source renders the same deltas as plan tactics —
> `Charge = +++ Bravery / -Prudence`, `Mixed = +++ Prudence / -Cautious`,
> `Cautious = +++ Caring / -Bravery`, `Run = --- Bravery / --- Motivation`.
> "Cautious" there is the third plan tactic and corresponds to the
> Caring-driven defensive plan referenced as "Cautious/Defensive" above.

## The feedback loop — how Motivation alters other trait gains

- **High Motivation (>150):** Acceleration curve. Heavily multiplies point
  gains for Courage when using the Charge tactic, enabling rapid reach of
  high-tier personalities (Hotblood, Daring). Grants a chance to deal **+50%
  damage** on all physical and magical attacks (the "strong attack" from
  `critical-attributes.md`). Dramatically triggers Co-Op skills.
- **Low Motivation (<50):** Suppression. Acts as a negative multiplier — even
  spamming Charge barely moves the baseline Courage stat.

## Design implications

- This closes the last **[Unknown]** from the coverage map's combat section
  (courage/motivation gain curve).
- The mechanic is now fully specified: starting value (**0**), cap (**255**),
  command-driven deltas (table above), and the high/low motivation multiplier
  effect.
- Two numerical gaps remain as **design calls**:
  - (a) the exact magnitude of "Large Increase" / "Small Increase" / "Massive
    Decrease" in points;
  - (b) the exact threshold curve for "lower-level monsters shift traits
    faster."

## Cross-references

- `mechanics/mcbick_guide/critical-attributes.md` — the strong-attack / +50%
  damage connection (motivation is the only stat checked for the strong
  attack, which stacks with a critical for massive damage).
- `mechanics/mcbick_guide/personality-guide.md` — the personality trait model
  (Bravery / Caring / Prudence / Motivation, their high/low effects, the plan
  tactic deltas, and the full 26-personality matrix).
- `mechanics/stat_combat_roles.md` — INT's role in AI quality, which interacts
  with tactic selection.
