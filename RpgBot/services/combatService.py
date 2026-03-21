from calendar import c
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

        if await self._checkForDeath(player, ch, target, targetCh): 
            summary.append(f"{ch.Name} has fallen and dropped their Gold")
            
            
        if await self._checkForDeath(target, targetCh, player, ch):
            summary.append(f"{targetCh.Name} has fallen and dropped their Gold")
        
        return {
            "Summary": summary    
        }

    async def UseAbilityPvP(self, player:str, target:str, abilityName):
        ch = self.cache.get(player) or Character()
        targetCh = self.cache.get(target) or Character()

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
            summary.append(f"{ch.Name} boosted {targetCh.Name}'s {stat} by {boostAmount}")
            match stat:
                case "AttackRating":
                    targetCh.AttackRating += boostAmount
                case "DamageReduction":
                    targetCh.DamageReduction += boostAmount
                case "SpellDamage":
                    targetCh.SpellDamage += boostAmount
                case "Evasion":
                    targetCh.Evasion += boostAmount
                case "CritChance":
                    targetCh.CritChance += boostAmount
        
        #debuff stats
        for stat in ability.Effects.Debuff:
            summary.append(f"{ch.Name} lowered {targetCh.Name}'s {stat} by {debuffAmount}")
            match stat:
                case "AttackRating":
                    targetCh.AttackRating -= debuffAmount
                case "DamageReduction":
                    targetCh.DamageReduction -= debuffAmount
                case "SpellDamage":
                    targetCh.SpellDamage -= debuffAmount
                case "Evasion":
                    targetCh.Evasion -= debuffAmount
                case "CritChance":
                    targetCh.CritChance -= debuffAmount
        
        #self heal
        selfNewHP = ch.CurrentHP + selfHealAmount - selfInflictAmount
        ch.CurrentHP = selfNewHP if selfNewHP <= ch.MaxHP else ch.MaxHP
        if selfHealAmount > 0:
            summary.append(f"{ch.Name} healed for {selfHealAmount} HP")
        
        #self inflict
        if selfInflictAmount > 0:
            summary.append(f"{ch.Name} hurt themself for {selfInflictAmount} {effectType} damage")

        #heal target
        critChance = random.randint(1,100)
        critStr = ""
        if ch.CritChance >= critChance:
            inflictAmount *= 2
            critStr = "critically "
        damageTaken = inflictAmount - targetCh.DamageReduction if inflictAmount - targetCh.DamageReduction > 0 else 0

        newHP = targetCh.CurrentHP + healAmount - damageTaken
        targetCh.CurrentHP =  newHP if newHP <= targetCh.MaxHP else targetCh.MaxHP
        if healAmount > 0:
            summary.append(f"{ch.Name} healed {targetCh.Name} for {healAmount} HP")

        #damage target
        if inflictAmount > 0:
            summary.append(f"{ch.Name} {critStr}inflicted {damageTaken} {effectType} damage to {targetCh.Name}")

        #target retaliates
        if inflictAmount > 0 or len(ability.Effects.Debuff) > 0:
            summary.append(self._combatMath(targetCh, ch))
        #save character states
        self.cache.set(player, ch)
        if target != player:
            self.cache.set(target, targetCh)

        if await self._checkForDeath(player, ch, target, targetCh): 
            summary.append(f"{ch.Name} has fallen and dropped their Gold")
            
        if target != "self":
            if await self._checkForDeath(target, targetCh, player, ch):
                summary.append(f"{targetCh.Name} has fallen and dropped their Gold")
        
        return {
            "Summary": summary    
        }

    def _combatMath(self, ch:Character, target:Character):
        evadeChance = random.randint(1,100)
        if target.Evasion >= evadeChance:
            return f"{ch.Name} attacked {target.Name}, but missed!"
        else:
            attackSummary = f"{ch.Name} attacked {target.Name} "
            critChance = random.randint(1,100)
            attackDmg = ch.AttackRating
            if ch.CritChance >= critChance:
                attackDmg *= 2
                attackSummary += "critically "
            damageTot = attackDmg - target.DamageReduction
            damageReal = damageTot if damageTot > 0 else 0
            target.CurrentHP -= damageReal

            damageType = ""
            weapon = list(filter(lambda i: i.Type == "Hand", ch.Inventory.Equipped))
            if len(weapon) == 0:
                damageType = "Unarmed"
            else:
                damageType = weapon[0].Effects.Type

            attackSummary += f"for {damageReal} {damageType} damage"
            
            return attackSummary
        return

    async def _checkForDeath(self, player:str, ch:Character, target:str, targetCh:Character):
        charIsDead = False
        if ch.CurrentHP <= 0:
            charIsDead = True
            targetCh.Inventory.Gold += ch.Inventory.Gold
            ch.Inventory.Gold = 0
            await self.characterService.SaveCharacter(player, ch)
            self.cache.delete(player)

            await self.characterService.SaveCharacter(target, targetCh)
            self.cache.set(target, targetCh)
        return charIsDead

