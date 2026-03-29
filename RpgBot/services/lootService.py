from copy import deepcopy
from data.dataContext import AbilityTable, Context, LootTable, RaidLootTable, SpecialLootTable
from models.loot import Effect, Loot
from sqlalchemy.orm import Session
from sqlalchemy import select
import random

from services.cacheService import SimpleCache

class LootService():
    def __init__(self, db: Context, systemCache:SimpleCache):
        self.db = db.engine
        self.systemCache = systemCache
    
    async def GetSetCache(self):
        lootPossibilities =  self.systemCache.get("Loot")
        if lootPossibilities is None:
            session = Session(bind=self.db)
            statement = select(LootTable)
            try:
                lootPossibilitiesLocal = session.execute(statement).scalars().all()
                session.close()
                self.systemCache.set("Loot", lootPossibilitiesLocal)
            except Exception as ex:
                session.close()
                print(ex)
        
        specialLootPossibilities = self.systemCache.get("SpecialLoot")
        if specialLootPossibilities is None:
            session = Session(bind=self.db)
            statement = select(SpecialLootTable)
            try:
                specialLootPossibilitiesLocal = session.execute(statement).scalars().all()
                session.close()
                self.systemCache.set("SpecialLoot", specialLootPossibilitiesLocal)
            except Exception as ex:
                session.close()
                print(ex)
        raidLootPossibilities = self.systemCache.get("RaidLoot")
        if raidLootPossibilities is None:
            session = Session(bind=self.db)
            statement = select(RaidLootTable)
            try:
                raidLootPossibilitiesLocal = session.execute(statement).scalars().all()
                session.close()
                self.systemCache.set("RaidLoot", raidLootPossibilitiesLocal)
            except Exception as ex:
                session.close()
                print(ex)

    async def GenerateLoot(self):
        lootPossibilities = deepcopy(self.systemCache.get("Loot"))

        if lootPossibilities is None:
            await self.GetSetCache()
            lootPossibilities =  deepcopy(self.systemCache.get("Loot"))

        lootObj = random.choice(lootPossibilities)
        if lootObj is None: 
            return None

        loot = Loot().fromLootTable(lootObj)
        if loot.Name == "Skill Scroll":
            lootScroll = await self._generateScroll(loot)
            return lootScroll
        return loot

    
    async def GenerateSpecialLoot(self):
        lootPossibilities = deepcopy(self.systemCache.get("SpecialLoot"))
        if lootPossibilities is None:
            await self.GetSetCache()
            lootPossibilities =  deepcopy(self.systemCache.get("SpecialLoot"))

        lootObj = random.choice(lootPossibilities)
        if lootObj is None: 
            return None

        loot = Loot().fromSpecialLootTable(lootObj)
        return loot
    
    async def GenerateRaidLoot(self):
        lootPossibilities = deepcopy(self.systemCache.get("RaidLoot"))

        if lootPossibilities is None:
            await self.GetSetCache()
            lootPossibilities =  deepcopy(self.systemCache.get("RaidLoot"))

        lootObj = random.choice(lootPossibilities)
        if lootObj is None: 
            return None
        loot = Loot().fromRaidLootTable(lootObj)
        return loot

    async def GenerateLootByName(self, lootName:str):
        lootPossibilities = deepcopy(self.systemCache.get("Loot"))

        if lootPossibilities is None:
            await self.GetSetCache()
            lootPossibilities =  deepcopy(self.systemCache.get("Loot"))
            
        lootObjList = list(filter(lambda i: i.name == lootName, lootPossibilities))
        if lootObjList is None or len(lootObjList) == 0: 
            return None
        loot = Loot().fromLootTable(lootObjList[0])
        if lootName == "Skill Scroll":
            lootScroll = await self._generateScroll(loot)
            return lootScroll
        return loot
    

    async def GenerateSpecialLootByName(self, lootName:str):
        lootPossibilities =  deepcopy(self.systemCache.get("SpecialLoot"))

        if lootPossibilities is None:
            await self.GetSetCache()
            lootPossibilities =  deepcopy(self.systemCache.get("SpecialLoot"))

        lootObjList = list(filter(lambda i: i.name == lootName, lootPossibilities))
        if lootObjList is None or len(lootObjList) == 0: 
            return None
        loot = Loot().fromSpecialLootTable(lootObjList[0])
        return loot

    async def GenerateRaidLootByName(self, lootName:str):
        lootPossibilities =  deepcopy(self.systemCache.get("RaidLoot"))

        if lootPossibilities is None:
            await self.GetSetCache()
            lootPossibilities =  deepcopy(self.systemCache.get("RaidLoot"))
            
        lootObj = list(filter(lambda i: i.name == lootName, lootPossibilities))
        if lootObj is None: 
            return None
        loot = Loot().fromRaidLootTable(lootObj[0])
        return loot
    
    async def GenerateLootByType(self, lootType:str):
        lootPossibilities = deepcopy(self.systemCache.get("Loot"))

        if lootPossibilities is None:
            await self.GetSetCache()
            lootPossibilities =  deepcopy(self.systemCache.get("Loot"))

        lootObj = list(filter(lambda i: i.type == lootType, lootPossibilities))
        if lootObj is None: 
            return None
        lootObj = random.choice(lootObj)
        loot = Loot().fromLootTable(lootObj)
        if loot.Name == "Skill Scroll":
            newloot = await self._generateScroll(loot)
            return newloot
        return loot
    
    async def GenerateSpecialLootByType(self, lootType:str):
        lootPossibilities =  deepcopy(self.systemCache.get("SpecialLoot"))

        if lootPossibilities is None:
            await self.GetSetCache()
            lootPossibilities =  deepcopy(self.systemCache.get("SpecialLoot"))

        lootObj = list(filter(lambda i: i.type == lootType, lootPossibilities))
        if lootObj is None: 
            return None
        lootObj = random.choice(lootObj)
        loot = Loot().fromSpecialLootTable(lootObj)
        return loot
    
    async def GenerateRaidLootByType(self, lootType:str):
        lootPossibilities =  deepcopy(self.systemCache.get("RaidLoot"))

        if lootPossibilities is None:
            await self.GetSetCache()
            lootPossibilities =  deepcopy(self.systemCache.get("RaidLoot"))

        lootObj = list(filter(lambda i: i.type == lootType, lootPossibilities))
        if lootObj is None: 
            return None
        lootObj = random.choice(lootObj)
        loot = Loot().fromRaidLootTable(lootObj)
        return loot

    async def GenerateStartingLoot(self):
        startingInv = []
        startingInv.append(await self.GenerateLootByType("Head"))
        startingInv.append(await self.GenerateLootByType("Body"))
        startingInv.append(await self.GenerateLootByType("Legs"))
        startingInv.append(await self.GenerateLootByType("Hand"))
        startingInv.append(await self.GenerateLootByType("Accessory"))

        return startingInv

    async def _generateScroll(self, loot:Loot):
        abilities = deepcopy(self.systemCache.get("Abilities"))

        if abilities is None:
            session = Session(bind=self.db)
            statement = select(AbilityTable)

            abilities = session.execute(statement).scalars().all()
            session.close()

            self.systemCache.set("Abilities", abilities)
                    
        ability = random.choice(abilities)
        abilityName = ability.name

        newLoot = loot
        newLoot.Description = loot.Description
        newLoot.Type = loot.Type
        newLoot.Effects = Effect(**loot.Effects.to_dict()) 

        learnEffect = newLoot.Effects.Use[0]
        learnEffect = f"Learn {abilityName}"
        newLoot.Effects.Use[0] = learnEffect
        newLoot.Name = f"{abilityName} Scroll"
        return newLoot

