-- =====================================================
-- GeoAudit - Generic Quality Rules V2.1
-- Generic rules for all PostGIS geometry types
-- POINT / MULTIPOINT / LINESTRING /
-- MULTILINESTRING / POLYGON / MULTIPOLYGON
-- =====================================================


-- =====================================================
-- G001 : Géométries invalides
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G001',
'GEOMETRY_VALID',
'{{TABLE_NAME}}',
CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERROR' END,
COUNT(*),
'Nombre de géométries invalides'

FROM {{TABLE_NAME}}

WHERE geometry IS NOT NULL
AND NOT ST_IsValid(geometry);



-- =====================================================
-- G002 : Géométries vides
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G002',
'EMPTY_GEOMETRY',
'{{TABLE_NAME}}',
CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERROR' END,
COUNT(*),
'Nombre de géométries vides'

FROM {{TABLE_NAME}}

WHERE geometry IS NULL
OR ST_IsEmpty(geometry);



-- =====================================================
-- G003 : Contrôle SRID
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G003',
'SRID_CHECK',
'{{TABLE_NAME}}',
CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ERROR' END,
COUNT(*),
'Système de coordonnées différent de EPSG:2154'

FROM {{TABLE_NAME}}

WHERE geometry IS NOT NULL
AND ST_SRID(geometry) <> 2154;



-- =====================================================
-- G004 : Type géométrique
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G004',
'GEOMETRY_TYPE',
'{{TABLE_NAME}}',
'INFO',
COUNT(*),
STRING_AGG(DISTINCT GeometryType(geometry), ', ')

FROM {{TABLE_NAME}};



-- =====================================================
-- G005 : Nombre total d'entités
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G005',
'ENTITY_COUNT',
'{{TABLE_NAME}}',
'INFO',
COUNT(*),
'Nombre total d entités'

FROM {{TABLE_NAME}};



-- =====================================================
-- G006 : Géométries NULL
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G006',
'NULL_GEOMETRY',
'{{TABLE_NAME}}',
CASE WHEN COUNT(*)=0 THEN 'OK' ELSE 'ERROR' END,
COUNT(*),
'Entités sans géométrie'

FROM {{TABLE_NAME}}

WHERE geometry IS NULL;



-- =====================================================
-- G007 : Doublons géométriques
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G007',
'DUPLICATE_GEOMETRY',
'{{TABLE_NAME}}',
CASE WHEN COUNT(*)=0 THEN 'OK' ELSE 'ERROR' END,
COUNT(*),
'Géométries identiques détectées'

FROM
(
SELECT geometry
FROM {{TABLE_NAME}}
GROUP BY geometry
HAVING COUNT(*) > 1
) duplicates;



-- =====================================================
-- G008 : Nombre de colonnes
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G008',
'COLUMN_COUNT',
'{{TABLE_NAME}}',
'INFO',
COUNT(*),
'Nombre de colonnes attributaires'

FROM information_schema.columns

WHERE table_name='{{TABLE_NAME}}';



-- =====================================================
-- G009 : Valeurs NULL attributaires
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G009',
'NULL_ATTRIBUTES',
'{{TABLE_NAME}}',
'INFO',
COUNT(*),
'Nombre de lignes avec valeurs NULL'

FROM {{TABLE_NAME}};



-- =====================================================
-- G010 : Nombre de sommets
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G010',
'VERTEX_COUNT',
'{{TABLE_NAME}}',
'INFO',
COALESCE(SUM(ST_NPoints(geometry)),0),
'Nombre total de sommets'

FROM {{TABLE_NAME}};



-- =====================================================
-- G011 : Emprise spatiale
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G011',
'SPATIAL_EXTENT',
'{{TABLE_NAME}}',
'INFO',
1,
ST_Extent(geometry)::text

FROM {{TABLE_NAME}};



-- =====================================================
-- G012 : Géométries multiparties
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G012',
'MULTIPART_GEOMETRY',
'{{TABLE_NAME}}',
'INFO',
COUNT(*),
'Nombre de géométries multiparties'

FROM {{TABLE_NAME}}

WHERE GeometryType(geometry) LIKE 'MULT%';



-- =====================================================
-- G013 : Surface nulle
-- POLYGON / MULTIPOLYGON uniquement
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G013',
'ZERO_AREA',
'{{TABLE_NAME}}',
CASE WHEN COUNT(*)=0 THEN 'OK' ELSE 'ERROR' END,
COUNT(*),
'Polygones avec surface nulle'

FROM {{TABLE_NAME}}

WHERE GeometryType(geometry)
IN ('POLYGON','MULTIPOLYGON')

AND ST_Area(geometry)=0;



-- =====================================================
-- G014 : Longueur nulle
-- LINESTRING / MULTILINESTRING uniquement
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G014',
'ZERO_LENGTH',
'{{TABLE_NAME}}',
CASE WHEN COUNT(*)=0 THEN 'OK' ELSE 'ERROR' END,
COUNT(*),
'Lignes avec longueur nulle'

FROM {{TABLE_NAME}}

WHERE GeometryType(geometry)
IN ('LINESTRING','MULTILINESTRING')

AND ST_Length(geometry)=0;



-- =====================================================
-- G015 : Complexité géométrique
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G015',
'GEOMETRY_COMPLEXITY',
'{{TABLE_NAME}}',
'INFO',
COALESCE(MAX(ST_NPoints(geometry)),0),
'Nombre maximum de sommets dans une géométrie'

FROM {{TABLE_NAME}};



-- =====================================================
-- G016 : Contrôle emprise vide
-- =====================================================

INSERT INTO quality_results
(
rule_code,
rule_name,
table_name,
status,
nb_errors,
details
)

SELECT
'G016',
'EMPTY_EXTENT',
'{{TABLE_NAME}}',
CASE 
WHEN ST_Extent(geometry) IS NULL THEN 'ERROR'
ELSE 'OK'
END,

CASE 
WHEN ST_Extent(geometry) IS NULL THEN 1
ELSE 0
END,

'Vérification de l emprise spatiale'

FROM {{TABLE_NAME}};