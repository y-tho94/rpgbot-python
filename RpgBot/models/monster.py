
import random
from data.dataContext import MonsterTable


class Monster():
    def __init__(self, Name="", Type="", Weakness=[], Resistance=[], Hp=0, AttackRating=0, DamageReduction=0, Evasion=0, CritChance=0, Ai:dict={}, DropTable:dict={}):
        self.Name = Name
        self.Type = Type
        self.Weakness = Weakness
        self.Resistance = Resistance
        self.MaxHP = Hp
        self.HP = Hp
        self.AttackRating = AttackRating
        self.DamageReduction = DamageReduction
        self.Evasion = Evasion
        self.CritChance = CritChance
        self.AI = MonsterAI(**Ai) if Ai is not None else MonsterAI()
        self.DropTable = DropTable
        self.InteractingPlayers = []

    def to_dict(self):
        return {
            "Name": self.Name,
            "Type": self.Type,
            "Weakness": self.Weakness,
            "Resistance": self.Resistance,
            "MaxHP": self.MaxHP,
            "HP": self.HP,
            "AttackRating": self.AttackRating,
            "DamageReduction": self.DamageReduction,
            "Evasion": self.Evasion,
            "CritChance": self.CritChance,
            "AI": self.AI.__dict__(),
            "DropTable": self.DropTable.__dict__()
        }

    def FromMonsterTable(self, mt:MonsterTable):
        self.Name = mt.name
        self.Type = mt.type
        self.Weakness = mt.weakness
        self.Resistance = mt.resistance
        self.MaxHP = self._applyVariance(mt.hp, mt.baseVariance)
        self.HP = self.MaxHP
        self.AttackRating = self._applyVariance(mt.attackRating, mt.baseVariance)
        self.DamageReduction = self._applyVariance(mt.damageReduction, mt.baseVariance)
        self.Evasion = self._applyVariance(mt.evasion, mt.baseVariance)
        self.CritChance = self._applyVariance(mt.critChance, mt.baseVariance)
        self.AI = MonsterAI(**mt.ai)
        self.DropTable = DropTable(**mt.dropTable)
        self.InteractingPlayers = []
        return self

    def ToMonsterTable(self):
        return MonsterTable(
            name = self.Name,
            type = self.Type,
            weakness = self.Weakness,
            resistance = self.Resistance,
            hp = self.HP,
            attackRating = self.AttackRating,
            damageReduction = self.DamageReduction,
            evasion = self.Evasion,
            critChance = self.CritChance,
            ai = self.AI,
            dropTable = self.DropTable
        )

    
    @staticmethod
    def _applyVariance(stat:int, variance: int):
        if stat == 0: 
            return 0
        rand = random.randint(variance * -1, variance)
        return stat + rand

class DropTable():
    def __init__(self, Gold:int=0, XP:int=0, Loot:list=[], SpecialLoot:list=[], RaidLoot:list=[]):
        self.Gold = Gold
        self.XP = XP
        self.Loot = Loot
        self.SpecialLoot = SpecialLoot
        self.RaidLoot = RaidLoot

class MonsterAI():
    def __init__(self, Actions:list = []):
        self.Actions = [MonsterAIAction(**a) for a in Actions]


class MonsterAIAction():
    def __init__(self, HPThreshold=0, Action:list=[]):
        self.HPThreshold = HPThreshold
        self.Action = Action