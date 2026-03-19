from discord.ext import tasks, commands
from services import merchantService
from services.cacheService import SimpleCache
from services.characterService import CharacterService
from services.merchantService import MerchantService
import json
class MerchantCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, merchantService:MerchantService, characterService:CharacterService):
        self.bot = bot
        self.cache = cache
        self.merchantService = merchantService
        self.characterService = characterService

        return

    @commands.command(breif="Show Merchant inventory")
    async def ShowMerchant(self, ctx):
        await self.merchantService.GetSetMerchant()

        retval = await self.merchantService.ShowMerchantInventory()
        await ctx.reply(json.dumps(retval, indent=4))

    @commands.command(brief="Describe item in merchant inventory")
    async def DescribeMerchant(self, ctx, *, itemName:str=""):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item name given to describe")
            return
        await self.merchantService.GetSetMerchant()
        merchant = self.cache.get("Wandering Merchant")
        itemList = list(filter(lambda i: i.Item.Name == itemName, merchant.Inventory.Wares))
        if len(itemList) == 0:
            await ctx.reply("No item of that name in inventory")
            return

        item = itemList[0].Item.to_dict()
        await ctx.reply(json.dumps(item, indent=4))
        return

    @commands.command(brief="Tells you the value of an item and how much the merchant will buy it for")
    async def AppraiseItem(self, ctx, *, itemName:str):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item name given to appraise")
            return

        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        ch = self.cache.get(player)
        itemToSell = list(filter(lambda i: i.Name == itemName, ch.Inventory.Stored))
        if len(itemToSell) == 0:
            await ctx.reply("No item of that name in stored inventory")
            return

        itemVal = self.merchantService.AppraiseItem(itemToSell[0])
        sellVal = itemVal // 2
        await ctx.reply(f"Your item is worth {itemVal} Gold. The merchant will buy it for {sellVal} Gold")

    @commands.command(brief="Buy item from merchant")
    async def BuyItem(self, ctx, *, itemName:str):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item name given to buy")
            return
        await self.merchantService.GetSetMerchant()
        player = ctx.author.name
        await self.characterService.GetSetChar(player)

        response = await self.merchantService.BuyItem(player, itemName)
        if response is not None:
            await ctx.reply(json.dumps(response, indent=4))
            return

        await ctx.reply(f"You bought {itemName} from the shop")

    @commands.command(brief="Sell item to merchant from stored inventory")
    async def SellItem(self, ctx, *, itemName:str):
        if len(itemName.strip()) == 0:
            await ctx.reply("No item name given to sell")
            return
        await self.merchantService.GetSetMerchant()
        player = ctx.author.name
        await self.characterService.GetSetChar(player)

        response = await self.merchantService.SellItem(player, itemName)
        if response is not None:
            await ctx.reply(json.dumps(response, indent=4))
            return

        await ctx.reply(f"You sold {itemName} to the shop")

