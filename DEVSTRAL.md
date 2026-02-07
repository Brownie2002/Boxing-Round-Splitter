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
