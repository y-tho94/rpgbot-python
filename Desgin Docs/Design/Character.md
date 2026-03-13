Characters are player agents that will interact with the game world. They will have inherent stats and derived stats, as well as an equipped inventory and a stored inventory. Each player will only be allowed a max of 1 character per account (for now)

Inherent Stats:
* Strength
* Dexterity
* Endurance
* Intelligence
* Faith
* Luck

Derived Stats (based stat):
* Attack Damage (Strength + Dexterity + gear)
* Damage Reduction (gear)
* Spell Damage (Intelligence or Faith depending on spell cast)
* Maximum Ability Points/Mana (Higher of Intelligence vs Faith + Endurance)
* Current Ability Points/Mana (Max AP - Abilities used)
* Maximum Hit Points (Endurance + gear)
* Current Hit Points (Max HP - damage accrued)
* Evasion (Dexterity + Luck + gear)
* Inventory Space (higher of Strength vs Intelligence)
	* Number of items a player can carry in their stored inventory
* Ability Inventory (Higher of Intelligence vs Faith)
	* Number of Abilities/Spells a player can know
* Crit Chance (Luck + Faith)

CHARACTER CREATION
---
Inherent stats will be randomized on character creation using values from 3-18 (simulating a 3d6 roll). This could be changed in the future to allow from a selection from one of a predetermined template of stats, aka **Class**. Characters will also start with a random equipped inventory, 100 gold, and 1 ability/spell

INVENTORY
---
Characters will have 3 types of inventory. Equipped, Stored, and Ability
* Equipped: Gear that will influence derived stats
	* Gold
	* Head
	* Body
	* Legs
	* Hand 1
	* Hand 2
	* 2 Accessories
* Stored: Gear that has no influence on derived stats
* Ability: Spells and special moves 
Inventory will be stored in the database as JSON with the following schema
{
	"Equipped" : {
		"Gold" : integer
		"Head" : {
			"Name" : string
			"Effects" : []
		},
		"Body" : {
			"Name" : string
			"Effects" : []
		},
		"Legs" : {
			"Name" : string
			"Effects" : []
		},
		"Hand1" : {
			"Name" : string
			"Effects" : []
		},
		"Hand2" : {
			"Name" : string
			"Effects" : []
		},
		"Accessory1" : {
			"Name" : string
			"Effects" : []
		},
		"Accessory2" : {
			"Name" : string
			"Effects" : []
		}
	},
	"Stored" : [
		"Name" : string
		"Type" : string
		"Effects" : []
	],
	"Abilities":[
		{
			"Name" : string
			 "Cost" : integer
			 "Effects" : []
		}
	]
}

-CHARACTER MANAGEMENT
A player may manage their inventory at any time. Once management is done, all derived stats will be calculated and stored in cache. Any inventory changes will be backed up to the database
