from discord.ext import commands
import discord
from services.cacheService import SimpleCache
from services.characterService import CharacterService
from services.abilityService import AbilityService
from services.lootService import LootService
from services.inventoryService import InventoryService
from services.merchantService import MerchantService
import json
import os

class AdminCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, characterService:CharacterService, abilityService:AbilityService, lootService:LootService, inventoryService:InventoryService, merchantService:MerchantService):
        self.bot = bot
        self.cache = cache
        self.characterService = characterService
        self.abilityService = abilityService
        self.lootService = lootService
        self.inventoryService = inventoryService
        self.merchantService = merchantService
        self.generalChatID = int(os.getenv("GENERAL_CHANNEL_ID"))
        return

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def ResetShop(self, ctx):
        self.cache.delete("Wandering Merchant")
        await ctx.reply("Shop Reset")
        return

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def AdminGiveGold(self, ctx, target:discord.Member, amount:int):
        chResponse = await self.characterService.GetSetChar(target.name)
        if chResponse["Error"] != "":
            await ctx.reply(json.dumps(response, indent=4))
            return

        response = await self.inventoryService.AdminGiveGold(target.name, amount)
        if response is not None:
            await ctx.reply(json.dumps(response, indent=4))
            return
        channel = self.bot.get_channel(self.generalChatID)

        await channel.send(f"The gods have given {target.mention} {amount} Gold")