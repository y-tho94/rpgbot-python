from discord.ext import commands
from services.cacheService import SimpleCache
from services.characterService import CharacterService
from services.abilityService import AbilityService
import json

class AbilityCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, characterService:CharacterService, abilityService:AbilityService):
        self.bot = bot
        self.cache = cache
        self.characterService = characterService
        self.abilityService = abilityService
        return

    @commands.command(brief="Show Ability List")
    async def ShowAbilities(self, ctx):
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        retval = await self.abilityService.ShowAbilityList(player)
        await ctx.reply(json.dumps(retval, indent=4))
        return

    @commands.command(brief="Describe an ability")
    async def DescribeAbility(self, ctx, *, abilityName:str = ""):
        if len(abilityName.strip()) == 0:
            await ctx.reply("No ability given to describe")
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        ch = self.cache.get(player)
        inv = ch.Inventory.Ability
        
        itemList = list(filter(lambda i: i.Name == abilityName, inv))
        if len(itemList) == 0:
            await ctx.reply("No ability of that name in abilities")
            return

        item = itemList[0].to_dict()
        await ctx.reply(json.dumps(item, indent=4))
        return 

    @commands.command(brief="Change name of ability")
    async def RenameAbility(self, ctx, abilityName:str="", newAbilityName:str=""):
        if len(abilityName.strip()) == 0:
            await ctx.reply("No ability name given")
            return
        if len(newAbilityName.strip()) == 0:
            await ctx.reply("No new name given")
            return
        
        player = ctx.author.name
        await self.characterService.GetSetChar(player)

        try:
            response = await self.abilityService.RenameAbility(player, abilityName, newAbilityName)
            if response is not None:
                await ctx.reply(json.dumps(response, indent=4))
            retval = await self.abilityService.ShowAbilityList(player)
            await ctx.reply(json.dumps(retval, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("Ability could not be renamed")

        return

    @commands.command(brief="Forget a learned ability")
    async def Forget(self, ctx, *, abilityName:str = ""):
        if len(abilityName.strip()) == 0:
            await ctx.reply("Enter an ability to forget")
            return

        player = ctx.author.name
        await self.characterService.GetSetChar(player)

        response = await self.abilityService.ForgetAbility(player, abilityName)