# ADR-0003 — Bell Detection Function

## Statut
Accepté

## Contexte
La détection des sonneries de cloche est une fonctionnalité clé du projet Boxing Round Splitter. Auparavant, cette logique était intégrée directement dans la fonction principale, ce qui rendait le code difficile à maintenir et à tester. Pour améliorer la modularité et la testabilité, il était nécessaire d'extraire cette logique dans une fonction dédiée.

## Décision
Créer une fonction `detect_bell_ringing` qui encapsule la logique de détection des sonneries de cloche. Cette fonction prend en entrée un fichier audio (WAV) et retourne une liste d'événements de sonnerie, où chaque événement est une liste de timestamps.

### Détails de la Fonction
- **Nom** : `detect_bell_ringing`
- **Entrées** :
  - `audio_path` (str) : Chemin vers le fichier audio (WAV).
  - `output_debug_file` (str, optionnel) : Chemin vers un fichier de debug pour enregistrer les informations de détection.
- **Sorties** :
  - `list` : Une liste de listes, où chaque sous-liste contient les timestamps d'un événement de sonnerie détecté.

### Algorithme
1. **Chargement de l'audio** : Utilisation de `librosa` pour charger le fichier audio.
2. **Filtrage passe-bande** : Application d'un filtre passe-bande autour de 2050 Hz pour isoler le son de la cloche.
3. **Détection des pics** : Utilisation de `scipy.signal.find_peaks` pour détecter les pics dans l'amplitude du signal filtré.
4. **Regroupement des pics** : Regroupement des pics en événements de sonnerie en fonction de leur proximité temporelle.

### Fichier de Debug
La fonction peut générer un fichier de debug qui liste les événements de sonnerie détectés. Cela facilite le débogage et la validation des résultats.

## Conséquences
- **Avantages** :
  - **Modularité** : La logique de détection est maintenant isolée et réutilisable.
  - **Testabilité** : La fonction peut être testée indépendamment du reste du code.
  - **Maintenabilité** : Les modifications futures de l'algorithme de détection seront plus faciles à implémenter.
- **Inconvénients** :
  - **Complexité accrue** : Le code est maintenant réparti sur plusieurs fonctions, ce qui peut rendre la compréhension initiale plus difficile.
  - **Gestion des dépendances** : La fonction dépend de bibliothèques externes (`librosa`, `scipy`), ce qui peut compliquer la configuration de l'environnement.

## Références
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Librosa Documentation](https://librosa.org/doc/latest/index.html)
- [Scipy Signal Processing](https://docs.scipy.org/doc/scipy/reference/signal.html)