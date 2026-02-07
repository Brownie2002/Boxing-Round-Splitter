# Documentation Pyramidale

Ce document décrit une approche pyramidale pour organiser la documentation technique, optimisant la clarté et la navigation entre les niveaux d'abstraction.

## Niveaux de Documentation

### Niveau 1: ADR (Architecture Decision Records)
Décisions architecturales majeures impactant le projet.

### Niveau 2: Architecture et Design
Structure globale, patterns et choix de conception.

### Niveau 3: Documentation du Code
Détails d'implémentation, APIs et commentaires techniques.

---

## Règles de Documentation

- **Lire README.md en premier** : Commencez par lire le README.md pour comprendre le projet.
- **ADRs comme source de vérité** : Toutes les décisions architecturales doivent être documentées dans les ADRs.
- **Ne pas inventer d'architecture non documentée** : Évitez les suppositions non documentées. Clarifiez ou documentez avant l'implémentation.

## Function Documentation Rules
- Function behavior is documented in docstrings
- Module-level rules are documented at top of file
- No deep logic explained outside code
- If documentation needs to be more explicit than just the minimum docstring, it will be placed in `docs/design/name_of_developed_doc.md` and a link will be added in the docstring. Example: "// See docs/design/identity-normalization.md"

---

## Structure des ADR

Chaque ADR suit ce format :
- **Titre** : `# ADR-XXXX — [Titre de la décision]`
- **Statut** : `Accepté | Rejeté | Supersédé`
- **Contexte** : Explication du problème ou de la nécessité.
- **Décision** : Solution choisie.
- **Conséquences** : Impact (avantages et inconvénients).

---

## Maintenance

- **Ajouter un ADR** : Créez un fichier dans `docs/adr/` avec le format `XXXX-nom-court.md`.
- **Mettre à jour** : Modifiez les fichiers existants et assurez-vous que les références sont à jour.

---

## Conclusion

Cette structure pyramidale maintient une documentation claire et organisée, facilitant la navigation et optimisant l'utilisation des ressources.

## Règles de Commit

- **Ajout des fichiers** : Avant de faire un commit, s'assurer d'ajouter (`git add`) tous les fichiers modifiés ou créés.
- **Résumé du commit** : Fournir un résumé clair des changements et des fichiers concernés.
- **Message de commit** : Suivre la spécification [Conventional Commits](https://www.conventionalcommits.org/) pour structurer les messages. Exemples :
  - `feat: ajouter une nouvelle fonctionnalité`.
  - `fix: corriger un bug`.
  - `docs: mettre à jour la documentation`.
- **Pas de réécriture de l'historique** : Ne jamais utiliser `git rebase`, `git commit --amend`, ou toute autre opération qui réécrit l'historique Git.

## Règles de Todo

- **Déplacer les TODOs terminés** : Lorsque qu'un TODO est marqué comme terminé (avec un `x`), le déplacer dans la catégorie "Completed" et associer le commit correspondant si possible.
- **Associer les commits** : Pour chaque TODO terminé, ajouter un lien vers le commit correspondant pour faciliter le suivi des changements.
