from data.dataContext import Context
from services.characterService import CharacterService
from services.lootService import LootService
import json

if __name__ == '__main__':
    print('starting...')
    
    #Dependency injection and startup services
    db = Context()
    characterService = CharacterService(db=db)
    lootService = LootService(db=db)


    DEBUG = True
    #simulate game in CLI
    while(DEBUG):
        command = input("Awaiting command: ")
        match command:
            case "create character":
                ch = characterService.createNewCharacter(chname="Bob", player="Jake")
                chJson = json.dumps(ch.to_dict())
                print(chJson)
            case "generate loot":
                l = lootService.GenerateLoot("Dagger")
                lJson = l.to_dict()
                print(lJson)

    #end debug loop

