Loot is in theory designed to be the main draw of the game and will feature heavy randomization and a myriad of effects.

Loot comes in 4 forms: 
* Equipment: Gear that influences stats in combat
* Consumables: Gear that can be used for a one time effect
* Gold: Primary currency among players
* Abilities: "scrolls" that can be used to learn a special ability or spell

All loot will have the following in the database:
* Name
* Description
* Type (equipment location, consumable, ability)
* Base Variance
	* In order to keep loot drops exciting, numbers in the Effects will vary on a range equal to -Base Variance to +Base Variance
* Base Effects
	* List of common traits across all instances of this loot drop


**Effects**
Effects are to be stored as JSON detailing a list of how exactly a piece of gear (equipment or consumable) or ability influences derived character stats (See Character).

**Loot Generation**
---
When a piece of loot is generated, the following will happen:
1) Determine if player has ample inventory space
2) Determine loot drop
3) Fetch loot data from the database
4) Apply variance to numeric values in base effects
5) Add generated loot to player stored inventory

Example loot:
---
Name: Sword
Description: "A length of blade affixed to a one-handed handle"
Type: Hand
Base Variance: 2
Base Effects: {
	"Type" : slashing
	"AttackDamage" : 10 (could be range of 8 to 12)
}