from models.loot import Loot
from data.dataContext import Context, VaultTable
from models.vault import Vault
from services.characterService import CharacterService
from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update

class VaultService():
    def __init__(self, db:Context, characterService:CharacterService):
        self.db = db.engine
        self.characterService = characterService
        return

    async def GetVault(self, player: str):
        session = Session(bind=self.db)
        statement = select(VaultTable).filter_by(playerName=player)
        vaultRow = session.execute(statement).scalars().first()
        session.close()

        if vaultRow is None:
            return Vault(PlayerName=player, Inventory={})

        vault = Vault().FromDataTable(vaultRow)
        return vault

    async def AddItemToVault(self, player: str, itemName: str):
        charResult = await self.characterService.GetSetChar(player)
        if charResult["Error"]:
            return charResult

        ch = charResult["Character"]
        itemIndex = next((i for i, item in enumerate(ch.Inventory.Stored) if item.Name == itemName), None)

        if itemIndex is None:
            return {"Error": f"Item {itemName} not found in stored inventory"}

        item = ch.Inventory.Stored.pop(itemIndex)
        itemDict = item.to_dict()

        vault = await self.GetVault(player)
        if vault.Inventory is None or vault.Inventory == {}:
            vault.Inventory = {}

        if "Items" not in vault.Inventory:
            vault.Inventory["Items"] = []

        vault.Inventory["Items"].append(itemDict)

        session = Session(bind=self.db)
        existingVault = session.query(VaultTable).filter_by(playerName=player).first()

        if existingVault is None:
            vaultTable = VaultTable(
                playerName=player,
                inventory=vault.Inventory
            )
            session.add(vaultTable)
        else:
            statement = update(VaultTable).where(VaultTable.playerName == player).values(
                inventory=vault.Inventory
            )
            session.execute(statement)

        session.commit()
        session.close()

        await self.characterService.SaveCharacter(player, ch)
        return {"Summary": f"{itemName} added to vault"}

    async def AddItemToInventory(self, player: str, itemName: str):
        vault = await self.GetVault(player)

        if vault.Inventory == {} or "Items" not in vault.Inventory:
            return {"Error": "No items in vault"}

        itemIndex = next((i for i, item in enumerate(vault.Inventory["Items"]) if item["Name"] == itemName), None)

        if itemIndex is None:
            return {"Error": f"Item {itemName} not found in vault"}

        itemDict = vault.Inventory["Items"].pop(itemIndex)
        lootItem = Loot(**itemDict)

        charResult = await self.characterService.GetSetChar(player)
        if charResult["Error"]:
            return charResult

        ch = charResult["Character"]

        if len(ch.Inventory.Stored) >= ch.MaxInventory:
            return {"Error": "Stored inventory is full"}

        ch.Inventory.Stored.append(lootItem)
        ch.Inventory.checkInventoryForDuplicates()
        await self.characterService.SaveCharacter(player, ch)

        session = Session(bind=self.db)
        statement = update(VaultTable).where(VaultTable.playerName == player).values(
            inventory=vault.Inventory
        )
        session.execute(statement)
        session.commit()
        session.close()

        return {"Summary": f"{itemName} moved from vault to stored inventory"}