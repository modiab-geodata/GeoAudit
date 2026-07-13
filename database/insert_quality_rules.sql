INSERT INTO quality_rules
(
rule_code,
rule_name,
category,
severity,
description,
parameters
)

VALUES

(
'G001',
'GEOMETRY_VALID',
'geometry',
'ERROR',
'Détection des géométries invalides',
NULL
),

(
'G002',
'EMPTY_GEOMETRY',
'geometry',
'ERROR',
'Détection des géométries vides',
NULL
),

(
'G003',
'SRID_CHECK',
'projection',
'ERROR',
'Contrôle du système de coordonnées',
'{"expected_srid":2154}'
),

(
'G004',
'GEOMETRY_TYPE',
'geometry',
'INFO',
'Identification du type géométrique',
NULL
),

(
'G005',
'ENTITY_COUNT',
'statistics',
'INFO',
'Nombre total d''entités',
NULL
),

(
'G006',
'NULL_GEOMETRY',
'geometry',
'ERROR',
'Présence de géométries NULL',
NULL
),

(
'G007',
'DUPLICATE_GEOMETRY',
'geometry',
'WARNING',
'Détection de doublons géométriques',
NULL
),

(
'G008',
'COLUMN_COUNT',
'structure',
'INFO',
'Nombre de colonnes',
NULL
),

(
'G009',
'NULL_ATTRIBUTES',
'attribute',
'WARNING',
'Valeurs attributaires NULL',
NULL
),

(
'G010',
'VERTEX_COUNT',
'geometry',
'INFO',
'Nombre de sommets',
NULL
),


(
'G011',
'SPATIAL_EXTENT',
'spatial',
'INFO',
'Calcul de l''emprise spatiale',
NULL
),

(
'G012',
'MULTIPART_GEOMETRY',
'geometry',
'INFO',
'Détection des géométries multiparties',
NULL
),

(
'G013',
'ZERO_AREA',
'geometry',
'ERROR',
'Détection des polygones avec surface nulle',
'{"min_area":1}'
),

(
'G014',
'ZERO_LENGTH',
'geometry',
'ERROR',
'Détection des lignes avec longueur nulle',
'{"min_length":1}'
),

(
'G015',
'GEOMETRY_COMPLEXITY',
'geometry',
'INFO',
'Mesure de la complexité géométrique',
'{"max_vertices":10000}'
),

(
'G016',
'EMPTY_EXTENT',
'spatial',
'ERROR',
'Vérification d''une emprise spatiale vide',
NULL
);