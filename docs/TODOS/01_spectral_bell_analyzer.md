# TODO 01 - Spectral Bell Frequency Analyzer

## 🎯 Objectif
Créer un outil d'analyse spectrale qui identifie la fréquence optimale de détection de cloche en analysant directement filtered_audio et amplitude.

## 📋 Tâches
- [ ] Créer `src/core/spectral_analyzer.py`
- [ ] Implémenter `analyze_spectral_response()` avec analyse spectrale
- [ ] Implémenter `evaluate_frequency()` pour évaluation par fréquence
- [ ] Créer `generate_test_audio()` pour générer des signaux synthétiques
- [ ] Créer test unitaire complet dans `tests/unit/test_spectral_analysis.py`
- [ ] Générer `temp_audio.wav` avec cloches à 1900Hz, 2050Hz, 2200Hz
- [ ] Documenter la méthodologie dans `docs/design/spectral_analysis.md`
- [ ] Intégrer avec CLI via `--spectral-analysis`

## 📚 Références
- `/docs/design/bell_detection.md` (design actuel)
- `/src/core/split_rounds.py` (fonction existante)
- `/tests/unit/test_bell_detection.py` (tests existants)

## 📊 Livrables
- Fichier `temp_audio.wav` à la racine du projet
- Test unitaire fonctionnel
- Module spectral_analyzer.py opérationnel
- Documentation technique
