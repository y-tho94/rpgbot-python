from data.dataContext import CharacterTable, Context
from services.cacheService import SimpleCache
from services.lootService import LootService
from models.loot import Loot
from models.merchant import Merchant, Wares
from sqlalchemy.orm import Session
from sqlalchemy import update

class MerchantService():
    def __init__(self, db:Context, cache:SimpleCache, lootService:LootService):
        self.db = db.engine
        self.cache = cache
        self.lootService = lootService
        return

    async def GetSetMerchant(self):
        merchant = self.cache.get("Wandering Merchant")
        if merchant is None:
            await self.CreateMerchant()

        scrollMerchant = self.cache.get("Scroll Merchant")
        if scrollMerchant is None:
            await self.CreateScrollMerchant()

        return

    async def CreateMerchant(self):
        merchant = Merchant()
        for _ in range(3):
            item = await self.lootService.GenerateLoot()
            ware = Wares()
            ware.Item = item
            ware.Value = self.AppraiseItem(item)

            merchant.Inventory.Wares.append(ware)
            continue

        for _ in range(4):
            item = await self.lootService.GenerateLootByType("Consumable")
            ware = Wares()
            ware.Item = item
            ware.Value = self.AppraiseItem(item)

            merchant.Inventory.Wares.append(ware)
            continue

        for _ in range(3):
            special = await self.lootService.GenerateSpecialLoot()
            specialWare = Wares()
            specialWare.Item = special
            specialWare.Value = self.AppraiseItem(special)
            merchant.Inventory.Wares.append(specialWare)
        
        merchant.Inventory.checkInventoryForDuplicates()
        self.cache.set("Wandering Merchant", merchant)
        return

    async def CreateScrollMerchant(self):
        merchant = Merchant()
        for _ in range(10):
            scroll = await self.lootService.GenerateLootByName("Skill Scroll")
            ware = Wares()
            ware.Item = scroll
            ware.Value = self.AppraiseItem(scroll)
            merchant.Inventory.Wares.append(ware)
            continue
        
        merchant.Inventory.checkInventoryForDuplicates()
        self.cache.set("Scroll Merchant", merchant)
        return

    async def ShowMerchantInventory(self, merchantName:str):
        merchant = self.cache.get(merchantName)
        if merchant is None:
            return {
                "Error": f"No merchant named {merchantName} found"    
            }

        wares = merchant.Inventory.Wares

        retval = []
        for w in wares:
            item = f"{w.Item.Name} | {w.Value}G"
            retval.append(item)
            continue

        return retval


    def AppraiseItem(self, item:Loot):
        effectsVals = [i for i in item.Effects.to_dict().values() if isinstance(i, int)]

        value = 0
        for val in effectsVals:
            value += val if val > 0 else (val * -1)
            continue

        nonMagicalTypes = ["Slash", "Pierce", "Bludgeon", "Heavy", "Light"]
        if item.Effects.Type not in nonMagicalTypes:
            value *= 5
            pass

        value += len(item.Effects.Use) * 10

        return (value * 10 if value > 1 else 1)

    async def BuyItem(self, playerName:str, itemName:str, merchantName:str):
        ch = self.cache.get(playerName)
        merchant = self.cache.get(merchantName)
        if merchant is None:
            return {
                "Error": f"No merchant named {merchantName} found"    
            }

        if len(ch.Inventory.Stored) == ch.MaxInventory:
            return {
                "Error": "No room in stored inventory"
            }

        itemToBuy = list(filter(lambda i: i.Item.Name == itemName, merchant.Inventory.Wares))
        if len(itemToBuy) == 0:
            return {
                "Error": f"Item {itemName} does not exist in merchant inventory"
            }

        itemVal = itemToBuy[0].Value
        playerGold = ch.Inventory.Gold

        if itemVal > playerGold:
            return {
                "Error": "Insufficient funds"
            }

        ch.Inventory.Gold -= itemVal
        merchant.Inventory.Wares.remove(itemToBuy[0])
        ch.Inventory.Stored.append(itemToBuy[0].Item)
        ch.Inventory.checkInventoryForDuplicates()

        session = Session(bind = self.db)
        chTable = ch.ToCharacterTable(playerName)

        statement = update(CharacterTable).where(CharacterTable.playerName == playerName).values(inventory = chTable.inventory)
        session.execute(statement)
        session.commit()
        session.close()

        self.cache.set(playerName, ch)
        return

    async def SellItem(self, playerName:str, itemName:str):
        ch = self.cache.get(playerName)
        merchant = self.cache.get("Wandering Merchant")

        if len(merchant.Inventory.Wares) >= 20:
            return {
                "Error": "No more room in merchant inventory"
            }

        itemToSell = list(filter(lambda i: i.Name == itemName, ch.Inventory.Stored))
        if len(itemToSell) == 0:
            return {
                "Error": "Item does not exist in player stored inventory"
            }
        
        ch.Inventory.Stored.remove(itemToSell[0])
        
        itemVal = self.AppraiseItem(itemToSell[0])

        ch.Inventory.Gold += itemVal // 2

        ware = Wares()
        ware.Item = itemToSell[0]
        ware.Value = itemVal
        merchant.Inventory.Wares.append(ware)
        merchant.Inventory.checkInventoryForDuplicates()

        session = Session(bind = self.db)
        chTable = ch.ToCharacterTable(playerName)

        statement = update(CharacterTable).where(CharacterTable.playerName == playerName).values(inventory = chTable.inventory)
        session.execute(statement)
        session.commit()
        session.close()

        self.cache.set(playerName, ch)
        return

