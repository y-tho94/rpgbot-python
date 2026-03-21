from cogs.ability_cog import AbilityCog
from cogs.admin_cog import AdminCog
from cogs.character_cog import CharacterCog
from cogs.combat_cog import CombatCog
from cogs.merchant_cog import MerchantCog
from cogs.tasks import TasksCog
from data.dataContext import Context
from models import merchant
from services.abilityService import AbilityService
from services.characterService import CharacterService
from services.cacheService import SimpleCache
from services.combatService import CombatService
from services.inventoryService import InventoryService
from services.lootService import LootService
from services.merchantService import MerchantService
import json
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import datetime

if __name__ == '__main__':
    load_dotenv()
    print('starting...')
    
    #Dependency injection and startup services
    db = Context()
    cache = SimpleCache()
    lootService = LootService(db=db)
    characterService = CharacterService(db=db, cache=cache, lootService=lootService)
    abilityService = AbilityService(db=db, cache=cache)
    inventoryService = InventoryService(db=db, cache=cache, abilityService=abilityService)
    merchantService = MerchantService(db=db, cache=cache, lootService=lootService)
    combatService = CombatService(cache=cache, characterService=characterService)

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.guilds = True
    bot = commands.Bot(command_prefix='$', intents=intents)

    genChannelId = int(os.getenv("GENERAL_CHANNEL_ID"))

    #Events
    @bot.event
    async def on_ready():
        await bot.add_cog(AdminCog(bot, cache, characterService, abilityService, lootService, inventoryService, merchantService))
        await bot.add_cog(TasksCog(bot, cache, characterService))
        await bot.add_cog(MerchantCog(bot, cache, merchantService, characterService))
        await bot.add_cog(CharacterCog(bot, cache, characterService))
        await bot.add_cog(CombatCog(bot, cache, combatService, characterService, abilityService))
        await bot.add_cog(AbilityCog(bot, cache, characterService, abilityService))
        print("We're alive!")
        return 

    @bot.event
    async def on_member_join(member):
        guild = member.guild
    
        # 1. Define the permission overwrites.
        # Deny everyone from viewing the channel by default
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, read_messages=True), # Grant access to the new member
            guild.me: discord.PermissionOverwrite(view_channel=True, read_messages=True) # Grant access to the bot
        }

        # Optional: Add an admin role to the overwrites
        # Replace 'Admin' with your actual admin role name or use a role ID
        admin_role = discord.utils.get(guild.roles, name="Admin")
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, read_messages=True)

        # 2. Create the private text channel.
        try:
            channel_name = f"{member.name}-private-channel"
            private_channel = await guild.create_text_channel(
                channel_name,
                overwrites=overwrites,
                topic=f"A private support channel for {member.name}."
            )
            # 3. Send a welcome message in the new channel
            await private_channel.send(f"Welcome, {member.mention}! This is your private channel. Use this for managing your character")
        except discord.Forbidden:
            print(f"Bot does not have the necessary permissions to create a channel in {guild.name}")
        except Exception as e:
            print(f"An error occurred: {e}")

    #Inventory Management
    @bot.command(brief="Show inventory")
    async def ShowInventory(ctx):
        player = ctx.author.name
        await characterService.GetSetChar(player)
        retval = await inventoryService.ShowInventorySimple(player)

        await ctx.reply(json.dumps(retval, indent=4))
        return  

    @bot.command(brief="Describe equipped item")
    async def DescribeEquipment(ctx, *, itemName:str = ""):
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

    @bot.command(brief="Describe stored item")
    async def DescribeItem(ctx, *, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to describe")
        player = ctx.author.name
        await characterService.GetSetChar(player)
        ch = cache.get(player)
        inv = ch.Inventory.Stored
        
        itemList = list(filter(lambda i: i.Name == itemName, inv))
        if len(itemList) == 0:
            await ctx.reply("No item of that name in stored inventory")
            return

        item = itemList[0].to_dict()
        await ctx.reply(json.dumps(item, indent=4))
        return 


    @bot.command(brief="Unequip Item")
    async def Unequip(ctx, *, itemName:str = ""):
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
    async def Equip(ctx, *, itemName:str = ""):
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
    async def Drop(ctx, *, itemName:str = ""):
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
    async def GiveItem(ctx, target:discord.Member="", itemName:str=""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item given to trade")

        player = ctx.author.name
        await characterService.GetSetChar(player)
        await characterService.GetSetChar(target.name)
        
        try:
            response = await inventoryService.GiveItem(player, target.name, itemName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            else:
                channel = bot.get_channel(genChannelId)
                sender = bot.get_user(ctx.author.id)
                await channel.send(f"{sender.mention} gave {target.mention} '{itemName}'")
        except Exception as ex:
            print(ex)
            await ctx.reply("Trade could not be completed")
        return
    
    @bot.command(brief="Give Player Gold")
    async def GiveGold(ctx, target:discord.Member="", amount:str=""):
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
        await characterService.GetSetChar(target.name)

        try:
            response = await inventoryService.GiveGold(player, target.name, amountInt)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            else:
                channel = bot.get_channel(genChannelId)
                sender = bot.get_user(ctx.author.id)
                await channel.send(f"{sender.mention} gave {target.mention} {amount} Gold")
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

    @bot.command(brief="Use an item in stored inventory on target or self")
    async def UseItem(ctx, itemName="", target:discord.Member="self"):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item name given")
            return

        player = ctx.author.name
        await characterService.GetSetChar(player)
        if target == "self":
            target = ctx.author
        await characterService.GetSetChar(target.name)

        response = await inventoryService.UseItem(player, target.name, itemName)
        await ctx.reply(json.dumps(response, indent=4))
        return

    token = os.getenv("DISCORD_TOKEN")
    bot.run(token)
