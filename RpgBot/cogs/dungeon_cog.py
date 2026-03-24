from discord.ext import tasks, commands
from services.cacheService import SimpleCache
from services.monsterservice import MonsterService
import json
import os


class DungeonCog(commands.Cog):
    def __init__(self, bot:commands.Bot, monsterCache:SimpleCache, monsterService:MonsterService):
        self.bot = bot
        self.monsterCache = monsterCache
        self.monsterService = monsterService
        self.dungeonChatId = int(os.getenv("DUNGEON_CHANNEL_ID"))
        return

    @commands.command(brief="Look around the dungeon to see what monsters are present")
    async def Look(self, ctx):
        if ctx.channel.id != self.dungeonChatId:
            return

        monstersPresent = list(self.monsterCache.cache.keys())

        await ctx.reply("You look around the dungeon and see the following monsters...")
        await ctx.reply(json.dumps(monstersPresent, indent=4))

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def AdminSpawnMonster(self, ctx):
        if ctx.channel.id != self.dungeonChatId:
            return

        monster = await self.monsterService.GetMobMonster()

        await ctx.reply(f"{monster.Name} has been spawned in the dungeon")