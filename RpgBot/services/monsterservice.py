from copy import deepcopy
from data.dataContext import Context, MonsterTable
from models.ability import Ability
from models.monster import Monster
from models.character import Character
from models.loot import Loot
from services.cacheService import MonsterCache, SimpleCache
from services.characterService import CharacterService
from services.lootService import LootService
from sqlalchemy.orm import Session
from sqlalchemy import select, update
import random
import math


class MonsterService:
    def __init__(self, db:Context, cache:SimpleCache, monsterCache:MonsterCache, systemCache:SimpleCache, characterService:CharacterService, lootService:LootService):
        self.db = db.engine
        self.cache = cache
        self.monsterCache = monsterCache
        self.systemCache = systemCache
        self.characterService = characterService
        self.lootService = lootService
        return

    #study a monster and learn its abilities
    async def StudyMonster(self, player:str, monsterName:str, floorIndex:int):
        ch = self.cache.get(player) or Character()

        chAbilities = ch.Inventory.Ability
        study = list(filter(lambda a: a.Description == "Gain the innate ability to study monsters", chAbilities))
        if len(study) == 0:
            return {
                "Error": "You don't know 'Study'"    
            }

        monster = self.monsterCache.get(floorIndex, monsterName) or Monster()
        if monster.Name == "":
            return {
                "Error": f"No monster '{monsterName}' exists in the dungeon."
            }

        monsterInfo = {
            "HP": monster.HP,
            "Attack Rating": monster.AttackRating,
            "Damage Reduction": monster.DamageReduction,
            "Evasion": monster.Evasion,
            "Crit Chance": monster.CritChance,
            "Weakness" : monster.Weakness,
            "Resistance": monster.Resistance,
            "Common Drops": monster.DropTable.Loot,
            "Rare Drops": monster.DropTable.SpecialLoot + monster.DropTable.RaidLoot
        }

        return monsterInfo


    #get mob monster from db then save it to monster cache and return it
    async def GetMobMonster(self, floor:int):
        moncache = {}
        try:
            moncache = self.monsterCache.floors[floor - 1]
        except:
            self.monsterCache.floors.append({})
            moncache = self.monsterCache.floors[floor - 1]

        monstersInDungeon = moncache.keys()
        if len(monstersInDungeon) >= 20:
            return None

        mobMonsters = deepcopy(self.systemCache.get("MobMonsters"))
        if mobMonsters is None:
            statement = select(MonsterTable).filter_by(type = "mob")

            session = Session(bind=self.db)
            try:
                monsters = session.execute(statement).scalars().all()
                session.close()
                if monsters is None: 
                    return None

                self.systemCache.set("MobMonsters", monsters)

                monstersByFloor = list(filter(lambda mt: mt.floor == floor, monsters))
                monsterObj = random.choice(monstersByFloor)

                monster = Monster().FromMonsterTable(monsterObj)
                monstersInCacheWithSameName = [m for m in self.monsterCache.floors[floor -1].keys() if m.startswith(monster.Name)]
                monsterName = f"{monster.Name} {len(monstersInCacheWithSameName) + 1}"
                monster.Name = monsterName
                self.monsterCache.set(floor - 1, monster.Name, monster)
                return monster
            except Exception as ex:
                print(ex)
                return None
        else:
            monstersByFloor = list(filter(lambda mt: mt.floor == floor, mobMonsters))
            monsterObj = random.choice(monstersByFloor)

            monster = Monster().FromMonsterTable(monsterObj)
            monstersInCacheWithSameName = [m for m in self.monsterCache.floors[floor - 1].keys() if m.startswith(monster.Name)]
            monsterName = f"{monster.Name} {len(monstersInCacheWithSameName) + 1}"
            monster.Name = monsterName
            self.monsterCache.set(floor - 1, monster.Name, monster)
            return monster

    #get raid monster from db then save it to monster cache and return it
    async def GetRaidMonster(self, floor:int):
        raidMonsters = deepcopy(self.systemCache.get("RaidMonsters"))

        if raidMonsters is None:
            statement = select(MonsterTable).filter_by(type = "raid")

            session = Session(bind=self.db)
            try:
                monsters = session.execute(statement).scalars().all()
                session.close()
                if monsters is None: 
                    return None

                self.systemCache.set("RaidMonsters", monsters)
                monstersByFloor = list(filter(lambda mt: mt.floor == floor, monsters))
                monsterObj = random.choice(monstersByFloor)

                monster = Monster().FromMonsterTable(monsterObj)
                self.monsterCache.set(floor - 1, monster.Name, monster)
                return monster
            except Exception as ex:
                print(ex)
                return None
        else:
            monstersByFloor = list(filter(lambda mt: mt.floor == floor, raidMonsters))
            monsterObj = random.choice(monstersByFloor)
            monster = Monster().FromMonsterTable(monsterObj)
            self.monsterCache.set(floor - 1, monster.Name, monster)
            return monster

    #use ability on monster
    async def UseAbility(self, player:str, target:str, abilityName:str, floorIndex:int):
        ch = self.cache.get(player) or Character()
        monster = self.monsterCache.get(floorIndex, target) or Monster()

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

        if ability.Description == "Gain the innate ability to study monsters":
            return {
                "Error": "This ability cannot be used in combat. Use the $Study command"
            }

        #deplete AP by cost
        ch.CurrentAP -= ability.Cost
        
        if player not in monster.InteractingPlayers:
            monster.InteractingPlayers.append(player)

        #apply effects
        summary = [f"{ch.Name} used {ability.Name}"]

        modstat = 0
        abilityType = ability.Type
        match abilityType:
            case "Skill":
                modstat = ch.AttackRating
            case "Spell":
                modstat = ch.SpellDamage
            case _:
                pass

        effectType = ability.Effects.Type
        modifier = 0
        match effectType:
            case "Holy":
                modifier += ((ch.Faith - 10) // 2)  + modstat
            case "Slash":
                dexMod = ((ch.Dexterity - 10) // 2)
                strMod = ((ch.Strength - 10) // 2)
                mod = strMod if strMod > dexMod else dexMod
                modifier = mod + modstat
            case "Pierce":
                dexMod = ((ch.Dexterity - 10) // 2)
                modifier = dexMod + modstat
            case "Bludgeon":
                strMod = ((ch.Strength - 10) // 2)
                modifier = strMod + modstat
            case _:
                modifier += ((ch.Intelligence - 10) // 2)  + modstat

        healAmount = 0 if ability.Effects.Heal == 0 else ability.Effects.Heal + modifier
        selfHealAmount = 0 if ability.Effects.SelfHeal == 0 else ability.Effects.SelfHeal + modifier
        inflictAmount = 0 if ability.Effects.Inflict == 0 else ability.Effects.Inflict + modifier
        selfInflictAmount = ability.Effects.SelfInflict
        boostAmount = 0 if len(ability.Effects.Boost) == 0 else math.floor(math.log10(modifier) * 5)
        debuffAmount = 0 if len(ability.Effects.Debuff) == 0 else math.floor(math.log10(modifier) * 5)

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
                    monster.DamageReduction = 1 if monster.DamageReduction - debuffAmount < 1 else monster.DamageReduction - debuffAmount
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
        if monster.Evasion >= evadeChance and inflictAmount > 0 and evadeChance < 90:
            inflictAmount = 0
            summary.append(f"{ch.Name} attacked {monster.Name} with {ability.Name}, but missed!")

        if effectType in monster.Weakness:
            inflictAmount *= 2

        if effectType in monster.Resistance:
            inflictAmount = inflictAmount // 2

        damageTaken = inflictAmount // monster.DamageReduction if inflictAmount // monster.DamageReduction > 0 else 0

        #apply heal and damage to target
        newHP = monster.HP + healAmount - damageTaken
        monster.HP =  newHP
        if healAmount > 0:
            summary.append(f"{ch.Name} healed {monster.Name} for {healAmount} HP")

        #damage target
        if inflictAmount > 0:
            summary.append(f"{ch.Name} {critStr}inflicted {damageTaken} {effectType} damage to {monster.Name}")

        #check for monster death, responds if alive
        if monster.HP <= 0:
            for playerInCombat in monster.InteractingPlayers:
                summary = await self.DropLoot(summary, playerInCombat, monster)
            self.monsterCache.delete(floorIndex, monster.Name)
        else:
            summary = await self.MonsterAIAction(summary, ch, player, monster, floorIndex)
        
        if ch.CurrentHP <= 0:
            summary = await self._CharDeath(summary, ch, player, monster, floorIndex)
        else:
            self.cache.set(player, ch)

        return {
            "Summary": summary      
        }

    #do monster combat
    async def MonsterCombat(self, player:str, monsterName:str, floorIndex:int):
        ch = self.cache.get(player) or Character()
        monster = self.monsterCache.get(floorIndex, monsterName) or Monster()

        if player not in monster.InteractingPlayers:
            monster.InteractingPlayers.append(player)

        summary = []
        #character attacks monster
        evadeChance = random.randint(1,100)
        if monster.Evasion >= evadeChance and evadeChance < 90:
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
            
            match damageType:
                case "Holy":
                    attackDmg += ((ch.Faith - 10) // 2)
                case "Arcane" | "Fire":
                    attackDmg += ((ch.Intelligence - 10) // 2)
                case "Slash":
                    dexMod = ((ch.Dexterity - 10) // 2)
                    strMod = ((ch.Strength - 10) // 2)
                    mod = strMod if strMod > dexMod else dexMod
                    attackDmg += mod
                case "Pierce":
                    dexMod = ((ch.Dexterity - 10) // 2)
                    attackDmg += dexMod
                case "Bludgeon" | "Thunder":
                    strMod = ((ch.Strength - 10) // 2)
                    attackDmg += strMod
                case _:
                    pass

            if damageType in monster.Weakness:
                attackDmg *= 2

            if damageType in monster.Resistance:
                attackDmg = attackDmg // 2

            if ch.CritChance >= critChance:
                attackDmg *= 2
                attackSummary += "critically "
            damageTot = attackDmg // monster.DamageReduction
            damageReal = damageTot if damageTot > 0 else 0
            monster.HP -= damageReal

            damageType = ""
            weapon = list(filter(lambda i: i.Type == "Hand", ch.Inventory.Equipped))
            if len(weapon) == 0:
                damageType = "Unarmed"
            else:
                damageType = weapon[0].Effects.Type

            attackSummary += f"for {damageReal} {damageType} damage"
            
            if weapon[0].Effects.Heal > 0:
                healAmount = weapon[0].Effects.Heal + (ch.AttackRating // 2)
                ch.CurrentHP += healAmount if ch.CurrentHP + healAmount <= ch.MaxHP else ch.MaxHP
                attackSummary += f" and healed {ch.Name} for {healAmount} HP"

            summary.append(attackSummary)

        #check for monster death, responds if alive
        if monster.HP <= 0:
            for playerInCombat in monster.InteractingPlayers:
                summary = await self.DropLoot(summary, playerInCombat, monster)
            self.monsterCache.delete(floorIndex, monster.Name)
        else:
            summary = await self.MonsterAIAction(summary, ch, player, monster, floorIndex)

        return {
            "Summary": summary      
        }

    #use item on monster
    async def UseItem(self, player:str, monster:Monster, itemName:str, floorIndex:int):
        ch = self.cache.get(player) or Character()
        
        itemToUse = list(filter(lambda i: i.Name.startswith(itemName), ch.Inventory.Stored))
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

        summary = []
        for e in useEffects:
            tokens = e.split()
            effect = tokens[0]

            match effect:
                case "Heal":
                    amount = int(tokens[1])
                    newHP = monster.HP + amount
                    monster.HP = newHP if newHP <= monster.MaxHP else monster.MaxHP
                    summary.append(f"{ch.Name} healed {monster.Name} for {amount} HP")
                case "Inflict":
                    amount = int(tokens[1])
                    dmgType = tokens[2]

                    if dmgType in monster.Weakness:
                        amount *= 2
                    if dmgType in monster.Resistance:
                        amount = amount // 2

                    newHP = monster.HP - amount
                    monster.HP = newHP
                    summary.append(f"{ch.Name} inflicted {amount} {dmgType} damage to {monster.Name}")
                case "Buff":
                    stat = tokens[1]
                    amount = int(tokens[2])

                    summary.append(f"{ch.Name} boosted {monster.Name}'s {stat} by {amount}")
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

                    summary.append(f"{ch.Name} lowered {monster.Name}'s {stat} by {amount}")
                    match stat:
                        case "AttackRating" | "SpellDamage":
                            monster.AttackRating = 0 if monster.AttackRating - amount < 0 else monster.AttackRating - amount
                        case "DamageReduction":
                            monster.DamageReduction = 1 if monster.DamageReduction - amount < 1 else monster.DamageReduction - amount
                        case "Evasion":
                            monster.Evasion = 0 if monster.Evasion - amount < 0 else monster.Evasion - amount
                        case "CritChance":
                            monster.CritChance = 0 if monster.CritChance - amount < 0 else monster.CritChance - amount
                case _:
                    pass
            continue

        #check for monster death, responds if alive
        if monster.HP <= 0:
            for playerInCombat in monster.InteractingPlayers:
                summary = await self.DropLoot(summary, playerInCombat, monster)
            self.monsterCache.delete(floorIndex, monster.Name)
        else:
            summary = await self.MonsterAIAction(summary, ch, player, monster)

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
            item = None
            if len(monsterLoot.RaidLoot) > 0:
                raidLootDrop = random.choice(monsterLoot.RaidLoot)
                raiditem = await self.lootService.GenerateLootByName(raidLootDrop)
                summary.append(f"{ch.Name} also received a legendary {raiditem.Name}!")
                ch.Inventory.Stored.append(raiditem)

        if ch.MaxInventory > len(ch.Inventory.Stored):
            rareDropChance = random.randint(1,100) + ch.Luck
            if len(monsterLoot.SpecialLoot) == 0 or rareDropChance <= 95:
                lootdrop =  random.choice(monsterLoot.Loot)
                item = await self.lootService.GenerateLootByName(lootdrop)
                summary.append(f"{ch.Name} also received {item.Name}!")
                ch.Inventory.Stored.append(item)
            else:
                specialLootDrop = random.choice(monsterLoot.SpecialLoot)
                item = await self.lootService.GenerateLootByName(specialLootDrop)
                summary.append(f"{ch.Name} also received a rare {item.Name}!")
                ch.Inventory.Stored.append(item)
                        
            ch.Inventory.checkInventoryForDuplicates()
            
        self.cache.set(player, ch)
        await self.characterService.SaveCharacter(player, ch)
        return summary

    async def MonsterAIAction(self, summary:list, ch:Character, pname:str, monster:Monster, floorIndex:int):
        aiActions = monster.AI.Actions
        monsterMaxHP = monster.MaxHP
        monsterHP = monster.HP

        for aiAction in aiActions:
            #check if % of HP is at or below threshold for action
            if ((monsterHP/monsterMaxHP) <= aiAction.HPThresholdUpper / 100) and ((monsterHP/monsterMaxHP) >= aiAction.HPThresholdLower / 100):
                actions = aiAction.Action
                for action in actions:
                    actionTokens = action.split(" ")
                    command = actionTokens[0]

                    match command:
                        case "Wait":
                            summary.append(f"{monster.Name} is waiting...")
                        case "Attack":
                            target = actionTokens[1]
                            dmgType = actionTokens[2]
                            match target:
                                case "All":
                                    for player in monster.InteractingPlayers:
                                        targetCh = self.cache.get(player) or Character()
                                        summary.append(await self._MonsterCombatMath(targetCh, monster, dmgType))
                                        if targetCh.CurrentHP <= 0:
                                            summary = await self._CharDeath(summary, targetCh, player, monster, floorIndex)
                                        else:
                                            self.cache.set(player, targetCh)
                                        continue
                                case "Char":
                                    summary.append(await self._MonsterCombatMath(ch, monster, dmgType))
                                    if ch.CurrentHP <= 0:
                                        summary = await self._CharDeath(summary, ch, pname, monster, floorIndex)
                                    else:
                                        self.cache.set(pname, ch)
                                    continue

                            self.monsterCache.set(floorIndex, monster.Name, monster)
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
                                case "AttackRating" | "SpellDamage":
                                    monster.AttackRating += boostAmount
                                case "DamageReduction":
                                    monster.DamageReduction += boostAmount
                                case "Evasion":
                                    monster.Evasion += boostAmount
                                case "CritChance":
                                    monster.CritChance += boostAmount
                            self.monsterCache.set(floorIndex, monster.Name, monster)
                        case "Debuff":
                            stat = actionTokens[1]
                            debuffAmount = int(actionTokens[2])
                            summary.append(f"{monster.Name} lowered {ch.Name}'s {stat} by {debuffAmount}")
                            match stat:
                                case "AttackRating":
                                    ch.Buffs.AttackRating -= debuffAmount
                                case "DamageReduction":
                                    ch.Buffs.DamageReduction -= debuffAmount
                                case "SpellDamage":
                                    ch.Buffs.SpellDamage -= debuffAmount
                                case "Evasion":
                                    ch.Buffs.Evasion -= debuffAmount
                                case "CritChance":
                                    ch.Buffs.CritChance -= debuffAmount
                            ch.deriveStats()
                            self.cache.set(pname, ch)
                        case "Flee":
                            summary.append(f"{monster.Name} fled the dungeon!")
                            self.monsterCache.delete(floorIndex, monster.Name)
                        case _:
                            pass
                    continue
            continue
        return summary

    async def FleeCombat(self, player:str, monster:Monster):
        ch = self.cache.get(player) 
        if player not in monster.InteractingPlayers:
            return {
                "Error": f"{ch.Name} is not currently in combat with {monster.Name}"
            }

        monster.InteractingPlayers.remove(player)
        return {
            "Summary": f"{ch.Name} fled from combat with {monster.Name}"     
        }

    async def _MonsterCombatMath(self, ch:Character, monster:Monster, dmgType:str):
        evadeChance = random.randint(1,100)
        if ch.Evasion >= evadeChance and evadeChance < 90:
            return f"{monster.Name} attacked {ch.Name}, but missed!"
        else:
            attackSummaryMon = f"{monster.Name} attacked {ch.Name} "
            critChance = random.randint(1,100)
            attackDmgMon = monster.AttackRating

            if monster.CritChance >= critChance:
                attackDmgMon *= 2
                attackSummaryMon += "critically "
            damageTotMon = attackDmgMon // ch.DamageReduction
            damageRealMon = damageTotMon if damageTotMon > 0 else 0
            ch.CurrentHP -= damageRealMon

            attackSummaryMon += f"for {damageRealMon} {dmgType} damage"

            return attackSummaryMon
    
    async def _CharDeath(self, summary:list, ch:Character, player:str, monster:Monster, floorIndex:int):
        summary.append(f"{ch.Name} has fallen. Their body has been claimed by the dungeon, never to be seen again.")
        lootables = self.systemCache.get("Lootables") or []
        
        #Add equipped items to lootables so they can be dropped on death and reclaimed later
        for item in ch.Inventory.Equipped:
            lootables.append(item)

        #deduplicate lootables
        for item in lootables:
            duplicates = list(filter(lambda i: i.Name == item.Name, lootables))
            #if more than one item with the same name...
            if len(duplicates) > 1:
                #loop through inventory and rename the item
                dupName = item.Name
                dupCount = 0
                for dup in lootables:
                    if dup.Name == dupName:
                        dup.Name += f" ({dupCount})"
                        dupCount += 1
        
        lootables.sort(key=lambda i: i.Name)
        self.systemCache.set("Lootables", lootables)

        self.cache.delete(player)
        monster.InteractingPlayers.remove(player)
        self.monsterCache.set(floorIndex, monster.Name, monster)
        await self.characterService.KillCharacter(player)
        return summary