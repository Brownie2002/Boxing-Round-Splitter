# Optimisation du Tri des Vidéos

## Vue d'ensemble

Ce document décrit l'optimisation apportée au traitement des vidéos multiples dans le Boxing Round Splitter, spécifiquement pour le tri chronologique des vidéos par date de création.

## Problème Initial

Lorsque plusieurs fichiers vidéo sont fournis en entrée (cas courant lorsque les caméras splitent les enregistrements), le système devait :

1. Extraire les métadonnées de chaque vidéo pour le tri
2. Extraire à nouveau les métadonnées pour obtenir la date de la première vidéo
3. Cela résultait en des appels redondants à FFprobe

## Solution Architecturale

### Nouvelle Fonction `get_video_creation_info()`

```python
def get_video_creation_info(video_path):
    """
    Extracts creation metadata from a video file in a single FFprobe call.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        tuple: (formatted_date_str, datetime_obj)
        - formatted_date_str: 'YYYY-MM-DD' or error message
        - datetime_obj: Full datetime object or None
    """
```

**Caractéristiques** :
- Un seul appel FFprobe par vidéo
- Retourne à la fois la date formatée et l'objet datetime complet
- Gestion centralisée des erreurs
- Logging unifié

### Fonction de Tri Optimisée

```python
def sort_videos_by_creation_date(video_files):
    """
    Sorts videos by creation date with single metadata extraction pass.
    
    Args:
        video_files (list): List of video file paths
        
    Returns:
        tuple: (sorted_videos, first_video_date, sorted_video_info)
        - sorted_videos: List of video paths sorted chronologically
        - first_video_date: Date of first video for output directory
        - sorted_video_info: Complete info for display purposes
    """
```

**Algorithme** :
1. Extraire les métadonnées de toutes les vidéos en un seul passage
2. Trier par date de création (plus ancienne en premier)
3. Les vidéos sans métadonnées sont placées à la fin
4. Retourner toutes les informations nécessaires pour le traitement et l'affichage

## Flux de Traitement Optimisé

```mermaid
graph TD
    A[Début] --> B[Recevoir liste de vidéos]
    B --> C[Extraire métadonnées (1 appel FFprobe/vidéo)]
    C --> D[Trier par date de création]
    D --> E[Retourner vidéos triées + date première vidéo + infos affichage]
    E --> F[Créer dossier de sortie avec date première vidéo]
    F --> G[Traitement des vidéos dans l'ordre trié]
```

## Performances

### Avant Optimisation
- 2N appels FFprobe pour N vidéos
- Temps proportionnel à 2N
- Complexité : O(2N)

### Après Optimisation  
- N appels FFprobe pour N vidéos
- Temps proportionnel à N
- Complexité : O(N)

**Amélioration** : 50% de réduction des appels système

## Intégration avec le Code Existant

### Compatibilité Ascendante

La fonction `get_video_metadata()` existante est conservée comme wrapper :

```python
def get_video_metadata(video_path):
    """Wrapper pour compatibilité ascendante"""
    formatted_date, _ = get_video_creation_info(video_path)
    return formatted_date
```

### Modifications dans `main()`

```python
# Ancienne version (2 appels séparés)
sorted_videos = sort_videos_by_creation_date(video_files)
creation_date = get_video_metadata(sorted_videos[0])

# Nouvelle version (1 appel unifié)
sorted_videos, creation_date, video_info = sort_videos_by_creation_date(video_files)
```

## Cas d'Utilisation

### Cas 1 : Vidéos avec métadonnées complètes
```
Entrée: [video2.mp4 (2026-02-15 14:30), video1.mp4 (2026-02-15 14:00)]
Sortie: [video1.mp4, video2.mp4]  # Tri chronologique
Dossier: 2026-02-15-boxing/
```

### Cas 2 : Vidéos avec métadonnées partielles
```
Entrée: [video1.mp4 (date inconnue), video2.mp4 (2026-02-15)]
Sortie: [video2.mp4, video1.mp4]  # Vidéos sans date à la fin
Dossier: 2026-02-15-boxing/
```

### Cas 3 : Toutes les vidéos sans métadonnées
```
Entrée: [video1.mp4 (inconnue), video2.mp4 (inconnue)]
Sortie: [video1.mp4, video2.mp4]  # Ordre original préservé
Dossier: Not-available-boxing/
```

## Gestion des Erreurs

### Erreurs FFprobe
- Journalisées avec niveau WARNING
- La vidéo concernée est traitée comme "date inconnue"
- Le traitement continue avec les autres vidéos

### Vidéos sans métadonnées
- Placées à la fin de la liste triée
- Date du dossier basée sur la première vidéo avec métadonnées
- Si aucune vidéo n'a de métadonnées, utilise "Not-available"

## Journalisation

Le système journalise :
- L'ordre de tri lorsque différent de l'ordre original
- Les dates de création de chaque vidéo
- Les avertissements pour les vidéos sans métadonnées

Exemple de log :
```
INFO: Videos sorted by creation date:
INFO:   1. video1.mp4 - 2026-02-15 14:00:00
INFO:   2. video2.mp4 - 2026-02-15 14:30:00
INFO:   3. video3.mp4 - Unknown
```

## Impact sur les Tests

- Tous les tests existants continuent de passer
- Aucun nouveau test requis pour cette optimisation
- La fonction `get_video_metadata()` conserve le même comportement

## Recommandations pour l'Avenir

1. **Cache optionnel** : Pour un grand nombre de vidéos, considérer un cache des métadonnées
2. **Parallélisation** : L'extraction des métadonnées pourrait être parallélisée pour de très grands ensembles
3. **Autres métadonnées** : La fonction unifiée pourrait être étendue pour extraire d'autres métadonnées utiles

## Conclusion

Cette optimisation réduit de 50% les appels système tout en améliorant la maintenabilité du code et l'expérience utilisateur. L'architecture est conçue pour être extensible et robuste face aux vidéos avec métadonnées incomplètes.