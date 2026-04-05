import discord
from discord.ext import tasks, commands
from services.cacheService import SimpleCache, MonsterCache
from services.characterService import CharacterService
from services.monsterservice import MonsterService
import os

class TasksCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, monsterCache:MonsterCache, systemCache:SimpleCache, characterService:CharacterService, monsterService:MonsterService):
        self.bot = bot
        self.cache = cache
        self.monsterCache = monsterCache
        self.systemCache = systemCache
        self.characterService = characterService
        self.monsterService = monsterService
        self.generalChatID = int(os.getenv("GENERAL_CHANNEL_ID"))
        self.dungeonChatsDict = {k: v for k,v in os.environ.items() if "DUNGEON_CHANNEL" in k}
        self.dungeonChatList = [int(c) for c in self.dungeonChatsDict.values()]

        self.ClearCache.start()
        self.ClearMerchant.start()
        self.SummonMobMonster.start()
        self.SummonRaidMonster.start()
    
    def cog_unload(self):
        self.ClearCache.cancel()

    @tasks.loop(hours=8)
    async def ClearCache(self):
        activePlayers = list(self.cache.cache.keys() - {"Wandering Merchant", "Scroll Merchant", "Pawn Merchant"})

        for player in activePlayers:
            ch = self.cache.get(player)
            ch.Inventory.Gold += 100

        await self.characterService.SaveCharacters()
        self.cache.clear()
        self.monsterCache.clear()
        self.systemCache.clear()

        channel = self.bot.get_channel(self.generalChatID)
        await channel.send("After a long rest, all characters have been restored to full and all temporary effects have been removed")

        print("Cache cleared")
        return

    @tasks.loop(hours=1)
    async def ClearMerchant(self):
        try:
            self.cache.delete("Wandering Merchant")
            self.cache.delete("Scroll Merchant")
            self.cache.delete("Pawn Merchant")
        except:
            pass

        channel = self.bot.get_channel(self.generalChatID)
        allowed_mentions = discord.AllowedMentions(everyone = True)
        await channel.send("@everyone The merchants have new inventory", allowed_mentions=allowed_mentions)
        return

    @tasks.loop(minutes=15)
    async def SummonMobMonster(self):
        await self.SummonMobMons(1)
        await self.SummonMobMons(2)
        await self.SummonMobMons(3)
        return

    async def SummonMobMons(self, floor:int):
        channelId = int(self.dungeonChatsDict[f"DUNGEON_CHANNEL_ID_FLOOR_{floor}"])
        channel = self.bot.get_channel(channelId)
        for _ in range(10):
            try:
                monster = await self.monsterService.GetMobMonster(floor)
                if monster is not None:
                    await channel.send(f"A wild {monster.Name} has appeared in the dungeon!")
            except Exception as e:
                await channel.send(e)
                break;


    @tasks.loop(hours=1)
    async def SummonRaidMonster(self):
        await self.SummonRaidMons(1)
        await self.SummonRaidMons(2)
        await self.SummonRaidMons(3)
        return

    async def SummonRaidMons(self, floor:int):
        channelId = int(self.dungeonChatsDict[f"DUNGEON_CHANNEL_ID_FLOOR_{floor}"])
        channel = self.bot.get_channel(channelId)
        
        try:
            monster = await self.monsterService.GetRaidMonster(floor)
            if monster is not None:
                await channel.send(f"A raid monster {monster.Name} has appeared in the dungeon!")
        except Exception as e:
            await channel.send(e)
