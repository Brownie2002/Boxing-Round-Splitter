# Patterns de Conception

## Pattern Strategy

**Contexte**: 
Le projet nécessite plusieurs algorithmes de découpage vidéo, et il est important de pouvoir en ajouter de nouveaux sans modifier le code existant.

**Solution**: 
Utiliser le pattern Strategy pour encapsuler les algorithmes de découpage vidéo. Cela permet de facilement ajouter de nouveaux algorithmes et de les interchanger dynamiquement.

**Exemple**:
```python
class VideoSplitter:
    def __init__(self, strategy):
        self._strategy = strategy

    def split(self, video_path):
        return self._strategy.split(video_path)
```

**Conséquences**:
- **Positif**: 
  - Facilité d'extension avec de nouveaux algorithmes.
  - Réduction de la duplication de code.
- **Négatif**: 
  - Peut introduire une complexité supplémentaire pour les petits projets.

## Pattern Factory

**Contexte**: 
La création d'objets complexes, comme les stratégies de découpage vidéo, peut être centralisée pour faciliter la maintenance.

**Solution**: 
Utiliser le pattern Factory pour créer des instances de stratégies de découpage vidéo.

**Exemple**:
```python
class StrategyFactory:
    @staticmethod
    def create_strategy(strategy_type):
        if strategy_type == "fixed_duration":
            return FixedDurationStrategy()
        elif strategy_type == "round_based":
            return RoundBasedStrategy()
        else:
            raise ValueError("Unknown strategy type")
```

**Conséquences**:
- **Positif**: 
  - Centralisation de la création d'objets.
  - Facilité de maintenance.
- **Négatif**: 
  - Peut introduire une dépendance supplémentaire.

## Références

- Voir [ADR-0001 — Structure de Documentation Pyramidale](../adr/0001-structure-documentation-pyramidale.md) pour la structure de documentation.
- Voir [ADR-0002 — Format des ADR](../adr/0002-format-adr.md) pour le format des décisions architecturales.
