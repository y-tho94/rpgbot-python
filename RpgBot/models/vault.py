from data.dataContext import VaultTable

class Vault():
    def __init__(self, PlayerName:str="", Inventory:str="{}"):
        self.PlayerName = PlayerName
        self.Inventory = Inventory
        return

    def to_dict(self):
        return {
            "PlayerName": self.PlayerName,
            "Inventory": self.Inventory
        }

    def ToDataTable(self):
        vt = VaultTable(
            playerName = self.PlayerName,
            inventory = self.Inventory
        )

        return vt

    def FromDataTable(self, vt:VaultTable):
        self.PlayerName = vt.playerName
        self.Inventory = vt.inventory

        return self