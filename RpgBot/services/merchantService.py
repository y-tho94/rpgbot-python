from cacheService import SimpleCache
from lootService import LootService
from models.loot import Loot
from models.merchant import Merchant, Wares

class MerchantService():
    def __init__(self, cache:SimpleCache, lootService:LootService):
        self.cache = cache
        self.lootService = lootService
        return

    async def GetSetMerchant(self):
        merchant = self.cache.get("Wandering Merchant")

        if merchant is None:
            await self.CreateMerchant()

        return

    async def CreateMerchant(self):
        merchant = Merchant()
        for i in range(10):
            item = self.lootService.GenerateLoot()
            ware = Wares()
            ware.Item = item
            ware.Value = self.AppraiseItem(item)

            merchant.MerchantInventory.Wares.append(ware)
            continue

        self.cache.set("Wandering Merchant", merchant)


    def AppraiseItem(self, item:Loot):
        effectsVals = item.Effects.to_dict().values()

        value = 0
        for val in effectsVals:
            value += val
            continue

        return (val * 10)


