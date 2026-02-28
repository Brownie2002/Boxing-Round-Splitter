# ADR-0005 — Optimisation du tri des vidéos par date de création

## Statut
Accepté

## Contexte

Le projet Boxing Round Splitter a été étendu pour accepter plusieurs fichiers vidéo en entrée, ce qui est utile lorsque les vidéos sont splittées par la caméra en plusieurs segments. Cependant, l'implémentation initiale avait les problèmes suivants :

1. **Appels redondants à FFprobe** : La fonction `get_video_metadata()` et une nouvelle fonction pour extraire la date complète appelaient toutes deux FFprobe séparément pour la même vidéo
2. **Inefficacité** : Pour N vidéos, nous avions 2N appels à FFprobe au lieu de N
3. **Complexité accrue** : Le code de tri et d'extraction des métadonnées était dupliqué

## Décision

Créer une architecture optimisée avec les composants suivants :

1. **Fonction unifiée `get_video_creation_info()`** :
   - Effectue un seul appel FFprobe par vidéo
   - Retourne à la fois la date formatée (YYYY-MM-DD) et l'objet datetime complet
   - Centralise toute la logique d'extraction des métadonnées

2. **Fonction de tri enrichie `sort_videos_by_creation_date()`** :
   - Appelle `get_video_creation_info()` une fois par vidéo
   - Retourne un tuple contenant :
     - Liste des vidéos triées par date (plus ancienne en premier)
     - Date de la première vidéo pour le nom du dossier de sortie
     - Informations complètes pour l'affichage des logs

3. **Maintien de la compatibilité** :
   - La fonction `get_video_metadata()` existante est conservée comme wrapper
   - Elle utilise maintenant `get_video_creation_info()` en interne
   - Aucune modification de l'API publique

## Conséquences

### Positives

- **Performances améliorées** : Réduction de 50% des appels à FFprobe
- **Code plus maintenable** : Logique centralisée et non dupliquée
- **Meilleure expérience utilisateur** : Les vidéos sont automatiquement triées par date de création
- **Logs plus informatifs** : Affichage clair de l'ordre de traitement
- **Robustesse** : Meilleure gestion des vidéos sans métadonnées

### Négatives

- **Complexité légèrement accrue** : La fonction de tri retourne maintenant un tuple au lieu d'une simple liste
- **Mémoire** : Stocke temporairement plus d'informations sur les vidéos pendant le tri

### Neutres

- **Compatibilité** : L'API publique reste inchangée pour les utilisateurs existants
- **Tests** : Les tests existants continuent de fonctionner sans modification

## Implémentation

```python
def get_video_creation_info(video_path):
    """
    Extracts creation metadata from a video file in a single FFprobe call.
    Returns both formatted date and full datetime object.
    """
    # Single FFprobe call
    # Returns (formatted_date_str, datetime_obj)

ndef sort_videos_by_creation_date(video_files):
    """
    Sorts videos by creation date and returns:
    - sorted video list
    - first video's date for output directory
    - complete info for display purposes
    """
    # Single pass to get all metadata
    # Returns (sorted_videos, first_date, video_info)
```

## Alternatives considérées

1. **Conserver l'implémentation initiale** : Rejeté en raison de l'inefficacité des appels multiples à FFprobe
2. **Utiliser un cache** : Considéré mais rejeté car cela ajouterait de la complexité sans résoudre le problème de fond
3. **Modifier l'API publique** : Rejeté pour maintenir la compatibilité ascendante

## Métriques

- **Avant** : 2N appels FFprobe pour N vidéos
- **Après** : N appels FFprobe pour N vidéos
- **Amélioration** : 50% de réduction des appels système

## Validation

Cette optimisation a été validée par :
- Tests unitaires existants (toujours passants)
- Tests manuels avec plusieurs vidéos
- Vérification des logs et de l'ordre de traitement

## Date
2026-02-15