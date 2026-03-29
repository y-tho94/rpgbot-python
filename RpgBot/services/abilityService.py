from copy import deepcopy
from data.dataContext import AbilityTable, CharacterTable, Context
from models.character import Character
from services.cacheService import SimpleCache
from models.ability import Ability
from sqlalchemy.orm import Session
from sqlalchemy import select, update
import random

class AbilityService():
    def __init__(self, db:Context, cache:SimpleCache, systemCache:SimpleCache):
        self.db = db.engine
        self.cache = cache
        self.systemCache = systemCache

        return

    async def GetSetCache(self):
        abilities = deepcopy(self.systemCache.get("Abilities"))
        if abilities is None:
            session = Session(bind=self.db)
            statement = select(AbilityTable)
            try:
                abilitiesLocal = session.execute(statement).scalars().all()
                session.close()
                self.systemCache.set("Abilities", abilitiesLocal)
                return deepcopy(abilitiesLocal)
            except Exception as ex:
                session.close()
                print(ex)
        else:
            return abilities

    async def GenerateAbility(self):
        possibilities = await self.GetSetCache()

        abilityObj = random.choice(possibilities)
        if abilityObj is None: 
            return None

        ability = Ability().fromAbilityTable(abilityObj)
        return ability

    async def GenerateAbilityByName(self, abilityName:str):
        abilities = await self.GetSetCache()
        
        abilityObj = list(filter(lambda i: i.name == abilityName, abilities))

        if abilityObj is None: 
            return None

        ability = Ability().fromAbilityTable(abilityObj[0])
        return ability

    async def ShowAbilityList(self, player:str):
        character = self.cache.get(player) or Character()
        inv = character.Inventory

        return {
            "AP": f"{character.MaxAP} / {character.CurrentAP}",
            "Ability": [f"{item.Name} | {item.Cost}" for item in inv.Ability]
        }

    async def DescribeAbility(self, ability:Ability):
        abilityDict = ability.to_dict()
        effects = ability.Effects.to_dict()
        for key, value in ability.Effects.to_dict().items():
            if value == 0 or value == [] or value == "":
                del effects[key]

        abilityDict["Effects"] = effects
        return abilityDict

    async def LearnAbility(self, player:str, ability:Ability):
        character = self.cache.get(player) or Character()

        if character.MaxAbilities > len(character.Inventory.Ability):
            character.Inventory.Ability.append(ability)
            session = Session(bind = self.db)
            chTable = character.ToCharacterTable(player)

            statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
            session.execute(statement)
            session.commit()
            session.close()
            
            self.cache.set(player, character)
            
            return f"{character.Name} learned {ability.Name}"
        else:
            return f"{character.Name} could not learn {ability.Name} because they know too many"

    async def ForgetAbility(self, player:str, abilityName:str):
        character = self.cache.get(player) or Character()

        abilityToForget = list(filter(lambda i: i.Name == abilityName, character.Inventory.Ability))
        if len(abilityToForget) == 0:
            return {
                "Error": f"No ability '{abilityName}' in abilities"    
            }

        character.Inventory.Ability.remove(abilityToForget[0])
        character.Inventory.checkInventoryForDuplicates()

        session = Session(bind = self.db)
        chTable = character.ToCharacterTable(player)

        statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
        session.execute(statement)
        session.commit()
        session.close()

        self.cache.set(player, character)
        return

    async def RenameAbility(self, player:str, abilityName:str, newAbilityName:str):
        character = self.cache.get(player)

        itemToRename = list(filter(lambda i: i.Name == abilityName, character.Inventory.Ability))
        if len(itemToRename) == 0:
            return {
                "Error": f"No ability '{abilityName}' in abilities"    
            }

        itemToRename[0].Name = newAbilityName
        character.Inventory.checkInventoryForDuplicates()

        session = Session(bind = self.db)
        chTable = character.ToCharacterTable(player)

        statement = update(CharacterTable).where(CharacterTable.playerName == player).values(inventory = chTable.inventory)
        session.execute(statement)
        session.commit()
        session.close()

        self.cache.set(player, character)
        return

