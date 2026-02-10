# Guide pour l'Humain (HUMAN.md)

Ce document fournit des lignes directrices concises pour vous, l'utilisateur humain, afin de travailler efficacement avec ce projet et en collaboration avec les agents IA. Il s'inspire des principes de l'agent, mais adapte le workflow à votre interaction.

---

## 🚀 Démarrage Rapide d'une Session

Lorsque vous commencez à travailler sur le projet :

1.  **Consultez `START_HERE.md` :** C'est votre point d'entrée. Il doit résumer l'état actuel du projet et les tâches prioritaires.
2.  **Identifiez la Tâche Active :** Regardez dans `docs/TODOS/`. Cherchez les fichiers `XX_nom_tache.md` (qui ne sont pas des `_STATUS.md`).
3.  **Lisez le Statut de la Tâche :** Pour la tâche choisie, lisez le fichier `docs/TODOS/XX_nom_tache_STATUS.md` associé. Cela vous donnera la progression et ce qu'il reste à faire.
4.  **Consultez les Références :** Si la tâche l'exige, référez-vous aux `docs/adr/` pour les décisions architecturales, `docs/` pour la documentation générale, ou `docs/design/` pour les détails de conception.

---

## 🛠️ Mon Flux de Travail pour une Session de Programmation

Voici une suggestion de flux de travail pour une session de développement :

1.  **Préparation (avant de coder) :**
    *   Faites un `git pull` pour être à jour.
    *   Lisez `START_HERE.md` et les fichiers `TODOS/XX_nom_tache.md` et `TODOS/XX_nom_tache_STATUS.md` pertinents.
    *   Si vous commencez une nouvelle tâche, créez son `XX_nom_tache.md` et `XX_nom_tache_STATUS.md` dans `docs/TODOS/`.

2.  **Codage et Tests :**
    *   Développez ou modifiez le code.
    *   Écrivez ou adaptez les tests unitaires et d'intégration. **Règle d'or :** Vos tests doivent toujours utiliser le code de production (`/src/`), jamais des copies.
    *   Vérifiez que tous les tests passent.

3.  **Documentation (pendant ou après) :**
    *   Mettez à jour les docstrings ou les commentaires si vous modifiez des fonctions/classes.
    *   Si une décision architecturale majeure est prise, rédigez un nouvel ADR dans `docs/adr/`.
    *   Si un design spécifique est nécessaire, documentez-le dans `docs/design/`.

4.  **Gestion des Commits :**
    *   Utilisez la convention [Conventional Commits](https://www.conventionalcommits.org/).
    *   Séparer les commits par type (feat, fix, docs, chore).
    *   **NE JAMAIS** réécrire l'historique (pas de `git rebase -i` ni `git commit --amend` sur des commits pushés).

5.  **Mise à Jour de la Progression :**
    *   Mettez à jour le fichier `docs/TODOS/XX_nom_tache_STATUS.md` avec la progression en pourcentage et les éléments cochés.
    *   Si un TODO est terminé, déplacez son fichier `XX_nom_tache.md` et `XX_nom_tache_STATUS.md` vers `/archive/TODOS/` et ajoutez une entrée dans `docs/TIMELINE.md`.

6.  **Fin de Session :**
    *   Créez un rapport de session concis dans `docs/reports/SESSION_YYYY-MM-DD_description.md` si pertinent.
    *   Vérifiez que tous les fichiers temporaires sont nettoyés.
    *   Faites un `git add` et `git commit` de vos changements.
    *   `git push` pour sauvegarder votre travail.

---

## 🤝 Conseils pour Travailler avec un Agent IA

La collaboration avec un agent IA requiert une approche spécifique pour maximiser l'efficacité et la clarté.

### 🚀 Démarrage d'une Session avec l'Agent (pour vous, l'humain, afin de guider l'agent)

Pour aider l'agent à se lancer rapidement et à se concentrer :

1.  **Indiquez clairement la tâche :** Donnez à l'agent l'objectif principal de la session. Référez-vous à un `XX_nom_tache.md` spécifique si c'est la tâche active.
2.  **Fournissez le Contexte Essentiel :**
    *   **Point de départ :** Demandez à l'agent de commencer par lire `START_HERE.md`.
    *   **Tâche en cours :** Indiquez-lui quel fichier `docs/TODOS/XX_nom_tache.md` et `docs/TODOS/XX_nom_tache_STATUS.md` sont pertinents pour la session.
    *   **Informations clés :** Si des fichiers de code ou de documentation spécifiques sont cruciaux pour la tâche, mentionnez-les explicitement pour que l'agent les lise (par exemple, "Lisez `src/core/split_rounds.py` et `docs/design/bell_detection.md`").
3.  **Encouragez la Concisions :** Rappelez à l'agent de privilégier les outils comme `glob`, `search_file_content` et de ne lire que les parties pertinentes des fichiers pour minimiser l'utilisation des tokens et rester focalisé.
    *   *Exemple de consigne :* "Agent, veuillez charger les tâches en cours depuis `docs/TODOS/` et prioriser la tâche `02_nouvelle_feature.md`. Limitez la lecture des fichiers non pertinents."

### 🏁 Fin de Session avec l'Agent (pour vous assurer d'une bonne clôture)

Avant de terminer la session avec l'agent, assurez-vous que les éléments suivants sont à jour pour une reprise fluide :

1.  **Statut de la Tâche à Jour :** Confirmez que le `docs/TODOS/XX_nom_tache_STATUS.md` de la tâche sur laquelle l'agent a travaillé est correctement mis à jour (progression, éléments cochés).
2.  **Rapports Créés :** Si l'agent a effectué des analyses ou généré des résultats, assurez-vous qu'un rapport de session (`docs/reports/SESSION_YYYY-MM-DD_description.md`) a été créé.
3.  **Timeline Mise à Jour :** Si une tâche a été complétée et archivée, ou si une nouvelle a été ajoutée, vérifiez que `docs/TIMELINE.md` reflète ces changements.
4.  **Nettoyage :** Demandez à l'agent de s'assurer qu'il n'y a pas de fichiers temporaires non nécessaires et que les modifications sont prêtes pour un `git commit` et `git push`.
    *   *Exemple de consigne :* "Agent, veuillez finaliser la session. Assurez-vous que `02_nouvelle_feature_STATUS.md` est à jour, qu'un rapport de session a été créé dans `docs/reports/`, et que le projet est prêt pour le commit."

---

## 📁 Structure des Fichiers Clé pour Vous

*   **`/` (Racine du Projet) :**
    *   `README.md` : Description générale du projet.
    *   `START_HERE.md` : Votre point d'entrée pour chaque session.
    *   `HUMAN.md` : Ce guide (pour vous !).
    *   `AGENT.md` : Guide pour les agents IA (pour comprendre comment ils opèrent).
*   **`/docs/` :**
    *   `adr/` : Décisions architecturales (ADRs).
    *   `design/` : Documents de conception spécifiques.
    *   `TODOS/` : Fiches de tâches actives (avec `XX_nom_tache.md` et `XX_nom_tache_STATUS.md`).
    *   `reports/` : Rapports de sessions, d'analyses.
    *   `TIMELINE.md` : Historique chronologique des TODOs.
    *   `INDEX.md` : Index de la documentation (à créer/maintenir si nécessaire).
*   **`/src/` :** Votre code source principal.
*   **`/archive/` :** Anciens TODOs, documents obsolètes.

---

En suivant ces lignes directrices, vous maintiendrez un projet bien organisé et faciliterez la collaboration, qu'elle soit humaine ou avec des agents IA.