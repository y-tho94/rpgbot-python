import discord
from discord.ext import tasks, commands
from services.cacheService import SimpleCache
from services.characterService import CharacterService
from services.monsterservice import MonsterService
import os

class TasksCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, characterService:CharacterService, monsterService:MonsterService):
        self.bot = bot
        self.cache = cache
        self.characterService = characterService
        self.monsterService = monsterService
        self.generalChatID = int(os.getenv("GENERAL_CHANNEL_ID"))
        self.dungeonChatID = int(os.getenv("DUNGEON_CHANNEL_ID"))

        self.ClearCache.start()
        self.ClearMerchant.start()
        self.SummonMobMonster.start()
    
    def cog_unload(self):
        self.ClearCache.cancel()

    @tasks.loop(hours=8)
    async def ClearCache(self):
        activePlayers = list(self.cache.cache.keys() - {"Wandering Merchant"})

        for player in activePlayers:
            ch = self.cache.get(player)
            ch.Inventory.Gold += 100

        await self.characterService.SaveCharacters()
        self.cache.clear()

        channel = self.bot.get_channel(self.generalChatID)
        await channel.send("After a long rest, all characters have been restored to full and all temporary effects have been removed")

        print("Cache cleared")
        return

    @tasks.loop(hours=1)
    async def ClearMerchant(self):
        try:
            self.cache.delete("Wandering Merchant")
        except:
            pass

        channel = self.bot.get_channel(self.generalChatID)
        allowed_mentions = discord.AllowedMentions(everyone = True)
        await channel.send("@everyone The merchant has new inventory", allowed_mentions=allowed_mentions)
        return

    @tasks.loop(minutes=15)
    async def SummonMobMonster(self):
        monster = await self.monsterService.GetMobMonster()

        channel = self.bot.get_channel(self.dungeonChatID)
        await channel.send(f"A wild {monster.Name} has appeared in the dungeon!")
        return