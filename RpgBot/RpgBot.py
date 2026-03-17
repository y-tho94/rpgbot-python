from data.dataContext import Context
from services.characterService import CharacterService
from services.cacheService import SimpleCache
from services.inventoryService import InventoryService
from services.lootService import LootService
import json
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import datetime
from cogs.tasks import TasksCog

if __name__ == '__main__':
    load_dotenv()
    print('starting...')
    
    #Dependency injection and startup services
    db = Context()
    cache = SimpleCache()
    lootService = LootService(db=db)
    characterService = CharacterService(db=db, cache=cache, lootService=lootService)
    inventoryService = InventoryService(db=db, cache=cache)

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='$', intents=intents)

    #Events
    @bot.event
    async def on_ready():
        await bot.add_cog(TasksCog(bot, cache))
        print("We're alive!")
        return 

    #Character Management
    @bot.command(brief="Delete exisiting character and create a new one")
    async def Create(ctx, *, characterName=""):
        player = ctx.author.name
        if len(characterName.strip()) == 0:
            await ctx.reply("Enter a valid name for your character")
            return
        try:
            await characterService.CreateNewCharacter(characterName, player)
            cachedChar = cache.get(player)
            print(json.dumps(cachedChar.to_dict()))
            await ctx.reply(f"Character {characterName} created successfully")
            ch = await characterService.DescribeCharacter(player)
            await ctx.reply(json.dumps(ch, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("There was an error creating your character :(")
        
        return

    @bot.command(brief="Show simple character sheet")
    async def DescribeCharacter(ctx):
        player = ctx.author.name
        await characterService.GetSetChar(player)
        ch = await characterService.DescribeCharacter(player)
        await ctx.reply(json.dumps(ch, indent=4))
        return

    #Inventory Management
    @bot.command(brief="Show inventory")
    async def ShowInventory(ctx):
        player = ctx.author.name
        await characterService.GetSetChar(player)
        retval = await inventoryService.ShowInventorySimple(player)

        await ctx.reply(json.dumps(retval, indent=4))
        return  

    @bot.command(brief="Describe equipped item")
    async def DescribeEquipment(ctx, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to describe")
        player = ctx.author.name
        await characterService.GetSetChar(player)
        ch = cache.get(player)
        inv = ch.Inventory.Equipped
        
        itemList = list(filter(lambda i: i.Name == itemName, inv))
        if len(itemList) == 0:
            await ctx.reply("No item of that name equipped")
            return

        item = itemList[0].to_dict()
        await ctx.reply(json.dumps(item, indent=4))
        return 

    @bot.command(brief="Unequip Item")
    async def Unequip(ctx, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to unequip")
        player = ctx.author.name
        await characterService.GetSetChar(player)
        try:
            response = await inventoryService.UnequipItem(player, itemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            retval = await inventoryService.ShowInventorySimple(player)
            await ctx.reply(json.dumps(retval, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("Item could not be unequipped")

        return
        
    @bot.command(brief="Equip Item")
    async def Equip(ctx, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to equip")
        player = ctx.author.name
        await characterService.GetSetChar(player)
        try:
            response = await inventoryService.EquipItem(player, itemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            retval = await inventoryService.ShowInventorySimple(player)
            await ctx.reply(json.dumps(retval, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("Item could not be equipped")

        return
        
    @bot.command(brief="Drop Stored Item")
    async def Drop(ctx, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to equip")
        player = ctx.author.name
        await characterService.GetSetChar(player)
        try:
            response = await inventoryService.DiscardItem(player, itemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            retval = await inventoryService.ShowInventorySimple(player)
            await ctx.reply(json.dumps(retval, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("Item could not be equipped")

        return

    @bot.command(brief="Give player a stored item")
    async def GiveItem(ctx, target:str="", itemName:str=""):
        if len(target.strip()) == 0:
            await ctx.reply("No player to give item identified")
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to trade")

        player = ctx.author.name
        await characterService.GetSetChar(player)
        await characterService.GetSetChar(target)
        
        try:
            response = await inventoryService.GiveItem(player, target, itemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            else:
                await ctx.reply(f"@{player} gave @{target} '{itemName}'")
        except Exception as ex:
            print(ex)
            await ctx.reply("Trade could not be completed")
        return
    
    @bot.command(brief="Give Player Gold")
    async def GiveGold(ctx, target:str="", amount:str=""):
        if len(target.strip()) == 0:
            await ctx.reply("No player to give gold identified")
            return
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
        await characterService.GetSetChar(player)
        await characterService.GetSetChar(target)

        try:
            response = await inventoryService.GiveGold(player, target, amountInt)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            else:
                await ctx.reply(f"@{player} gave @{target} {amount} Gold")
        except Exception as ex:
            print(ex)
            await ctx.reply("Trade could not be completed")
        return


    @bot.command(brief="Change name of stored item in inventory")
    async def Rename(ctx, itemName:str="", newItemName:str=""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item name given")
            return
        if len(newItemName.strip()) == 0:
            await ctx.reply("No new name given")
            return
        
        player = ctx.author.name
        await characterService.GetSetChar(player)

        try:
            response = await inventoryService.RenameItem(player, itemName, newItemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            retval = await inventoryService.ShowInventorySimple(player)
            await ctx.reply(json.dumps(retval, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("Item could not be renamed")

        return


    token = os.getenv("DISCORD_TOKEN")
    bot.run(token)
