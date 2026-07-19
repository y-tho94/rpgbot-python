-- Config 1/2: set base ability values
SET @AbilityName = 'Bullseye';
SET @AbilityDescription = '';
SET @AbilityType = 'test';
SET @AbilityCost = 0;
SET @AbilityBaseVariance = 0;

-- Config 2/2: Set values to build `baseProperties` JSON object
SET @Heal = 0;
SET @Type = 'test';
SET @Boost = JSON_ARRAY('', '');
SET @Debuff = JSON_ARRAY('', '');
SET @Inflict = 0;
SET @SelfHeal = 0;
SET @SelfInflict = 0;

-- End config: build baseProperties JSON object
SET @BaseProperties = JSON_OBJECT(
        'Heal', @Heal,
        'Type', @Type,
        'Boost', JSON_EXTRACT(@Boost, '$'),
        'Debuff', JSON_EXTRACT(@Debuff, '$'),
        'Inflict', @Inflict,
        'SelfHeal', @SelfHeal,
        'SelfInflict', @SelfInflict);

DROP PROCEDURE IF EXISTS create_ability;
DELIMITER //
CREATE PROCEDURE create_ability()
    BEGIN
        DECLARE AbilityName VARCHAR(32);
        DECLARE AbilityDescription VARCHAR(1000);
        DECLARE AbilityType VARCHAR(32);
        DECLARE AbilityCost INT;
        DECLARE AbilityBaseVariance INT;
        DECLARE Heal INT;
        DECLARE Type VARCHAR(10);
        DECLARE Boost JSON;
        DECLARE Debuff JSON;
        DECLARE Inflict INT;
        DECLARE SelfHeal INT;
        DECLARE SelfInflict INT;
        DECLARE BaseProperties JSON;
        DECLARE EXIT HANDLER FOR SQLEXCEPTION
        BEGIN
            ROLLBACK;
            RESIGNAL;
        END;

        SET AbilityName = @AbilityName;
        SET AbilityDescription = @AbilityDescription;
        SET AbilityType = @AbilityType;
        SET AbilityCost = @AbilityCost;
        SET AbilityBaseVariance = @AbilityBaseVariance;
        SET Heal = @Heal;
        SET Type = @Type;
        SET Boost = @Boost;
        SET Debuff = @Debuff;
        SET Inflict = @Inflict;
        SET SelfHeal = @SelfHeal;
        SET SelfInflict = @SelfInflict;
        SET BaseProperties = @BaseProperties;

        START TRANSACTION;
            INSERT INTO ability(name, description, type, cost, baseVariance, baseEffects)
            VALUES (AbilityName, AbilityDescription, AbilityType, AbilityCost, AbilityBaseVariance, BaseProperties);
        COMMIT;
    END//
DELIMITER ;

CALL create_ability();
DROP PROCEDURE IF EXISTS create_ability;