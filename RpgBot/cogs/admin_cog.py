from discord.ext import commands
import discord
from numpy.core.multiarray import item

from services.monsterservice import MonsterService
from models.character import Character
from services.cacheService import MonsterCache, SimpleCache
from services.characterService import CharacterService
from services.abilityService import AbilityService
from services.lootService import LootService
from services.inventoryService import InventoryService
from services.merchantService import MerchantService
import json
import os

class AdminCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, monsterCache:MonsterCache, systemCache:SimpleCache, characterService:CharacterService, abilityService:AbilityService, lootService:LootService, inventoryService:InventoryService, merchantService:MerchantService, monsterService:MonsterService):
        self.bot = bot
        self.cache = cache
        self.monsterCache = monsterCache
        self.systemCache = systemCache
        self.characterService = characterService
        self.abilityService = abilityService
        self.lootService = lootService
        self.inventoryService = inventoryService
        self.merchantService = merchantService
        self.monsterService = monsterService

        self.generalChatID = int(os.getenv("GENERAL_CHANNEL_ID"))
        self.dungeonChatID = int(os.getenv("DUNGEON_CHANNEL_ID_FLOOR_1"))
        self.dungeonChatsDict = {k: v for k,v in os.environ.items() if "DUNGEON_CHANNEL" in k}
        self.dungeonChatList = [int(c) for c in self.dungeonChatsDict.values()]
        return

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def ResetShop(self, ctx):
        self.cache.delete("Wandering Merchant")
        self.cache.delete("Scroll Merchant")
        await ctx.reply("Shop Reset")
        channel = self.bot.get_channel(self.generalChatID)
        allowed_mentions = discord.AllowedMentions(everyone = True)
        await channel.send("@everyone The merchants have new inventory", allowed_mentions=allowed_mentions)
        return

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def AdminGiveGold(self, ctx, target:discord.Member, amount:int):
        chResponse = await self.characterService.GetSetChar(target.name)
        if chResponse["Error"] != "":
            await ctx.reply(chResponse["Error"])
            return

        response = await self.inventoryService.AdminGiveGold(target.name, amount)
        if response is not None:
            await ctx.reply(json.dumps(response, indent=4))
            return
        channel = self.bot.get_channel(self.generalChatID)

        await channel.send(f"The gods have given {target.mention} {amount} Gold")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def AdminGiveGoldAll(self, ctx, amount:int):
        activePlayers = list(self.cache.cache.keys() - {"Wandering Merchant"})
        for player in activePlayers:
            await self.inventoryService.AdminGiveGold(player, amount)
        channel = self.bot.get_channel(self.generalChatID)
        await channel.send(f"The gods have given all players {amount} Gold")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def AdminGiveItem(self, ctx, target:discord.Member, itemName:str):
        chResponse = await self.characterService.GetSetChar(target.name)
        if chResponse["Error"] != "":
            await ctx.reply(chResponse["Error"])
            return

        item = await self.lootService.GenerateLootByName(itemName)
        ch = chResponse["Character"] or Character()

        ch.Inventory.Stored.append(item)
        ch.Inventory.checkInventoryForDuplicates()

        await self.characterService.SaveCharacter(target.name, ch)
        channel = self.bot.get_channel(self.generalChatID)
        await channel.send(f"The gods have given {target.mention} {itemName}")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def AdminGiveScroll(self, ctx, target:discord.Member, abilityName:str):
        chResponse = await self.characterService.GetSetChar(target.name)
        if chResponse["Error"] != "":
            await ctx.reply(chResponse["Error"])
            return

        scroll = await self.lootService.GenerateScrollByAbilityName(abilityName)
        ch = chResponse["Character"] or Character()

        ch.Inventory.Stored.append(scroll)
        ch.Inventory.checkInventoryForDuplicates()
        await self.characterService.SaveCharacter(target.name, ch)
        channel = self.bot.get_channel(self.generalChatID)
        await channel.send(f"The gods have given {target.mention} {abilityName} Scroll")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def AdminDescribeCharacter(self, ctx, *, player:discord.Member):
        removeFromCache = False
        ch = self.cache.get(player.name)
        if ch is None:
            removeFromCache = True
            await self.characterService.GetSetChar(player.name)

        response = await self.characterService.DescribeCharacter(player.name)
        await ctx.reply(json.dumps(response, indent=4))
        if removeFromCache:
            self.cache.delete(player.name)
        return
        
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def AdminSpawnMonster(self, ctx, floor:int):
        
        monster = await self.monsterService.GetMobMonster(floor)

        await ctx.reply(f"{monster.Name} has been spawned in the dungeon")
        
        channel = self.bot.get_channel(int(self.dungeonChatsDict[f"DUNGEON_CHANNEL_ID_FLOOR_{floor}"]))
        await channel.send(f"A wild {monster.Name} has appeared in the dungeon!")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def InspectCache(self, ctx):
        print(json.dumps(self.systemCache.cache, indent=4))
        await ctx.reply("Cache printed to console")