from cogs.ability_cog import AbilityCog
from cogs.admin_cog import AdminCog
from cogs.character_cog import CharacterCog
from cogs.combat_cog import CombatCog
from cogs.dungeon_cog import DungeonCog
from cogs.inventory_cog import InventoryCog
from cogs.merchant_cog import MerchantCog
from cogs.tasks import TasksCog
from data.dataContext import Context
from services.abilityService import AbilityService
from services.characterService import CharacterService
from services.cacheService import SimpleCache
from services.combatService import CombatService
from services.inventoryService import InventoryService
from services.lootService import LootService
from services.merchantService import MerchantService
from services.monsterservice import MonsterService
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
    monsterCache = SimpleCache()
    lootService = LootService(db=db)
    characterService = CharacterService(db=db, cache=cache, lootService=lootService)
    abilityService = AbilityService(db=db, cache=cache)
    inventoryService = InventoryService(db=db, cache=cache, abilityService=abilityService)
    merchantService = MerchantService(db=db, cache=cache, lootService=lootService)
    combatService = CombatService(cache=cache, characterService=characterService)
    monsterService = MonsterService(db=db, cache=cache, monsterCache=monsterCache, characterService=characterService, lootService=lootService)

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.guilds = True
    bot = commands.Bot(command_prefix='$', intents=intents)

    genChannelId = int(os.getenv("GENERAL_CHANNEL_ID"))

    #Events
    @bot.event
    async def on_ready():
        await bot.add_cog(AdminCog(bot, cache, monsterCache, characterService, abilityService, lootService, inventoryService, merchantService, monsterService))
        await bot.add_cog(TasksCog(bot, cache, characterService, monsterService))
        await bot.add_cog(MerchantCog(bot, cache, merchantService, characterService, inventoryService))
        await bot.add_cog(CharacterCog(bot, cache, characterService))
        await bot.add_cog(CombatCog(bot, cache, monsterCache, combatService, characterService, abilityService, monsterService))
        await bot.add_cog(AbilityCog(bot, cache, characterService, abilityService))
        await bot.add_cog(InventoryCog(bot, cache, monsterCache, inventoryService, characterService, monsterService))
        await bot.add_cog(DungeonCog(bot, monsterCache, monsterService))
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
    

    token = os.getenv("DISCORD_TOKEN")
    bot.run(token)
