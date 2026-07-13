# 🗺️ GeoAudit

## Contrôle qualité automatisé des données géospatiales

GeoAudit est une plateforme développée en **Python** permettant d'automatiser le contrôle qualité de données géospatiales stockées dans **PostgreSQL/PostGIS** ou importées par l'utilisateur.

L'application exécute automatiquement un ensemble de règles de validation spatiale et attributaire, calcule un score de qualité pondéré, génère des rapports détaillés et met à disposition un tableau de bord interactif développé avec **Streamlit**.

---

# Objectifs

Les organismes manipulant des données SIG doivent garantir leur qualité avant leur diffusion ou leur intégration dans des traitements métiers.

GeoAudit permet de :

* automatiser les contrôles qualité ;
* détecter les erreurs géométriques et attributaires ;
* calculer un score global de qualité ;
* générer des rapports d'audit exploitables ;
* fournir un tableau de bord interactif pour l'analyse des résultats.

---

# Fonctionnalités

## Audit automatique

* Détection automatique des couches spatiales PostGIS.
* Audit d'une ou plusieurs couches.
* Exécution automatique des règles de qualité actives.

---

## Contrôles géométriques

GeoAudit vérifie notamment :

* Validité des géométries.
* Géométries nulles.
* Géométries vides.
* Vérification du SRID.
* Vérification du type de géométrie.
* Détection des géométries dupliquées.
* Détection des géométries multipart.
* Vérification de l'emprise spatiale.
* Contrôle du nombre de sommets.
* Détection des surfaces nulles.
* Détection des longueurs nulles.
* Vérification de la complexité géométrique.

---

## Contrôles attributaires

* Nombre d'entités.
* Nombre de colonnes.
* Détection des valeurs NULL.
* Comptage des erreurs détectées.
* Vérification de la cohérence des données.

---

## Score qualité

Chaque règle possède un poids configurable.

GeoAudit calcule automatiquement :

* Score qualité (%)
* Nombre de règles exécutées
* Nombre d'erreurs
* Niveau de qualité

Classification automatique :

| Score   | Niveau       |
| ------- | ------------ |
| ≥ 95    | EXCELLENT |
| 80 - 94 | BON       |
| 50 - 79 | MOYEN     |
| < 50    | CRITIQUE  |

---

## Tableau de bord Streamlit

Le tableau de bord permet de visualiser :

* Nombre de couches auditées
* Score moyen
* Nombre de contrôles exécutés
* Nombre d'erreurs détectées
* Résumé des scores
* Détail des contrôles

---

## Import de données

GeoAudit permet d'importer directement des données SIG depuis l'interface web.

Formats actuellement supportés :

* GeoJSON
* GeoPackage (.gpkg)
* Shapefile (prise en charge en cours d'amélioration)

---

## Génération de rapports

Après chaque audit, GeoAudit génère automatiquement :

* Rapport Excel (.xlsx)
* Rapport HTML interactif
* Rapport PDF

Les rapports contiennent :

* synthèse des audits ;
* score qualité ;
* détail des contrôles exécutés ;
* nombre d'erreurs détectées.

---

# Architecture


                +----------------+
                |   Utilisateur  |
                +--------+-------+
                         |
                         v
                  Streamlit UI
                         |
                         v
                 Moteur GeoAudit
                         |
        +----------------+----------------+
        |                                 |
        v                                 v
 Contrôles qualité                Calcul du score
        |                                 |
        +----------------+----------------+
                         |
                         v
               Génération des rapports
                         |
                         v
        Excel / HTML / PDF / Dashboard
```

---

# Stacks techniques

| Domaine            | Technologies                   |
| ------------------ | ------------------------------ |
| Langage            | Python 3                       |
| Base de données    | PostgreSQL                     |
| Extension spatiale | PostGIS                        |
| ORM                | SQLAlchemy                     |
| Analyse de données | Pandas                         |
| Données spatiales  | GeoPandas                      |
| Interface web      | Streamlit                      |
| Rapports Excel     | OpenPyXL                       |
| Rapports PDF       | ReportLab                      |
| Formats SIG        | GeoJSON, GeoPackage, Shapefile |
| Versionnement      | Git / GitHub                   |

---

#  Structure du projet


GeoAudit/


├── log/
|	├── geoaudit.log

├── config/
|	├── config.yaml

|
├── database/
│   ├── rules/
│   └── scripts/

│
├── reports/
│   ├── geoaudit_report.xlsx
│   ├── geoaudit_report.html
│   └── geoaudit_report.pdf
|
├── img/
│   ├── vue_ensemble.png
│   ├── import_donnees.png
    ├── qualites_de_donnes_par_couche.png
	├── details_controles.png
│   └── exporter_rapports_de_controles.png
│
├── src/
│   ├── audit_runner.py
│   ├── dashboard.py
    |── audit_summary.py
│   ├── database.py
│   ├── logger.py
│   ├── main.py
│   ├── config.py
│   ├── load_data.py
│   ├── quality_results.py
│   ├── quality_check.py
│   ├── quality_score.py
│   ├── report.py
│   ├── streamlit_app.py
│   └── upload.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example


# Installation

## 1. Cloner le dépôt

```bash
git clone https://github.com/modiab-geodata/GeoAudit.git

cd GeoAudit
```


## 2. Créer un environnement virtuel

### Windows

```powershell
python -m venv .venv

.venv\Scripts\activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

# Configuration

Créer un fichier `.env` à la racine du projet.

Exemple :

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=geoaudit
DB_USER=postgres
DB_PASSWORD=your_password
```


#  Exécution

## Mode ligne de commande

```bash
python src/main.py
```

---

## Mode interface web

```bash
streamlit run src/streamlit_app.py
```

Puis ouvrir :

```text
http://localhost:8501
```

---

# Utilisation

1. Importer une couche SIG.
2. Lancer l'audit.
3. Consulter le tableau de bord.
4. Analyser le score qualité.
5. Télécharger les rapports générés.

---


# Évolutions futures

Les évolutions envisagées sont notamment :

* Amélioration de l'interface Streamlit
* Authentification des utilisateurs.
* Déploiement Docker.
* Gestion multi-utilisateurs.
* Intégration CI/CD.
* Déploiement Cloud.

---

# Contribution

Les contributions sont les bienvenues.

Pour contribuer :

1. Fork du projet.
2. Création d'une branche.
3. Développement de la fonctionnalité.
4. Pull Request.

---


# Auteur

**Moussa DIABY**

Ingénieur SIG • Consultant Data & Géomatique

* GitHub : https://github.com/modiab-geodata
* LinkedIn : https://www.linkedin.com/in/moussadiaby/
