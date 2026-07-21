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
                dupName = item.Name
                dupCount = 1
                # ensure the highest "(int)" in each item.Name duplicate is always assigned to dupCount
                splitName = ""
                for dup in wares:
                    splitName = dup.Name.split("|")
                    if dup.Name.startswith(splitName[0]) and "|" in dup.Name:
                        dupCount = max(dupCount, int(splitName[-1]) + 1)

                for dup in wares:
                    if dup.Name == dupName:
                        dup.Name = f"{splitName[0]} | {dupCount}"
                        dupCount += 1

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