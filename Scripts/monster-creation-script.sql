
-- Config: Set base monster values
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

-- Config: Set drop values
set @DropXP = 0;
set @DropGold = 0;
set @DropLoot = JSON_ARRAY('', '');
set @DropRaidLoot = JSON_ARRAY('', '');
set @DropSpecialLoot = JSON_ARRAY('', '');

-- Do not config: Create temporary table to hold monster AI actions
DROP PROCEDURE IF EXISTS create_temp_table;
DELIMITER //
CREATE PROCEDURE create_temp_table()
    BEGIN
        DECLARE EXIT HANDLER FOR SQLEXCEPTION
        BEGIN
            ROLLBACK;
            RESIGNAL;
        END;
        START TRANSACTION;
            DROP TEMPORARY TABLE IF EXISTS monsterAIActions;
            CREATE TEMPORARY TABLE monsterAIActions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                actionList JSON,
                hpThresholdLower INT,
                hpThresholdUpper INT
            );

            -- Config: Insert AI actions into this table as part of configuration
            INSERT INTO monsterAIActions (actionList, hpThresholdLower, hpThresholdUpper)
            VALUES (JSON_ARRAY(''), 0, 0);

            -- Aggregate all data from monsterAIActions into one JSON array of JSON objects, one object for each action/record
            SET @MonsterAIActions = (
                SELECT JSON_ARRAYAGG(JSON_OBJECT(
                    'Action', JSON_EXTRACT(actionList, '$'),
                    'HPThresholdLower', hpThresholdLower,
                    'HPThresholdUpper', hpThresholdUpper
                ))
                FROM monsterAIActions
                );

            -- Create JSON object containing array of all objects/actions/records from @MonsterAIActions
            SET @MonsterAI = JSON_OBJECT('Actions', COALESCE(JSON_EXTRACT(@MonsterAIActions, '$'), JSON_ARRAY()));
            DROP TEMPORARY TABLE IF EXISTS monsterAIActions;
        COMMIT;
    END //
DELIMITER ;

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

CALL create_temp_table();
CALL create_monster();
DROP PROCEDURE IF EXISTS create_temp_table;
DROP PROCEDURE IF EXISTS create_monster;

