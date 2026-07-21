from discord.ext import commands
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from data.dataContext import Base, Context
import os

class VaultCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.engine = create_engine(os.getenv("CONNECTION_STRING"))
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    async def cog_load(self):
        print("VaultCog loaded")

    async def cog_unload(self):
        print("VaultCog unloaded")
