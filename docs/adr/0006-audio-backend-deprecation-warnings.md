# ADR-0006 — Gestion des avertissements de dépréciation des dépendances audio

**Statut** : Accepté

**Date** : 2025-02-08

## Contexte

Lors de l'exécution des tests unitaires, des avertissements de dépréciation apparaissent provenant des dépendances internes de `librosa` et `audioread` :

```
DeprecationWarning: 'aifc' is deprecated and slated for removal in Python 3.13
DeprecationWarning: 'audioop' is deprecated and slated for removal in Python 3.13  
DeprecationWarning: 'sunau' is deprecated and slated for removal in Python 3.13
```

Ces avertissements proviennent du module `audioread.rawread.py` qui utilise ces bibliothèques standard Python pour lire certains formats audio. Bien que ces avertissements n'affectent pas la fonctionnalité actuelle, ils indiquent que le code utilise des bibliothèques qui seront supprimées dans les versions futures de Python.

## Décision

### Solution immédiate (implémentée)

Pour les tests unitaires, nous avons choisi de supprimer ces avertissements en utilisant un contexte `warnings.catch_warnings()` autour de l'appel à `detect_bell_ringing()`. Cette approche permet :

- De maintenir des tests propres sans avertissements
- De ne pas affecter le code de production
- De conserver la fonctionnalité existante
- D'éviter de masquer d'autres avertissements importants

### Solution à long terme (à envisager)

Nous devons évaluer la migration vers un backend audio plus moderne. Les options incluent :

1. **Utilisation de `soundfile` comme backend pour librosa** (si supporté)
2. **Migration vers une autre bibliothèque audio** qui ne dépend pas de ces modules dépréciés
3. **Attendre les mises à jour de librosa/audioread** qui résoudront probablement ce problème

## Conséquences

### Avantages de la solution actuelle

- **Tests propres** : Les sorties de tests sont maintenant exemptes d'avertissements
- **Stabilité** : Aucune modification du code de production nécessaire
- **Compatibilité** : Le code continue de fonctionner avec les versions actuelles de Python
- **Maintenabilité** : Solution simple et localisée dans les tests

### Inconvénients et risques

- **Dépendance dépréciée** : Le code dépend toujours de bibliothèques qui seront supprimées
- **Migration future nécessaire** : Il faudra probablement migrer avant Python 3.13
- **Avertissements masqués** : D'autres avertissements de dépréciation pourraient être ignorés

### Considérations pour la migration future

- **Compatibilité** : Vérifier que le nouveau backend supporte tous les formats audio nécessaires
- **Performances** : Évaluer l'impact sur les performances de détection des cloches
- **Stabilité** : Tester rigoureusement avec les fichiers audio existants
- **Documentation** : Mettre à jour la documentation technique si le backend change

## Alternatives envisagées

1. **Ignorer tous les avertissements globalement** - Rejeté car trop large et pourrait masquer d'autres problèmes
2. **Modifier le code de production pour utiliser soundfile** - Rejeté pour l'instant car nécessite plus de recherche et de tests
3. **Créer un wrapper autour de librosa** - Rejeté car ajoute de la complexité inutile
4. **Attendre et surveiller les mises à jour** - Option retenue pour la solution à long terme

## Plan d'action

1. **Court terme** (fait) : Implémenter la suppression des avertissements dans les tests
2. **Moyen terme** : Rechercher les options de migration vers un backend audio moderne
3. **Long terme** : Migrer vers une solution durable avant la suppression des modules dépréciés

## Références

- [Python 3.13 Release Notes](https://docs.python.org/3/whatsnew/3.13.html)
- [Librosa Documentation](https://librosa.org/doc/latest/index.html)
- [SoundFile Documentation](https://pysoundfile.readthedocs.io/)
- [Audioread Source Code](https://github.com/beetbox/audioread)