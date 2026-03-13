from data.dataContext import Context, LootTable
from models.loot import Loot, Effect
import json
from sqlalchemy.orm import Session
from sqlalchemy import select
import random

class LootService():
    def __init__(self, db: Context):
        self.db = db.engine

    def GenerateLoot(self, lootName:str):
        session = Session(bind=self.db)
        statement = select(LootTable).filter_by(name = lootName)
        lootObj = None
        try:
            lootObj = session.scalars(statement).first()
        except Exception as ex:
            print(ex)
        finally:
            session.close()

        if lootObj is None:
            print("oops")
            return None

        loot = Loot()
        loot.Name = lootObj.Name
        loot.Description = lootObj.Description
        loot.Type = lootObj.Type

        effectsDict = json.loads(lootObj.baseEffects)
        baseEffects = Effect(**effectsDict)
        loot.Effects.Type = baseEffects.Type
        loot.Effects.AttackRating = self._applyVariance(baseEffects.AttackRating, lootObj.baseVariance)
        loot.Effects.DamageReduction = self._applyVariance(baseEffects.DamageReduction, lootObj.baseVariance)
        loot.Effects.SpellDamage = self._applyVariance(baseEffects.SpellDamage, lootObj.baseVariance)
        loot.Effects.MaxAP = self._applyVariance(baseEffects.MaxAP, lootObj.baseVariance)
        loot.Effects.MaxHP = self._applyVariance(baseEffects.MaxHP, lootObj.baseVariance)
        loot.Effects.Evasion = self._applyVariance(baseEffects.Evasion, lootObj.baseVariance)
        loot.Effects.Heal = self._applyVariance(baseEffects.Heal, lootObj.baseVariance)
        loot.Effects.CritChance = self._applyVariance(baseEffects.CritChance, lootObj.baseVariance)
        loot.Effects.Use = baseEffects.Use

        return loot

    @staticmethod
    def _applyVariance(stat:int, variance: int):
        if stat == 0: 
            return 0
        rand = random.randint(variance * -1, variance)
        return stat + rand

