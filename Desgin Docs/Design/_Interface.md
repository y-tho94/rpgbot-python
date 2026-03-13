The primary interface for this project is intended to be a discord bot. As such, players will input commands directly as server messages.

The structure of commands should follow a template of `[command] [target]`

List of commands
---
* Management: commands to managed a player character. Ideally this would be in a DM to the bot
	* `/create "[character name]"`: creates a new character with the given name. Deletes existing character.
	* `/view stats`: shows all character stats 
	* Items
		* `/view [equipment|inventory|abilities]`: displays a list of items in selected inventory
		* `/equip "[item name]"`: equips an item from the stored inventory to appropriate location. Unequips item in current slot(s) and moves it to stored inventory
		* `/use "[item name|ability]" self`: applies the "use" effects of an item or ability to oneself
		* `/drop "[item name]"`: discards the item from the inventory
		* `/inspect "[item name]"`: Shows the description and list of effects of an item
		* `/rename "[item name]" "[new name]"`: Changes the name of an item to a new name
* Player to player: interactions between players in general chat
	* `/give "[player name]" "gold" [ammount]`: Subtracts gold from player inventory and gives to target player
	* `/give "[player name]" "[item name]"`: Gives target player item from stored inventory
	* `/attack "[player name]"`: Applies attack rating to target player
	* `/use "[item name|ability]" "[player name]"`: Applies item's/ability's "use" effects to  target player
* Monster: commands for interaction with monsters
	* `/attack "[monster name]"`: Applies attack rating to target monster
		* add `--auto` to continuously attack until monster is defeated
	* `/use "[item name|ability]" "[monster name]"`: Applies item's/ability's "use" effects to  target monster
	* `/flee "[monster name]"`: removes player from monster's interaction list
