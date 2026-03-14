from data.dataContext import Context, LootTable
from models.loot import Loot, Effect
import json
from sqlalchemy.orm import Session
from sqlalchemy import select
import random

class LootService():
    def __init__(self, db: Context):
        self.db = db.engine
    
    def GenerateLoot(self):
        session = Session(bind=self.db)
        statement = select(LootTable)
        try:
            lootPossibilities = session.execute(statement).scalars().all()
            lootObj = random.choice(lootPossibilities)
            session.close()

            if lootObj is None: 
                return None

            loot = Loot().fromLootTable(lootObj)
            return loot

        except Exception as ex:
            session.close()
            print(ex)


    def GenerateLootByName(self, lootName:str):
        session = Session(bind=self.db)
        statement = select(LootTable).filter_by(name = lootName)
        try:
            lootObj = session.execute(statement).scalars().first()
            session.close()

            if lootObj is None: 
                return None

            loot = Loot().fromLootTable(lootObj)
            return loot

        except Exception as ex:
            session.close()
            print(ex)
    
    def GenerateLootByType(self, lootType:str):
        session = Session(bind=self.db)
        statement = select(LootTable).filter_by(type = lootType)
        try:
            lootPossibilities = session.execute(statement).scalars().all()
            lootObj = random.choice(lootPossibilities)
            session.close()

            if lootObj is None: 
                return None

            loot = Loot().fromLootTable(lootObj)
            return loot

        except Exception as ex:
            session.close()
            print(ex)


    def GenerateStartingLoot(self):
        session = Session(bind=self.db)
        startingInv = []
        startingInv.append(self.GenerateLootByType("Head"))
        startingInv.append(self.GenerateLootByType("Body"))
        startingInv.append(self.GenerateLootByType("Legs"))
        startingInv.append(self.GenerateLootByType("Hand"))
        startingInv.append(self.GenerateLootByType("Hand"))

        return startingInv


