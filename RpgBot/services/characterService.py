from models.character import Character, Inventory
from models.loot import Loot
from data.dataContext import Context, CharacterTable
from services.cacheService import SimpleCache
import json
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from services.lootService import LootService

class CharacterService():
    def __init__(self, db: Context, cache: SimpleCache, lootService: LootService):
        self.db = db.engine
        self.cache = cache
        self.lootService = lootService

    def CreateNewCharacter(self, chname: str, player: str):
        ch = Character.new(self=Character(), name=chname)
        ch.Inventory.Equipped = self.lootService.GenerateStartingLoot()
        ch.Inventory = self.checkInventoryForDuplicates(ch.Inventory)

        chTable = CharacterTable(
            playerName = player,
            charName = ch.Name,
            strength = ch.Strength,
            dexterity = ch.Dexterity,
            endurance = ch.Endurance,
            intelligence = ch.Intelligence,
            faith = ch.Faith,
            luck = ch.Luck,
            inventory = {
                "Equipped":[item.to_dict() for item in ch.Inventory.Equipped],
                "Stored": [item.to_dict() for item in ch.Inventory.Stored],
                "Ability": [item.to_dict() for item in ch.Inventory.Ability],
            }
        )

        session = Session(bind=self.db)
        statement = select(CharacterTable).filter_by(playerName=player)
        existing = session.execute(statement).scalars().first()
        if existing is None: 
            session.add(chTable)
        else:
            statement = update(CharacterTable).where(CharacterTable.id == existing.id).values(
                charName = chTable.charName,
                strength = chTable.strength,
                dexterity = chTable.dexterity,
                endurance = chTable.endurance,
                intelligence = chTable.intelligence,
                faith = chTable.faith,
                luck = chTable.luck,
                inventory = chTable.inventory 
            )
            session.execute(statement)
        session.commit()
        session.close()

        self.deriveStats(ch)

        self.cache.set(player, ch)
        return ch

    def GetCharacter(self, playerName:str):
        session = Session(bind=self.db)
        statement = select(CharacterTable).filter_by(playerName=playerName)
        charObj = session.execute(statement).scalars().first()
        session.close()

        if charObj is None:
            print(f"Character for player {playerName} not found")
            return Character()

        ch = Character()
        ch.Name = charObj.charName
        ch.Strength = charObj.strength 
        ch.Dexterity = charObj.dexterity
        ch.Endurance = charObj.endurance
        ch.Intelligence = charObj.intelligence
        ch.Faith = charObj.faith
        ch.Luck = charObj.luck
        inv = Inventory()
        inv.Equipped = [Loot(**item) for item in charObj.inventory["Equipped"]]
        inv.Stored = [Loot(**item) for item in charObj.inventory["Stored"]]
        inv.Ability = [Loot(**item) for item in charObj.inventory["Ability"]]
        ch.Inventory = inv

        self.deriveStats(ch)
        self.cache.set(playerName, ch)
        return ch
    
    def UnequipItem(self, player:str, itemName:str):
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
        
        character.Inventory = self.checkInventoryForDuplicates(character.Inventory)

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

        self.deriveStats(character)
        self.cache.set(player, character)

        return character

    def EquipItem(self, player:str, itemName:str):
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

        
        character.Inventory = self.checkInventoryForDuplicates(character.Inventory)

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

        self.deriveStats(character)
        self.cache.set(player, character)

    #calculates derived stats
    @staticmethod
    def deriveStats(ch:Character):
        strMod = (ch.Strength - 10) // 2
        dexMod = (ch.Dexterity - 10) // 2
        endMod = (ch.Endurance - 10) // 2
        intMod = (ch.Intelligence - 10) // 2
        fthMod = (ch.Faith - 10) // 2
        luckMod = (ch.Luck - 10) // 2

        ch.AttackRating = strMod if strMod > dexMod else dexMod
        ch.MaxHP = 10 + endMod
        ch.MaxAP = 10 + intMod
        ch.Evasion = 10 + dexMod
        ch.MaxInventory = ch.Strength if ch.Strength > ch.Intelligence else ch.Intelligence
        ch.MaxAbilities = ch.Faith if ch.Faith > ch.Intelligence else ch.Intelligence
        ch.CritChance = ch.Luck + fthMod

        equipped = ch.Inventory.Equipped
        for i in equipped:
            effects = i.Effects
            ch.AttackRating += effects.AttackRating
            ch.DamageReduction += effects.DamageReduction
            ch.SpellDamage += effects.SpellDamage
            ch.MaxHP += effects.MaxHP
            ch.MaxAP += effects.MaxAP
            ch.Evasion += effects.Evasion
            ch.CritChance += effects.CritChance
            
        ch.CurrentHP = ch.MaxHP
        ch.CurrentAP = ch.MaxAP
    
    @staticmethod
    def checkInventoryForDuplicates(inv:Inventory):
        equipped = inv.Equipped
        stored = inv.Stored
        ability = inv.Ability

        for item in equipped:
            #get list of all items with the same name
            duplicates = list(filter(lambda i: i.Name == item.Name, equipped))

            #if more than one item with the same name...
            if len(duplicates) > 1:
                #loop through inventory and rename the item
                dupName = item.Name
                dupCount = 0
                for dup in equipped:
                    if dup.Name == dupName:
                        dup.Name += f" ({dupCount})"
                        dupCount += 1
        
        for item in stored:
            #get list of all items with the same name
            duplicates = list(filter(lambda i: i.Name == item.Name, stored))

            #if more than one item with the same name...
            if len(duplicates) > 1:
                #loop through inventory and rename the item
                dupName = item.Name
                dupCount = 0
                for dup in stored:
                    if dup.Name == dupName:
                        dup.Name += f" ({dupCount})"
                        dupCount += 1
        
        for item in ability:
            #get list of all items with the same name
            duplicates = list(filter(lambda i: i.Name == item.Name, ability))

            #if more than one item with the same name...
            if len(duplicates) > 1:
                #loop through inventory and rename the item
                dupName = item.Name
                dupCount = 0
                for dup in ability:
                    if dup.Name == dupName:
                        dup.Name += f" ({dupCount})"
                        dupCount += 1
        
        return inv
