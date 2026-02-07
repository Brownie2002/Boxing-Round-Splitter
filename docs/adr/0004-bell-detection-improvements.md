# ADR-0004 — Bell Detection Improvements

## Statut
Accepté

## Contexte
La détection des sonneries de cloche dans le projet Boxing Round Splitter a été améliorée pour mieux capturer les événements, notamment à des moments spécifiques comme 7:04. Les paramètres initiaux ne permettaient pas de détecter toutes les sonneries de manière fiable, en particulier celles qui étaient plus faibles ou moins distinctes.

## Décision
Ajuster les paramètres de détection des sonneries pour améliorer la sensibilité et la précision. La modification suivante a été apportée :

### Paramètres Modifiés
- **`MIN_PEAK_HEIGHT`** : Réduit de `0.04` à `0.03` pour capturer des sonneries plus faibles.

### Justification
- **`MIN_PEAK_HEIGHT`** : Une valeur plus basse permet de détecter des sonneries plus faibles, mais peut aussi augmenter le risque de fausses détections. Un équilibre a été trouvé avec `0.03`.

## Conséquences
- **Avantages** :
  - Meilleure détection des sonneries, notamment à des moments spécifiques comme 7:04.
  - Plus de flexibilité pour capturer des sonneries variées.
  - Meilleure adaptabilité à différents types de vidéos de boxe.
- **Inconvénients** :
  - Risque accru de fausses détections si les paramètres sont trop permissifs.
  - Nécessité de tester et d'ajuster les paramètres pour différents types de vidéos.

## Tests et Validation
- Les tests unitaires ont été mis à jour pour vérifier que les timestamps sont correctement formatés et que le fichier de debug est généré.
- Les améliorations ont été validées en testant avec des vidéos réelles et en vérifiant que les sonneries sont détectées correctement.

## Références
- [ADR-0003 — Bell Detection Function](0003-bell-detection-function.md)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Librosa Documentation](https://librosa.org/doc/latest/index.html)
- [Scipy Signal Processing](https://docs.scipy.org/doc/scipy/reference/signal.html)