import discord
from discord.ext import commands
from services.characterService import CharacterService
from services.vaultService import VaultService
import json

class VaultCog(commands.Cog):
    def __init__(self, bot:commands.Bot, characterService:CharacterService, vaultService:VaultService):
        self.bot = bot
        self.characterService = characterService
        self.vaultService = vaultService

    async def cog_load(self):
        print("VaultCog loaded")

    async def cog_unload(self):
        print("VaultCog unloaded")

    @commands.command(brief="Show vault contents")
    async def Vault(self, ctx):
        player = ctx.author.name
        vault = await self.vaultService.GetVault(player)

        if vault.Inventory == {} or "Items" not in vault.Inventory or len(vault.Inventory["Items"]) < 1:
            await ctx.reply("Your vault is empty")
            return

        await ctx.reply(json.dumps(vault.Inventory["Items"], indent=4))
        return

    @commands.command(brief="Deposit item from stored inventory to vault")
    async def Deposit(self, ctx, *, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item name given")
            return

        player = ctx.author.name
        response = await self.vaultService.AddItemToVault(player, itemName)
        await ctx.reply(json.dumps(response, indent=4))
        return

    @commands.command(brief="Withdraw item from vault to stored inventory")
    async def Withdraw(self, ctx, *, itemName:str = ""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item name given")
            return

        player = ctx.author.name
        response = await self.vaultService.AddItemToInventory(player, itemName)
        await ctx.reply(json.dumps(response, indent=4))
        return
