-- =====================================================
-- GeoAudit - Generic Rules
-- =====================================================

-- -----------------------------------------------------
-- G001 : Validité des géométries
-- -----------------------------------------------------

INSERT INTO quality_results
(rule_name, table_name, status, nb_errors, details)

SELECT
'G001_GEOMETRY_VALID',
'{{TABLE_NAME}}',
CASE
    WHEN COUNT(*) = 0 THEN 'OK'
    ELSE 'ERROR'
END,
COUNT(*),
'Invalid geometries'

FROM {{TABLE_NAME}}

WHERE NOT ST_IsValid(geometry);



-- -----------------------------------------------------
-- G002 : Géométries vides
-- -----------------------------------------------------

INSERT INTO quality_results
(rule_name, table_name, status, nb_errors, details)

SELECT
'G002_GEOMETRY_EMPTY',
'{{TABLE_NAME}}',
CASE
    WHEN COUNT(*) = 0 THEN 'OK'
    ELSE 'ERROR'
END,
COUNT(*),
'Empty geometries'

FROM {{TABLE_NAME}}

WHERE geometry IS NULL
OR ST_IsEmpty(geometry);



-- -----------------------------------------------------
-- G003 : SRID attendu = 2154
-- -----------------------------------------------------

INSERT INTO quality_results
(rule_name, table_name, status, nb_errors, details)

SELECT
'G003_SRID_CHECK',
'{{TABLE_NAME}}',
CASE
    WHEN COUNT(*) = 0 THEN 'OK'
    ELSE 'ERROR'
END,
COUNT(*),
'SRID different from EPSG:2154'

FROM {{TABLE_NAME}}

WHERE ST_SRID(geometry) <> 2154;