from data.dataContext import AbilityTable, CharacterTable, Context
from models.character import Character
from services.cacheService import SimpleCache
from models.ability import Ability
from sqlalchemy.orm import Session
from sqlalchemy import select, update
import random

class AbilityService():
    def __init__(self, db:Context, cache:SimpleCache):
        self.db = db.engine
        self.cache = cache

        return

    async def GenerateAbility(self):
        session = Session(bind=self.db)
        statement = select(AbilityTable)
        try:
            possibilities = session.execute(statement).scalars().all()
            abilityObj = random.choice(possibilities)
            session.close()

            if abilityObj is None: 
                return None

            ability = Ability().fromAbilityTable(abilityObj)
            return ability

        except Exception as ex:
            session.close()
            print(ex)

        return

    async def GenerateAbilityByName(self, abilityName:str):
        session = Session(bind=self.db)
        statement = select(AbilityTable).filter_by(name = abilityName)
        try:
            abilityObj = session.execute(statement).scalars().first()
            session.close()

            if abilityObj is None: 
                return None

            ability = Ability().fromAbilityTable(abilityObj)
            return ability

        except Exception as ex:
            session.close()
            print(ex)
            return None
    
    async def ShowAbilityList(self, player:str):
        character = self.cache.get(player) or Character()
        inv = character.Inventory

        return {
            "Ability": [item.Name for item in inv.Ability]
        }

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
            return f"{character.Name} could not learn {ability.Name}"

    async def ForgetAbility(self, player:str, abilityName:str):
        character = self.cache.get(player) or Character()

        abilityToForget = list(filter(lambda i: i.Name == abilityName, character.Inventory.Ability))
        if len(abilityToForget) == 0:
            return {
                "Error": "No ability of that name in abilities"    
            }

        character.Inventory.Ability = [ability for ability in character.Inventory.Ability if ability.Name != abilityName]
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
                "Error": "No ability of that name in abilities"    
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

