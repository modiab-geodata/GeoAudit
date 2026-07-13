# \# GeoAudit

# 

# \## Présentation

# 

# GeoAudit est une application Python permettant d'automatiser le contrôle qualité de données géographiques stockées dans PostGIS.

# 

# Le projet permet de :

# 

# \- importer automatiquement plusieurs formats SIG ;

# \- exécuter des contrôles qualité spatiaux ;

# \- calculer un score de qualité ;

# \- générer des rapports Excel et HTML ;

# \- produire des indicateurs synthétiques (KPI).

# 

# \---

# 

# \## Fonctionnalités

# 

# \### Import de données

# 

# ✔ GeoJSON

# 

# ✔ Shapefile

# 

# ✔ GeoPackage

# 

# \---

# 

# \### Contrôles qualité

# 

# \- Géométrie invalide

# \- Géométrie vide

# \- SRID

# \- Type de géométrie

# \- Nombre d'entités

# \- Géométries dupliquées

# \- Nombre de sommets

# \- Emprise spatiale

# \- Surface nulle

# \- Longueur nulle

# \- Complexité géométrique

# \- ...

# 

# \---

# 

# \## Score qualité

# 

# Chaque règle possède un poids.

# 

# Le score est calculé automatiquement sur 100%.

# 

# Classification :

# 

# | Score | Niveau |

# |-------:|---------|

# | ≥95 | Excellent |

# | ≥80 | Bon |

# | ≥50 | Moyen |

# | <50 | Critique |

# 

# \---

# 

# \## Rapports

# 

# GeoAudit génère automatiquement :

# 

# \- rapport Excel

# \- rapport HTML

# \- Rapport PDF

# 

# \---

# 

# \## Installation

# 

# ```bash

# git clone https://github.com/modiab-geodata/GeoAudit.git

# 

# cd GeoAudit

# 

# python -m venv .venv

# 

# source .venv/bin/activate

# ```

# 

# Installer les dépendances :

# 

# ```bash

# pip install -r requirements.txt

# ```

# 

# Créer un fichier :

# 

# ```

# .env

# ```

# 

# \## Lancer un audit

# 

# ```ligne de commande

# python src/main.py

# ```

# 

# \---

# 

# \## Résultats

# 

# Les rapports sont générés dans :

# 

# ```

# reports/

# ```

# 

# \- geoaudit\_report.xlsx

# \- geoaudit\_report.html

# \- geoaudit\_report.pdf



# 

# \---

# 

# \## Stack technique

# 

# \- Python

# \- GeoPandas

# \- PostGIS

# \- PostgreSQL

# \- SQLAlchemy

# \- Pandas

# \- OpenPyXL

# 

# \---

# 

# \## Feuille de route

# 

# \### Version 1.0

# 

# \- Import automatique

# \- Audit SQL

# \- Score qualité

# \- Rapports Excel

# \- Rapports HTML

# \- Rapports PDF

# 

# \### Version 2.0

# 

# \- Interface Streamlit

# \- Carte interactive

# \- Upload de fichiers

# \- Téléchargement des rapports

# 

# \---

# 

# \## Auteur

# 

# Moussa DIABY

# 

# Consultant Data \& Géomatique

