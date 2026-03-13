from models.character import Character
from data.dataContext import Context, CharacterTable
import json
from sqlalchemy.orm import Session

class CharacterService():
    def __init__(self, db: Context):
        self.db = db.engine

    def createNewCharacter(self, chname: str, player: str):
        ch = Character.new(self=Character(), name=chname)
        chTable = CharacterTable(
            playerName = player,
            charName = ch.Name,
            strength = ch.Strength,
            dexterity = ch.Dexterity,
            endurance = ch.Endurance,
            intelligence = ch.Intelligence,
            faith = ch.Faith,
            luck = ch.Luck,
            inventory = json.dumps(ch.Inventory.to_dict())
        )

        session = Session(bind=self.db)
        session.add(chTable)
        session.commit()
        session.close()

        return ch