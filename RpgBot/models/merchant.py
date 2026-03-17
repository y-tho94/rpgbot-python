from loot import Loot

class Merchant():
    def __init__(self):
        self.Inventory = MerchantInventory()
        return

class MerchantInventory():
    def __init__(self):
        self.Wares = [Wares()]
        return

    def to_dict(self):
        return {
            "Wares": [ware.to_dict() for ware in self.Wares]
        }

class Wares():
    def __init__(self):
        self.Item = Loot()
        self.value
        return

    def to_dict(self):
        return {
            "Item": self.Item.to_dict(),
            "Value": self.Value
        }