import librosa
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks, welch
from scipy import stats
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union

# Constantes configurables
DEFAULT_MIN_PEAK_HEIGHT = 0.03
DEFAULT_BANDWIDTH = 50
DEFAULT_MAX_GAP = 0.6
DEFAULT_MIN_PEAKS = 4
DEFAULT_SAMPLE_RATE = 44100

class SpectralAnalyzer:
    """
    Classe pour l'analyse spectrale et la détection de sons de cloche.

    Cette classe fournit des méthodes pour :
    - Analyser la réponse spectrale
    - Évaluer des fréquences spécifiques
    - Détecter et regrouper des événements
    """

    def __init__(self, min_peak_height: float = DEFAULT_MIN_PEAK_HEIGHT,
                 bandwidth: float = DEFAULT_BANDWIDTH,
                 max_gap: float = DEFAULT_MAX_GAP,
                 min_peaks: int = DEFAULT_MIN_PEAKS):
        """
        Initialise le SpectralAnalyzer avec des paramètres configurables.

        Args:
            min_peak_height: Seuil de hauteur minimale pour la détection de pics
            bandwidth: Bande passante autour de la fréquence cible (Hz)
            max_gap: Gap maximal entre pics pour un même événement (secondes)
            min_peaks: Nombre minimal de pics pour valider un événement
        """
        self.min_peak_height = min_peak_height
        self.bandwidth = bandwidth
        self.max_gap = max_gap
        self.min_peaks = min_peaks

    def _save_audio(self, output_path: str, audio: np.ndarray, sample_rate: int) -> None:
        """Sauvegarde l'audio dans un fichier WAV."""
        try:
            import soundfile as sf
            sf.write(output_path, audio, sample_rate)
        except ImportError:
            try:
                librosa.output.write_wav(output_path, audio, sample_rate)
            except AttributeError:
                from scipy.io.wavfile import write
                audio_int16 = (audio * 32767).astype(np.int16)
                write(output_path, sample_rate, audio_int16)

    def group_peaks_into_events(self, peak_times: np.ndarray) -> List[List[float]]:
        """
        Regroupe les temps de pics en événements de sonnerie de cloche.

        Args:
            peak_times: Tableau de temps de pics en secondes

        Returns:
            Liste d'événements, où chaque événement est une liste de temps de pics
        """
        if len(peak_times) == 0:
            return []

        valid_events = []
        current_group = [peak_times[0]]

        for t in peak_times[1:]:
            if t - current_group[-1] <= self.max_gap:
                current_group.append(t)
            else:
                if len(current_group) >= self.min_peaks:
                    valid_events.append(current_group)
                current_group = [t]

        # Vérifier le dernier groupe
        if len(current_group) >= self.min_peaks:
            valid_events.append(current_group)

        return valid_events

    def calculate_event_consistency(self, events: List[List[float]]) -> float:
        """
        Calcule le score de cohérence basé sur la régularité des événements.

        Args:
            events: Liste d'événements (chaque événement est une liste de temps de pics)

        Returns:
            Score de cohérence (0-1)
        """
        if len(events) < 2:
            return 0.0

        # Calculer le temps entre le premier pic de chaque événement
        event_starts = [event[0] for event in events]
        time_diffs = []

        for i in range(1, len(event_starts)):
            diff = event_starts[i] - event_starts[i-1]
            time_diffs.append(diff)

        if len(time_diffs) < 2:
            return 0.5  # Score neutre pour des données insuffisantes

        avg_diff = np.mean(time_diffs)
        std_diff = np.std(time_diffs)

        # Score plus élevé pour une temporisation plus cohérente
        if avg_diff > 0:
            return max(0, 1 - (std_diff / avg_diff))
        return 0.0

    def evaluate_frequency(self, audio_path: str, target_freq: float) -> Dict:
        """
        Évalue la performance de détection de cloche à une fréquence spécifique.

        Args:
            audio_path: Chemin vers le fichier audio
            target_freq: Fréquence à tester (Hz)

        Returns:
            Dictionnaire avec les résultats d'évaluation
        """
        # Charger l'audio
        y, sr = librosa.load(audio_path, sr=None)

        # Créer un filtre passe-bande
        low = (target_freq - self.bandwidth) / (sr / 2)
        high = (target_freq + self.bandwidth) / (sr / 2)
        b, a = butter(N=4, Wn=[low, high], btype='band')
        filtered = filtfilt(b, a, y)

        # Calculer l'enveloppe d'amplitude
        amplitude = np.abs(filtered)

        # Détecter les pics
        peaks, _ = find_peaks(amplitude, height=self.min_peak_height, distance=sr*0.1)
        peak_times = peaks / sr

        # Regrouper en événements
        events = self.group_peaks_into_events(peak_times)

        return {
            'frequency': target_freq,
            'events_detected': len(events),
            'event_timestamps': events,
            'amplitude_stats': {
                'mean': float(np.mean(amplitude)),
                'std': float(np.std(amplitude)),
                'max': float(np.max(amplitude))
            },
            'consistency_score': self.calculate_event_consistency(events)
        }

    def analyze_spectral_response(self, audio_path: str, analysis_band: Tuple[float, float] = (1500, 2500),
                                output_report: Optional[str] = None, n_peaks: int = 5) -> Dict:
        """
        Effectue une analyse spectrale pour identifier la fréquence optimale de détection de cloche.

        Args:
            audio_path: Chemin vers le fichier WAV
            analysis_band: Plage de fréquences à analyser (Hz)
            output_report: Chemin pour sauvegarder le rapport d'analyse (JSON)
            n_peaks: Nombre de pics spectraux à analyser

        Returns:
            Dictionnaire avec les résultats de l'analyse spectrale
        """
        # Valider les entrées
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Fichier audio non trouvé: {audio_path}")

        if analysis_band[0] >= analysis_band[1]:
            raise ValueError("La bande d'analyse doit avoir une fréquence de début inférieure à la fréquence de fin")

        # Charger l'audio
        y, sr = librosa.load(audio_path, sr=None)

        # Créer un filtre passe-bande large pour l'analyse
        low = analysis_band[0] / (sr / 2)
        high = analysis_band[1] / (sr / 2)
        b, a = butter(N=4, Wn=[low, high], btype='band')
        filtered_audio = filtfilt(b, a, y)

        # Calculer la densité spectrale de puissance
        f, Pxx = welch(filtered_audio, fs=sr, nperseg=min(2048, len(filtered_audio)//2))

        # Trouver les pics significatifs dans le spectre
        peak_height = np.percentile(Pxx, 95)  # 95ème percentile comme seuil
        spectral_peaks, _ = find_peaks(Pxx, height=peak_height)

        # Trier les pics par puissance (descendant) et limiter à n_peaks
        peak_data = [(f[peak_idx], Pxx[peak_idx]) for peak_idx in spectral_peaks]
        peak_data.sort(key=lambda x: x[1], reverse=True)
        top_peaks = peak_data[:n_peaks]

        # Analyser chaque pic significatif
        results = {
            'audio_file': os.path.basename(audio_path),
            'sample_rate': sr,
            'analysis_band': analysis_band,
            'analysis_date': datetime.now().isoformat(),
            'spectral_peaks': [],
            'recommended_frequency': None
        }

        for freq, power in top_peaks:
            # Ignorer si en dehors de notre plage cible
            if not (analysis_band[0] <= freq <= analysis_band[1]):
                continue

            # Évaluer cette fréquence
            freq_result = self.evaluate_frequency(audio_path, freq)
            freq_result.update({
                'spectral_power': float(power),
                'power_percentage': float(power / Pxx.max())
            })

            results['spectral_peaks'].append(freq_result)

        # Déterminer la recommandation
        if results['spectral_peaks']:
            results['recommended_frequency'] = self.select_optimal_frequency(results['spectral_peaks'])

        # Sauvegarder le rapport si demandé
        if output_report:
            self.save_spectral_report(results, output_report)

        return results

    def select_optimal_frequency(self, frequency_results: List[Dict]) -> float:
        """
        Sélectionne la fréquence optimale basée sur plusieurs critères.

        Args:
            frequency_results: Liste des résultats d'évaluation de fréquence

        Returns:
            Fréquence optimale en Hz
        """
        scored_freqs = []

        for result in frequency_results:
            # Normaliser les métriques (échelle 0-1)
            power_score = result['power_percentage']
            event_score = min(1.0, result['events_detected'] / 10.0)  # Limiter à 10 événements
            consistency_score = result['consistency_score']

            # Score pondéré (puissance 40%, événements 30%, cohérence 30%)
            total_score = (0.4 * power_score +
                          0.3 * event_score +
                          0.3 * consistency_score)

            scored_freqs.append({
                'frequency': result['frequency'],
                'score': total_score,
                'details': {
                    'power': power_score,
                    'events': event_score,
                    'consistency': consistency_score
                }
            })

        # Retourner la fréquence avec le score le plus élevé
        optimal = max(scored_freqs, key=lambda x: x['score'])
        return optimal['frequency']

    def save_spectral_report(self, results: Dict, output_path: str) -> None:
        """
        Sauvegarde les résultats de l'analyse spectrale avec un formatage supplémentaire.

        Args:
            results: Dictionnaire des résultats d'analyse
            output_path: Chemin pour sauvegarder le rapport
        """
        # Ajouter des détails de scoring pour chaque fréquence
        if results['spectral_peaks']:
            scoring = {}
            for peak in results['spectral_peaks']:
                freq = peak['frequency']
                power_score = peak['power_percentage']
                event_score = min(1.0, peak['events_detected'] / 10.0)
                consistency_score = peak['consistency_score']
                total_score = 0.4 * power_score + 0.3 * event_score + 0.3 * consistency_score

                scoring[str(freq)] = {
                    'total_score': total_score,
                    'power': power_score,
                    'events': event_score,
                    'consistency': consistency_score
                }

            results['scoring_details'] = scoring

        # Sauvegarder en JSON
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
