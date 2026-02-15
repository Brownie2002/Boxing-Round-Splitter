import librosa
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks, welch
from scipy import stats
import json
import os
import sys
from datetime import datetime

# Default peak height threshold (same as in split_rounds.py)
MIN_PEAK_HEIGHT = 0.03

def generate_test_audio(output_path, sample_rate=44100, duration=10.0, 
                       bell_frequencies=[1900, 2050, 2200], 
                       bell_times=[2.0, 5.0, 8.0]):
    """
    Generate synthetic audio with bell sounds at specified frequencies and times.
    
    Args:
        output_path: Path to save WAV file
        sample_rate: Sample rate in Hz
        duration: Total duration in seconds
        bell_frequencies: List of frequencies for each bell
        bell_times: List of times (in seconds) when bells ring
    """
    # Create silent audio
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = np.zeros_like(t)
    
    # Add bell sounds at specified times and frequencies
    for freq, bell_time in zip(bell_frequencies, bell_times):
        # Create a short bell sound (damped sine wave)
        bell_duration = 0.5  # seconds
        bell_t = np.linspace(0, bell_duration, int(sample_rate * bell_duration))
        
        # Damped sine wave (more realistic bell sound)
        decay = np.exp(-bell_t * 5)  # Exponential decay
        bell_sound = 0.5 * decay * np.sin(2 * np.pi * freq * bell_t)
        
        # Find position in main audio
        start_idx = int(bell_time * sample_rate)
        end_idx = start_idx + len(bell_sound)
        
        # Add to main audio (with bounds checking)
        if end_idx <= len(audio):
            audio[start_idx:end_idx] += bell_sound
    
    # Normalize to prevent clipping
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    # Save as WAV file (librosa 0.10+ API)
    try:
        import soundfile as sf
        sf.write(output_path, audio, sample_rate)
    except ImportError:
        # Fallback for older librosa versions
        try:
            librosa.output.write_wav(output_path, audio, sample_rate)
        except AttributeError:
            # Use scipy as last resort
            from scipy.io.wavfile import write
            # Convert to 16-bit integers
            audio_int16 = (audio * 32767).astype(np.int16)
            write(output_path, sample_rate, audio_int16)
    return audio

def group_peaks_into_events(peak_times, max_gap=0.6, min_peaks=4):
    """
    Group peak times into bell ringing events.
    
    Args:
        peak_times: Array of peak times in seconds
        max_gap: Maximum gap between peaks to be considered same event
        min_peaks: Minimum number of peaks to validate an event
    
    Returns:
        List of events, where each event is a list of peak times
    """
    if len(peak_times) == 0:
        return []
    
    valid_events = []
    current_group = [peak_times[0]]
    
    for t in peak_times[1:]:
        if t - current_group[-1] <= max_gap:
            current_group.append(t)
        else:
            if len(current_group) >= min_peaks:
                valid_events.append(current_group)
            current_group = [t]
    
    # Check the last group
    if len(current_group) >= min_peaks:
        valid_events.append(current_group)
    
    return valid_events

def calculate_event_consistency(events):
    """
    Calculate consistency score based on event regularity.
    
    Args:
        events: List of events (each event is list of peak times)
    
    Returns:
        float: Consistency score (0-1)
    """
    if len(events) < 2:
        return 0.0
    
    # Calculate time between first peak of each event
    event_starts = [event[0] for event in events]
    time_diffs = []
    
    for i in range(1, len(event_starts)):
        diff = event_starts[i] - event_starts[i-1]
        time_diffs.append(diff)
    
    if len(time_diffs) < 2:
        return 0.5  # Neutral score for insufficient data
    
    avg_diff = np.mean(time_diffs)
    std_diff = np.std(time_diffs)
    
    # Higher score for more consistent timing
    if avg_diff > 0:
        return max(0, 1 - (std_diff / avg_diff))
    else:
        return 0.0

def evaluate_frequency(audio_path, target_freq, bandwidth=50, min_peaks=4):
    """
    Evaluate bell detection performance at specific frequency.
    
    Args:
        audio_path: Path to audio file
        target_freq: Frequency to test (Hz)
        bandwidth: Bandwidth around target frequency (Hz)
        min_peaks: Minimum peaks per event
    
    Returns:
        dict: Evaluation results
    """
    # Load audio
    y, sr = librosa.load(audio_path, sr=None)
    
    # Create bandpass filter
    low = (target_freq - bandwidth) / (sr / 2)
    high = (target_freq + bandwidth) / (sr / 2)
    b, a = butter(N=4, Wn=[low, high], btype='band')
    filtered = filtfilt(b, a, y)
    
    # Compute amplitude envelope
    amplitude = np.abs(filtered)
    
    # Detect peaks
    peaks, _ = find_peaks(amplitude, height=MIN_PEAK_HEIGHT, distance=sr*0.1)
    peak_times = peaks / sr
    
    # Group into events
    events = group_peaks_into_events(peak_times, min_peaks=min_peaks)
    
    return {
        'frequency': target_freq,
        'events_detected': len(events),
        'event_timestamps': events,
        'amplitude_stats': {
            'mean': float(np.mean(amplitude)),
            'std': float(np.std(amplitude)),
            'max': float(np.max(amplitude))
        },
        'consistency_score': calculate_event_consistency(events)
    }

def analyze_spectral_response(audio_path, analysis_band=(1500, 2500), 
                             output_report=None, n_peaks=5):
    """
    Perform spectral analysis to identify optimal bell detection frequency.
    
    Args:
        audio_path: Path to WAV file
        analysis_band: Frequency range to analyze (Hz)
        output_report: Path to save analysis report (JSON)
        n_peaks: Number of spectral peaks to analyze
    
    Returns:
        dict: Spectral analysis results
    """
    # Load audio
    y, sr = librosa.load(audio_path, sr=None)
    
    # Create wide bandpass filter for analysis
    low = analysis_band[0] / (sr / 2)
    high = analysis_band[1] / (sr / 2)
    b, a = butter(N=4, Wn=[low, high], btype='band')
    filtered_audio = filtfilt(b, a, y)
    
    # Compute power spectral density
    f, Pxx = welch(filtered_audio, fs=sr, nperseg=min(2048, len(filtered_audio)//2))
    
    # Find significant peaks in the spectrum
    peak_height = np.percentile(Pxx, 95)  # 95th percentile as threshold
    spectral_peaks, _ = find_peaks(Pxx, height=peak_height)
    
    # Sort peaks by power (descending) and limit to n_peaks
    peak_data = [(f[peak_idx], Pxx[peak_idx]) for peak_idx in spectral_peaks]
    peak_data.sort(key=lambda x: x[1], reverse=True)
    top_peaks = peak_data[:n_peaks]
    
    # Analyze each significant peak
    results = {
        'audio_file': os.path.basename(audio_path),
        'sample_rate': sr,
        'analysis_band': analysis_band,
        'analysis_date': datetime.now().isoformat(),
        'spectral_peaks': [],
        'recommended_frequency': None
    }
    
    for freq, power in top_peaks:
        # Skip if outside our target range
        if not (analysis_band[0] <= freq <= analysis_band[1]):
            continue
        
        # Evaluate this frequency
        freq_result = evaluate_frequency(audio_path, freq)
        freq_result.update({
            'spectral_power': float(power),
            'power_percentage': float(power / Pxx.max())
        })
        
        results['spectral_peaks'].append(freq_result)
    
    # Determine recommendation
    if results['spectral_peaks']:
        results['recommended_frequency'] = select_optimal_frequency(results['spectral_peaks'])
    
    # Save report if requested
    if output_report:
        with open(output_report, 'w') as f:
            json.dump(results, f, indent=2)
    
    return results

def select_optimal_frequency(frequency_results):
    """
    Select optimal frequency based on multiple criteria.
    
    Args:
        frequency_results: List of frequency evaluation results
    
    Returns:
        float: Optimal frequency in Hz
    """
    scored_freqs = []
    
    for result in frequency_results:
        # Normalize metrics (0-1 scale)
        power_score = result['power_percentage']
        event_score = min(1.0, result['events_detected'] / 10.0)  # Cap at 10 events
        consistency_score = result['consistency_score']
        
        # Weighted score (power 40%, events 30%, consistency 30%)
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
    
    # Return frequency with highest score
    optimal = max(scored_freqs, key=lambda x: x['score'])
    return optimal['frequency']

def save_spectral_report(results, output_path):
    """
    Save spectral analysis results with additional formatting.
    
    Args:
        results: Analysis results dict
        output_path: Path to save report
    """
    # Add scoring details for each frequency
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
    
    # Save as JSON
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    # Generate test audio if run directly
    print("Generating test audio file...")
    generate_test_audio("temp_audio.wav")
    print("Test audio generated: temp_audio.wav")
    
    # Perform spectral analysis
    print("Performing spectral analysis...")
    results = analyze_spectral_response("temp_audio.wav", output_report="spectral_analysis.json")
    print(f"Analysis complete. Recommended frequency: {results['recommended_frequency']:.1f}Hz")
    print(f"Full report saved to: spectral_analysis.json")