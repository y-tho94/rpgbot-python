from services.cacheService import SimpleCache

class DungeonService():
    def __init__(self, cache:SimpleCache, systemCache:SimpleCache):
        self.cache = cache
        self.systemCache = systemCache

    async def ShowLootables(self):
        lootables = self.systemCache.get("Lootables")
        if lootables is None:
            return "No lootables found"
        
        lootList = []
        for l in lootables:
            lootList.append(l.Name)

        return lootList

    async def DescribeLoot(self, lootName:str):
        lootables = self.systemCache.get("Lootables") or []
        if lootables is None or len(lootables) == 0:
            return {
                "Error": "No lootables found"
            }
        
        lootObj = list(filter(lambda i: i.Name == lootName, lootables))
        if len(lootObj) == 0:
            return {
                "Error": "Item not found"
            }

        lootObj = lootObj[0]
        itemdict = lootObj.to_dict()
        effects = lootObj.Effects.to_dict()
        for key, value in lootObj.Effects.to_dict().items():
            if value == 0 or value == [] or value == "":
                del effects[key]
        itemdict["Effects"] = effects
        return itemdict

    async def TakeLoot(self, player:str, lootName:str):
        character = self.cache.get(player)
        if character is None:
            return "Error: Character not found"
        lootables = self.systemCache.get("Lootables")
        if lootables is None or len(lootables) == 0:
            return "Error: No lootables found"
        
        lootObj = list(filter(lambda i: i.Name == lootName, lootables))
        if len(lootObj) == 0:
            return f"Error: Item '{lootName}' not found"
        lootObj = lootObj[0]
        lootables.remove(lootObj)
        character.Inventory.Stored.append(lootObj)
        self.cache.set(player, character)
        self.systemCache.set("Lootables", lootables)
        return f"{lootName} added to inventory"
