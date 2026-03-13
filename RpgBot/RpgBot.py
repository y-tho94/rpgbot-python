from data.dataContext import Context
from services.characterService import CharacterService
import json

if __name__ == '__main__':
    print('starting...')
    
    #Dependency injection and startup services
    db = Context()
    characterService = CharacterService(db=db)

    DEBUG = True
    #simulate game in CLI
    while(DEBUG):
        command = input("Awaiting command: ")
        if command == "create character":
            ch = characterService.createNewCharacter(chname="Bob", player="Jake")
            chJson = json.dumps(ch.to_dict())
            print(chJson)
    #end debug loop

