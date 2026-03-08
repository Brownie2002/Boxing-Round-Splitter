# ADR-0006 — Éviter les Variables Globales

## Statut

Accepté

## Contexte

Dans le développement initial du projet, des variables globales ont été utilisées pour configurer les paramètres de détection de cloche et d'autres fonctionnalités. Cette approche présente plusieurs problèmes :

1. **Difficulté de test** : Les variables globales rendent les tests unitaires plus difficiles car elles créent des dépendances implicites entre les tests.
2. **Maintenabilité** : Les variables globales rendent le code plus difficile à comprendre et à maintenir, car leur état peut être modifié n'importe où dans le code.
3. **Flexibilité** : Les variables globales limitent la flexibilité du code, car elles ne peuvent pas être facilement modifiées pour différents scénarios d'utilisation.

## Décision

Nous avons décidé d'éliminer l'utilisation des variables globales dans le code et de les remplacer par des paramètres explicites passés aux fonctions ou encapsulés dans des classes.

## Conséquences

### Positives

1. **Meilleure testabilité** : Le code devient plus facile à tester car les dépendances sont explicites et peuvent être facilement mockées.
2. **Meilleure maintenabilité** : Le code devient plus facile à comprendre et à maintenir, car l'état est explicitement passé entre les fonctions.
3. **Flexibilité accrue** : Le code devient plus flexible, car les paramètres peuvent être facilement modifiés pour différents scénarios d'utilisation.

### Négatives

1. **Plus de paramètres** : Les fonctions peuvent nécessiter plus de paramètres, ce qui peut rendre les appels de fonction plus longs et plus complexes.
2. **Complexité accrue** : L'encapsulation de l'état dans des classes peut introduire une complexité supplémentaire pour les petits projets.

## Implémentation

### Avant

```python
# Variables globales
ROUND_TIME = 120
TARGET_FREQ = 2080
BANDWIDTH = 50

def detect_bell_ringing(audio_path):
    # Utilise les variables globales
    low = (TARGET_FREQ - BANDWIDTH) / (sr / 2)
    high = (TARGET_FREQ + BANDWIDTH) / (sr / 2)
    # ...
```

### Après

```python
def detect_bell_ringing(audio_path, target_freq=2080, bandwidth=50):
    # Utilise les paramètres explicites
    low = (target_freq - bandwidth) / (sr / 2)
    high = (target_freq + bandwidth) / (sr / 2)
    # ...
```

## Références

- [ADR-0001 — Structure de Documentation Pyramidale](0001-structure-documentation-pyramidale.md)
- [ADR-0002 — Format des ADR](0002-format-adr.md)
- [Patterns de Conception — Éviter les Variables Globales](../architecture/patterns-conception.md#éviter-les-variables-globales)
