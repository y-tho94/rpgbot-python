from data.dataContext import Context, MonsterTable
from models.ability import Ability
from models.monster import Monster
from models.character import Character
from models.loot import Loot
from services.cacheService import SimpleCache
from services.characterService import CharacterService
from services.lootService import LootService
from sqlalchemy.orm import Session
from sqlalchemy import select, update
import random


class MonsterService:
    def __init__(self, db:Context, cache:SimpleCache, monsterCache:SimpleCache, characterService:CharacterService, lootService:LootService):
        self.db = db.engine
        self.cache = cache
        self.monsterCache = monsterCache
        self.characterService = characterService
        self.lootService = lootService
        return

    #get mob monster from db then save it to monster cache and return it
    async def GetMobMonster(self):
        monstersInDungeon = self.monsterCache.cache.keys()
        if len(monstersInDungeon) == 20:
            return None

        statement = select(MonsterTable).filter_by(type = "mob")

        session = Session(bind=self.db)
        try:
            monsters = session.execute(statement).scalars().all()
            session.close()
            if monsters is None: 
                return None

            monsterObj = random.choice(monsters)

            monster = Monster().FromMonsterTable(monsterObj)
            monstersInCacheWithSameName = [m for m in self.monsterCache.cache.keys() if m.startswith(monster.Name)]
            monsterName = f"{monster.Name} {len(monstersInCacheWithSameName) + 1}"
            monster.Name = monsterName
            self.monsterCache.set(monster.Name, monster)
            return monster
        except Exception as ex:
            print(ex)
            return None
            

    #get raid monster from db then save it to monster cache and return it
    async def GetRaidMonster(self):
        statement = select(MonsterTable).filter_by(type = "raid")

        session = Session(bind=self.db)
        try:
            monsters = session.execute(statement).scalars()
            session.close()
            if monsters is None: 
                return None

            monsterObj = random.choice(monsters)

            monster = Monster().FromMonsterTable(monsterObj)
            self.monsterCache.set(monster.Name, monster)
            return monster
        except Exception as ex:
            print(ex)
            return None

    #use ability on monster
    async def UseAbility(self, player:str, target:str, abilityName):
        ch = self.cache.get(player) or Character()
        monster = self.monsterCache.get(target) or Monster()

        abilityToUse = list(filter(lambda a: a.Name == abilityName, ch.Inventory.Ability))
        if len(abilityToUse) == 0:
            return {
                "Error": "No ability of that name available"
            }
        
        ability = abilityToUse[0] or Ability()

        #check if enough AP
        if ch.CurrentAP < ability.Cost:
            return {
                "Error": "Insufficient AP"    
            }

        #deplete AP by cost
        ch.CurrentAP -= ability.Cost
        
        if player not in monster.InteractingPlayers:
            monster.InteractingPlayers.append(player)

        #apply effects
        summary = [f"{ch.Name} used {ability.Name}"]

        abilityType = ability.Type
        effectType = ability.Effects.Type

        modifier = 0

        match effectType:
            case "Holy":
                modifier += ((ch.Faith - 10) // 2)  + ch.SpellDamage
            case _:
                modifier += ((ch.Intelligence - 10) // 2)  + ch.SpellDamage

        healAmount = 0 if ability.Effects.Heal == 0 else ability.Effects.Heal + modifier
        selfHealAmount = 0 if ability.Effects.SelfHeal == 0 else ability.Effects.SelfHeal + modifier
        inflictAmount = 0 if ability.Effects.Inflict == 0 else ability.Effects.Inflict + modifier
        selfInflictAmount = ability.Effects.SelfInflict
        boostAmount = 0 if len(ability.Effects.Boost) == 0 else modifier
        debuffAmount = 0 if len(ability.Effects.Debuff) == 0 else modifier

        #boost stats
        for stat in ability.Effects.Boost:
            summary.append(f"{ch.Name} boosted {monster.Name}'s {stat} by {boostAmount}")
            match stat:
                case "AttackRating" | "SpellDamage":
                    monster.AttackRating += boostAmount
                case "DamageReduction":
                    monster.DamageReduction += boostAmount
                case "Evasion":
                    monster.Evasion += boostAmount
                case "CritChance":
                    monster.CritChance += boostAmount
        
        #debuff stats
        for stat in ability.Effects.Debuff:
            summary.append(f"{ch.Name} lowered {monster.Name}'s {stat} by {debuffAmount}")
            match stat:
                case "AttackRating" | "SpellDamage":
                    monster.AttackRating = 0 if monster.AttackRating - debuffAmount < 0 else monster.AttackRating - debuffAmount
                case "DamageReduction":
                    monster.DamageReduction = 0 if monster.DamageReduction - debuffAmount < 0 else monster.DamageReduction - debuffAmount
                case "Evasion":
                    monster.Evasion = 0 if monster.Evasion - debuffAmount < 0 else monster.Evasion - debuffAmount
                case "CritChance":
                    monster.CritChance = 0 if monster.CritChance - debuffAmount < 0 else monster.CritChance - debuffAmount
        
        #self heal
        selfNewHP = ch.CurrentHP + selfHealAmount - selfInflictAmount
        ch.CurrentHP = selfNewHP if selfNewHP <= ch.MaxHP else ch.MaxHP
        if selfHealAmount > 0:
            summary.append(f"{ch.Name} healed for {selfHealAmount} HP")
        
        #self inflict
        if selfInflictAmount > 0:
            summary.append(f"{ch.Name} hurt themself for {selfInflictAmount} {effectType} damage")

        #calc net damage
        critChance = random.randint(1,100)
        critStr = ""
        if ch.CritChance >= critChance:
            inflictAmount *= 2
            critStr = "critically "

        evadeChance = random.randint(1,100)
        if monster.Evasion >= evadeChance:
            inflictAmount = 0
            summary.append(f"{ch.Name} attacked {monster.Name} with {ability.Name}, but missed!")

        if effectType in monster.Weakness:
            inflictAmount *= 2

        if effectType in monster.Resistance:
            inflictAmount = inflictAmount // 2

        damageTaken = inflictAmount - monster.DamageReduction if inflictAmount - monster.DamageReduction > 0 else 0

        #apply heal and damage to target
        newHP = monster.HP + healAmount - damageTaken
        monster.HP =  newHP
        if healAmount > 0:
            summary.append(f"{ch.Name} healed {monster.Name} for {healAmount} HP")

        #damage target
        if damageTaken > 0:
            summary.append(f"{ch.Name} {critStr}inflicted {damageTaken} {effectType} damage to {monster.Name}")

        #check for monster death, responds if alive
        if monster.HP <= 0:
            for playerInCombat in monster.InteractingPlayers:
                summary = await self.DropLoot(summary, playerInCombat, monster)
            self.monsterCache.delete(monster.Name)
        else:
            summary = await self.MonsterAIAction(summary, ch, monster)
        
        #check for character death
        if ch.CurrentHP <= 0:
            summary.append(f"{ch.Name} has fallen. Their body has been claimed by the dungeon, never to be seen again.")
            self.cache.delete(player)
            monster.InteractingPlayers.remove(player)
            self.monsterCache.set(monster.Name, monster)
            await self.characterService.KillCharacter(player)
        else:
            self.cache.set(player, ch)
        
        return {
            "Summary": summary      
        }

    #do monster combat
    async def MonsterCombat(self, player:str, monsterName:str):
        ch = self.cache.get(player) or Character()
        monster = self.monsterCache.get(monsterName) or Monster()

        if player not in monster.InteractingPlayers:
            monster.InteractingPlayers.append(player)

        summary = []
        #character attacks monster
        evadeChance = random.randint(1,100)
        if monster.Evasion >= evadeChance:
            summary.append(f"{ch.Name} attacked {monsterName}, but missed!")
        else:
            attackSummary = f"{ch.Name} attacked {monsterName} "
            critChance = random.randint(1,100)
            attackDmg = ch.AttackRating

            damageType = ""
            weapon = list(filter(lambda i: i.Type == "Hand", ch.Inventory.Equipped))
            if len(weapon) == 0:
                damageType = "Unarmed"
            else:
                damageType = weapon[0].Effects.Type

            if damageType in monster.Weakness:
                attackDmg *= 2

            if damageType in monster.Resistance:
                attackDmg = attackDmg // 2

            if ch.CritChance >= critChance:
                attackDmg *= 2
                attackSummary += "critically "
            damageTot = attackDmg - monster.DamageReduction
            damageReal = damageTot if damageTot > 0 else 0
            monster.HP -= damageReal

            damageType = ""
            weapon = list(filter(lambda i: i.Type == "Hand", ch.Inventory.Equipped))
            if len(weapon) == 0:
                damageType = "Unarmed"
            else:
                damageType = weapon[0].Effects.Type

            attackSummary += f"for {damageReal} {damageType} damage"
            
            summary.append(attackSummary)

        #check for monster death, responds if alive
        if monster.HP <= 0:
            for playerInCombat in monster.InteractingPlayers:
                summary = await self.DropLoot(summary, playerInCombat, monster)
            self.monsterCache.delete(monster.Name)
        else:
            summary = await self.MonsterAIAction(summary, ch, monster)

        #check for character death
        if ch.CurrentHP <= 0:
            summary.append(f"{ch.Name} has fallen. Their body has been claimed by the dungeon, never to be seen again.")
            self.cache.delete(player)
            monster.InteractingPlayers.remove(player)
            await self.characterService.KillCharacter(player)
        else:
            self.cache.set(player, ch)
        return {
            "Summary": summary      
        }

    #use item on monster
    async def UseItem(self, player:str, monster:Monster, itemName:str):
        character = self.cache.get(player) or Character()
        
        itemToUse = list(filter(lambda i: i.Name == itemName, character.Inventory.Stored))
        if len(itemToUse) == 0:
            return {
                "Error": "No item of that name in stored inventory"    
            }

        item = itemToUse[0] or Loot()
        useEffects = item.Effects.Use

        if len(useEffects) == 0:
            return {
                "Error": f"{itemName} has no on-use effects"    
            }
        
        if player not in monster.InteractingPlayers:
            monster.InteractingPlayers.append(player)

        for e in useEffects:
            tokens = e.split()
            effect = tokens[0]

            summary = []
            match effect:
                case "Heal":
                    amount = int(tokens[1])
                    newHP = monster.HP + amount
                    monster.HP = newHP if newHP <= monster.MaxHP else monster.MaxHP
                    summary.append(f"{character.Name} healed {monster.Name} for {amount} HP")
                case "Inflict":
                    amount = int(tokens[1])
                    dmgType = tokens[2]

                    if dmgType in monster.Weakness:
                        amount *= 2
                    if dmgType in monster.Resistance:
                        amount = amount // 2

                    newHP = monster.HP - amount
                    monster.HP = newHP
                    summary.append(f"{character.Name} inflicted {amount} {dmgType} damage to {monster.Name}")
                case "Buff":
                    stat = tokens[1]
                    amount = int(tokens[2])

                    summary.append(f"{character.Name} boosted {monster.Name}'s {stat} by {amount}")
                    match stat:
                        case "AttackRating" | "SpellDamage":
                            monster.AttackRating += amount
                        case "DamageReduction":
                            monster.DamageReduction += amount
                        case "SpellDamage":
                            monster.SpellDamage += amount
                        case "Evasion":
                            monster.Evasion += amount
                        case "CritChance":
                            monster.CritChance += amount
                case "Debuff":
                    stat = tokens[1]
                    amount = int(tokens[2])

                    summary.append(f"{character.Name} boosted {monster.Name}'s {stat} by {amount}")
                    match stat:
                        case "AttackRating" | "SpellDamage":
                            monster.AttackRating = 0 if monster.AttackRating - amount < 0 else monster.AttackRating - amount
                        case "DamageReduction":
                            monster.DamageReduction = 0 if monster.DamageReduction - amount < 0 else monster.DamageReduction - amount
                        case "Evasion":
                            monster.Evasion = 0 if monster.Evasion - amount < 0 else monster.Evasion - amount
                        case "CritChance":
                            monster.CritChance = 0 if monster.CritChance - amount < 0 else monster.CritChance - amount
                case _:
                    pass
            

            #check for monster death, responds if alive
        if monster.HP <= 0:
            for playerInCombat in monster.InteractingPlayers:
                summary = await self.DropLoot(summary, playerInCombat, monster)
            self.monsterCache.delete(monster.Name)
        else:
            summary = await self.MonsterAIAction(summary, character, monster)

        return {
            "Summary" : summary    
        }

    async def DropLoot(self, summary:list, player:str, monster:Monster):
        ch = self.cache.get(player)
        if ch is None:
            return summary
        monsterLoot = monster.DropTable

        summary.append(f"{ch.Name} defeated {monster.Name} and received {monsterLoot.Gold} gold and {monsterLoot.XP} XP!")
        ch.Inventory.Gold += monsterLoot.Gold
        ch.Inventory.XP += monsterLoot.XP

        if ch.MaxInventory > len(ch.Inventory.Stored):
            lootdrop =  random.choice(monsterLoot.Loot)
            item = await self.lootService.GenerateLootByName(lootdrop)
            summary.append(f"{ch.Name} also received {item.Name}!")
            ch.Inventory.Stored.append(item)
            ch.Inventory.checkInventoryForDuplicates()
        self.cache.set(player, ch)
        await self.characterService.SaveCharacter(player, ch)
        return summary

    async def MonsterAIAction(self, summary:list, ch:Character, monster:Monster):
        aiActions = monster.AI.Actions
        monsterMaxHP = monster.MaxHP
        monsterHP = monster.HP

        for aiAction in aiActions:
            #check if % of HP is at or below threshold for action
            if (monsterHP/monsterMaxHP) <= aiAction.HPThreshold / 100:
                actions = aiAction.Action
                for action in actions:
                    actionTokens = action.split(" ")
                    command = actionTokens[0]

                    match command:
                        case "Attack":
                            if len(actionTokens) > 1:
                                target = actionTokens[1]
                                match target:
                                    case "All":
                                        for player in monster.InteractingPlayers:
                                            targetCh = self.cache.get(player) or Character()
                                            summary.append(await self._MonsterCombatMath(targetCh, monster))
                                            self.cache.set(player, targetCh)
                                            continue
                                    case _:
                                        pass
                            else:
                                summary.append(await self._MonsterCombatMath(ch, monster))
                            self.monsterCache.set(monster.Name, monster)
                        case "Heal":
                            amount = int(actionTokens[1])
                            monster.HP += amount
                            summary.append(f"{monster.Name} healed for {amount} HP")
                            self.monsterCache.set(monster.Name, monster)
                        case "Buff":
                            stat = actionTokens[1]
                            boostAmount = int(actionTokens[2])
                            summary.append(f"{monster.Name} boosted its {stat} by {boostAmount}")
                            match stat:
                                case "AttackRating":
                                    monster.AttackRating += boostAmount
                                case "DamageReduction":
                                    monster.DamageReduction += boostAmount
                                case "SpellDamage":
                                    monster.SpellDamage += boostAmount
                                case "Evasion":
                                    monster.Evasion += boostAmount
                                case "CritChance":
                                    monster.CritChance += boostAmount
                            self.monsterCache.set(monster.Name, monster)
                        case "Debuff":
                            stat = actionTokens[1]
                            debuffAmount = int(actionTokens[2])
                            summary.append(f"{monster.Name} lowered {ch.Name}'s {stat} by {debuffAmount}")
                            match stat:
                                case "AttackRating":
                                    ch.AttackRating = 0 if ch.AttackRating - debuffAmount < 0 else ch.AttackRating - debuffAmount
                                case "DamageReduction":
                                    ch.DamageReduction = 0 if ch.DamageReduction - debuffAmount < 0 else ch.DamageReduction - debuffAmount
                                case "SpellDamage":
                                    ch.SpellDamage = 0 if ch.SpellDamage - debuffAmount < 0 else ch.SpellDamage - debuffAmount
                                case "Evasion":
                                    ch.Evasion = 0 if ch.Evasion - debuffAmount < 0 else ch.Evasion - debuffAmount
                                case "CritChance":
                                    ch.CritChance = 0 if ch.CritChance - debuffAmount < 0 else ch.CritChance - debuffAmount
                            self.monsterCache.set(monster.Name, monster)
                        case "Flee":
                            summary.append(f"{monster.Name} fled the dungeon!")
                            self.monsterCache.delete(monster.Name)
                        case _:
                            pass
                    continue
            continue
        return summary


    async def _MonsterCombatMath(self, ch:Character, monster:Monster):
        evadeChance = random.randint(1,100)
        if ch.Evasion >= evadeChance:
            return f"{monster.Name} attacked {ch.Name}, but missed!"
        else:
            attackSummaryMon = f"{monster.Name} attacked {ch.Name} "
            critChance = random.randint(1,100)
            attackDmgMon = monster.AttackRating

            if monster.CritChance >= critChance:
                attackDmgMon *= 2
                attackSummaryMon += "critically "
            damageTotMon = attackDmgMon - ch.DamageReduction
            damageRealMon = damageTotMon if damageTotMon > 0 else 0
            ch.CurrentHP -= damageRealMon

            attackSummaryMon += f"for {damageRealMon} damage"

            return attackSummaryMon

