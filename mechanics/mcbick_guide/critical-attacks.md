# Critical Attacks

> Source: McBick "Advanced Skill Guide" FAQ #78461, v1.1 (Neoseeker mirror)
> GameFAQs section URL: https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/78461/critical-attacks
> Neoseeker mirror URL: https://www.neoseeker.com/dwm2/faqs/3080761-dragon-quest-monsters-2-cobis-journey-advanced-skill.html (single-page)

---

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
