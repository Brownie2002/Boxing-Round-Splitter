# Structure Globale du Projet

Le projet est organisé en modules indépendants, chacun ayant une responsabilité claire. Les modules communiquent entre eux via des interfaces bien définies.

## Modules Principaux

### Module de Traitement Vidéo

**Responsabilité**: 
- Lecture, découpage et export des vidéos.
- Utilisation de bibliothèques comme `moviepy` pour le traitement.

**Interfaces**:
- `split_video(video_path, output_dir, segment_duration)`: Découpe une vidéo en segments.
- `extract_audio(video_path, output_path)`: Extrait la piste audio d'une vidéo.

### Module de Gestion des Fichiers

**Responsabilité**: 
- Lecture et écriture des fichiers vidéo et audio.
- Gestion des chemins et des noms de fichiers.

**Interfaces**:
- `get_file_list(directory)`: Récupère la liste des fichiers dans un répertoire.
- `generate_output_path(input_path, output_dir)`: Génère un chemin de sortie pour un fichier.

### Module d'Interface Utilisateur

**Responsabilité**: 
- Fournit une interface en ligne de commande pour interagir avec l'utilisateur.
- Affiche les progrès et les résultats des opérations.

**Interfaces**:
- `display_progress(current, total)`: Affiche la progression d'une opération.
- `get_user_input(prompt)`: Récupère une entrée utilisateur.

## Références

- Voir [ADR-0001 — Structure de Documentation Pyramidale](../adr/0001-structure-documentation-pyramidale.md) pour la structure de documentation.
- Voir [ADR-0002 — Format des ADR](../adr/0002-format-adr.md) pour le format des décisions architecturales.
