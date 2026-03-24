import discord
from discord.ext import commands
from services.cacheService import SimpleCache
from services.characterService import CharacterService
from services.abilityService import AbilityService
from services.combatService import CombatService
from services.monsterservice import MonsterService
import json
import os

class CombatCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, monsterCache:SimpleCache, combatService:CombatService, characterService:CharacterService, abilityService:AbilityService, monsterService:MonsterService):
        self.bot = bot
        self.cache = cache
        self.monsterCache = monsterCache
        self.combatService = combatService
        self.characterService = characterService
        self.abilityService = abilityService
        self.monsterService = monsterService
        self.genChatId = int(os.getenv("GENERAL_CHANNEL_ID"))
        self.dungeonChatId = int(os.getenv("DUNGEON_CHANNEL_ID"))
        return

    @commands.command(brief="Initiate Combat")
    async def Attack(self, ctx, *, targetName:str=""):
        channelId = ctx.channel.id
        if channelId != self.genChatId and channelId != self.dungeonChatId:
            await ctx.reply("This command is only valid in the general channel or the dungeon")
            return

        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        if channelId == self.genChatId:
            target = ctx.guild.get_member_named(targetName)
            targetCh = self.cache.get(target.name)
            if targetCh is None:
                await ctx.reply(f"{target.mention} is not online")
                await ctx.reply(f"{ctx.author.mention} wants to duel {target.mention}")
                return

            response = await self.combatService.DoPvPCombat(player, target.name)
            await ctx.reply(json.dumps(response, indent=4))
        if channelId == self.dungeonChatId:
            targetMon = self.monsterCache.get(targetName)
            if targetMon is None:
                await ctx.reply(f"{targetName} is not a valid monster in this dungeon")
                return

            response = await self.monsterService.MonsterCombat(player, targetName)
            await ctx.reply(json.dumps(response, indent=4))
        return

    @commands.command(brief="Use an ability on a target")
    async def Cast(self, ctx, abilityName, targetName:str="self"):
        channelId = ctx.channel.id
        if channelId != self.genChatId and channelId != self.dungeonChatId:
            await ctx.reply("This command is only valid in the general channel or the dungeon")
            return

        if len(abilityName.strip()) == 0:
            await ctx.reply("No ability specified")
            return

        player = ctx.author.name
        await self.characterService.GetSetChar(player)

        target = None
        if targetName == "self":
            target = ctx.author
            response = await self.combatService.UseAbilityPvP(player, target.name, abilityName)
            await ctx.reply(json.dumps(response, indent=4))

        elif ctx.guild.get_member_named(targetName) is not None:
            target = ctx.guild.get_member_named(targetName)

            targetCh = self.cache.get(target.name)
            if targetCh is None:
                await ctx.reply(f"{target.mention} is not online")
                await ctx.reply(f"{ctx.author.mention} wants to duel {target.mention}")
                return

            response = await self.combatService.UseAbilityPvP(player, target.name, abilityName)
            await ctx.reply(json.dumps(response, indent=4))

        elif channelId == self.dungeonChatId:
            targetMon = self.monsterCache.get(targetName)
            if targetMon is None:
                await ctx.reply(f"{targetName} is not a valid monster in this dungeon")
                return
            response = await self.monsterService.UseAbility(player, targetName, abilityName)
            await ctx.reply(json.dumps(response, indent=4))

        return