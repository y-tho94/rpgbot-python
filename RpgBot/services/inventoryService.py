from models.character import Character
from models.loot import Loot
from services.cacheService import SimpleCache
from services.abilityService import AbilityService
from data.dataContext import Context, CharacterTable
from sqlalchemy.orm import Session
from sqlalchemy import update

class InventoryService():
    def __init__(self, db: Context, cache: SimpleCache, abilityService: AbilityService):
        self.db = db.engine
        self.cache = cache
        self.abilityService = abilityService
        return

    
    async def ShowInventorySimple(self, player:str):
        character = self.cache.get(player)

        inv = character.Inventory

        return {
            "Gold": inv.Gold,
            "XP": inv.XP,
            "Equipped": [item.Name for item in inv.Equipped],
            "Stored": [item.Name for item in inv.Stored]
        }

    async def DescribeItem(self, item:Loot):
        itemdict = item.to_dict()
        effects = item.Effects.to_dict()
        for key, value in item.Effects.to_dict().items():
            if value == 0 or value == [] or value == "":
                del effects[key]

        itemdict["Effects"] = effects
        return itemdict

    async def UnequipItem(self, player:str, itemName:str):
        character = self.cache.get(player)

        if character.Inventory.Stored.count == character.MaxInventory:
            return {
                "Error": "No room in stored inventory"
            }

        itemToUnequip = list(filter(lambda i: i.Name == itemName, character.Inventory.Equipped))
        if len(itemToUnequip) == 0:
            return {
                "Error": "Item doesn't exist in equipped inventory"
            }

        character.Inventory.Equipped.remove(itemToUnequip[0])
        character.Inventory.Stored.append(itemToUnequip[0])
        character.Inventory.checkInventoryForDuplicates()

        session = Session(bind = self.db)
        chTable = character.ToCharacterTable(player)

        statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
        session.execute(statement)
        session.commit()
        session.close()

        character.deriveStats()
        self.cache.set(player, character)

        return

    async def EquipItem(self, player:str, itemName:str):
        character = self.cache.get(player)

        itemToEquip = list(filter(lambda i: i.Name == itemName, character.Inventory.Stored))
        if len(itemToEquip) == 0:
            return {
                "Error": "No item of that name in inventory"    
            }

        itemType = itemToEquip[0].Type
        if itemType == "Consumable":
            return {
                "Error": "Consumable items cannot be equipped"    
            }

        #check to see if type is already equipped
        availableSlots = 2 if itemType == "Accessory" else 1
        slotIsFree = len(list(filter(lambda i: i.Type == itemType, character.Inventory.Equipped))) < availableSlots
        if slotIsFree == False:
            return {
                "Error": f"Slot unavailable. Unequip item in {itemType}"   
            }

        character.Inventory.Stored.remove(itemToEquip[0])
        character.Inventory.Equipped.append(itemToEquip[0])
        character.Inventory.checkInventoryForDuplicates()

        session = Session(bind = self.db)
        chTable = character.ToCharacterTable(player)

        statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
        session.execute(statement)
        session.commit()
        session.close()

        character.deriveStats()
        self.cache.set(player, character)

        return

    async def SwapItem(self, player:str, itemName:str):
        character = self.cache.get(player) or Character()
        
        itemToEquip = list(filter(lambda i: i.Name == itemName, character.Inventory.Stored))
        if len(itemToEquip) == 0:
            return {
                "Error": "No item of that name in inventory"    
            }

        itemType = itemToEquip[0].Type
        if itemType == "Consumable":
            return {
                "Error": "Consumable items cannot be equipped"    
            }

        itemToUnequip = list(filter(lambda i: i.Type == itemType, character.Inventory.Equipped))
        if len(itemToUnequip) > 0:
            character.Inventory.Stored.append(itemToUnequip[0])
            character.Inventory.Equipped.remove(itemToUnequip[0])

        character.Inventory.Equipped.append(itemToEquip[0])
        character.Inventory.Stored.remove(itemToEquip[0])
        character.Inventory.checkInventoryForDuplicates()
       
        session = Session(bind = self.db)
        chTable = character.ToCharacterTable(player)

        statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
        session.execute(statement)
        session.commit()
        session.close()

        character.deriveStats()
        self.cache.set(player, character)

    async def DiscardItem(self, player:str, itemName:str):
        character = self.cache.get(player) or Character()

        itemToDrop = list(filter(lambda i: i.Name.startswith(itemName), character.Inventory.Stored))
        if len(itemToDrop) == 0:
            return {
                "Error": "No item of that name in inventory"    
            }

        if itemToDrop[0].Type == "Consumable":
            itemTokens = itemToDrop[0].Name.split()
            try:
                amount = int(itemTokens[-1])
                amount -= 1
                if amount == 0:
                    character.Inventory.Stored.remove(itemToDrop[0])
                else:
                    itemTokens[-1] = str(amount)
                    itemToDrop[0].Name = " ".join(itemTokens)
            except:
                character.Inventory.Stored.remove(itemToDrop[0])
        else:
            character.Inventory.Stored.remove(itemToDrop[0])
        
        character.Inventory.checkInventoryForDuplicates()

        session = Session(bind = self.db)
        chTable = character.ToCharacterTable(player)

        statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
        session.execute(statement)
        session.commit()
        session.close()

        self.cache.set(player, character)

        return
    
    async def GiveGold(self, player:str, targetPlayer:str, amount:int):
        ch = self.cache.get(player)
        target = self.cache.get(targetPlayer)

        playerGold = ch.Inventory.Gold
        if playerGold < amount:
            return {
                "Error": "Insufficient gold to give"    
            }
        if amount <= 0:
            return {
                "Error": "Can not give less than 1 gold"
            }

        ch.Inventory.Gold -= amount
        target.Inventory.Gold += amount

        session = Session(bind = self.db)
        try:
            chTable = ch.ToCharacterTable(player)
            statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
            session.execute(statement)

            targetTable = target.ToCharacterTable(targetPlayer)
            statement = update(CharacterTable).where(CharacterTable.playerName == targetPlayer).values(inventory = targetTable.inventory)
            session.execute(statement)

            session.commit()
            self.cache.set(player, ch)
            self.cache.set(targetPlayer, target)
        except Exception as ex:
            print(ex)
            session.rollback()
            return {
                "Error": "Trade could not be completed"    
            }
        session.close()

        return
    
    async def AdminGiveGold(self, targetPlayer:str, amount:int):
        target = self.cache.get(targetPlayer)

        target.Inventory.Gold += amount

        session = Session(bind = self.db)
        try:
            targetTable = target.ToCharacterTable(targetPlayer)
            statement = update(CharacterTable).where(CharacterTable.playerName == targetPlayer).values(inventory = targetTable.inventory)
            session.execute(statement)

            session.commit()
            self.cache.set(targetPlayer, target)
        except Exception as ex:
            print(ex)
            session.rollback()
            return {
                "Error": "Trade could not be completed"    
            }
        session.close()

        return

    async def GiveItem(self, player:str, targetPlayer:str, itemName:str):
        ch = self.cache.get(player)
        target = self.cache.get(targetPlayer)

        if len(target.Inventory.Stored) + 1 == target.MaxInventory:
            return {
                "Error": "No room in target's stored inventory"
            }

        itemToGive = list(filter(lambda i: i.Name == itemName, ch.Inventory.Stored))
        if len(itemToGive) == 0:
            return {
                "Error": "No item of that name in inventory"    
            }

        ch.Inventory.Stored.remove(itemToGive[0])
        target.Inventory.Stored.append(itemToGive[0])
        target.Inventory.checkInventoryForDuplicates()

        session = Session(bind = self.db)
        try:
            chTable = ch.ToCharacterTable(player)
            statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
            session.execute(statement)

            targetTable = target.ToCharacterTable(player)
            statement = update(CharacterTable).where(CharacterTable.playerName == targetPlayer).values(inventory = targetTable.inventory)
            session.execute(statement)

            session.commit()
            self.cache.set(player, ch)
            self.cache.set(targetPlayer, target)
        except Exception as ex:
            print(ex)
            session.rollback()
            return {
                "Error": "Trade could not be completed"    
            }
        session.close()

        return

    async def RenameItem(self, player:str, itemName:str, newItemName:str):
        character = self.cache.get(player)

        itemToRename = list(filter(lambda i: i.Name == itemName, character.Inventory.Stored))
        if len(itemToRename) == 0:
            return {
                "Error": "No item of that name in stored inventory"    
            }

        itemType = itemToRename[0].Type
        if itemType == "Consumable":
            return {
                "Error": "Consumable items cannot be renamed"
            }

        itemToRename[0].Name = newItemName
        character.Inventory.checkInventoryForDuplicates()

        session = Session(bind = self.db)
        chTable = character.ToCharacterTable(player)

        statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
        session.execute(statement)
        session.commit()
        session.close()

        self.cache.set(player, character)
        return

    async def UseItem(self, player:str, target:str, itemName:str):
        character = self.cache.get(player) or Character()
        targetCh = self.cache.get(target) or Character()

        # Check for exact match first
        itemToUse = list(filter(lambda i: i.Name == itemName, character.Inventory.Stored))
        if len(itemToUse) == 0:
            # If no exact match
            itemToUse = list(filter(lambda i: i.Name.startswith(itemName), character.Inventory.Stored))
        else:
            return {
                "Error": f"No item '{itemName}' in stored inventory"    
            }

        item = itemToUse[0] or Loot()
        useEffects = item.Effects.Use

        if len(useEffects) == 0:
            return {
                "Error": f"{itemName} has no on-use effects"    
            }
        
        summary = []
        for e in useEffects:
            tokens = e.split()
            effect = tokens[0]

            match effect:
                case "Heal":
                    amount = int(tokens[1])
                    newHP = targetCh.CurrentHP + amount
                    targetCh.CurrentHP = newHP if newHP <= targetCh.MaxHP else targetCh.MaxHP
                    summary.append(f"{character.Name} healed {targetCh.Name} for {amount} HP")
                case "Replenish":
                    amount = int(tokens[1])
                    newAP = targetCh.CurrentAP + amount
                    targetCh.CurrentAP = newAP if newAP <= targetCh.MaxAP else targetCh.MaxAP
                    summary.append(f"{character.Name} replenished {targetCh.Name} for {amount} AP")
                case "Learn":
                    abilityName = tokens[1]
                    ability = await self.abilityService.GenerateAbilityByName(abilityName)
                    if ability is not None:
                        summary.append(await self.abilityService.LearnAbility(target, ability))
                case "Inflict":
                    amount = int(tokens[1])
                    dmgType = tokens[2]
                    newHP = targetCh.CurrentHP - amount
                    targetCh.CurrentHP = newHP if newHP >= 0 else 0
                    summary.append(f"{character.Name} inflicted {amount} {dmgType} damage to {targetCh.Name}")
                case "Buff":
                    stat = tokens[1]
                    amount = int(tokens[2])
                    match stat:
                        case "AttackRating":
                            targetCh.Buffs.AttackRating += amount
                        case "DamageReduction":
                            targetCh.Buffs.DamageReduction += amount
                        case "Evasion":
                            targetCh.Buffs.Evasion += amount
                        case "SpellDamage":
                            targetCh.Buffs.SpellDamage += amount
                        case "CritChance":
                            targetCh.Buffs.CritChance += amount
                    targetCh.deriveStats()
                    summary.append(f"{character.Name} buffed {targetCh.Name}'s {stat} by {amount}")
                case "Debuff":
                    stat = tokens[1]
                    amount = int(tokens[2])
                    match stat:
                        case "AttackRating":
                            targetCh.Buffs.AttackRating -= amount
                        case "DamageReduction":
                            targetCh.Buffs.DamageReduction -= amount
                        case "Evasion":
                            targetCh.Buffs.Evasion -= amount
                        case "SpellDamage":
                            targetCh.Buffs.SpellDamage -= amount
                        case "CritChance":
                            targetCh.Buffs.CritChance -= amount
                    targetCh.deriveStats()
                    summary.append(f"{character.Name} debuffed {targetCh.Name}'s {stat} by {amount}")
                case "Cleanse":
                    targetCh.Buffs.AttackRating = 0
                    targetCh.Buffs.DamageReduction = 0
                    targetCh.Buffs.Evasion = 0
                    targetCh.Buffs.SpellDamage = 0
                    targetCh.Buffs.CritChance = 0
                    targetCh.Buffs.MaxHP = 0
                    targetCh.Buffs.MaxAP = 0

                    targetCh.deriveStats()
                    summary.append(f"{character.Name} cleansed all buffs and debuffs from {targetCh.Name}")
                case _:
                    summary.append(f"{effect} is not a valid effect")
            
        self.cache.set(target, targetCh)
        return {
            "Summary" : summary    
        }