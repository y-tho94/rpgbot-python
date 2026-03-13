A monster is the primary antagonist of the game. Monsters are a collection of stats that will act against the Character in an attempt to defeat them. For now, monsters will only attack the player until I can think of a way to make a more robust "AI" rubric a monster can follow

Monster Stats
---
* Name: Monster name
* HP: Base hit points of a monster
* Attack Rating: How much damage a monster will do per attack
* Damage Reduction: How much damage will be prevented when the player attacks
* Evasion: Chance to avoid damage entirely
* Weakness: Effect Type that will cause 2x damage
* Resistance: Effect Type that will cause .5x damage
* XP: Function of HP, AR, DR, EVA. Total XP rewards to players who defeat the monster
* Base Variance: Variance applied to monster stats on generation
* Loot Table: A monster has a chance to drop any item listed in here

Monster Derived Stats
---
The following stat block will be cached after a monster is generated
* Name
* HP: After variance applied
* Attack Rating: After variance applied
* Damage Reduction: After variance applied
* Evasion: After variance applied
* Weakness
* Resistance
* XP
* Players Engaging: List of players who have interacted with the monster

Monster Generation
---
1) Monster appears
2) Monster data is pulled from database
3) Apply variance
4) Cache result