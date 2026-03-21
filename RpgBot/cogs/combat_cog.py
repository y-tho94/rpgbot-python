import discord
from discord.ext import commands
from services.cacheService import SimpleCache
from services.characterService import CharacterService
from services.abilityService import AbilityService
from services.combatService import CombatService
import json
import os
class CombatCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, combatService:CombatService, characterService:CharacterService, abilityService:AbilityService):
        self.bot = bot
        self.cache = cache
        self.combatService = combatService
        self.characterService = characterService
        self.abilityService = abilityService

        return

    @commands.command(brief="Initiate PVP Combat")
    async def Attack(self, ctx, *, target:discord.Member=""):
        genchatId = int(os.getenv("GENERAL_CHANNEL_ID"))
        channelId = ctx.channel.id
        if channelId != genchatId:
            await ctx.reply("This command is only valid in the general channel")
            return

        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        await self.characterService.GetSetChar(target.name)

        response = await self.combatService.DoPvPCombat(player, target.name)
        await ctx.reply(json.dumps(response, indent=4))
        return

    @commands.command(brief="Use an ability on a target")
    async def Cast(self, ctx, abilityName, target:discord.Member="self"):
        genchatId = int(os.getenv("GENERAL_CHANNEL_ID"))
        channelId = ctx.channel.id
        if channelId != genchatId:
            await ctx.reply("This command is only valid in the general channel")
            return

        if len(abilityName.strip()) == 0:
            await ctx.reply("No target specified")
            return

        player = ctx.author.name
        await self.characterService.GetSetChar(player)

        if target == "self":
            target = ctx.author
        await self.characterService.GetSetChar(target.name)

        response = await self.combatService.UseAbilityPvP(player, target.name, abilityName)
        await ctx.reply(json.dumps(response, indent=4))
        return