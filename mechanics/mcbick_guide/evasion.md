# Evasion Rates

> Source: McBick "Advanced Skill Guide" FAQ #78461, v4.0 (GameFAQs, saved HTML)
> GameFAQs URL: https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461/evasion-rates
> Captured: 2026-07-05 from browser-saved HTML

---

## Evasion Rates

**Battle Mechanics**

A monster always has a chance to evade any physical attack. There are two evasion rates for monsters, the monster's natural evasion rate and the AGL difference battling monsters. A monster's natural evasion rate is directly tied to their size. You can the sizes of monster at the library by checking the list of monsters you have bred or tamed. Smaller monsters are more evasive. The second evasion rate, AGL difference, is a much bigger factor. If the attacking monster has significantly less AGL than their target, the evasion rate can be as high as 40%. The game will check both rates, giving you two chances to evade an attack. You can view the table below for evasion rates.

A monster can also evade an attack by having too much DEF. If the attacking monster's ATK is too low to inflict damage then the targeted monster will have a 50% chance to evade the attack or take 1 damage. If this occurs, any effects that a skill had will also miss. For example, NapAttack's sleep effect will not occur in this scenario.

| Monster Size | Evasion Rate | AGL Difference | Evasion Rate |
|---|---|---|---|
| S | 2/100 | 0 | 1/100 |
| M | 1/100 | 1 to 99 | 2/100 |
| L | 1/100 | 100 to 149 | 3/100 |
| LL | 0 | 150 to 199 | 5/100 |
| G | 0 | 200 to 299 | 10/100 |
|  |  | 300 to 449 | 25/100 |
|  |  | 450+ | 40/100 |

**Secret Monsters**

| Monster | Size | Evasion Rate |
|---|---|---|
| Kagebou | M | 1/100 |
| Lamia | LL | 0 |
| Dimensaur | LL | 0 |

---

## SideStep skill mechanic (from v1.1, not restated in v4.0 page)

> Note: The v4.0 "Evasion Rates" page above does not cover the **SideStep**
> skill's effect on the evasion check. The v1.1 FAQ described it; that text is
> preserved verbatim here so the full evasion model is in one place. The v1.1
> text also gives the AGI-difference as "Defender's AGI − Attacker's AGI" and
> lists slightly different bucket boundaries (300–450 / greater than 450).

Evasion is the probability of a normal attack or Physical skill missing. The evasion rate is based off a monster's size and the AGI difference of the monsters battling. If a monster would take 0 damage from an attack or skill, then it will be missed instead. If it is a non-Physical skill then the monster will be unaffected instead, essentially the same as missing.

Evasion Rate by Size
Size of S = 2/100 Evasion Rate
Size of M = 1/100 Evasion Rate
Size of L = 0/100 Evasion Rate
Size of LL = 0/100 Evasion Rate
Size of G = 0/100 Evasion Rate

Evasion Rate by AGI
Difference = Defender's AGI - Attacker's AGI
Difference of less than 0 = 1/100 Evasion Rate
Difference of 0 to 99 = 2/100 Evasion Rate
Difference of 100 to 149 = 3/100 Evasion Rate
Difference of 150 to 199 = 5/100 Evasion Rate
Difference of 200 to 299 = 10/100 Evasion Rate
Difference of 300 to 450 = 25/100 Evasion Rate
Difference of greater than 450 = 40/100 Evasion Rate

Evasion Rate by Skill
SideStep = 40/100 Evasion Rate

Battle Mechanics
The game first checks the size rate and then the AGI rate. If the skill SideStep is used, then the game will not check the AGI rate and instead will check the size rate followed by the skill rate. This effectively makes the evasion rate (Size Rate + AGI Rate or Skill Rate). The maximum evasion rate is 42/100, with a size S monster and an AGI difference of 451-999 or using SideStep. The minimum evasion rate is 1/100, there will always be a chance for a monster to evade normal attacks and Physical skills.
