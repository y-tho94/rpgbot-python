from data.dataContext import AbilityTable
import random

class Ability():
    def __init__(self, Name:str = "", Description:str = "", Cost:int = 0, Type:str = "", Effects:dict = None):
        self.Name = Name
        self.Description = Description
        self.Cost = Cost
        self.Type = Type
        self.Effects = AbilityEffects(**Effects) if Effects is not None else AbilityEffects()

    def to_dict(self):
        return {
            "Name": self.Name,
            "Description": self.Description,
            "Cost": self.Cost,
            "Type": self.Type,
            "Effects": self.Effects.to_dict()
        }

    def fromAbilityTable(self, at:AbilityTable):
        self.Name = at.name
        self.Description = at.description
        self.Type = at.type
        self.Cost = at.cost

        effectsDict = at.baseEffects
        baseEffects = AbilityEffects(**effectsDict)
        self.Effects.Type = baseEffects.Type
        self.Effects.Heal = self._applyVariance(baseEffects.Heal, at.baseVariance)
        self.Effects.SelfHeal = self._applyVariance(baseEffects.SelfHeal, at.baseVariance)
        self.Effects.Inflict = self._applyVariance(baseEffects.Inflict, at.baseVariance)
        self.Effects.SelfInflict = self._applyVariance(baseEffects.SelfInflict, at.baseVariance)
        self.Effects.Boost = baseEffects.Boost
        self.Effects.Debuff = baseEffects.Debuff
        return self

    @staticmethod
    def _applyVariance(stat:int, variance: int):
        if stat == 0: 
            return 0
        rand = random.randint(variance * -1, variance)
        return stat + rand

class AbilityEffects():
    def __init__(self, Type:str="", SelfHeal:int = 0, Heal:int=0, SelfInflict:int = 0, Inflict:int=0, Boost:list = [], Debuff:list = [] ):
        self.Type = Type
        self.SelfHeal = SelfHeal
        self.SelfInflict = SelfInflict
        self.Heal = Heal
        self.Inflict = Inflict
        self.Boost = Boost
        self.Debuff = Debuff

    def to_dict(self):
        return {
            "Type": self.Type,
            "SelfHeal": self.SelfHeal,
            "Heal": self.Heal,
            "SelfInflict": self.SelfInflict,
            "Inflict": self.Inflict,
            "Boost": self.Boost,
            "Debuff": self.Debuff
        }