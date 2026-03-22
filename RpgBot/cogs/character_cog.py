from discord.ext import tasks, commands
from services.cacheService import SimpleCache
from services.characterService import CharacterService
import json

class CharacterCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, characterService:CharacterService):
        self.bot = bot
        self.cache = cache
        self.characterService = characterService
        return

    @commands.command(brief="Delete exisiting character and create a new one")
    async def Create(self, ctx:commands.Context, *, characterName=""):
        characterName = characterName.replace("\"", "")
        player = ctx.author.name
        member = ctx.author
        try:
            checkforname = ctx.guild.get_member_named(characterName)
            if checkforname is not None and checkforname.id != member.id:
                await ctx.reply("That name is already taken by another player. Please choose a different name")
                return
            await member.edit(nick=characterName)
        except Exception as ex:
            print(ex)

        if len(characterName.strip()) == 0:
            await ctx.reply("Enter a valid name for your character")
            return
        try:
            await self.characterService.CreateNewCharacter(characterName, player)
            cachedChar = self.cache.get(player)
            print(json.dumps(cachedChar.to_dict()))
            await ctx.reply(f"Character {characterName} created successfully")
            ch = await self.characterService.DescribeCharacter(player)
            await ctx.reply(json.dumps(ch, indent=4))
        except Exception as ex:
            print(ex)
            await ctx.reply("There was an error creating your character :(")
        
        return

    @commands.command(brief="Show simple character sheet")
    async def DescribeCharacter(self, ctx):
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        ch = await self.characterService.DescribeCharacter(player)
        await ctx.reply(json.dumps(ch, indent=4))
        return