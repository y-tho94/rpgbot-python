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

        if ch.CurrentHP < 0: 
            targetCh.Inventory.Gold += ch.Inventory.Gold
            self.cache.set(target, targetCh)
            summary.append(f"{ch.Name} has fallen and dropped {ch.Inventory.Gold} Gold")
            await self.characterService.KillCharacter(player)
        if targetCh.CurrentHP < 0:
            ch.Inventory.Gold += targetCh.Inventory.Gold
            self.cache.set(player, ch)
            summary.append(f"{targetCh.Name} has fallen and dropped {targetCh.Inventory.Gold} Gold")
            await self.characterService.KillCharacter(target)

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
