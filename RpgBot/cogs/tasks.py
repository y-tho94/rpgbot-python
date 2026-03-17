from discord.ext import tasks, commands
from services.cacheService import SimpleCache

class TasksCog(commands.Cog):
    def __init__(self, bot:commands.Bot, cache:SimpleCache):
        self.bot = bot
        self.cache = cache
        self.ClearCache.start()
    
    def cog_unload(self):
        self.ClearCache.cancel()

    @tasks.loop(hours=8)
    async def ClearCache(self):
        self.cache.clear()
        print("Cache cleared")
        return