from discord.ext import commands
from services.cacheService import SimpleCache
from services.dungeonService import DungeonService
from services.monsterservice import MonsterService
import json
import os


class DungeonCog(commands.Cog):
    def __init__(self, bot:commands.Bot, monsterCache:SimpleCache, monsterService:MonsterService, dungeonService:DungeonService):
        self.bot = bot
        self.monsterCache = monsterCache
        self.monsterService = monsterService
        self.dungeonService = dungeonService
        self.dungeonChatId = int(os.getenv("DUNGEON_CHANNEL_ID"))
        return

    @commands.command(brief="Look around the dungeon to see what monsters are present")
    async def Look(self, ctx):
        if ctx.channel.id != self.dungeonChatId:
            return

        monstersPresent = list(self.monsterCache.cache.keys())

        await ctx.reply("You look around the dungeon and see the following monsters...")
        await ctx.reply(json.dumps(monstersPresent, indent=4))
        return

    @commands.command(brief="Get Monster info. Requires Study Ability")
    async def Study(self, ctx, *, monsterName:str):
        if ctx.channel.id != self.dungeonChatId:
            return

        player = ctx.author.name
        response = await self.monsterService.StudyMonster(player, monsterName)
        await ctx.reply(json.dumps(response, indent=4))


    @commands.command(brief="Search dungeon for loot")
    async def Loot(self, ctx, *, itemName:str=""):
        if ctx.channel.id != self.dungeonChatId:
            await ctx.reply("You can't loot here!")
            return

        if itemName == "":
            response = await self.dungeonService.ShowLootables()
            await ctx.reply(json.dumps(response, indent=4))
            return
        else:
            player = ctx.author.name
            
            response = await self.dungeonService.TakeLoot(player, itemName)
            await ctx.reply(response)
            return

    @commands.command(brief="Inspect an item found in the dungeon")
    async def DescribeLoot(self, ctx, *, itemName:str):
        if ctx.channel.id != self.dungeonChatId:
            await ctx.reply("You can't inspect loot here!")
            return
        response = await self.dungeonService.DescribeLoot(itemName)
        await ctx.reply(json.dumps(response, indent=4))
        return
        
        