from services.cacheService import SimpleCache
from data.dataContext import Context, CharacterTable
from sqlalchemy.orm import Session
from sqlalchemy import update

class InventoryService():
    def __init__(self, db: Context, cache: SimpleCache):
        self.db = db.engine
        self.cache = cache
        return

    
    async def ShowInventorySimple(self, player:str):
        character = self.cache.get(player)

        inv = character.Inventory

        return {
            "Equipped": [item.Name for item in inv.Equipped],
            "Stored": [item.Name for item in inv.Stored],
            "Ability": [item.Name for item in inv.Ability]
        }


    async def UnequipItem(self, player:str, itemName:str):
        character = self.cache.get(player)

        if character.Inventory.Stored.count == character.MaxInventory:
            print("Item cannot be unequipped")
            return

        itemToUnequip = list(filter(lambda i: i.Name == itemName, character.Inventory.Equipped))
        if len(itemToUnequip) == 0:
            print("Item doesn't exist in equipped inventory")
            return character

        character.Inventory.Equipped = [item for item in character.Inventory.Equipped if item.Name != itemName]
        character.Inventory.Stored.append(itemToUnequip[0])
        
        character.Inventory.checkInventoryForDuplicates()

        session = Session(bind = self.db)
        chTable = CharacterTable(
            playerName = player,
            charName = character.Name,
            strength = character.Strength,
            dexterity = character.Dexterity,
            endurance = character.Endurance,
            intelligence = character.Intelligence,
            faith = character.Faith,
            luck = character.Luck,
            inventory = {
                "Equipped":[item.to_dict() for item in character.Inventory.Equipped],
                "Stored": [item.to_dict() for item in character.Inventory.Stored],
                "Ability": [item.to_dict() for item in character.Inventory.Ability],
            }
        )

        statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
        session.execute(statement)
        session.commit()
        session.close()

        character.deriveStats()
        self.cache.set(player, character)

        return character

    async def EquipItem(self, player:str, itemName:str):
        character = self.cache.get(player)

        itemToEquip = list(filter(lambda i: i.Name == itemName, character.Inventory.Stored))
        if len(itemToEquip) == 0:
            return {
                "Error": "No item of that name in inventory"    
            }

        itemType = itemToEquip[0].Type
        #check to see if type is already equipped
        slotIsFree = False
        if itemType == "Hand":
            slotIsFree = len(list(filter(lambda i: i.Type == itemType, character.Inventory.Equipped))) < 2
        else:
            slotIsFree = len(list(filter(lambda i: i.Type == itemType, character.Inventory.Equipped))) == 0
        
        if slotIsFree == False:
            return {
                "Error": f"Slot unavailable. Unequip item in {itemType}"   
            }

        character.Inventory.Stored = [item for item in character.Inventory.Stored if item.Name != itemName]
        character.Inventory.Equipped.append(itemToEquip[0])

        
        character.Inventory.checkInventoryForDuplicates()

        session = Session(bind = self.db)
        chTable = CharacterTable(
            playerName = player,
            charName = character.Name,
            strength = character.Strength,
            dexterity = character.Dexterity,
            endurance = character.Endurance,
            intelligence = character.Intelligence,
            faith = character.Faith,
            luck = character.Luck,
            inventory = {
                "Equipped":[item.to_dict() for item in character.Inventory.Equipped],
                "Stored": [item.to_dict() for item in character.Inventory.Stored],
                "Ability": [item.to_dict() for item in character.Inventory.Ability],
            }
        )

        statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
        session.execute(statement)
        session.commit()
        session.close()

        character.deriveStats()
        self.cache.set(player, character)

        return

    