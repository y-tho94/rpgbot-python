from models.ability import Ability
from models.character import Character
from services.cacheService import SimpleCache
import random
from services.characterService import CharacterService

class CombatService():
    def __init__(self, cache:SimpleCache, characterService:CharacterService):
        self.cache = cache
        self.characterService = characterService
        return

    async def DoPvPCombat(self, player:str, target:str):
        ch = self.cache.get(player)
        targetCh = self.cache.get(target)
        
        summary = []

        #Player action
        summary.append(self._combatMath(ch, targetCh))

        #Defender reaction
        summary.append(self._combatMath(targetCh, ch))

        self.cache.set(player, ch)
        self.cache.set(target, targetCh)

        if await self._checkForDeath(player, ch, targetCh): 
            summary.append(f"{ch.Name} has fallen and dropped their Gold")
            
            
        if await self._checkForDeath(target, targetCh, ch):
            summary.append(f"{targetCh.Name} has fallen and dropped their Gold")
        
        return {
            "Summary": summary    
        }

    async def UseAbilityPvP(self, player:str, target:str, abilityName):
        ch = self.cache.get(player)
        targetCh = self.cache.get(target)

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
        boostAmount = 0 if len(ability.Effects.Boost) == 0 else modifier
        debuffAmount = 0 if len(ability.Effects.Debuff) == 0 else modifier

        #boost stats
        for stat in ability.Effects.Boost:
            summary.append(f"{ch.Name} boosted {targetCh.Name}'s {stat} by {boostAmount}")
            match stat:
                case "AttackRating":
                    targetCh.Buffs.AttackRating += boostAmount
                case "DamageReduction":
                    targetCh.Buffs.DamageReduction += boostAmount
                case "SpellDamage":
                    targetCh.Buffs.SpellDamage += boostAmount
                case "Evasion":
                    targetCh.Buffs.Evasion += boostAmount
                case "CritChance":
                    targetCh.Buffs.CritChance += boostAmount
            targetCh.deriveStats()
        #debuff stats
        for stat in ability.Effects.Debuff:
            summary.append(f"{ch.Name} lowered {targetCh.Name}'s {stat} by {debuffAmount}")
            match stat:
                case "AttackRating":
                    targetCh.Buffs.AttackRating -= debuffAmount
                case "DamageReduction":
                    targetCh.Buffs.DamageReduction -= debuffAmount
                case "SpellDamage":
                    targetCh.Buffs.SpellDamage -= debuffAmount
                case "Evasion":
                    targetCh.Buffs.Evasion -= debuffAmount
                case "CritChance":
                    targetCh.Buffs.CritChance -= debuffAmount
            targetCh.deriveStats()
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
        if targetCh.Evasion >= evadeChance and inflictAmount > 0 and evadeChance < 90:
            inflictAmount = 0
            summary.append(f"{ch.Name} attacked {targetCh.Name} with {ability.Name}, but missed!")

        damageTaken = inflictAmount - targetCh.DamageReduction if inflictAmount - targetCh.DamageReduction > 0 else 0

        #apply heal and damage to target
        newHP = targetCh.CurrentHP + healAmount - damageTaken
        targetCh.CurrentHP =  newHP if newHP <= targetCh.MaxHP else targetCh.MaxHP
        if healAmount > 0:
            summary.append(f"{ch.Name} healed {targetCh.Name} for {healAmount} HP")

        #damage target
        if inflictAmount > 0:
            summary.append(f"{ch.Name} {critStr}inflicted {damageTaken} {effectType} damage to {targetCh.Name}")

        #target retaliates
        if (targetCh != ch) and (inflictAmount > 0 or len(ability.Effects.Debuff) > 0):
            summary.append(self._combatMath(targetCh, ch))
        #save character states
        self.cache.set(player, ch)
        if target != player:
            self.cache.set(target, targetCh)

        if await self._checkForDeath(player, ch, targetCh): 
            summary.append(f"{ch.Name} has fallen and dropped their Gold")
            
        if target != "self":
            if await self._checkForDeath(target, targetCh, ch):
                summary.append(f"{targetCh.Name} has fallen and dropped their Gold")
        
        return {
            "Summary": summary    
        }

    def _combatMath(self, ch:Character, target:Character):
        evadeChance = random.randint(1,100)
        if target.Evasion >= evadeChance and evadeChance < 90:
            return f"{ch.Name} attacked {target.Name}, but missed!"
        else:
            attackSummary = f"{ch.Name} attacked {target.Name} "
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
            
            critChance = random.randint(1,100)
            if ch.CritChance >= critChance:
                attackDmg *= 2
                attackSummary += "critically "
            
            damageTot = attackDmg - target.DamageReduction
            damageReal = damageTot if damageTot > 0 else 0
            target.CurrentHP -= damageReal
            attackSummary += f"for {damageReal} {damageType} damage"

            if weapon[0].Effects.Heal > 0:
                healAmount = weapon[0].Effects.Heal + (ch.AttackRating // 2)
                ch.CurrentHP += healAmount if ch.CurrentHP + healAmount <= ch.MaxHP else ch.MaxHP
                attackSummary += f" and healed {ch.Name} for {healAmount} HP"

            return attackSummary

    async def _checkForDeath(self, player:str, ch:Character, targetCh:Character):
        charIsDead = False
        if ch.CurrentHP <= 0:
            charIsDead = True
            targetCh.Inventory.Gold += ch.Inventory.Gold
            ch.Inventory.Gold = 0
            await self.characterService.SaveCharacter(player, ch)
            self.cache.delete(player)
        return charIsDead

