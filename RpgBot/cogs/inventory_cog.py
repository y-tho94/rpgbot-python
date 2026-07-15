import discord
from discord.ext import tasks, commands
from services.cacheService import MonsterCache, SimpleCache
from services.monsterservice import MonsterService
from services.characterService import CharacterService
from services.inventoryService import InventoryService
import json
import os

class InventoryCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, monsterCache:MonsterCache, inventoryService:InventoryService, characterService:CharacterService, monsterService:MonsterService):
        self.bot = bot
        self.cache = cache
        self.inventoryService = inventoryService
        self.characterService = characterService
        self.monsterCache = monsterCache
        self.monsterService = monsterService
        self.generalChatId = int(os.getenv("GENERAL_CHANNEL_ID"))
        self.dungeonChatId = int(os.getenv("DUNGEON_CHANNEL_ID_FLOOR_1"))
        self.dungeonChatsDict = {k: v for k,v in os.environ.items() if "DUNGEON_CHANNEL" in k}
        self.dungeonChatList = [int(c) for c in self.dungeonChatsDict.values()]

    @commands.command(brief="Show inventory", aliases=["ShowInv"])
    async def ShowInventory(self, ctx):
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        retval = await self.inventoryService.ShowInventorySimple(player)

        await ctx.reply(json.dumps(retval, indent=4))
        return  

    @commands.command(brief="Describe equipped item", aliases=["DescEq"])
    async def DescribeEquipment(self, ctx, *, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to describe")
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        ch = self.cache.get(player)
        inv = ch.Inventory.Equipped
        
        itemList = list(filter(lambda i: i.Name == itemName, inv))
        if len(itemList) == 0:
            await ctx.reply("No item of that name equipped")
            return

        item = await self.inventoryService.DescribeItem(itemList[0])

        await ctx.reply(json.dumps(item, indent=4))
        return 

    @commands.command(brief="Describe stored item", aliases=["DescSt"])
    async def DescribeItem(self, ctx, *, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to describe")
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        ch = self.cache.get(player)
        inv = ch.Inventory.Stored
        
        itemList = list(filter(lambda i: i.Name == itemName, inv))
        if len(itemList) == 0:
            await ctx.reply("No item of that name in stored inventory")
            return

        item = await self.inventoryService.DescribeItem(itemList[0])
        await ctx.reply(json.dumps(item, indent=4))
        return 


    @commands.command(brief="Unequip Item")
    async def Unequip(self, ctx, *, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to unequip")
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        try:
            response = await self.inventoryService.UnequipItem(player, itemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            retval = await self.inventoryService.ShowInventorySimple(player)
            await ctx.reply(json.dumps(retval, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("Item could not be unequipped")

        return
        
    @commands.command(brief="Equip Item")
    async def Equip(self, ctx, *, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to equip")
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        try:
            response = await self.inventoryService.EquipItem(player, itemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            retval = await self.inventoryService.ShowInventorySimple(player)
            await ctx.reply(json.dumps(retval, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("Item could not be equipped")

        return
    
    @commands.command(brief="Swap stored item with equiped item in the same slot")
    async def Swap(self, ctx, *, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to swap")
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        try:
            response = await self.inventoryService.SwapItem(player, itemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            retval = await self.inventoryService.ShowInventorySimple(player)
            await ctx.reply(json.dumps(retval, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("Item could not be swapped")
        return

    @commands.command(brief="Drop Stored Item")
    async def Drop(self, ctx, *, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to equip")
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        try:
            response = await self.inventoryService.DiscardItem(player, itemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            retval = await self.inventoryService.ShowInventorySimple(player)
            await ctx.reply(json.dumps(retval, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("Item could not be equipped")

        return

    @commands.command(brief="Give player a stored item")
    async def Give(self, ctx, target:discord.Member, itemName:str=""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to trade")

        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        await self.characterService.GetSetChar(target.name)
        
        try:
            response = await self.inventoryService.GiveItem(player, target.name, itemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            else:
                channel = self.bot.get_channel(self.generalChatId)
                sender = self.bot.get_user(ctx.author.id)
                await channel.send(f"{sender.mention} gave {target.mention} '{itemName}'")
        except Exception as ex:
            print(ex)
            await ctx.reply("Trade could not be completed")
        return
    
    @commands.command(brief="Give Player Gold", aliases=["GG"])
    async def GiveGold(self, ctx, target:discord.Member, amount:str=""):
        if len(amount.strip()) == 0:
            await ctx.reply("Gold amount cannot be identified")
            return
        amountInt = 0
        try:
            amountInt = int(amount)
        except Exception as ex:
            await ctx.reply("Gold amount cannot be identified")
            return
        
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        await self.characterService.GetSetChar(target.name)

        try:
            response = await self.inventoryService.GiveGold(player, target.name, amountInt)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            else:
                channel = self.bot.get_channel(self.generalChatId)
                sender = self.bot.get_user(ctx.author.id)
                await channel.send(f"{sender.mention} gave {target.mention} {amount} Gold")
        except Exception as ex:
            print(ex)
            await ctx.reply("Trade could not be completed")
        return


    @commands.command(brief="Change name of stored item in inventory")
    async def Rename(self, ctx, itemName:str="", newItemName:str=""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item name given")
            return
        if len(newItemName.strip()) == 0:
            await ctx.reply("No new name given")
            return
        
        player = ctx.author.name
        await self.characterService.GetSetChar(player)

        try:
            response = await self.inventoryService.RenameItem(player, itemName, newItemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            retval = await self.inventoryService.ShowInventorySimple(player)
            await ctx.reply(json.dumps(retval, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("Item could not be renamed")

        return

    @commands.command(brief="Use an item in stored inventory on target or self")
    async def Use(self, ctx, itemName:str = "", target:str = "self"):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item name given")
            return

        channel = ctx.channel.id
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        if target == "self":
            target = ctx.author
            response = await self.inventoryService.UseItem(player, target.name, itemName)
            await ctx.reply(json.dumps(response, indent=4))
        elif ctx.guild.get_member_named(target) is not None:
            target = ctx.guild.get_member_named(target)
            await self.characterService.GetSetChar(target.name)
            response = await self.inventoryService.UseItem(player, target.name, itemName)
            await ctx.reply(json.dumps(response, indent=4))
        elif ctx.guild.get_member_named(target) is None:
            await ctx.reply("Invalid character name")
            return
        elif channel in self.dungeonChatList:
            for i in range(len(self.dungeonChatList)):
                if channel == self.dungeonChatList[i]:
                    monster = self.monsterCache.get(i, target)
                    if monster is not None:
                        response = await self.monsterService.UseItem(player, monster, itemName, i)
                        await ctx.reply(json.dumps(response, indent=4))

        await self.inventoryService.DiscardItem(player, itemName)
        return