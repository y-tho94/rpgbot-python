import discord
from discord.ext import commands
from services.cacheService import MonsterCache, SimpleCache
from services.characterService import CharacterService
from services.abilityService import AbilityService
from services.combatService import CombatService
from services.monsterservice import MonsterService
import json
import os

class CombatCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, monsterCache:MonsterCache, combatService:CombatService, characterService:CharacterService, abilityService:AbilityService, monsterService:MonsterService):
        self.bot = bot
        self.cache = cache
        self.monsterCache = monsterCache
        self.combatService = combatService
        self.characterService = characterService
        self.abilityService = abilityService
        self.monsterService = monsterService
        self.genChatId = int(os.getenv("GENERAL_CHANNEL_ID"))
        self.dungeonChatsDict = {k: v for k,v in os.environ.items() if "DUNGEON_CHANNEL" in k}
        self.dungeonChatList = [int(c) for c in self.dungeonChatsDict.values()]
        return

    @commands.command(brief="Initiate Combat")
    async def Attack(self, ctx, *, targetName:str=""):
        channelId = ctx.channel.id
        if channelId != self.genChatId and channelId not in self.dungeonChatList:
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
        if channelId in self.dungeonChatList:
            for i in range(len(self.dungeonChatList)):
                if channelId == self.dungeonChatList[i]:
                    targetMon = self.monsterCache.get(i, targetName)
                    if targetMon is None:
                        await ctx.reply(f"{targetName} is not a valid monster in this dungeon")
                        return

                    response = await self.monsterService.MonsterCombat(player, targetName, i)
                    await ctx.reply(json.dumps(response, indent=4))
                    return
        return

    @commands.command(brief="Use an ability on a target")
    async def Cast(self, ctx, abilityName, targetName:str="self"):
        channelId = ctx.channel.id
        if channelId != self.genChatId and channelId not in self.dungeonChatList:
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

        elif channelId in self.dungeonChatList:
            for i in range(len(self.dungeonChatList)):
                if channelId == self.dungeonChatList[i]:
                    targetMon = self.monsterCache.get(i, targetName)
                    if targetMon is None:
                        await ctx.reply(f"{targetName} is not a valid monster in this dungeon")
                        return
                    response = await self.monsterService.UseAbility(player, targetName, abilityName, i)
                    await ctx.reply(json.dumps(response, indent=4))
                    return

        return

    @commands.command(brief="Flee from combat")
    async def Disengage (self, ctx, *, monsterName:str):
        channelId = ctx.channel.id
        if channelId not in self.dungeonChatList:
            await ctx.reply("This command is only valid in the dungeon")
            return

        for i in range(len(self.dungeonChatList)):
            if channelId == self.dungeonChatList[i]:
                monster = self.monsterCache.get(i, monsterName)

                response = await self.monsterService.FleeCombat(ctx.author.name, monster)
                await ctx.reply(json.dumps(response, indent=4))
                return