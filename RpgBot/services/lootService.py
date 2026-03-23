from data.dataContext import AbilityTable, Context, LootTable
from models.loot import Loot
from sqlalchemy.orm import Session
from sqlalchemy import select
import random

class LootService():
    def __init__(self, db: Context):
        self.db = db.engine
    
    async def GenerateLoot(self):
        session = Session(bind=self.db)
        statement = select(LootTable)
        try:
            lootPossibilities = session.execute(statement).scalars().all()
            lootObj = random.choice(lootPossibilities)
            session.close()

            if lootObj is None: 
                return None

            loot = Loot().fromLootTable(lootObj)
            if loot.Name == "Skill Scroll":
                loot = await self._generateScroll(loot)
            return loot

        except Exception as ex:
            session.close()
            print(ex)


    async def GenerateLootByName(self, lootName:str):
        session = Session(bind=self.db)
        statement = select(LootTable).filter_by(name = lootName)
        try:
            lootObj = session.execute(statement).scalars().first()
            session.close()

            if lootObj is None: 
                return None

            loot = Loot().fromLootTable(lootObj)

            if lootName == "Skill Scroll":
                loot = await self._generateScroll(loot)
            return loot

        except Exception as ex:
            session.close()
            print(ex)
    
    async def GenerateLootByType(self, lootType:str):
        session = Session(bind=self.db)
        statement = select(LootTable).filter_by(type = lootType)
        try:
            lootPossibilities = session.execute(statement).scalars().all()
            lootObj = random.choice(lootPossibilities)
            session.close()

            if lootObj is None: 
                return None

            loot = Loot().fromLootTable(lootObj)
            if loot.Name == "Skill Scroll":
                loot = await self._generateScroll(loot)
            return loot

        except Exception as ex:
            session.close()
            print(ex)


    async def GenerateStartingLoot(self):
        startingInv = []
        startingInv.append(await self.GenerateLootByType("Head"))
        startingInv.append(await self.GenerateLootByType("Body"))
        startingInv.append(await self.GenerateLootByType("Legs"))
        startingInv.append(await self.GenerateLootByType("Hand"))
        startingInv.append(await self.GenerateLootByType("Accessory"))

        return startingInv

    async def _generateScroll(self, loot:Loot):
        session = Session(bind=self.db)
        statement = select(AbilityTable)

        abilities = session.execute(statement).scalars().all()
        ability = random.choice(abilities)
        session.close()

        abilityName = ability.name

        learnEffect = loot.Effects.Use[0]
        learnEffect = learnEffect.replace("***", abilityName)
        loot.Effects.Use[0] = learnEffect
        loot.Name = f"{abilityName} Scroll"
        return loot

