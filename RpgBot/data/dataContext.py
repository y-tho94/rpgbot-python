from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Context:
    def __init__(self):
        self.engine = create_engine("sqlite:///rpgbot.db")
        self._base = Base
        self._base.metadata.create_all(self.engine)
        print("Tables created")

class CharacterTable(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    playerName = Column(String, nullable=False)
    charName = Column(String, nullable=False)
    strength = Column(Integer, nullable=False)
    dexterity = Column(Integer, nullable=False)
    endurance = Column(Integer, nullable=False)
    intelligence = Column(Integer, nullable=False)
    faith = Column(Integer, nullable=False)
    luck = Column(Integer, nullable=False)
    inventory = Column(JSON, nullable=False)