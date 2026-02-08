# ADR-0005 — Logo Parameter Support

## Statut
Accepté

## Contexte
Le projet Boxing Round Splitter a besoin de permettre aux utilisateurs d'ajouter un logo personnalisé aux vidéos générées. Cela permettrait aux utilisateurs de personnaliser les vidéos de sortie avec leur propre branding ou identification visuelle. Actuellement, le projet ne supporte pas cette fonctionnalité, ce qui limite les possibilités de personnalisation.

## Décision
Ajouter un paramètre `--logo` à l'interface en ligne de commande qui permet aux utilisateurs de spécifier un fichier image à utiliser comme logo. Le logo sera superposé sur les vidéos de sortie.

### Implémentation
- **Paramètre CLI** : Ajouter `--logo <path>` comme argument optionnel
- **Gestion des chemins** : Convertir les chemins relatifs en chemins absolus pour éviter les problèmes de chemins
- **Validation** : Vérifier que le fichier logo existe et est dans un format supporté (PNG, JPG, etc.)
- **Intégration** : Utiliser ffmpeg pour superposer le logo sur les vidéos générées

### Format du paramètre
```bash
python split_rounds.py --logo ./logo_test.png video1.mp4 video2.mp4
```

## Conséquences
- **Avantages** :
  - Permet la personnalisation des vidéos de sortie
  - Améliore l'expérience utilisateur avec des options de branding
  - Maintenir la cohérence avec les autres options CLI existantes
  - Utilisation de chemins absolus pour éviter les problèmes de chemins relatifs

- **Inconvénients** :
  - Complexité supplémentaire dans le code de traitement vidéo
  - Nécessité de gérer les erreurs de fichiers manquants ou invalides
  - Performance potentielle impactée par le traitement supplémentaire du logo
  - Compatibilité à maintenir avec différents formats d'image

## Tests et Validation
- Ajouter des tests pour vérifier que le paramètre logo est correctement analysé
- Tester avec des chemins relatifs et absolus
- Vérifier que les fichiers logo inexistants génèrent des erreurs appropriées
- Valider que le logo est correctement superposé sur les vidéos de sortie

## Références
- [ADR-0002 — Format ADR](0002-format-adr.md)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Python argparse Documentation](https://docs.python.org/3/library/argparse.html)