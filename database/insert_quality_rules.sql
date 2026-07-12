INSERT INTO quality_rules
(
rule_code,
rule_name,
category,
severity,
description
)

VALUES

(
'G001',
'GEOMETRY_VALID',
'geometry',
'ERROR',
'Détection des géométries invalides'
),

(
'G002',
'EMPTY_GEOMETRY',
'geometry',
'ERROR',
'Détection des géométries vides'
),

(
'G003',
'SRID_CHECK',
'projection',
'ERROR',
'Contrôle du système de coordonnées'
),

(
'G004',
'GEOMETRY_TYPE',
'geometry',
'INFO',
'Identification du type géométrique'
),

(
'G005',
'ENTITY_COUNT',
'statistics',
'INFO',
'Nombre total d entités'
),

(
'G006',
'NULL_GEOMETRY',
'geometry',
'ERROR',
'Présence de géométries NULL'
),

(
'G007',
'DUPLICATE_GEOMETRY',
'geometry',
'WARNING',
'Détection de doublons géométriques'
),

(
'G008',
'COLUMN_COUNT',
'structure',
'INFO',
'Nombre de colonnes'
),

(
'G009',
'NULL_ATTRIBUTES',
'attribute',
'WARNING',
'Valeurs attributaires NULL'
),

(
'G010',
'VERTEX_COUNT',
'geometry',
'INFO',
'Nombre de sommets'
);