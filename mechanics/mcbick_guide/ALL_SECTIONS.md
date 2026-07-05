# McBick "Advanced Skill Guide" FAQ #78461 — Full Capture

Dragon Warrior Monsters 2: Cobi's Journey (Game Boy Color)
Author: McBick | FAQ #: 78461 | Version captured: **v1.1**

## Sources

- Primary capture: Neoseeker mirror (single-page, no Cloudflare): https://www.neoseeker.com/dwm2/faqs/3080761-dragon-quest-monsters-2-cobis-journey-advanced-skill.html
- Original GameFAQs (Cloudflare-protected, v4.0 current): https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461
- Wayback Machine (2022 capture, intro only): http://web.archive.org/web/20220601003739/https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461

## Capture notes

The Neoseeker mirror is v1.1 of the FAQ (the version submitted Jul 16, 2020). The current GameFAQs version is v4.0 (2025) which adds: an expanded per-monster critical-rate table across ALL monster families (the v1.1 "Critical Attributes" section below lists only the Slime family), an "Intro to Skills" section with attribute-code definitions and the base damage formula, and Field Skills. Those v4.0-only additions could not be faithfully captured to disk (see STATUS.md). All core skill data, damage formulas, status mechanics, resistance multipliers, evasion rules, and critical-attack rules below are complete and verbatim from v1.1.

---

=== SECTION: intro ===
URL: https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461/intro
TITLE: Intro

Intro

This guide is a compilation of battle data for skills. In this version and the coming versions I hope to elaborate on how each skill functions in battle. I will be adding more info on how resistances affect each skill, resistance bonuses from items, skill battle algorithms, co-op skill damage mechanics, and battle mechanics in general to this guide. I am not sure how often I will update this guide. I have a lot of data compiled for this game and it takes quite a bit of time to double check it and organize it, but I hope to release the bulk of the info in this first version. If you happen to read my guide please inform me of any information missing that you may know. I may already have it and have yet to add it to my guide, but I may not, so please inform me so I can add it to the guide later.

=== END SECTION ===

=== SECTION: evasion ===
URL: https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461/evasion
TITLE: Evasion

Evasion

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

=== END SECTION ===

=== SECTION: critical-attacks ===
URL: https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461/critical-attacks
TITLE: Critical Attacks

Critical Attacks

Critical attacks occur when using a normal attack or Physical skill. The critical rate is based on a monster's critical attribute and/or their Courage stat. Each monster is assigned a value from 0-3 for their critical attribute, this cannot be raised through breeding. This rate is fixed to the monster's type and can not be altered. A monster's Courage stat however can be raised and is based on the actions your monster takes during each battle, see my personality mechanics for more info. Critical attacks can only be done on normal attacks and Physical skills, see my list of skills for info.

Critical Rate by Attribute
Critical Attribute of 0 = 0/128 Critical Rate
Critical Attribute of 1 = 1/128 Critical Rate
Critical Attribute of 2 = 2/128 Critical Rate
Critical Attribute of 3 = 4/128 Critical Rate

Critical Rate by Courage

Courage of 0 = 0/128 Critical Rate
*Courage of ? to ?= 1/128 Critical Rate
*Courage of ? to ?= 2/128 Critical Rate
*Courage of ? to ?= 4/128 Critical Rate
Courage of 255 = 7/128 Critical Rate
*There are three different number ranges for each critical rate, they are currently unknown.

Critical Rate by Skill
EvilSlash = 64/128
Massacre = 128/128

Battle Mechanics
The game will first check the attribute rate and then the courage rate. This means the actual probability to get a critical attack is (Critical Attribute + Critical Courage). The game ignores these checks for critical skills and will only check the skill rate. The maximum critical rate is 11/128, with an attribute of 3 and courage of 255. The miniumum critical rate is 0/128.

=== END SECTION ===

=== SECTION: critical-attributes ===
URL: https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461/critical-attributes
TITLE: Critical Attributes

Critical Attributes

This is a compilation of all monster's critical attribute.
Monster Name (Attribute Value) - Critical Rate

Slime
DrakSlime (2) - Critical Rate 2/128
SpotSlime (2) - Critical Rate 2/128
WingSlime (2) - Critical Rate 2/128
TreeSlime (2) - Critical Rate 2/128
Snaily (2) - Critical Rate 2/128
SlimeNite (3) - Critical Rate 4/128
Babble (2) - Critical Rate 2/128
BoxSlime (2) - Critical Rate 2/128
PearlGel (2) - Critical Rate 2/128
Slime (3) - Critical Rate 4/128
Healer (2) - Critical Rate 2/128
FangSlime (3) - Critical Rate 4/128
RockSlime (2) - Critical Rate 2/128
Slimeborg (3) - Critical Rate 4/128
Slabbit (2) - Critical Rate 2/128
KingSlime (2) - Critical Rate 2/128
Metaly (2) - Critical Rate 2/128
Metabble (2) - Critical Rate 2/128
SpotKing (2) - Critical Rate 2/128
TropicGel (2) - Critical Rate 2/128
MimeSlime (2) - Critical Rate 2/128
HaloSlime (2) - Critical Rate 2/128
MetalKing (1) - Critical Rate 1/128
GoldSlime (1) - Critical Rate 1/128
GranSlime(2) - Critical Rate 2/128
WonderEgg (1) - Critical Rate 2/128

=== END SECTION ===

=== SECTION: list-of-item-resistances ===
URL: https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461/list-of-item-resistances
TITLE: List of Item Resistances

List of Item Resistances

Several items offer increased resistances. These bonuses will stack with buffs. Something to keep in mind when breeding is that these bonuses will not affect the child's resistances. It will still use the parent's base resistances to determine the child's resistances.

List of Item Resistances
MagicCape: +1 resistance to A, B, C, D, and E (Spell Damage)
DracoCape: +1 resistance to Q and R (Breath Damage)
OrcaCape: +1 resistance to Water (Geyser/Watershot/TidalWave)
SilvrCape: +1 resistance to H, L, and S (Sleep/Confusion/Poison Debuff)
Gold Cape: +1 resistance to G, H, L, S, and T (Blind/Sleep/Confusion/Poison/Paralysis Debuff)
PltnmCape: +1 resistance to G, H, I, J, O, S, T, and U (Blind/Sleep/EerieLite, UltraDown, Death/Suicide/Confusion/Poison/Paralysis/Curse Debuff)
BraveCape: +1 resistance to V, W, and X (Stun/DanceShut/MouthShut Debuff)

=== END SECTION ===

=== SECTION: list-of-resistance-multipliers ===
URL: https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461/list-of-resistance-multipliers
TITLE: List of Resistance Multipliers

List of Resistance Multipliers

Each monster will have a resistance ranging from 0-3 that determines how effective a skill is against them. There are a total of 27 resistances in this version. Many skills share a resistance. For example, Blaze and FireSlash share the same resistance attribute. However, Blaze is a Spell skill and FireSlash is not. This is important to know because some skills will nullify the actions of a skill based on its type instead of its attribute.

List of Resistance Multipliers;
Resistance of 3 = Damage Multiplier of 0, Success Rate of 0
Resistance of 2 = Damage Multiplier of 0.5, Success Rate of 1/3(33%)
Resistance of 1 = Damage Multiplier of 1, Success Rate of 2/3(66%)
Resistance of 0 = Damage Multiplier of 1.5, Success Rate of 3/3(100%)

=== END SECTION ===

=== SECTION: list-of-battle-skills ===
URL: https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461/list-of-battle-skills
TITLE: List of Battle Skills

List of Battle Skills
Skill Name (Type, MP) - Skill Details

Defensive Skills, No Attribute;
SideStep (Dance, 1) - This will apply the SideStep buff to itself for one round of battle. A monster with this status has a 40% chance to evade any attack or Physical skill. This skill will take effect at the start of the round and has priority over SquallHit.
Dodge (None, 4) - This redirects all attacks and Physical skills to a random ally or enemy for one round. This skill will take effect at the start of the round and has priority over SquallHit.
StrongD (None, 3) - This will apply a damage multiplier of 0.1 to all attacks and skills that affects the user for one round. This skill will take effect at the start of the round and has priority over SquallHit.
Cover (None, 2) - The user will receive all damage and effects on behalf of one ally for one round of battle. This skill will take effect at the start of the round and has priority over SquallHit.
Guardian (None, 2) - The user will receive all damage and effects on behalf of all allies for one round of battle. This skill will take effect at the start of the round and has priority over SquallHit.
Imitate (None, 4) - The user will copy and return any action that targets it for one round of battle, damage is applied normally to the user. Any attacks or targeted skills that are copied will use the user's stats and buffs for damage calculation. This skill will take effect at the start of the round and has priority over SquallHit.
TailWind (None, 6) - The user will redirect the next enemy Breath skill used back to the skill's user, lasts for one round of battle or until a Breath skill is nullified and returned. This skill will take effect at the start of the round and has priority over SquallHit.
StormWind (None, 10) - The user redirects all enemy Breath skills for one round of battle back to the skill's user. This skill will take effect at the start of the round and has priority over SquallHit.
SuckAll (Breath, 2) - The user nullifies all enemy Breath skills for one round of battle. This skill will take effect at the start of the round and has priority over SquallHit.

Damage Amp Skills, No Attribute;
Focus (None, 0) - This will apply the Focus buff to the user. A monster with this buff will have their next attack or skill applied twice that turn. The buff is removed afterwards.
ChargeUp (None, 0) - This will apply the ChargeUp buff to the user. A monster with this buff will have a damage multiplier of 2 applied to their next attack or Physical skill used, after the damage is calculated. The buff is removed afterwards.
SuckAir (Breath, 0) - This will apply the SuckAir buff to the user. A monster with this buff will have a damage multiplier of 2 applied to their next Breath skill used, after the damage is calculated. The status is removed afterwards.

Physical Skills, No Attribute;

SquallHit (Physical, 2) - This will attack one enemy at the start of the round. A damage multiplier of 0.1 is applied to the attack, after the damage is calculated.
BiAttack (Physical, 3) - This will attack one enemy 2 times, consecutively. A damage multiplier of 0.5 is applied to the attack, after the damage is calculated.
QuadHits (Physical, 6) - This will attack one random enemy 4 times, consecutively. A damage multiplier of 0.5 is applied to the attack, after the damage is calculated.
RainSlash (Physical, 5) - This will attack all enemies, consecutively.
TwinSlash (Physical, 3) - This will attack one enemy, but the user will lose HP equal to 20% of the damage inflicted. A damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
PsycheUp (Physical, 3) - This will attack one enemy at the end of this round of battle. A damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
HighJump (Physical, 5) - This will remove the user from battle until its next turn, unaffected by attacks and skill while removed. When the user returns they will attack one enemy. A damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
Berserker (Physical, 1) - This will attack one enemy. A damage multiplier of 2 is applied to the attack, after the damage is calculated. The user will have a damage multipler of 2 applied to all attacks and skills that affect it for this round of battle. This will take effect at the start of the round and has priority over SquallHit.
Massacre (Physical, 3) - This will critically attack a random enemy or ally, including itself.
EvilSlash (Physical, 3) - This will critically attack one enemy, but may fail. The success rate is 64/128(50%).

Anti-Monster Skills, No Attribute;
SlimeBlow (Physical, 3) - This will attack one enemy. If the enemy target is a Slime monster, a damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
DrakSlash (Physical, 3) - This will attack one enemy. If the enemy target is a Dragon monster, a damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
BeastCut (Physical, 3) - This will attack one enemy. If the enemy target is a Beast monster, a damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
BirdBlow (Physical, 3) - This will attack one enemy. If the enemy target is a Bird monster, a damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
BugBlow (Physical, 3) - This will attack one enemy. If the enemy target is a Bug monster, a damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
Shears (Physical, 3) - This will attack one enemy. If the enemy target is a Plant monster, a damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
DevilCut (Physical, 3) - This will attack one enemy. If the enemy target is a Devil monster, a damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
ZombieCut (Physical, 3) - This will attack one enemy. If the enemy target is a Zombie monster, a damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
CleanCut (Physical, 3) - This will attack one enemy. If the enemy target is a Material monster, a damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
AquaCut (Physical, 3) - This will attack one enemy. If the enemy target is a Water monster, a damage multiplier of 1.5 is applied to the attack, after the damage is calculated.
MetalCut (Physical, 3) - This will attack one enemy. If the enemy target is a Metal monster, the minimum attack damage will be 1. The only Metal monsters are Metaly, Mettable, MetalKing, GoldSlime, and GranSlime.

Healing Skills, No Attribute;
Heal (Spell, 2) - This will restore one ally's HP by 30-40 points.
HealMore (Spell, 5) - This will restore one ally's HP by 75-90 points.
HealAll (Spell, 7) - This will fully restore one ally's HP.
HealUs (Spell, 18) - This will restore all ally's HP by 75-90 points.
HealUsAll (Spell, 36) - This will fully restore all ally's HP.
Vivify (Spell, 10) - This will revive one ally with half of their HP, may fail. The success rate is 50/100.
Revive (Spell, 20) - This will revive one ally with all of their HP.
Farewell (Spell, 32) - This will revive all allies with all of their HP, instant death for user. (May survive with 1 HP?)
Hustle (Dance, 12) - This will restore all ally's HP by 70-80 points.
LifeDance (Dance, All) - This will revive all allies with all of their HP, instant death for user. (May survive with 1 HP?)
Meditate (None, 8) - This will restore the user's HP by 500 points.
LoveRain (None, 28) - This will restore all ally's HP by random{20-100%} of their max HP at the start of the user's next turn, may fail. The success rate is unknown, but is likely to be 40/100, 50/100, or 60/100.
LifeSong (None, 20) - This will revive all allies with all of their HP at the start of the user's next turn, may fail. The success rate is unknown, but is likely to be 40/100, 50/100, or 60/100.

MP Skills, No Attribute;
MPass (Spell, 20) - This will restore one ally's MP by 15 points.
MPassmore (Spell, 40) - This will restore one ally's MP by 30 points.
MPassmost (Spell, 100) - This will restore one ally's MP by 80 points.
TakeMagic (Spell, 2) - This will restore the user's MP by the MP cost of any skill that affects it for this round of battle, damage is applied normally. This will not restore MP if the user does not take damage from a skill.

Purge Skills, No Attribute;
Antidote (Spell, 2) - This will remove the Poison and/or Venom debuff from one ally.
DeChaos (Spell, 2) - This will remove the Confusion debuff from all allies.
NumbOff (Spell, 2) - This will remove the Paralysis debuff from all allies.
CurseOff (Spell, 2) - This will remove the Curse debuff from all allies.
Surge (None, 7) - This will remove the Poison, Confusion, Paralysis and Curse debuff from all allies.
DeMagic (None, 7) - This will remove the effects of TakeMagic, TwinHits, MagicWall, Barrier, Upper, Increase, Speed, SpeedUp, MagicBack, Bounce, Ironize, Transform, BeDragon, Surround, Sleep, SleepAll, StopSpell, PanicAll, Sap, Defense, Slow, and SlowAll from all enemies.
ThickFog (None, 8) - This will remove the effects of TakeMagic, TwinHits, MagicWall, Barrier, Upper, Increase, Speed, SpeedUp, MagicBack, Bounce, Ironize, Transform, BeDragon, Surround, Sleep, SleepAll, StopSpell, PanicAll, Sap, Defense, Slow, and SlowAll from all allies and enemies. All Spell skills used afterwards are blocked when used. This effect lasts for 3 rounds of battle.
SealPray (None, 15) - This will seal the next skill used on the user. A skill that is sealed will be nullified when used, by ally or enemy. There can only be one skill sealed at a time. Only one skill may be sealed during battle, by ally or enemy. If another skill is sealed while there is a sealed skill, the sealed skill will be released and usable again.

Buff Skills, No Attribute;
MagicWall (Spell, 3) - This will apply the MagicWall buff to all allies. A monster with this buff will have a damage multiplier of 0.5 applied to any Spell skill that affects it, after the damage is calculated.
Barrier (Spell, 3) - This will apply the Barrier buff to all allies. A monster with this buff will have a damage multiplier of 0.5 appliedto any Breath skill that affects it, after the damage is calculated.
MagicBack (Spell, 4) - This will apply the MagicBack buff to the user. A monster with this buff will redirect the next Spell skill that affects it back to the skill's user, will return any enemy or ally Spell skills! The status is removed afterwards.
Bounce (Spell, 4) - This will apply the Bounce buff to the user. A monster with this buff will redirect any Spell skill that affects it back to the skill's user, will return any enemy or ally Spell skills!
AquaWall (None, 5) - This will apply the AquaWall buff to itself. A monster with this buff will be unaffected by the next enemy attack or skill that affects it. The status is removed afterwards.
Ironize (Spell, 2) - This will apply the Ironize buff to all allies. A monster with this buff is immune to all attacks, skills, effects of skills, and current debuffs, but cannot act. This buff will be removed after 3 turns of inaction.

Stat Mod. Skills, No Attribute;
Upper (Spell, 2) - This will increase one ally's DEF by 50% of their base DEF, can be used twice successively or more if the ally's DEF is decreased. Stats cannot be raised above 999.
Increase (Spell, 3) - This will increase all ally's DEF by 50% of their base DEF, can be used twice successively or more if the ally's DEF is decreased. Stats cannot be raised above 999.
Speed (Spell, 2) - This will Increase one ally's AGI by 50% of their default AGI, can be used twice successively or more if the ally's AGI is decreased. Stats cannot be raised above 999.
SpeedUp (Spell, 3) - This will increase all ally's AGI by 50% of their default AGI, can be used twice successively or more if the ally's AGI is decreased. Stats cannot be raised above 999.

Unique Skills, No Attribute;
Transform (Spell, 5) - This will transform the user into one enemy. The user's skills, resistances and stats are changed to the enemy target, bonuses from items are reapplied afterwards.
*BeDragon (Spell, 9) - This will transform...
*TatsuCall (None, 20) - Summon...
*DiagoCall (None, 20) - Summon...
*SamsiCall (None, 20) - Summon...
*BazooCall (None, 20) - Summon...
Chance (Spell, 20) - This will randomly trigger one of the following effects;

1. Restores all ally's HP by 100%. (9%)
2. Revive all allies with 100% HP. (9%)
3. ThickFog is used. (8%)
4. Party is full of power. All allies will critical on their next normal attack or Physical skill. (11%)
5. Inflict the Sleep status to all allies and enemies, lasts for up to 2 turns, ignores resistances. (6%)
6. Reduce all allies and enemies MP to 0, ignores resistances. (6%)
7. Nothing happens. (18%)
8. BeDragon is used. (2%)
9. A Genie attacks all enemies. (17%)
10. Inflict the Stun status to all enemies, lasts for one turn, ignores resistances. (6%)
11. Restore all ally's MP by 100%. (3%)
12. Reduce all allies and enemies HP to 1, ignore resistances. (5%)
The percentages are based off a test sampling of 100 uses.

Fire1 Skills, Attribute A
Blaze (Spell, 2) - This will inflict (12-15 x resistance) points of damage to one enemy.
Blazemore (Spell, 4) - This will inflict (70-90 x resistance) points of damage to one enemy.
Blazemost (Spell, 10) - This will inflict (180-200 x resistance) points of damage to one enemy.
BigBang (None, 30) - This will inflict (300-400 x resistance) points of damage to all enemies.
FireSlash (Physical, 3) - This will attack one enemy, attack misses if enemy's A resistance is 3. A damage multiplier equal to the enemy's A resistance multiplier is applied to the attack, after damage calculation.

Fire2 Skills, Attribute B
Firebal (Spell, 4) - This will inflict (16-24 x resistance) points of damage to all enemies.
Firebane (Spell, 6) - This will inflict (30-40 x resistance) points of damage to all enemies.
Firebal (Spell, 10) - This will inflict (88-112 x resistance) points of damage to all enemies.

Explosion Skills, Attribute C
Bang (Spell, 5) - This will inflict (20-30 x resistance) points of damage to all enemies.
Boom (Spell, 8) - This will inflict (52-68 x resistance) points of damage to all enemies.
Explodet (Spell, 15) - This will inflict (130-150 x resistance) points of damage to all enemies.

Wind Skills, Attribute D
Infernos (Spell, 2) - This will inflict (8-24 x resistance) points of damage to all enemies.
Infermore (Spell, 4) - This will inflict (25-55 x resistance) points of damage to all enemies.
Infermost (Spell, 8) - This willnflict (80-180 x resistance) points of damage to all enemies.
*WindBeast (None, 3) - This will inflict ([Lv + ?] x resistance, max 180?) points of damage to one enemy.
*Vacuum (None, 6) - This will inflict ([Lv + ?] x resistance, max 180?) points of damage to all enemies.
MultiCut (None, 20) - This will inflict (180-210 x resistance or [180-210 x resistance] x 1.5 against Zombie type) points of damage to all enemies.
VacuSlash (Physical, 3) - (Physical, 3) - This will attack one enemy, attack misses if enemy's D resistance is 3. A damage multiplier equal to the enemy's D resistance multiplier is applied to the attack, after damage calculation.

Lightning Skills, Attribute E
Bolt (Spell, 5) - This will inflict (35-50 x resistance) points of damage to all enemies.
Zap (Spell, 10) - This will inflict (45-75 x resistance) points of damage to all enemies.
Thordain (Spell, 15) - This will inflict (175-225 x resistance) points of damage to all enemies.
*Lightning (None, 3) - This will inflict ([? + Lv/?] x resistance, max 70?) points of damage to all enemies.
Hellblast (None, 25) - This will inflict (210-290 x resistance) points of damage to all enemies.
BoltSlash (Physical, 3) - This will attack one enemy, attack misses if enemy's E resistance is 3. A damage multiplier equal to the enemy's E resistance multiplier is applied to the attack, after damage calculation.

Ice 1 Skills, Attribute F
IceBolt (Spell, 3) - This will inflict (25-35 x resistance) points of damage to one enemy.
SnowStorm (Spell,5) - This will inflict (42-58 x resistance) points of damage to one enemy.
Blizzard (Spell, 12) - This will inflict (80-104 x resistance) points of damage to one enemy.
IceSlash (Physical, 3) - This will attack one enemy, attack misses if enemy's F resistance is 3. A damage multiplier equal to the enemy's F resistance multiplier is applied to the attack, after damage calculation.

Blind Skills, Attribute G
Surround (Spell, 3) - This will inflict the Blind debuff to one enemy.
SandStorm (None, 2) - This will inflict the Blind debuff to one enemy.
Radiant (None, 2) - This will inflict the Blind debuff to one enemy.
A monster with the Blind debuff will have a miss rate of 2/3 for all of their attacks and physical skills.

Sleep Skills, Attribute H
Sleep (Spell, 3) - This will inflict the Sleep debuff to one enemy.
SleepAll (Spell, 5) - This will inflict the Sleep debuff to all enemies.
SleepAir (Breath, 3) - This will inflict the Sleep debuff to all enemies.
NapAttack (Physical, 2) - This will attack one enemy, attack misses if enemy's H resistance is 3. The enemy will be inflicted with the Sleep debuff if the attack does damage, checks enemy's H resistance before applying.
A monster with the Sleep debuff will be unable to act for 2 turns. They have a 50% chance to recover each turn or when attacked.

Death/Debuff Skills, Attribute I
Beat (Spell, 4) - This will reduce one enemy's HP to 0.
Defeat (Spell, 7) - This will reduce all enemy's HP to 0.
K.O.Dance (Dance, 6) - This will reduce one enemy's HP to 0.
EerieLite (None, 2) - This will inflict the EerieLite debuf to all enemies. A monster with this debuff will have a damage multiplier of 1.5 applied to any Spell skill that affects it, after the damage is calculated.
UltraDown (None, 7) - This will apply the effects of Surround, Slow, and Sap to one enemy, only checks the enemy's I resistance.
The success rate for these skills is equal to the enemy's I resistance.

MP Drain Skills, Attribute J
RobMagic (Spell, 0) - This will absorb the MP of one enemy by (1-8 x resistance).
RobDance (Dance, 0) - This will absorb the MP of one enemy by (1-8 x resistance).
OddDance (Dance, 0) - Reduce the MP of one enemy by (1-8 x resistance).

Anti-Spell Skills, Attribute K
StopSpell (Spell, 3) - This will inflict the StopSpell debuff to all enemies. A monster with this debuff will have all of their Spell skills blocked when used.

Confusion Skills, Attribute L
PanicAll (Spell, 5) - This will inflict the Confusion debuff to all enemies.
PaniDance (Dance, 4) - This will inflict the Confusion debuff to all enemies.
A monster with the Confusion debuff will have a 50% chance to attack a random enemy or ally during their turn, otherwise they act normally.

DEF Mod Skills, Attribute M
Sap (Spell, 3) - This will decrease one enemy's DEF stat by 50% of their default DEF, can be used twice successively or more if the enemy's DEF is increased. Stats cannot be lower than 1.
Defense (Spell, 4) - This will decrease all enemy's DEF stat by 50% of their default DEF, can be used twice successively or more if the enemy's DEF is increased. Stats cannot be lower than 1.
SickLick (None, 4) - This will inflict the Stun debuff to one enemy and reduce their DEF to 1. A monster with this debuff will be unable to act on their next turn. The debuff is removed afterwards.
The success rate for these skills is equal to the enemy's M resistance.

AGI Mod Skills, Attribute N
Slow (Spell, 3) - This will decrease one enemy's AGI stat by 50% of their default AGI, can be used twice successively or more if the enemy's AGI is increased. Stats cannot be lower than 1.
SlowAll (Spell, 4) - This will decrease all enemy's AGI stat by 50% of their default AGI, can be used twice successively or more if the enemy's AGI is increased. Stats cannot be lower than 1.
The success rate for these skills is equal to the enemy's N resistance.

Suicide Skills, Attribute O
Sacrifice (Spell, 1) - This will reduce all enemies HP to 0-1, instant death for user. (May survive with 1 HP?)
Ramming (None, 1) - This will reduce the user and one enemy's HP by 80%(?) of their current HP.
Kamikaze (None, 1) - This will reduce the user and one enemy's HP to 0-1(?).
The success rate for these skills is equal to the enemy's O resistance.

Ultimate Skills, Attribute P
MegaMagic (None, All) - This will inflict ([(MP+Lv) x 2] x resistance) points of damage to all enemies. This is the only skill that monsters can't have a resistance of 3 for. The maximum resistance for this skill is 2, without cheating/glitches. Against a resistance of 0, 1, and 2 this skill will inflict a maximum of 2196, 1464, and 732 points of damage, respectively. This requires a monster at Lv 99 with 999 MP to achieve.
This skill uses the success rate multiplier for its damage multiplier.

Breathe Fire Skills, Attribute Q
FireAir (Breath, 2) - This will inflict (14-22 x resistance) points of damage to all enemies.
BlazeAir (Breath, 4) - This will inflict (32-48 x resistance) points of damage to all enemies.
Scorching (Breath, 8) - This will inflict (75-100 x resistance) points of damage to all enemies.
WhiteFire (Breath, 16) - This will inflict (150-170 x resistance) points of damage to all enemies.

Breathe Ice Skills, Attribute R
FrigidAir (Breath, 2) - This will inflict (16-24 x resistance) points of damage to all enemies.
IceAir (Breath, 4) - This will inflict (42-54 x resistance) points of damage to all enemies.
IceStorm (Breath, 8) - This will inflict (82-112 x resistance) points of damage to all enemies.
WhiteAir (Breath, 16) - This will inflict (160-180 x resistance) points of damage to all enemies.

Poison Skills, Attribute S
PoisonGas (Breath, 3) - Inflict the Poison debuff to all enemies. The debuff is removed after battle.
PoisonAir (Breath, 4) - Inflict the Poison status to all enemies.
PoisonHit (Physical, 2) - This will attack one enemy, attack misses if enemy's S resistance is 3. The enemy will be inflicted with the Poison debuff if the attack does damage, checks enemy's S resistance before applying.
A monster with the Poison debuff will lose min{max{1,MaxHP/16}, 50} points of HP after each of their turns. This debuff persists after battle, reducing the monster's HP by 1 point for each step it takes.

Paralysis Skills, Attribute T
PalsyAir (Breath, 4) - Inflict the Paralysis status to all enemies.
Paralyze (Physical, 3) - This will attack one enemy, attack misses if enemy's T resistance is 3. The enemy will be inflicted with the Paralysis debuff if the attack does damage, checks enemy's T resistance before applying.
A monster with the Paralysis debuff will be unable to act. If all of your monsters have this debuff, the battle immediately ends and your party is considered to be wiped out. This debuff persists after battle.

Curse Skills, Attribute U
Curse (U, None/3) - Inflict the Curse debuff to all enemies.
A monster with the Curse debuff will have a chance of a random effect occuring during their turn, otheriwse they act normally. This debuff persists after battle.

Effect 1 - The monster will be unable to act.
Effect 2 - The monster will lose min{max{1,MaxHP/16}, 50} points of HP before they act.

Inaction Skills, Attribute V
Ahhh (None, 1) - If the user is male, this will inflict ((ATK - DEF/2)/4) points of damage to one enemy. If the user is female, this will inflict the Stun debuff to one enemy.
LushLicks(None, 2) - This will inflict the Stun debuff to one enemy.
LegSweep (None, 1) - This will inflict the Stun debuff to one enemy.
BigTrip (None, 3) - This will inflict the Stun debuff to all enemies.
WarCry (None, 3) - This will inflict the Stun debuff to all enemies.
LureDance (Dance, 2) - This will inflict the Stun debuff to all enemies.
A monster with the Stun debuff will be unable to act on their next turn. The debuff is removed afterwards.

Anti-Dance Skills, Attribute W
DanceShut (Dance, 6) - This will inflict the DanceShut debuff to all enemies.
A monster with the DanceShut debuff will have all of their Dance skills blocked when used.

Anti-Breathe Skills, Attribute X
MouthShut (None, 6) - This will inflict the MouthShut debuff to one enemy.
A monster with the Mouthshut debuff will have all of their Breath skills blocked when used.

Nature Skills, Attribute Y
*RockThrow (None, 5) - This will inflict ([? + Lv/?] x resistance, max 130?) points of damage to all enemies.
*CallHelp (None, 4) - This will inflict ([Lv + 20-40?] x resistance) points of damage to one random enemy 1 to 4 times, all hits will miss if the enemy's Y resistance is 3.
*YellHelp (None, 8) - This will inflict ([Lv + 20-40?] x resistance) points of damage to one random enemy 1 to 8 times, all hits will miss if the enemy's Y resistance is 3.

Giga Skills, Attribute Z
Gigaslash (None, 20) - This will inflict (350-410 x resistance) points of damage to one enemy.

Water Skills, Attribute Water
*Geyser (None, 2) - This will remove one enemy from the battle for one round of battle. When the monster returns, there is a chance to inflict ([1/8 x MaxHP] x resistance) points of damage upon their return. This skill will always miss if the enemy's Water resistance is 3. The success rate is unknown, but is likely to be 40/100, 50/100, or 60/100.
Watershot (None, 5) - This will inflict (30-40 x resistance) points of damage to one enemy.
Tidalwave (None, 15) - This will inflict (120-160 x resistance) points of damage to one enemy.

*I will expand on it in a later version.

=== END SECTION ===

=== SECTION: version-updates ===
URL: https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461/version-updates
TITLE: Version Updates

Version Updates

Version 1.1
I added the evasion, critical attacks, and critical attributes section. I also better formatted my list of battle skills.

=== END SECTION ===

