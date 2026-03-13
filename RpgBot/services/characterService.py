from models.character import Character, Inventory
from data.dataContext import Context, CharacterTable
from services.cacheService import SimpleCache
import json
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from services.lootService import LootService

class CharacterService():
    def __init__(self, db: Context, cache: SimpleCache, lootService: LootService):
        self.db = db.engine
        self.cache = cache
        self.lootService = lootService

    def createNewCharacter(self, chname: str, player: str):
        ch = Character.new(self=Character(), name=chname)
        ch.Inventory.Equipped.append(self._getStartingLoot())
        chTable = CharacterTable(
            playerName = player,
            charName = ch.Name,
            strength = ch.Strength,
            dexterity = ch.Dexterity,
            endurance = ch.Endurance,
            intelligence = ch.Intelligence,
            faith = ch.Faith,
            luck = ch.Luck,
            inventory = {
                "Equipped":[item.to_dict() for item in ch.Inventory.Equipped],
                "Stored": [item.to_dict() for item in ch.Inventory.Stored],
                "Ability": [item.to_dict() for item in ch.Inventory.Ability],
            }
        )

        session = Session(bind=self.db)
        statement = select(CharacterTable).filter_by(playerName=player)
        existing = session.execute(statement).scalars().first()
        if existing is None: 
            session.add(chTable)
        else:
            statement = update(CharacterTable).where(CharacterTable.id == existing.id).values(
                charName = chTable.charName,
                strength = chTable.strength,
                dexterity = chTable.dexterity,
                endurance = chTable.endurance,
                intelligence = chTable.intelligence,
                faith = chTable.faith,
                luck = chTable.luck,
                inventory = chTable.inventory 
            )
            session.execute(statement)
        session.commit()
        session.close()

        self.deriveStats(ch)

        self.cache.set(player, ch)
        return ch

    def getCharacter(self, playerName:str):
        session = Session(bind=self.db)
        statement = select(CharacterTable).filter_by(playerName=playerName)
        charObj = session.execute(statement).scalars().first()
        session.close()

        if charObj is None:
            print(f"Character for player {playerName} not found")
        
        return charObj
    
    
    def _getStartingLoot(self):
        loot = self.lootService.GenerateLoot("Dagger")
        return loot

    #calculates derived stats
    @staticmethod
    def deriveStats(ch:Character):
        strMod = (ch.Strength - 10) // 2
        dexMod = (ch.Dexterity - 10) // 2
        endMod = (ch.Endurance - 10) // 2
        intMod = (ch.Intelligence - 10) // 2
        fthMod = (ch.Faith - 10) // 2
        luckMod = (ch.Luck - 10) // 2

        ch.AttackRating = strMod if strMod > dexMod else dexMod
        ch.MaxHP = 10 + endMod
        ch.CurrentHP = ch.MaxHP
        ch.MaxAP = 10 + intMod
        ch.CurrentAP = ch.MaxAP
        ch.Evasion = 10 + dexMod
        ch.MaxInventory = ch.Strength if ch.Strength > ch.Intelligence else ch.Intelligence
        ch.MaxAbilities = ch.Faith if ch.Faith > ch.Intelligence else ch.Intelligence
        ch.CritChance = ch.Luck + fthMod

        equipped = ch.Inventory.Equipped
        for i in equipped:
            effects = i.Effects
            ch.AttackRating += effects.AttackRating
            ch.DamageReduction += effects.DamageReduction
            ch.SpellDamage += effects.SpellDamage
            ch.MaxHP += effects.MaxHP
            ch.MaxAP += effects.MaxAP
            ch.Evasion += effects.Evasion
            ch.CritChance += effects.CritChance
    
