import random
import time
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

        #inventory
        self.Inventory = Inventory()

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

        self.AttackRating = strMod if strMod > dexMod else dexMod
        self.MaxHP = 10 + endMod
        self.MaxAP = 10 + intMod
        self.Evasion = 10 + dexMod
        self.MaxInventory = self.Strength if self.Strength > self.Intelligence else self.Intelligence
        self.MaxAbilities = self.Faith if self.Faith > self.Intelligence else self.Intelligence
        self.CritChance = self.Luck + fthMod
        self.DamageReduction = dexMod + endMod
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
            
        
    def calcStartingGold(self):
        luckMod = (self.Luck - 10) // 2
        self.Inventory.Gold = 180 + (luckMod * 20)
    
    def calcMaxHPandAP(self):
        self.CurrentHP = self.MaxHP
        self.CurrentAP = self.MaxAP
        
    
#end class def


class Inventory():
    def __init__(self):
        self.Gold = 0
        self.Equipped = [] #list of loot
        self.Stored = [] #list of loot
        self.Ability = [] #list of abilities

    def to_dict(self):
        return {
            "Gold": self.Gold,
            "Equipped":[item.to_dict() for item in self.Equipped],
            "Stored": [item.to_dict() for item in self.Stored],
            "Ability": [item.to_dict() for item in self.Ability],
        }

    def checkInventoryForDuplicates(self):
        equipped = self.Equipped
        stored = self.Stored
        ability = self.Ability

        for item in equipped:
            #get list of all items with the same name
            duplicates = list(filter(lambda i: i.Name == item.Name, equipped))

            #if more than one item with the same name...
            if len(duplicates) > 1:
                #loop through inventory and rename the item
                dupName = item.Name
                dupCount = 0
                for dup in equipped:
                    if dup.Name == dupName:
                        dup.Name += f" ({dupCount})"
                        dupCount += 1
        
        for item in stored:
            #get list of all items with the same name
            duplicates = list(filter(lambda i: i.Name == item.Name, stored))

            #if more than one item with the same name...
            if len(duplicates) > 1:
                #loop through inventory and rename the item
                dupName = item.Name
                dupCount = 0
                for dup in stored:
                    if dup.Name == dupName:
                        dup.Name += f" ({dupCount})"
                        dupCount += 1
        
        for item in ability:
            #get list of all items with the same name
            duplicates = list(filter(lambda i: i.Name == item.Name, ability))

            #if more than one item with the same name...
            if len(duplicates) > 1:
                #loop through inventory and rename the item
                dupName = item.Name
                dupCount = 0
                for dup in ability:
                    if dup.Name == dupName:
                        dup.Name += f" ({dupCount})"
                        dupCount += 1
        
        return