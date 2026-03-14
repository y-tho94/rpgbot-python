from data.dataContext import Context
from services.characterService import CharacterService
from services.cacheService import SimpleCache
from services.lootService import LootService
import json

if __name__ == '__main__':
    print('starting...')
    
    #Dependency injection and startup services
    db = Context()
    cache = SimpleCache()
    lootService = LootService(db=db)
    characterService = CharacterService(db=db, cache=cache, lootService=lootService)


    DEBUG = True
    #simulate game in CLI
    while(DEBUG):
        command = input("Awaiting command: ")
        match command:
            case "create character":
                ch = characterService.CreateNewCharacter(chname="Bob", player="Jake")
                cachedChar = cache.get("Jake")
                chJson = json.dumps(cachedChar.to_dict(), indent=4)
                print(chJson)
            case "get character":
                ch = characterService.GetCharacter("Jake")
                cachedChar = cache.get("Jake")
                chJson = json.dumps(cachedChar.to_dict(), indent=4)
                print(chJson)
            case "generate loot":
                l = lootService.GenerateLootByName("Dagger")
                try:
                    lJson = l.to_dict()
                    print(lJson)
                except Exception as ex:
                    print(ex)
            case "unequip test":
                ch = characterService.UnequipItem(player="Jake", itemName="Leather Helmet")
                cachedChar = cache.get("Jake")
                chJson = json.dumps(cachedChar.to_dict(), indent=4)
                print(chJson)
            case "equip test":
                ch = characterService.EquipItem(player="Jake", itemName="Leather Helmet")
                cachedChar = cache.get("Jake")
                chJson = json.dumps(cachedChar.to_dict(), indent=4)
                print(chJson)
    #end debug loop

