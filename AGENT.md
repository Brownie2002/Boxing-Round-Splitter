# 🤖 Guide de Contribution pour l'Agent IA - Boxing Round Splitter

## 🗂️ Structure des Dossiers

### Dossiers Principaux

- **`/docs`** : Documentation de référence (stratégie, protocoles) du projet global
- **`/docs/adr`** : **Architecture Decision Records** - Décisions architecturales documentées
- **`/docs/architecture`** : Documentation architecturale et patterns de conception
- **`/docs/design`** : Documentation de conception détaillée
- **`/docs/reports`** : Rapports générés par les outils et sessions de travail
- **`/docs/todos`** : Fiches de tâches **actives uniquement**
- **`/src`** : Code source principal
- **`/tests`** : Tests unitaires et d'intégration
- **`/archive`** : Documents et tâches **terminés ou obsolètes**

### Documents à la Racine

**Règle** : Garder la racine minimaliste avec uniquement les documents de navigation

**Documents autorisés à la racine** :
- ✅ `README.md` - Description générale du projet
- ✅ `START_HERE.md` - Point d'entrée pour démarrage rapide
- ✅ `AGENT.md` - Ce guide
- ✅ `DEVSTRAL.md` - Règles de développement
- ✅ `TODO.md` - Liste des tâches actives
- ❌ Autres documents → doivent aller dans `/docs/`, `/archive/` ou autres sous-dossiers

---

## 🔄 Cycle de Vie d'une Tâche

### 1. Planification
**Où** : Feuille de route (`/docs/todos/XX_MYTASK.md`)
**Action** : Identifier la tâche à faire

### 2. Exécution
**Où** : Créer une fiche dans `/docs/todos/XX_nom_tache.md`
**Format** :
- Numéro séquentiel (01, 02, 03...)
- Nom descriptif
- Exemple : `03_implement_bell_detection.md`

**Contenu minimum** :
- Objectif clair
- Liste simple des tâches (checklist)
- Références aux documents existants si nécessaire

### 3. Suivi de Progression
**Où** : Créer un fichier STATUS associé `/docs/todos/XX_nom_tache_STATUS.md`
**Contenu (simplicité maximale)** :
- Liste de tâches avec coches
- Progression globale en pourcentage uniquement
- **PAS d'indicateurs temporels** (durée, timeline, etc.)

### 4. Analyse et Résultats
**Où** : `/docs/reports/`
**Type de documents** :
- Rapports de session : `SESSION_YYYY-MM-DD_description.md`
- Rapports d'analyse : `nom_analyse_report.md`
- Datasets : `/tools/datasets/nom_dataset.json`

**Contenu (simplicité maximale)** :
- Liste des objectifs atteints
- Résultats concrets
- **PAS d'indicateurs temporels**

### 5. Archivage
**Quand** : Tâche complétée OU devenue obsolète

**Action** :
```bash
# Déplacer le TODO et son STATUS
mv /docs/todos/XX_nom_tache.md /archive/todos/
mv /docs/todos/XX_nom_tache_STATUS.md /archive/todos/

# Mettre à jour la timeline
 echo "YYYY-MM-DD | TODO XX archivé (complété/obsolète)" >> /docs/TIMELINE.md
```

**Important** : Les rapports de session restent dans `/docs/reports/` (historique du projet)

### 6. Synthèse
**Où** : Documentation principale (`/docs`)
**Action** : Intégrer le savoir acquis dans la documentation permanente

**Fichiers à maintenir** :
- `/docs/INDEX.md` - Index de la documentation
- `/docs/TIMELINE.md` - Historique chronologique des TODOs (une ligne par TODO avec date)

---

## ⚠️ RÈGLE CRITIQUE : Tests et Code de Production

**IMPÉRATIF** : Les tests doivent **TOUJOURS** utiliser le code de production, jamais des copies ou des mocks du code métier.

### Vérifications obligatoires :
- [ ] Les tests importent depuis les modules de production (`/src/`)
- [ ] Aucune duplication de logique métier dans les tests
- [ ] Les fixtures utilisent les vraies classes/fonctions de production
- [ ] Les tests échouent si le code de production change

**Exemple CORRECT** :
```python
from core.split_rounds import detect_bell_ringing  # Import depuis production
```

**Exemple INCORRECT** :
```python
def detect_bell_ringing(...):  # Copie dans le fichier de test ❌
    # logique dupliquée
```

---

## 📋 Workflow de Démarrage de Session

### Pour l'Agent IA (au début de chaque session)

1. **Lire les fichiers de référence** :
   ```bash
   # Lire dans l'ordre : HUMAN.md → AGENT.md → README.md
   cat /HUMAN.md
   cat /AGENT.md
   ```

2. **Identifier la tâche active** :
   ```bash
   ls /docs/TODOS/*.md
   # Chercher les fichiers SANS "_STATUS" → ce sont les plans de tâches
   ```

3. **Lire le STATUS de la tâche** :
   ```bash
   cat /docs/TODOS/XX_nom_tache_STATUS.md
   # Voir la progression, ce qui reste à faire
   ```

4. **Consulter les références** selon la tâche

### RÈGLE CRITIQUE : Lecture Seule à l'Initialisation

**IMPÉRATIF** : La phase d'initialisation est une phase de **chargement de contexte et d'analyse uniquement**. Aucune exécution de code, création de fichiers ou modification ne doit être effectuée pendant cette phase.

**Objectifs de la phase d'initialisation** :
1. ✅ Charger et comprendre les fichiers de configuration (`AGENT.md`, `README.md`)
2. ✅ Identifier les tâches actives en cours via `/docs/todos/03_current_backlog.md`
3. ✅ Analyser l'état actuel du projet via les fichiers STATUS
4. ✅ Consulter la documentation pertinente pour comprendre le contexte
5. ✅ **Présenter des propositions** pour la session de travail courante

**Exemple de workflow correct** :
```
1. Lire AGENT.md, README.md (chargement des règles)
2. Analyser /docs/todos/* (identification des tâches)
3. Lire les fichiers STATUS (compréhension de la progression)
4. Consulter la documentation technique pertinente
5. **Présenter des propositions d'actions** pour la session
6. Attendre validation avant toute exécution
```

**Exemple de workflow incorrect** :
```
1. Lire AGENT.md
2. Créer immédiatement un nouveau fichier TODO (❌ modification pendant initialisation)
3. Exécuter des tests sans analyse complète (❌ exécution pendant initialisation)
4. Proposer des actions sans comprendre le contexte (❌ propositions non fondées)
```

### PHASE DE PROPOSITION ET VALIDATION

**Après l'initialisation**, l'agent doit :

1. **Présenter une analyse claire** de l'état actuel
2. **Proposer un plan d'action détaillé** avec priorités
3. **Attendre validation explicite** avant toute exécution
4. **Documenter les décisions** dans les fichiers STATUS appropriés

**Format de proposition recommandé** :
```
## Analyse de l'état actuel
- Tâche active: [description]
- Progression: [X%]
- Blocages identifiés: [liste]

## Propositions pour cette session
1. [Action 1] - Priorité: [Haute/Moyenne/Basse]
   - Objectif: [description claire]
   - Résultat attendu: [résultat concret]
   - Fichiers concernés: [liste]

2. [Action 2] - Priorité: [Haute/Moyenne/Basse]
   - Objectif: [description claire]
   - Résultat attendu: [résultat concret]
   - Fichiers concernés: [liste]

## Questions/Clarifications nécessaires
- [Question 1]
- [Question 2]
```

---

## 🧹 Règles d'Organisation

### Ce qui va dans `/docs/todos/`

✅ **Autorisé** :
- Fiches de tâches actives (`XX_nom.md`)
- Fichiers de statut (`XX_nom_STATUS.md`)
- Guides pour la prochaine phase (`XX_nom_suite.md`)

❌ **Interdit** :
- Rapports de session (→ `/docs/reports/`)
- Documentation permanente (→ `/docs` ou `/src/docs`)
- Documents obsolètes (→ `/archive/`)

### Ce qui va dans `/docs/reports/`

✅ **Autorisé** :
- Rapports de session (`SESSION_*.md`)
- Rapports d'analyse générés par les outils
- Synthèses de travail
- Validation et statistiques

❌ **Interdit** :
- Plans de tâches (→ `/docs/todos/`)
- Documentation technique (→ `/docs`)

### Ce qui va dans `/archive/`

✅ **Autorisé** :
- TODOs complétés (→ `/archive/todos/`)
- Documents obsolètes (→ `/archive/sessions/` ou autre)
- Anciennes versions de documents

**Important** : Toujours inclure un `README.md` dans les dossiers d'archive expliquant pourquoi les documents ont été archivés.

### Ce qui reste à la racine

**Strict minimum** :
- `README.md` - Documentation complète du projet (technique + utilisation)
- `HUMAN.md` - Guide de collaboration humain-agent
- `AGENT.md` - Règles et workflow pour l'agent IA

**Tout le reste doit être organisé dans les dossiers appropriés.**

> ⚠️ **Notes importantes** :
> - Les TODOs sont centralisés dans `/docs/todos/` pour une gestion unifiée
> - `START_HERE.md` a été supprimé (redondant avec README.md)
> - `TODO.md` a été supprimé (remplacé par `/docs/todos/03_current_backlog.md`)

---

## 📛 Convention de Nommage

### Documentation dans `/docs/`

**RÈGLE IMPÉRATIVE** : Tous les fichiers de documentation dans `/docs/` doivent être préfixés par un indice numérique.

**Format** : `XX_nom_descriptif.md`

**Exemples** :
- ✅ `01_architecture.md`
- ✅ `02_api_design.md`
- ✅ `10_security.md`
- ❌ `architecture.md` (pas d'indice)
- ❌ `doc.md` (pas d'indice)

**Exceptions** : Seuls `INDEX.md` et `TIMELINE.md` ne suivent pas cette règle car ils sont des fichiers système.

### TODOs dans `/docs/todos/`

**Format** : `XX_nom_tache.md` + `XX_nom_tache_STATUS.md`

**Exemples** :
- `01_setup_project.md` + `01_setup_project_STATUS.md`
- `02_implement_bell_detection.md` + `02_implement_bell_detection_STATUS.md`

### Rapports dans `/docs/reports/`

**Format** : `SESSION_YYYY-MM-DD_description.md`

**Exemple** :
- `SESSION_2026-02-15_bell_detection_improvements.md`

---

## 📝 Templates de Documents

### Template : Fichier TODO
```markdown
# TODO XX - Titre de la Tâche

## 🎯 Objectif
[Description claire et concise]

## 📋 Tâches
- [ ] Tâche 1
- [ ] Tâche 2
- [ ] Tâche 3

## 📚 Références
- `/docs/xxx.md` si nécessaire
```

### Template : Rapport de Session
```markdown
# Rapport de Session - Description

**Date** : YYYY-MM-DD

## 🎯 Objectifs Atteints
- ✅ Objectif 1
- ✅ Objectif 2

## 📊 Résultats
[Résultats concrets, statistiques si pertinent]

## 🚀 Prochaines Étapes
[Ce qui reste à faire]
```

⚠️ **RÈGLE CRITIQUE** : Les rapports de session (`SESSION_*.md`) sont **uniquement créés sur demande explicite de l'utilisateur**. L'agent IA ne doit **JAMAIS** créer automatiquement de rapports de session sans validation préalable. Ces rapports documentent les sessions de travail réelles avec des résultats tangibles, pas les opérations techniques internes.

### Template : Fichier STATUS
```markdown
# STATUS - TODO XX : Titre

**Progression** : XX%

## ✅ Complété
- [x] Tâche complétée

## ⏳ En cours / À faire
- [ ] Tâche en cours
- [ ] Tâche à faire
```

### Template : Rapport de Session
```markdown
# Rapport de Session - Description

**Date** : YYYY-MM-DD

## 🎯 Objectifs Atteints
- ✅ Objectif 1
- ✅ Objectif 2

## 📊 Résultats
[Résultats concrets, statistiques si pertinent]

## 🚀 Prochaines Étapes
[Ce qui reste à faire]
```

---

## ✅ Checklist Avant de Terminer une Session

- [ ] Fichier STATUS mis à jour avec progression actuelle
- [ ] `/docs/TIMELINE.md` mis à jour avec nouvelle entrée si TODO créé/archivé
- [ ] Rapport de session créé dans `/docs/reports/` si pertinent
- [ ] Fichiers obsolètes archivés dans `/archive/`
- [ ] Racine du projet propre (pas de fichiers temporaires)

---

## 🚨 Erreurs Courantes à Éviter

### ❌ Ne PAS faire

1. **Créer des documents à la racine** (sauf les 3 autorisés)
   - ❌ `NEXT_SESSION.md` à la racine
   - ✅ `/docs/todos/04_prochaine_phase.md`

2. **Mélanger rapports et TODOs**
   - ❌ Rapport de session dans `/docs/todos/`
   - ✅ Rapport dans `/docs/reports/`, TODO dans `/docs/todos/`

3. **Oublier d'archiver les TODOs complétés**
   - ❌ Garder `03_implementation.md` dans `/docs/todos/` une fois terminé
   - ✅ Déplacer vers `/archive/todos/03_implementation.md`

4. **Créer plusieurs fichiers STATUS**
   - ❌ `03_xxx_STATUS.md` + `03_xxx_PROGRESS.md`
   - ✅ Un seul fichier `03_xxx_STATUS.md` qui centralise tout

5. **Ajouter des indicateurs temporels dans TODO/STATUS/rapports**
   - ❌ Durée estimée, timeline, dates dans les tâches
   - ✅ Uniquement pourcentage de progression et liste de tâches
   - ℹ️ L'historique temporel est dans `/docs/TIMELINE.md`

6. **Tests qui n'utilisent pas le code de production**
   - ❌ Copier/dupliquer la logique métier dans les tests
   - ✅ Toujours importer depuis les modules de production

### ✅ Bonnes Pratiques

1. **Toujours partir de `START_HERE.md`** en début de session
2. **Un TODO = Un fichier + Un STATUS** (paire indissociable)
3. **Les rapports restent dans `/docs/reports/`** (historique permanent)
4. **Archiver dès que complété ou obsolète**
5. **Mettre à jour `/docs/TIMELINE.md`** pour chaque TODO créé/archivé
6. **Simplicité maximale** : liste de tâches + pourcentage (pas de durées)
7. **Tests = code de production** : jamais de duplication de logique

---

## 📞 Aide Rapide

| Situation | Action |
|-----------|--------|
| Je commence une session | Lire `HUMAN.md` puis `AGENT.md` |
| Je veux créer une nouvelle tâche | Créer `/docs/todos/XX_nom.md` + `/docs/todos/XX_nom_STATUS.md` + ligne dans `/docs/TIMELINE.md` |
| Je veux voir les tâches actives | Consulter `/docs/todos/03_current_backlog.md` |
| Je veux documenter ma session | **Demander explicitement** la création de `/docs/reports/SESSION_YYYY-MM-DD_xxx.md` |
| J'ai terminé un TODO | Déplacer vers `/archive/todos/` + mettre à jour `/docs/TIMELINE.md` |
| Un document devient obsolète | Déplacer vers `/archive/` |
| Je veux voir l'historique | Consulter `/docs/TIMELINE.md` |

---

## 🗃️ Documentation Pyramidale

Ce projet utilise une approche pyramidale pour organiser la documentation technique, optimisant la clarté et la navigation entre les niveaux d'abstraction.

### Niveaux de Documentation

1. **Niveau 1: ADR (Architecture Decision Records)**
   - Décisions architecturales majeures impactant le projet
   - Exemples : ADR-0001, ADR-0002, ADR-0003, ADR-0004

2. **Niveau 2: Architecture et Design**
   - Structure globale, patterns et choix de conception
   - Exemples : structure-globale.md, patterns-conception.md

3. **Niveau 3: Documentation du Code**
   - Détails d'implémentation, APIs et commentaires techniques
   - Docstrings dans le code source

### Règles de Documentation

- **Lire README.md en premier** : Commencez par lire le README.md pour comprendre le projet.
- **ADRs comme source de vérité** : Toutes les décisions architecturales doivent être documentées dans les ADRs.
- **Ne pas inventer d'architecture non documentée** : Évitez les suppositions non documentées. Clarifiez ou documentez avant l'implémentation.

### Function Documentation Rules

- Function behavior is documented in docstrings
- Module-level rules are documented at top of file
- No deep logic explained outside code
- If documentation needs to be more explicit than just the minimum docstring, it will be placed in `docs/design/name_of_developed_doc.md` and a link will be added in the docstring. Example: "// See docs/design/identity-normalization.md"

---

## 📋 Structure des ADR

Chaque ADR suit ce format :
- **Titre** : `# ADR-XXXX — [Titre de la décision]`
- **Statut** : `Accepté | Rejeté | Supersédé`
- **Contexte** : Explication du problème ou de la nécessité.
- **Décision** : Solution choisie.
- **Conséquences** : Impact (avantages et inconvénients).

---

## 🔧 Règles de Développement et Maintenance

### Règles de Commit

- **Ajout des fichiers** : Avant de faire un commit, s'assurer d'ajouter (`git add`) tous les fichiers modifiés ou créés.
- **Résumé du commit** : Fournir un résumé clair des changements et des fichiers concernés.
- **Message de commit** : Suivre la spécification [Conventional Commits](https://www.conventionalcommits.org/) pour structurer les messages.

**Exemples** :
- `feat: ajouter une nouvelle fonctionnalité`
- `fix: corriger un bug`
- `docs: mettre à jour la documentation`
- `chore: nettoyage du code`

- **Séparation des Commits** : Séparer les commits par type pour maintenir un historique Git clair et organisé. Chaque commit doit se concentrer sur un seul type de changement pour faciliter la revue et la maintenance.
- **Pas de réécriture de l'historique** : Ne jamais utiliser `git rebase`, `git commit --amend`, ou toute autre opération qui réécrit l'historique Git.

### Règles de Todo

- **Déplacer les TODOs terminés** : Lorsque qu'un TODO est marqué comme terminé (avec un `x`), le déplacer dans la catégorie "Completed" et associer le commit correspondant si possible.
- **Associer les commits** : Pour chaque TODO terminé, ajouter un lien vers le commit correspondant pour faciliter le suivi des changements.

### Règles de Développement

- **Utilisation des Arguments de Ligne de Commande** : Toujours utiliser `argparse` pour parser les arguments de ligne de commande. Cela permet une gestion cohérente et flexible des options et des arguments.
- **Logging** : Utiliser le module `logging` pour gérer les logs. Les logs de debug doivent être activés avec une option `--debug` pour éviter d'encombrer la sortie standard.
- **Chemins Absolus** : Toujours utiliser des chemins absolus pour les fichiers et répertoires afin d'éviter les problèmes de chemins relatifs.
- **Gestion des Erreurs** : Utiliser des blocs `try-except` pour gérer les erreurs et fournir des messages d'erreur clairs et utiles.

### Maintenance des ADRs

- **Ajouter un ADR** : Créez un fichier dans `docs/adr/` avec le format `XXXX-nom-court.md`.
- **Mettre à jour** : Modifiez les fichiers existants et assurez-vous que les références sont à jour.

### Règles de Commit

- **Ajout des fichiers** : Avant de faire un commit, s'assurer d'ajouter (`git add`) tous les fichiers modifiés ou créés.
- **Résumé du commit** : Fournir un résumé clair des changements et des fichiers concernés.
- **Message de commit** : Suivre la spécification [Conventional Commits](https://www.conventionalcommits.org/) pour structurer les messages.

**Exemples** :
- `feat: ajouter une nouvelle fonctionnalité`
- `fix: corriger un bug`
- `docs: mettre à jour la documentation`
- `chore: nettoyage du code`

- **Séparation des Commits** : Séparer les commits par type pour maintenir un historique Git clair et organisé.
- **Pas de réécriture de l'historique** : Ne jamais utiliser `git rebase`, `git commit --amend`, ou toute autre opération qui réécrit l'historique Git.

### Règles de Todo

- **Déplacer les TODOs terminés** : Lorsque qu'un TODO est marqué comme terminé (avec un `x`), le déplacer dans la catégorie "Completed" et associer le commit correspondant si possible.
- **Associer les commits** : Pour chaque TODO terminé, ajouter un lien vers le commit correspondant pour faciliter le suivi des changements.

### Règles de Développement

- **Utilisation des Arguments de Ligne de Commande** : Toujours utiliser `argparse` pour parser les arguments de ligne de commande.
- **Logging** : Utiliser le module `logging` pour gérer les logs. Les logs de debug doivent être activés avec une option `--debug`.
- **Chemins Absolus** : Toujours utiliser des chemins absolus pour les fichiers et répertoires.
- **Gestion des Erreurs** : Utiliser des blocs `try-except` pour gérer les erreurs.

---

**Respectez impérativement ce cycle pour toute modification.**

**Version** : 1.0
**Dernière mise à jour** : 2026-02-15
**Projet** : Boxing Round Splitter