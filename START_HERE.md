# 🚀 Point de Départ Rapide - Boxing Round Splitter

Bienvenue dans le projet Boxing Round Splitter! Ce fichier vous guide pour commencer rapidement.

## 📋 Structure du Projet

```
Boxe2/
├── README.md               # Description générale du projet
├── START_HERE.md           # Ce fichier - point d'entrée rapide
├── AGENT.md               # Guide pour l'agent IA
├── DEVSTRAL.md            # Règles de développement et documentation
├── TODO.md                # Liste des tâches actives
├── requirements.txt        # Dépendances Python
├── src/
│   └── core/
│       └── split_rounds.py # Code principal
├── tests/
│   └── unit/
│       └── test_bell_detection.py # Tests unitaires
└── docs/
    ├── adr/                # Architecture Decision Records
    ├── architecture/       # Documentation architecturale
    └── design/             # Documentation de conception
```

## 🎯 Objectif du Projet

Créer un outil Python pour découper automatiquement les vidéos de boxe en rounds individuels en détectant le son de la cloche.

## 🚀 Démarrage Rapide

### 1. Lire la documentation essentielle
- **README.md** : Description complète du projet
- **AGENT.md** : Guide pour l'agent IA (si vous êtes un agent)
- **DEVSTRAL.md** : Règles de développement et documentation

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Exécuter le script principal
```bash
python src/core/split_rounds.py --debug path/to/your/video.mp4
```

### 4. Exécuter les tests
```bash
python -m unittest discover -s tests/unit -p "test_*.py"
```

## 📂 Tâches Actives

Consultez **TODO.md** pour voir:
- Les tâches de haute priorité
- Les tâches en cours
- Les tâches complétées

## 📚 Documentation Technique

### Architecture Decision Records (ADRs)
- **ADR-0001** : Structure de documentation pyramidale
- **ADR-0002** : Format des ADRs
- **ADR-0003** : Fonction de détection de cloche
- **ADR-0004** : Améliorations de la détection de cloche

### Documentation de Conception
- **docs/design/bell_detection.md** : Algorithme de détection de cloche
- **docs/architecture/structure-globale.md** : Structure globale du projet

## 🤖 Pour les Agents IA

Si vous êtes un agent IA, veuillez consulter **AGENT.md** pour les règles spécifiques de contribution et le workflow recommandé.

## 📊 Prochaines Étapes

1. Lire le README.md complet
2. Explorer la documentation dans /docs/
3. Consulter les tâches dans TODO.md
4. Exécuter les tests pour vérifier l'environnement

Bonne chance avec le projet Boxing Round Splitter! 🥊