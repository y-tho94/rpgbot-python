from calendar import c
from models.character import Buffs, Character, Inventory
from models.loot import Loot
from data.dataContext import Context, CharacterTable
from services.cacheService import SimpleCache
from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update
from services.lootService import LootService

class CharacterService():
    def __init__(self, db: Context, cache: SimpleCache, lootService: LootService):
        self.db = db.engine
        self.cache = cache
        self.lootService = lootService

    async def CreateNewCharacter(self, chname: str, player: str):
        ch = Character.new(self=Character(), name=chname)
        ch.Inventory.Equipped = await self.lootService.GenerateStartingLoot()
        ch.Inventory.Stored = [await self.lootService.GenerateLootByType("Consumable"), await self.lootService.GenerateLootByName("Skill Scroll")]
        ch.Inventory.checkInventoryForDuplicates()
        ch.calcStartingGold()

        chTable = ch.ToCharacterTable(player)

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
                inventory = chTable.inventory,
                isDead = 0
            )
            session.execute(statement)
        session.commit()
        session.close()

        ch.deriveStats()
        ch.calcMaxHPandAP()

        self.cache.set(player, ch)
        return ch

    async def GetCharacter(self, player:str):
        session = Session(bind=self.db)
        statement = select(CharacterTable).filter_by(playerName=player, isDead=0)
        charObj = session.execute(statement).scalars().first()
        session.close()

        if charObj is None:
            print(f"Character for player {player} not found")
            return

        ch = Character().FromCharacterTable(charObj)

        ch.deriveStats()
        ch.calcMaxHPandAP()
        self.cache.set(player, ch)
        return ch

    async def SaveCharacter(self, player:str, ch:Character):
        chTable = ch.ToCharacterTable(player)
        session = Session(bind=self.db)
            
        statement = update(CharacterTable).where(CharacterTable.playerName == player).values(
            charName = chTable.charName,
            strength = chTable.strength,
            dexterity = chTable.dexterity,
            endurance = chTable.endurance,
            intelligence = chTable.intelligence,
            faith = chTable.faith,
            luck = chTable.luck,
            inventory = chTable.inventory,
            isDead = 0
        )
        session.execute(statement)
        session.commit()
        session.close()
        return

    async def SaveCharacters(self):
        allActivePlayers = list(self.cache.cache.keys() - {"Wandering Merchant", "Scroll Merchant"})

        for player in allActivePlayers:
            ch = self.cache.get(player) or Character()

            chTable = ch.ToCharacterTable(player)
            session = Session(bind=self.db)
            
            statement = update(CharacterTable).where(CharacterTable.playerName == player).values(
                charName = chTable.charName,
                strength = chTable.strength,
                dexterity = chTable.dexterity,
                endurance = chTable.endurance,
                intelligence = chTable.intelligence,
                faith = chTable.faith,
                luck = chTable.luck,
                inventory = chTable.inventory,
                isDead = 0
            )
            session.execute(statement)
            session.commit()
            session.close()
            continue
        return

    async def DescribeCharacter(self, player:str):
        character = self.cache.get(player)

        if character is None:
            return {}

        return {
            "Character Name": character.Name,
            "Level": character.Level,
            "XP": character.Inventory.XP,
            "Next Level": character.NextXPtoLevel,
            "Gold": character.Inventory.Gold,
            "HP": f"{character.MaxHP} / {character.CurrentHP}",
            "AP": f"{character.MaxAP} / {character.CurrentAP}",
            "Inventory": f"{character.MaxInventory} / {len(character.Inventory.Stored)}",
            "Abilities": f"{character.MaxAbilities} / {len(character.Inventory.Ability)}",
            "Attributes": {
                "Strength": character.Strength,
                "Dexterity": character.Dexterity,
                "Endurance": character.Endurance,
                "Intelligence": character.Intelligence,
                "Faith": character.Faith,
                "Luck": character.Luck,
            },
            "Attack Rating": character.AttackRating,
            "Spell Damage": character.SpellDamage,
            "Damage Reduction": character.DamageReduction,
            "Evasion": character.Evasion,
            "Crit Chance": character.CritChance,
        }

    async def GetSetChar(self, player):
        cachedChar = self.cache.get(player)

        if cachedChar is None:
            ch = await self.GetCharacter(player)
            if ch is None:
                return {
                    "Error": f"Character for {player} does not exist",
                    "Character" : Character()
                } 
            else:
                cachedChar = ch

        return {
            "Error" : "",
            "Character": cachedChar
        }

    async def LevelUpChar(self, player:str, stat:str):
        ch = self.cache.get(player)
        if ch is None:
            return {
                "Error": f"Character for {player} does not exist"
            }
        if ch.Inventory.XP < ch.NextXPtoLevel:
            return {
                "Error": f"Not enough XP to level up. {ch.NextXPtoLevel - ch.Inventory.XP} more XP needed"
            }

        stat = stat.lower()
        match stat:
            case "strength":
                ch.Strength += 1
            case "dexterity":
                ch.Dexterity += 1
            case "endurance":
                ch.Endurance += 1
            case "intelligence":
                ch.Intelligence += 1
            case "faith":
                ch.Faith += 1
            case "luck":
                ch.Luck += 1
            case _:
                return {
                    "Error": f"{stat} is not a valid attribute to level up"
                }
        
        
        ch.Inventory.XP -= ch.NextXPtoLevel
        ch.Buffs = Buffs()
        ch.deriveStats()
        ch.calcMaxHPandAP()

        self.cache.set(player, ch)
        await self.SaveCharacter(player, ch)
        return {
            "Summary": f"{ch.Name} has leveled up {stat.upper()}"     
        }

    async def KillCharacter(self, player:str):

        session = Session(bind = self.db)
        statement = update(CharacterTable).where(CharacterTable.playerName==player).values(isDead = 1)
        session.execute(statement)
        session.commit()
        session.close()

        self.cache.delete(player)

    async def RestCharacter(self, player:str):
        ch = self.cache.get(player)
        if ch is None:
            return {
                "Error": f"Character for {player} does not exist"
            }
        
        cost = ((ch.MaxHP - ch.CurrentHP) + (ch.MaxAP - ch.CurrentAP)) * 100

        if ch.Inventory.Gold < cost:
            return {
                "Error": f"Not enough gold to rest. Resting costs {cost} Gold"
            }

        ch.Inventory.Gold -= cost
        ch.calcMaxHPandAP()
        ch.Buffs = Buffs()
        self.cache.set(player, ch)
        await self.SaveCharacter(player, ch)
        return {
            "Summary": f"{ch.Name} has rested and restored HP and AP in exchange for {cost} Gold"    
        }
        