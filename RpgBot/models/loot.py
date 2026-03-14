import json
import random
from data.dataContext import LootTable


class Loot():
    def __init__(self, Name:str = "", Description:str = "", Type:str = "", Effects:dict = None):
        self.Name = Name
        self.Description = Description
        self.Type = Type
        self.Effects = Effect(**Effects) if Effects is not None else Effect()

    def to_dict(self):
        return {
            "Name": self.Name,
            "Description": self.Description,
            "Type": self.Type,
            "Effects": self.Effects.to_dict()
        }

    def fromLootTable(self, lt:LootTable):
        self.Name = lt.name
        self.Description = lt.description
        self.Type = lt.type

        effectsDict = lt.baseEffects
        baseEffects = Effect(**effectsDict)
        self.Effects.Type = baseEffects.Type
        self.Effects.AttackRating = self._applyVariance(baseEffects.AttackRating, lt.baseVariance)
        self.Effects.DamageReduction = self._applyVariance(baseEffects.DamageReduction, lt.baseVariance)
        self.Effects.SpellDamage = self._applyVariance(baseEffects.SpellDamage, lt.baseVariance)
        self.Effects.MaxAP = self._applyVariance(baseEffects.MaxAP, lt.baseVariance)
        self.Effects.MaxHP = self._applyVariance(baseEffects.MaxHP, lt.baseVariance)
        self.Effects.Evasion = self._applyVariance(baseEffects.Evasion, lt.baseVariance)
        self.Effects.Heal = self._applyVariance(baseEffects.Heal, lt.baseVariance)
        self.Effects.CritChance = self._applyVariance(baseEffects.CritChance, lt.baseVariance)
        self.Effects.Use = baseEffects.Use

        return self
    
    @staticmethod
    def _applyVariance(stat:int, variance: int):
        if stat == 0: 
            return 0
        rand = random.randint(variance * -1, variance)
        return stat + rand

class Effect():
    def __init__(self, Type:str="", AttackRating:int=0, DamageReduction:int=0, Evasion:int=0, Heal:int=0, CritChance:int=0, SpellDamage:int=0, MaxHP:int=0, MaxAP:int=0, Use:list=[]):
        self.Type = Type
        self.AttackRating = AttackRating
        self.DamageReduction = DamageReduction
        self.Evasion = Evasion
        self.Heal = Heal
        self.CritChance = CritChance
        self.SpellDamage = SpellDamage
        self.MaxHP = MaxHP
        self.MaxAP = MaxAP
        self.Use = Use

    def to_dict(self):
        return {
            "Type": self.Type,
            "AttackRating": self.AttackRating,
            "DamageReduction": self.DamageReduction,
            "Evasion": self.Evasion,
            "Heal": self.Heal,
            "CritChance": self.CritChance,
            "SpellDamage": self.SpellDamage,
            "MaxHP": self.MaxHP,
            "MaxAP": self.MaxAP,
            "Use": self.Use
        }