from models.character import Character, Inventory
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
                inventory = chTable.inventory 
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
        statement = select(CharacterTable).filter_by(playerName=player)
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
            inventory = chTable.inventory 
        )
        session.execute(statement)
        session.commit()
        session.close()
        return

    async def SaveCharacters(self):
        allActivePlayers = list(self.cache.cache.keys() - {"Wandering Merchant"})

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
                inventory = chTable.inventory 
            )
            session.execute(statement)
            session.commit()
            session.close()
            continue
        return

    async def DescribeCharacter(self, player:str):
        character = self.cache.get(player)

        return {
            "Character Name": character.Name,
            "Gold": character.Inventory.Gold,
            "HP": character.CurrentHP,
            "AP": character.CurrentAP,
            "Max Inventory": character.MaxInventory,
            "Strength": character.Strength,
            "Dexterity": character.Dexterity,
            "Endurance": character.Endurance,
            "Intelligence": character.Intelligence,
            "Faith": character.Faith,
            "Luck": character.Luck,
            "Attack Rating": character.AttackRating,
            "Spell Damage": character.SpellDamage,
            "Damage Reduction": character.DamageReduction,
            "Evasion": character.Evasion,
            "Crit Chance": character.CritChance,
        }

    async def GetSetChar(self, player):
        cachedChar = self.cache.get(player)

        if cachedChar is None:
            await self.GetCharacter(player)

        return

    async def KillCharacter(self, player:str):
        self.cache.delete(player)

        session = Session(bind = self.db)
        statement = delete(CharacterTable).where(CharacterTable.playerName==player)
        session.execute(statement)
        session.commit()

    
    
