import json


class Loot():
    def __init__(self):
        self.Name = ""
        self.Description = ""
        self.Type = ""
        self.Effects = Effect()

    def to_dict(self):
        return {
            "Name": self.Name,
            "Description": self.Description,
            "Type": self.Type,
            "Effects": self.Effects.to_dict()
        }

class Effect():
    def __init__(self):
        self.Type = ""
        self.AttackRating = 0
        self.DamageReduction = 0
        self.Evasion = 0
        self.Heal = 0
        self.CritChance = 0
        self.SpellDamage = 0
        self.MaxHP = 0
        self.MaxAP = 0
        self.Use = []

    def __init__(self, ltype:str, ar:int, dr:int, ev:int, heal:int, cc:int, sd:int, mhp:int, lmap:int, use:str):
        self.Type = ltype
        self.AttackRating = ar
        self.DamageReduction = dr
        self.Evasion = ev
        self.Heal = heal
        self.CritChance = cc
        self.SpellDamage = sd
        self.MaxHP = mhp
        self.MaxAP = lmap
        self.Use = json.loads(use)

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