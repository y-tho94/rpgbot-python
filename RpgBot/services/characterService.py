from models.character import Character, Inventory
from models.loot import Loot
from data.dataContext import Context, CharacterTable
from services.cacheService import SimpleCache
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from services.lootService import LootService

class CharacterService():
    def __init__(self, db: Context, cache: SimpleCache, lootService: LootService):
        self.db = db.engine
        self.cache = cache
        self.lootService = lootService

    async def CreateNewCharacter(self, chname: str, player: str):
        ch = Character.new(self=Character(), name=chname)
        ch.Inventory.Equipped = self.lootService.GenerateStartingLoot()
        ch.Inventory.checkInventoryForDuplicates()

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
                "Gold": ch.Inventory.Gold,
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

        ch.deriveStats()

        self.cache.set(player, ch)
        return ch

    async def GetCharacter(self, player:str):
        session = Session(bind=self.db)
        statement = select(CharacterTable).filter_by(playerName=player)
        charObj = session.execute(statement).scalars().first()
        session.close()

        if charObj is None:
            print(f"Character for player {player} not found")
            return Character()

        ch = Character()
        ch.Name = charObj.charName
        ch.Strength = charObj.strength 
        ch.Dexterity = charObj.dexterity
        ch.Endurance = charObj.endurance
        ch.Intelligence = charObj.intelligence
        ch.Faith = charObj.faith
        ch.Luck = charObj.luck
        inv = Inventory()
        inv.Gold = charObj.inventory["Gold"]
        inv.Equipped = [Loot(**item) for item in charObj.inventory["Equipped"]]
        inv.Stored = [Loot(**item) for item in charObj.inventory["Stored"]]
        inv.Ability = [Loot(**item) for item in charObj.inventory["Ability"]]
        ch.Inventory = inv

        ch.deriveStats()
        self.cache.set(player, ch)
        return ch
    
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

    
    
