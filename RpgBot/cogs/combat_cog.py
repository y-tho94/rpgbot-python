from discord.ext import tasks, commands
from services import merchantService
from services.cacheService import SimpleCache
from services.characterService import CharacterService
from services.combatService import CombatService
import json
import os
class CombatCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, combatService:CombatService, characterService:CharacterService):
        self.bot = bot
        self.cache = cache
        self.combatService = combatService
        self.characterService = characterService

        return

    @commands.command(brief="Initiate PVP Combat")
    async def Attack(self, ctx, *, target=""):
        genchatId = int(os.getenv("GENERAL_CHANNEL_ID"))
        channelId = ctx.channel.id
        if channelId != genchatId:
            await ctx.reply("This command is only valid in the general channel")
            return

        if len(target.split()) == 0:
            await ctx.reply("No target specified")
            return
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        await self.characterService.GetSetChar(target)

        response = await self.combatService.DoPvPCombat(player, target)
        await ctx.reply(json.dumps(response, indent=4))
        return