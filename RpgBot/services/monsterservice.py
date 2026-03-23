from data.dataContext import Context, MonsterTable
from models.monster import Monster
from services.cacheService import SimpleCache
from services.characterService import CharacterService
from sqlalchemy.orm import Session
from sqlalchemy import select, update
import random

class MonsterService:
    def __init__(self, db:Context, cache:SimpleCache, monsterCache:SimpleCache, characterService:CharacterService):
        self.db = db.engine
        self.cache = cache
        self.monsterCache = monsterCache
        self.characterService = characterService
        return

    #get monster from db then save it to monster cache and return it
    async def GetMobMonster(self):
        statement = select(MonsterTable).filter_by(type = "mob")

        session = Session(bind=self.db)
        try:
            monsters = session.execute(statement).scalars()
            session.close()
            if monsters is None: 
                return None

            monsterObj = random.choice(monsters)

            monster = Monster().fromMonsterTable(monsterObj)
            self.monsterCache.set("mob", monster)
            return monster
        except Exception as ex:
            print(ex)
            return None
            