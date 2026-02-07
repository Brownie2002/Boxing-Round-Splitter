# Index des Décisions Architecturales

Ce fichier sert d'index pour les décisions architecturales et les documents de conception. Il facilite la navigation et la compréhension de la structure du projet.

## ADR (Architecture Decision Records)

Les ADR sont des documents qui capturent les décisions architecturales majeures du projet. Ils sont stockés dans le répertoire `docs/adr` et suivent un format standardisé.

### Liste des ADR

1. **[ADR-0001 — Structure de Documentation Pyramidale](adr/0001-structure-documentation-pyramidale.md)**
   - **Statut**: Accepté
   - **Description**: Adoption d'une structure pyramidale pour la documentation.

2. **[ADR-0002 — Format des ADR](adr/0002-format-adr.md)**
   - **Statut**: Accepté
   - **Description**: Standardisation du format des décisions architecturales.

## Architecture et Design

Les documents d'architecture et de design décrivent la structure globale du projet, les modules, et les patterns de conception utilisés.

### Structure Globale

- **[Structure Globale du Projet](architecture/structure-globale.md)**: Description des modules principaux et de leurs responsabilités.

### Patterns de Conception

- **[Patterns de Conception](architecture/patterns-conception.md)**: Description des patterns utilisés dans le projet, comme le pattern Strategy et le pattern Factory.

## Documentation du Code

La documentation du code est intégrée directement dans le code source et décrit les détails d'implémentation, les APIs, et les commentaires techniques. Elle est générée automatiquement à partir des docstrings et des commentaires dans le code.

## Comment Utiliser Ce Document

- **Pour les nouvelles décisions**: Ajoutez un nouvel ADR dans le répertoire `docs/adr` en suivant le format standardisé.
- **Pour les mises à jour**: Modifiez les documents existants et mettez à jour les références si nécessaire.
- **Pour la navigation**: Utilisez les liens dans ce document pour accéder rapidement aux informations pertinentes.

## Références

- Voir [ADR-0001 — Structure de Documentation Pyramidale](adr/0001-structure-documentation-pyramidale.md) pour la structure de documentation.
- Voir [ADR-0002 — Format des ADR](adr/0002-format-adr.md) pour le format des décisions architecturales.
