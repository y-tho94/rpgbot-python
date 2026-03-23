from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Context:
    def __init__(self):
        self.engine = create_engine("sqlite:///rpgbotDEV.db")
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

class LootTable(Base):
    __tablename__ = "loot"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)
    baseVariance = Column(Integer, nullable=False)
    baseEffects = Column(JSON, nullable=False)

class AbilityTable(Base):
    __tablename__ = "ability"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)
    cost = Column(Integer, nullable=False)
    baseVariance = Column(Integer, nullable=False)
    baseEffects = Column(JSON, nullable=False)

class MonsterTable(Base):
    __tablename__ = "monster"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    weakness = Column(JSON, nullable=False)
    resistance = Column(JSON, nullable=False)
    baseVariance = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    attackRating = Column(Integer, nullable=False)
    damageReduction = Column(Integer, nullable=False)
    evasion = Column(Integer, nullable=False)
    critChance = Column(Integer, nullable=False)
    ai = Column(JSON, nullable=False)
    dropTable = Column(JSON, nullable=False)