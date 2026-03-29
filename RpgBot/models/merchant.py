from models.loot import Loot

class Merchant():
    def __init__(self):
        self.Inventory = MerchantInventory()
        return

class MerchantInventory():
    def __init__(self):
        self.Wares = []
        return

    def to_dict(self):
        return {
            "Wares": [ware.to_dict() for ware in self.Wares]
        }

    def checkInventoryForDuplicates(self):
        wares = self.Wares

        for item in wares:
            if item.Item.Type == "Consumable":
                continue
            #get list of all items with the same name
            duplicates = list(filter(lambda i: i.Item.Name == item.Item.Name, wares))

            #if more than one item with the same name...
            if len(duplicates) > 1:
                #loop through inventory and rename the item
                dupName = item.Item.Name
                dupCount = 0
                for dup in wares:
                    if dup.Item.Name == dupName:
                        dup.Item.Name += f" ({dupCount})"
                        dupCount += 1
                    continue
            continue

        wares.sort(key=lambda w: w.Item.Name)
        return
        
class Wares():
    def __init__(self):
        self.Item = Loot()
        self.Value = 0
        return

    def to_dict(self):
        return {
            "Item": self.Item.to_dict(),
            "Value": self.Value
        }