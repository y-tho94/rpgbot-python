from copy import deepcopy
import random
import time
import math
from data.dataContext import CharacterTable
from models.ability import Ability
from models.loot import Loot

class Character:
    #default constructor
    def __init__(self):
        #inherent stats
        self.Name = ""
        self.Strength = 0
        self.Dexterity = 0
        self.Endurance = 0
        self.Intelligence = 0
        self.Faith = 0
        self.Luck = 0

        #derived stats
        self.Level = 0
        self.NextXPtoLevel = 0
        self.AttackRating = 0
        self.DamageReduction = 0
        self.SpellDamage = 0
        self.MaxHP = 0
        self.CurrentHP = 0
        self.MaxAP = 0
        self.CurrentAP = 0
        self.Evasion = 0
        self.MaxInventory = 0
        self.MaxAbilities = 0
        self.CritChance = 0

        self.Weakness = []
        self.Resistance = []

        #inventory
        self.InventoryCap = 16
        self.Inventory = Inventory()
        self.Buffs = Buffs()

    #Make a new character
    def new(self, name:str):
        self.Name = name
        self.Strength = self._rollStat()
        self.Dexterity = self._rollStat()
        self.Endurance = self._rollStat()
        self.Intelligence = self._rollStat()
        self.Faith = self._rollStat()
        self.Luck = self._rollStat()

        return self

    #required for JSON dump
    def to_dict(self):
        return {
            "Name": self.Name,
            "Level": self.Level,
            "NextXPtoLevel": self.NextXPtoLevel,
            "Strength": self.Strength,
            "Dexterity": self.Dexterity,
            "Endurance": self.Endurance,
            "Intelligence": self.Intelligence,
            "Faith": self.Faith,
            "Luck": self.Luck,
            "AttackRating": self.AttackRating,
            "DamageReduction": self.DamageReduction,
            "SpellDamage": self.SpellDamage,
            "Evasion": self.Evasion,
            "CritChance": self.CritChance,
            "InventorySpace": self.MaxInventory,
            "MaxAbilities": self.MaxAbilities,
            "MaxHP": self.MaxHP,
            "CurrentHP": self.CurrentHP,
            "MaxAP": self.MaxAP,
            "CurrentAP": self.CurrentAP,
            "Inventory": {
                "Gold": self.Inventory.Gold,
                "XP": self.Inventory.XP, 
                "Equipped":[item.to_dict() for item in self.Inventory.Equipped],
                "Stored": [item.to_dict() for item in self.Inventory.Stored],
                "Ability": [item.to_dict() for item in self.Inventory.Ability],
            }
        }

    def FromCharacterTable(self, chTable):
        self.Name = chTable.charName
        self.Strength = chTable.strength 
        self.Dexterity = chTable.dexterity
        self.Endurance = chTable.endurance
        self.Intelligence = chTable.intelligence
        self.Faith = chTable.faith
        self.Luck = chTable.luck
        inv = Inventory()
        inv.Gold = chTable.inventory["Gold"]
        inv.XP = chTable.inventory["XP"]
        inv.Equipped = [Loot(**item) for item in chTable.inventory["Equipped"]]
        inv.Stored = [Loot(**item) for item in chTable.inventory["Stored"]]
        inv.Ability = [Ability(**item) for item in chTable.inventory["Ability"]]
        self.Inventory = inv
        
        return self


    def ToCharacterTable(self, playerName:str):
        chTable = CharacterTable(
            playerName = playerName,
            charName = self.Name,
            strength = self.Strength,
            dexterity = self.Dexterity,
            endurance = self.Endurance,
            intelligence = self.Intelligence,
            faith = self.Faith,
            luck = self.Luck,
            inventory = {
                "Gold": self.Inventory.Gold,
                "XP": self.Inventory.XP, 
                "Equipped":[item.to_dict() for item in self.Inventory.Equipped],
                "Stored": [item.to_dict() for item in self.Inventory.Stored],
                "Ability": [item.to_dict() for item in self.Inventory.Ability],
            }
        )

        return chTable

    #Private method. Used to determine stat
    def _rollStat(self):
        #refresh seed based on nanosecond time
        random.seed(time.time_ns())
        #range 3-16 simulates a 3d6 roll
        return random.randint(3,18)

    #calculates derived stats
    def deriveStats(self):
        strMod = (self.Strength - 10) // 2
        dexMod = (self.Dexterity - 10) // 2
        endMod = (self.Endurance - 10) // 2
        intMod = (self.Intelligence - 10) // 2
        fthMod = (self.Faith - 10) // 2
        luckMod = (self.Luck - 10) // 2

        self.Level = self.Strength + self.Dexterity + self.Endurance + self.Intelligence + self.Faith + self.Luck 
        self.NextXPtoLevel = self.calcXpToLevel()
        self.AttackRating = strMod if strMod > dexMod else dexMod
        self.MaxHP = (10 + endMod)
        self.MaxAP = 10 + (intMod if intMod > fthMod else fthMod)
        self.Evasion = 10 + dexMod + luckMod
        maxinvraw = self.Strength if self.Strength > self.Intelligence else self.Intelligence
        self.MaxInventory = maxinvraw if maxinvraw <= self.InventoryCap else self.InventoryCap
        maxabraw = 10 + (fthMod if fthMod > intMod else intMod)
        self.MaxAbilities = maxabraw if maxabraw <= 20 else 20
        self.CritChance = self.Luck + fthMod
        self.DamageReduction = max(1, dexMod + endMod)
        self.SpellDamage = intMod if intMod > fthMod else fthMod

        equipped = self.Inventory.Equipped
        for i in equipped:
            effects = i.Effects
            self.AttackRating += effects.AttackRating
            self.DamageReduction += effects.DamageReduction
            self.SpellDamage += effects.SpellDamage
            self.MaxHP += effects.MaxHP
            self.MaxAP += effects.MaxAP
            self.Evasion += effects.Evasion
            self.CritChance += effects.CritChance
        
        #apply buffs
        CAP_MULT = 2

        maxARBuff = self.Buffs.AttackRating if self.Buffs.AttackRating <= self.AttackRating * CAP_MULT else self.AttackRating * CAP_MULT
        maxDRBuff = self.Buffs.DamageReduction if self.Buffs.DamageReduction <= self.DamageReduction * CAP_MULT else self.DamageReduction * CAP_MULT
        maxSDBuff = self.Buffs.SpellDamage if self.Buffs.SpellDamage <= self.SpellDamage * CAP_MULT else self.SpellDamage * CAP_MULT
        maxHPBuff = self.Buffs.MaxHP if self.Buffs.MaxHP <= self.MaxHP * CAP_MULT else self.MaxHP * CAP_MULT
        maxAPBuff = self.Buffs.MaxAP if self.Buffs.MaxAP <= self.MaxAP * CAP_MULT else self.MaxAP * CAP_MULT
        maxEVBuff = self.Buffs.Evasion if self.Buffs.Evasion <= self.Evasion * CAP_MULT else self.Evasion * CAP_MULT
        maxCCBuff = self.Buffs.CritChance if self.Buffs.CritChance <= self.CritChance * CAP_MULT else self.CritChance * CAP_MULT

        self.AttackRating = 0 if self.AttackRating + maxARBuff < 0 else self.AttackRating + maxARBuff
        self.DamageReduction = 1 if self.DamageReduction + maxDRBuff < 0 else self.DamageReduction + maxDRBuff
        self.SpellDamage = 0 if self.SpellDamage + maxSDBuff < 0 else self.SpellDamage + maxSDBuff
        self.MaxHP = 0 if self.MaxHP + maxHPBuff < 0 else self.MaxHP + maxHPBuff
        self.MaxAP = 0 if self.MaxAP + maxAPBuff < 0 else self.MaxAP + maxAPBuff
        self.Evasion = 0 if self.Evasion + maxEVBuff < 0 else self.Evasion + maxEVBuff
        self.CritChance = 0 if self.CritChance + maxCCBuff < 0 else self.CritChance + maxCCBuff

        if self.CurrentAP > self.MaxAP:
            self.CurrentAP = self.MaxAP
        if self.CurrentHP > self.MaxHP:
            self.CurrentHP = self.MaxHP
            
        
    def calcStartingGold(self):
        luckMod = (self.Luck - 10) // 2
        self.Inventory.Gold = 180 + (luckMod * 20)
    
    def calcMaxHPandAP(self):
        self.CurrentHP = self.MaxHP
        self.CurrentAP = self.MaxAP
        
    def calcXpToLevel(self):
        return int((1.5 * math.pow(self.Level - 1, 1.5) // 1))
#end class def


class Inventory():
    def __init__(self):
        self.Gold = 0
        self.XP = 0
        self.Equipped = [] #list of loot
        self.Stored = [] #list of loot
        self.Ability = [] #list of abilities

    def to_dict(self):
        return {
            "Gold": self.Gold,
            "XP": self.XP,
            "Equipped":[item.to_dict() for item in self.Equipped],
            "Stored": [item.to_dict() for item in self.Stored],
            "Ability": [item.to_dict() for item in self.Ability],
        }

    def checkInventoryForDuplicates(self):
        equipped = self.Equipped
        stored = self.Stored
        ability = self.Ability

        equipped = self.dedupe(equipped)
        stored = self.dedupe(stored)
        ability = self.dedupe(ability)
        
        equipped.sort(key=lambda i: i.Type)
        stored.sort(key=lambda i: i.Name)
        ability.sort(key=lambda i: i.Name)
        return

    @staticmethod
    def dedupe(items:list):
        for item in items:
            #stack consumables without renaming
            if item.Type == "Consumable":
                itemNameRaw = item.Name
                itemCount = 0
                itemNameTokens = itemNameRaw.split()
                
                try:
                    #gets number of items in stack if name ends with number                    
                    itemCount = int(itemNameTokens[-1])
                    itemName = " ".join(itemNameTokens[:-1])
                    #count other items with the same name and add count to end of name
                    itemCount += len(list(filter(lambda i: i.Name == itemName, items)))
                    item.Name = f"{itemName} {itemCount}"
                    #remove items with the same name but different count
                    duplicates = list(filter(lambda i: i.Name.startswith(itemName), items))
                    dupsSet = set(duplicates)
                    items[:] = [i for i in items if i not in dupsSet or i == item]  

                except Exception as e:
                    #if not, count number of items with the same name and add count to end of name
                    duplicates = list(filter(lambda i: i.Name == itemNameRaw, items))
                    itemCount = len(duplicates)
                    if itemCount > 0:
                        item.Name += f" {itemCount}"
                    #remove other items with the same name
                    dupsSet = set(duplicates)
                    items[:] = [i for i in items if i not in dupsSet or i == item]  
                continue

            #get list of all items with the same name
            duplicates = list(filter(lambda i: i.Name == item.Name, items))
            #if more than one item with the same name...
            if len(duplicates) > 1:
                dupName = item.Name
                dupCount = 1
                # ensure the highest "(int)" in each item.Name duplicate is always assigned to dupCount
                for dup in items:
                    if dup.Name.startswith(dupName) and "|" in dup.Name:
                        num = int(dup.Name.split("|")[-1])
                        dupCount = max(dupCount, num + 1) 

                for dup in items:
                    if dup.Name == dupName:
                        dup.Name += f" | {dupCount}"
                        dupCount += 1

        return items

class Buffs():
    def __init__(self):
        self.AttackRating = 0
        self.DamageReduction = 0
        self.SpellDamage = 0
        self.MaxHP = 0
        self.MaxAP = 0
        self.Evasion = 0
        self.CritChance = 0