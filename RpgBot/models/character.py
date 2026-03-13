import random
import time

class Character:
    #default constructor
    def __init__(self):
        self.Name = ""
        self.Strength = 0
        self.Dexterity = 0
        self.Endurance = 0
        self.Intelligence = 0
        self.Faith = 0
        self.Luck = 0
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
            "Inventory": self.Inventory.to_dict()
        }

    #Private method. Used to determine stat
    def _rollStat(self):
        #refresh seed based on nanosecond time
        random.seed(time.time_ns())
        #range 3-16 simulates a 3d6 roll
        return random.randint(3,18)
    
class Inventory():
    def __init__(self):
        self.Equipped = "{}"
        self.Stored = "{}"
        self.Ability = "{}"

    def to_dict(self):
        return {
            "Equipped": self.Equipped,
            "Stored": self.Stored,
            "Ability": self.Ability
        }