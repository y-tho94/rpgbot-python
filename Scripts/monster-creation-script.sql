

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

set @MonsterAI = JSON_OBJECT
                    (
                    'aggressiveness', 0,
                    'intelligence' , 0,
                    'preferredAttack', 'melee',
                    'fleeThreshold', 0
                    );

set @DropTable = JSON_OBJECT(
                 'commonDrops', JSON_ARRAY
                                (
                                    JSON_OBJECT('item', 1 , 'dropRate', 0.5, 'quantity', 1),
                                    JSON_OBJECT()
                                ),
                 'rareDrops', JSON_ARRAY
                                (
                                    JSON_OBJECT('itemID', 2, 'dropRate', 0.1, 'quantity', 1),
                                    JSON_OBJECT('itemID', 3, 'dropRate', 0.1, 'quantity', 1)
                                )

                 );


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
VALUES              (
                    @MonsterFloor,
                    @MonsterType,
                    @MonsterName,
                    @MonsterWeakness,
                    @MonsterResistance,
                    @MonsterBaseVariance,
                    @MonsterHP,
                    @MonsterAttackRating,
                    @MonsterDamageReduction,
                    @MonsterEvasion,
                    @MonsterCritChance,
                    @MonsterAI,
                    @DropTable
                    );
COMMIT;