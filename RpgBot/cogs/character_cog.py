import discord
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
        if len(characterName.strip()) == 0:
            await ctx.reply("Enter a valid name for your character")
            return

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

    @commands.command(brief="Show simple character sheet", aliases=["Describe"])
    async def DescribeCharacter(self, ctx):
        player = ctx.author.name
        await self.characterService.GetSetChar(player)
        ch = await self.characterService.DescribeCharacter(player)
        await ctx.reply(json.dumps(ch, indent=4))
        return

    @commands.command(brief="Rename your character", aliases=["RenameCh"])
    async def RenameCharacter(self, ctx:commands.Context, *, newName=""):
        newName = newName.replace("\"", "")
        player = ctx.author.name
        member = ctx.author
        
        if len(newName.strip()) == 0:
            await ctx.reply("Enter a valid name for your character")
            return
        try:
            checkforname = ctx.guild.get_member_named(newName)
            if checkforname is not None and checkforname.id != member.id:
                await ctx.reply("That name is already taken by another player. Please choose a different name")
                return
            await member.edit(nick=newName)
        except Exception as ex:
            print(ex)

        try:
            ch = self.cache.get(player)
            ch.Name = newName
            await self.characterService.SaveCharacter(player, ch)
            await ctx.reply(f"Character renamed to {newName} successfully")
        except Exception as ex:
            print(ex)
            await ctx.reply("There was an error renaming your character :(")
        
        return

    @commands.command(brief="Level up an attribute. ex: $LevelUp Strength")
    async def LevelUp(self, ctx, stat:str):
        player = ctx.author.name
        await self.characterService.GetSetChar(player)

        response = await self.characterService.LevelUpChar(player, stat)
        await ctx.reply(json.dumps(response, indent=4))
        return

    #This command lets players rest at the inn to restore their HP and AP to full. It can only be used in the general channel
    # @commands.command(brief="Rest at the inn to restore HP and AP to full. Can only be used in the general channel", aliases=["Rest"])
    # async def RestAtInn(self, ctx):
    #     channel = ctx.channel