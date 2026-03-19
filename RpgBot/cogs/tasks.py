from discord.ext import tasks, commands
from services.cacheService import SimpleCache
from services.characterService import CharacterService

class TasksCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache, characterService:CharacterService):
        self.bot = bot
        self.cache = cache
        self.characterService = characterService
        self.ClearCache.start()
    
    def cog_unload(self):
        self.ClearCache.cancel()

    @tasks.loop(hours=8)
    async def ClearCache(self):
        await self.characterService.SaveCharacters()
        self.cache.clear()
        print("Cache cleared")
        return