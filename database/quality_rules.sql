-- Règle 1 : Vérification des géométries invalides

INSERT INTO quality_results
(
    rule_name,
    table_name,
    status,
    nb_errors,
    details
)

SELECT
    'GEOMETRY_VALID',
    'iris',
    CASE
        WHEN COUNT(*) = 0 THEN 'OK'
        ELSE 'ERROR'
    END,
    COUNT(*),
    'Nombre de géométries invalides'
FROM iris
WHERE ST_IsValid(geometry) = false;


-- Règle 2 : Vérification des géométries vides

INSERT INTO quality_results
(
    rule_name,
    table_name,
    status,
    nb_errors,
    details
)

SELECT
    'GEOMETRY_EMPTY',
    'iris',
    CASE
        WHEN COUNT(*) = 0 THEN 'OK'
        ELSE 'ERROR'
    END,
    COUNT(*),
    'Nombre de géométries vides'
FROM iris
WHERE geometry IS NULL
   OR ST_IsEmpty(geometry);


-- Règle 3 : Vérification du système de coordonnées

INSERT INTO quality_results
(
    rule_name,
    table_name,
    status,
    nb_errors,
    details
)

SELECT
    'SRID_CHECK',
    'iris',
    CASE
        WHEN COUNT(*) = 0 THEN 'OK'
        ELSE 'ERROR'
    END,
    COUNT(*),
    'Nombre de géométries avec un SRID différent de 2154'
FROM iris
WHERE ST_SRID(geometry) <> 2154;

-- Règle 4 : Vérification des codes IRIS manquants

INSERT INTO quality_results
(
    rule_name,
    table_name,
    status,
    nb_errors,
    details
)

SELECT
    'CODE_IRIS_NULL',
    'iris',
    CASE
        WHEN COUNT(*) = 0 THEN 'OK'
        ELSE 'ERROR'
    END,
    COUNT(*),
    'Nombre de codes IRIS manquants'
FROM iris
WHERE code_iris IS NULL
   OR code_iris = '';

-- Règle 5 : Vérification des doublons de code IRIS

INSERT INTO quality_results
(
    rule_name,
    table_name,
    status,
    nb_errors,
    details
)

SELECT
    'CODE_IRIS_DUPLICATE',
    'iris',
    CASE
        WHEN COUNT(*) = 0 THEN 'OK'
        ELSE 'ERROR'
    END,
    COUNT(*),
    'Nombre de codes IRIS dupliqués'
FROM
(
    SELECT 
        code_iris
    FROM iris
    GROUP BY code_iris
    HAVING COUNT(*) > 1
) duplicates;