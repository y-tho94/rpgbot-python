
-- Set base monster values
set @MonsterName = '';
set @MonsterType = '';
set @MonsterFloor = 0;
set @MonsterBaseVariance = 0;
set @MonsterHP = 0;
set @MonsterAttackRating = 0;
set @MonsterDamageReduction = 0;
set @MonsterEvasion = 0;
set @MonsterCritChance = 0;
set @MonsterWeakness = JSON_ARRAY('', '');
set @MonsterResistance = JSON_ARRAY('', '');

-- Set drop values
set @DropXP = 0;
set @DropGold = 0;
set @DropLoot = JSON_ARRAY('', '');
set @DropRaidLoot = JSON_ARRAY('', '');
set @DropSpecialLoot = JSON_ARRAY('', '');

-- Set actions for the MonsterAI column (needs work) might be better to remove this section?
set @AIActionsList = JSON_ARRAY('', '');
set @AIHPThresholdLower = 10;
set @AIHPThresholdUpper = 20;

-- Builds MonsterAI column from variables defined above; might be easier to do this manually? \
set @MonsterAI = JSON_OBJECT(
    'Actions', JSON_ARRAY(
        JSON_OBJECT(
            'Action', JSON_EXTRACT(@AIActionsList, '$'),
            'HPThresholdLower', @AIHPThresholdLower,
            'HPThresholdUpper', @AIHPThresholdUpper
        )
    )
);

-- Builds loot drop column from variables defined above
set @DropTable = JSON_OBJECT(
    'XP', @DropXP,
    'Gold', @DropGold,
    'Loot', JSON_EXTRACT(@DropLoot, '$'),
    'RaidLoot', JSON_EXTRACT(@DropRaidLoot, '$'),
    'SpecialLoot', JSON_EXTRACT(@DropSpecialLoot, '$')
);

-- Check for procedure and data integrity before inserting, rollback and yell on failure
DROP PROCEDURE IF EXISTS create_monster;
DELIMITER //
CREATE PROCEDURE create_monster()
    BEGIN
        DECLARE MonsterName VARCHAR(32);
        DECLARE MonsterType VARCHAR(10);
        DECLARE MonsterFloor INT;
        DECLARE MonsterBaseVariance INT;
        DECLARE MonsterHP INT;
        DECLARE MonsterAttackRating INT;
        DECLARE MonsterDamageReduction INT;
        DECLARE MonsterEvasion INT;
        DECLARE MonsterCritChance INT;
        DECLARE MonsterWeakness JSON;
        DECLARE MonsterResistance JSON;

        DECLARE DropXP INT;
        DECLARE DropGold INT;
        DECLARE DropLoot JSON;
        DECLARE DropRaidLoot JSON;
        DECLARE DropSpecialLoot JSON;

        DECLARE AIActionsList JSON;
        DECLARE AIHPThresholdLower INT;
        DECLARE AIHPThresholdUpper INT;

        DECLARE MonsterAI JSON;

        DECLARE DropTable JSON;

        DECLARE EXIT HANDLER FOR SQLEXCEPTION
        BEGIN
            ROLLBACK;
            RESIGNAL;
        END;

        SET MonsterName = @MonsterName;
        SET MonsterType = @MonsterType;
        SET MonsterFloor = @MonsterFloor;
        SET MonsterBaseVariance = @MonsterBaseVariance;
        SET MonsterHP = @MonsterHP;
        SET MonsterAttackRating = @MonsterAttackRating;
        SET MonsterDamageReduction = @MonsterDamageReduction;
        SET MonsterEvasion = @MonsterEvasion;
        SET MonsterCritChance = @MonsterCritChance;
        SET MonsterWeakness = @MonsterWeakness;
        SET MonsterResistance = @MonsterResistance;

        SET DropXP = @DropXP;
        SET DropGold = @DropGold;
        SET DropLoot = @DropLoot;
        SET DropRaidLoot = @DropRaidLoot;
        SET DropSpecialLoot = @DropSpecialLoot;

        SET AIActionsList = @AIActionsList;
        SET AIHPThresholdLower = @AIHPThresholdLower;
        SET AIHPThresholdUpper = @AIHPThresholdUpper;

        SET MonsterAI = @MonsterAI;

        SET DropTable = @DropTable;


        START TRANSACTION;
            INSERT INTO monster (
                 floor,
                 type,
                 name,
                 weakness,
                 resistance,
                 baseVariance,
                 hp,
                 attackRating,
                 damageReduction,
                 evasion,
                 critChance,
                 ai,
                 dropTable
                )
            VALUES (
                MonsterFloor,
                MonsterType,
                MonsterName,
                MonsterWeakness,
                MonsterResistance,
                MonsterBaseVariance,
                MonsterHP,
                MonsterAttackRating,
                MonsterDamageReduction,
                MonsterEvasion,
                MonsterCritChance,
                MonsterAI,
                DropTable
                );
        COMMIT;
    END//
DELIMITER ;

CALL create_monster();
DROP PROCEDURE IF EXISTS create_monster;

