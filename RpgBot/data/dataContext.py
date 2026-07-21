from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()

class Context:
    def __init__(self):
        connectionString = os.getenv("CONNECTION_STRING")
        self.engine = create_engine(connectionString)
        self._base = Base
        self._base.metadata.create_all(self.engine)
        print("Tables created")

class CharacterTable(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    playerName = Column(String(32), nullable=False)
    charName = Column(String(32), nullable=False)
    strength = Column(Integer, nullable=False)
    dexterity = Column(Integer, nullable=False)
    endurance = Column(Integer, nullable=False)
    intelligence = Column(Integer, nullable=False)
    faith = Column(Integer, nullable=False)
    luck = Column(Integer, nullable=False)
    inventory = Column(JSON, nullable=False)
    isDead = Column(Integer, nullable=False, default=0)

class LootTable(Base):
    __tablename__ = "loot"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    description = Column(String(1000), nullable=False)
    type = Column(String(11), nullable=False)
    baseVariance = Column(Integer, nullable=False)
    baseEffects = Column(JSON, nullable=False)
    rarity = Column(String(11), nullable=True)

class AbilityTable(Base):
    __tablename__ = "ability"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    description = Column(String(1000), nullable=False)
    type = Column(String(10), nullable=False)
    cost = Column(Integer, nullable=False)
    baseVariance = Column(Integer, nullable=False)
    baseEffects = Column(JSON, nullable=False)

class MonsterTable(Base):
    __tablename__ = "monster"
    id = Column(Integer, primary_key=True, autoincrement=True)
    floor = Column(Integer, nullable=True)
    type = Column(String(10), nullable=False)
    name = Column(String(32), nullable=False)
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

class VaultTable(Base):
    __tablename__ = 'vault'

    vault_id = Column(Integer, primary_key=True)
    playerName = Column(Integer, ForeignKey('characters.playerName'), nullable=False)
    inventory = Column(JSON, nullable=False)

    def __repr__(self):
        return f"<Vault(vault_id={self.vault_id}, playerName={self.playerName})>"