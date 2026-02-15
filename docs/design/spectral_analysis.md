# Spectral Bell Frequency Analysis Design

## Overview

The spectral bell frequency analyzer is a tool designed to identify the optimal frequency for detecting boxing bell sounds in audio recordings. This document explains the design choices, algorithms, and implementation details of the spectral analysis system.

## Problem Statement

Boxing bell sounds can vary in frequency due to:
- Different bell types and sizes
- Recording equipment variations
- Environmental factors (reverberation, noise)
- Audio compression artifacts

A fixed detection frequency (e.g., 2050Hz) may not work optimally for all recordings. The spectral analyzer solves this by automatically determining the best frequency for each specific audio file.

## System Architecture

```
┌───────────────────────────────────────────────────────┐
│                 Spectral Analysis System               │
├─────────────────┬─────────────────┬─────────────────┐
│  Audio Loading   │  Spectral       │  Frequency      │
│  & Preprocessing │  Analysis       │  Evaluation      │
└─────────────────┴─────────────────┴─────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────┐
│                    Recommendation Engine               │
├─────────────────┬─────────────────┬─────────────────┐
│  Scoring         │  Optimal        │  Report         │
│  Algorithm       │  Selection      │  Generation      │
└─────────────────┴─────────────────┴─────────────────┘
```

## Design Decisions

### 1. Wideband Spectral Analysis

**Decision**: Analyze a wide frequency band (1500-2500Hz) rather than testing discrete frequencies.

**Rationale**:
- Covers the typical range of boxing bells (1800-2200Hz)
- Identifies actual spectral peaks rather than arbitrary test frequencies
- More efficient than iterating through many discrete frequencies
- Captures harmonics and sidebands that may contain energy

**Implementation**:
```python
def analyze_spectral_response(audio_path, analysis_band=(1500, 2500), ...):
    # Apply wide bandpass filter
    low = analysis_band[0] / (sr / 2)
    high = analysis_band[1] / (sr / 2)
    b, a = butter(N=4, Wn=[low, high], btype='band')
    filtered_audio = filtfilt(b, a, y)
    
    # Compute power spectral density using Welch's method
    f, Pxx = welch(filtered_audio, fs=sr, nperseg=min(2048, len(filtered_audio)//2))
```

### 2. Peak Detection Algorithm

**Decision**: Use percentile-based thresholding (95th percentile) for peak detection.

**Rationale**:
- Adaptive to different audio levels
- Robust to background noise
- Avoids hard-coded thresholds that may fail on quiet/load recordings
- Automatically adjusts to signal dynamics

**Implementation**:
```python
peak_height = np.percentile(Pxx, 95)  # 95th percentile as threshold
spectral_peaks, _ = find_peaks(Pxx, height=peak_height)
```

### 3. Multi-Criteria Scoring System

**Decision**: Use weighted scoring combining power, events, and consistency.

**Rationale**:
- **Power alone** may select noise peaks
- **Events alone** may select frequencies with many false positives
- **Consistency alone** may fail on recordings with irregular bell patterns
- Weighted combination provides robust selection

**Scoring Weights**:
- Power: 40% (spectral energy)
- Events: 30% (number of detections)
- Consistency: 30% (timing regularity)

**Implementation**:
```python
total_score = (0.4 * power_score + 
                0.3 * event_score + 
                0.3 * consistency_score)
```

### 4. Human-Readable Timestamps

**Decision**: Format timestamps as HH:MM:SS.ss for media player compatibility.

**Rationale**:
- Easy navigation in VLC, MPV, and other media players
- Standard format understood by most video/audio software
- More intuitive than raw seconds
- Enables quick verification of detections

**Implementation**:
```python
def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 10000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
```

### 5. Modular Design

**Decision**: Separate analysis logic from user interface.

**Rationale**:
- `spectral_analyzer.py`: Core algorithms (reusable)
- `analyze_bell_frequency.py`: User interface (CLI)
- Enables integration with other tools
- Facilitates unit testing
- Clear separation of concerns

## Algorithms

### Spectral Analysis Pipeline

1. **Audio Loading**
   - Load WAV file using librosa
   - Support for various sample rates
   - Automatic normalization

2. **Wideband Filtering**
   - 4th-order Butterworth bandpass filter
   - Configurable frequency range (default: 1500-2500Hz)
   - Zero-phase filtering to preserve timing

3. **Power Spectral Density Estimation**
   - Welch's method for robust spectral estimation
   - Configurable segment size (default: 2048 samples)
   - 50% overlap between segments
   - Hanning window for reduced spectral leakage

4. **Peak Detection**
   - 95th percentile thresholding
   - Minimum peak distance enforcement
   - Peak sorting by power (descending)

5. **Frequency Evaluation**
   - Narrow bandpass filtering at each peak frequency
   - Amplitude envelope computation
   - Peak detection in filtered signal
   - Event grouping and consistency calculation

6. **Optimal Frequency Selection**
   - Weighted scoring for each candidate frequency
   - Selection of highest-scoring frequency
   - Fallback mechanisms for edge cases

### Event Grouping Algorithm

```python
def group_peaks_into_events(peak_times, max_gap=0.6, min_peaks=4):
    """
    Group peak times into bell ringing events.
    
    Parameters:
    - max_gap: Maximum time between peaks in same event (0.6s)
    - min_peaks: Minimum peaks per valid event (4)
    
    Returns:
    - List of events, where each event is a list of peak times
    """
```

**Rationale for Parameters**:
- `max_gap=0.6s`: Boxing bells typically ring 4-6 times per second
- `min_peaks=4`: Requires at least 4 consecutive rings to validate

### Consistency Scoring

```python
def calculate_event_consistency(events):
    """
    Calculate consistency score based on event regularity.
    
    Higher scores indicate more regular timing between events,
    which is characteristic of round bells in boxing.
    """
```

**Algorithm**:
1. Calculate time differences between event starts
2. Compute mean and standard deviation of differences
3. Score = 1 - (std_dev / mean) [normalized to 0-1 range]

## Implementation Details

### Core Module: `src/core/spectral_analyzer.py`

**Functions**:
- `generate_test_audio()`: Create synthetic test signals
- `group_peaks_into_events()`: Event grouping logic
- `calculate_event_consistency()`: Consistency scoring
- `evaluate_frequency()`: Frequency performance evaluation
- `analyze_spectral_response()`: Main analysis function
- `select_optimal_frequency()`: Optimal frequency selection
- `save_spectral_report()`: Report generation
- `format_timestamp()`: Timestamp formatting
- `generate_visualization()`: Graph generation

**Dependencies**:
- librosa (audio I/O)
- numpy (numerical operations)
- scipy.signal (DSP functions)
- matplotlib (visualization, optional)

### CLI Tool: `src/tools/analyze_bell_frequency.py`

**Features**:
- Homogeneous CLI with `split_rounds.py`
- Configurable analysis parameters
- JSON report generation
- Visualization generation
- Comprehensive logging
- Error handling

**Command Line Options**:
```
usage: analyze_bell_frequency.py [-h] [--output OUTPUT] [--band BAND BAND]
                                [--peaks PEAKS] [--visualize] [--viz-dir VIZ_DIR]
                                [--debug] audio_file
```

## Performance Considerations

### Computational Complexity

1. **Audio Loading**: O(N) where N = number of samples
2. **Filtering**: O(N) for each filter application
3. **PSD Estimation**: O(N log N) for FFT operations
4. **Peak Detection**: O(M) where M = number of frequency bins
5. **Frequency Evaluation**: O(K × N) where K = number of peaks

**Overall**: Dominated by filtering and PSD estimation - O(N log N)

### Memory Usage

- Audio data: O(N) samples
- Filtered audio: O(N)
- PSD arrays: O(M) where M ≈ N/2
- Peak data: O(K) where K << M

**Typical Values**:
- 10-minute audio at 44.1kHz: ~26MB
- PSD arrays: ~13MB
- Peak data: <1MB

### Optimization Opportunities

1. **Streaming Processing**: For very long recordings
2. **Parallel Evaluation**: Evaluate multiple frequencies simultaneously
3. **Caching**: Cache filtered audio for repeated analyses
4. **Downsampling**: For frequencies <10kHz, can downsample to reduce computation

## Validation and Testing

### Unit Tests

**Test Coverage** (7/7 tests):
- `test_generate_test_audio()`: Audio generation
- `test_group_peaks_into_events()`: Event grouping
- `test_calculate_event_consistency()`: Consistency scoring
- `test_evaluate_frequency()`: Frequency evaluation
- `test_analyze_spectral_response()`: Full pipeline
- `test_select_optimal_frequency()`: Selection logic
- `test_integration_with_real_audio()`: End-to-end test

### Test Data

**Synthetic Audio**:
- Generated with `generate_test_audio()`
- Bells at 1900Hz, 2050Hz, 2200Hz
- Timestamps at 2s, 5s, 8s
- Damped sine waves for realism

**Real Audio**:
- Manual verification with VLC
- Timestamp navigation
- Visual inspection of waveforms

## Usage Examples

### Basic Analysis
```bash
python src/tools/analyze_bell_frequency.py fight.wav
```

### Advanced Analysis
```bash
python src/tools/analyze_bell_frequency.py fight.wav \
    --output report.json \
    --band 1800 2200 \
    --peaks 5 \
    --visualize \
    --debug
```

### Integration with Main Tool
```bash
# First find optimal frequency
FREQ=$(python src/tools/analyze_bell_frequency.py fight.wav | grep "Recommended" | awk '{print $3}')

# Then use it in main analysis
python src/core/split_rounds.py fight.mp4 --target-freq $FREQ
```

## Limitations and Future Work

### Current Limitations

1. **Single Frequency Recommendation**: Currently selects one optimal frequency
2. **No Adaptive Thresholding**: Uses fixed percentile for peak detection
3. **No Machine Learning**: Purely signal-processing based
4. **WAV Only**: Best results with uncompressed WAV files

### Future Enhancements

1. **Multi-Frequency Detection**: Detect and use multiple frequencies simultaneously
2. **Adaptive Thresholding**: Dynamic thresholds based on signal characteristics
3. **Machine Learning**: Train model on labeled bell sounds
4. **Real-Time Processing**: Stream processing for live applications
5. **Batch Processing**: Analyze multiple files in one command
6. **GUI Interface**: Graphical user interface for non-technical users

## References

### Academic Papers
- Welch, P. D. (1967). "The use of fast Fourier transform for the estimation of power spectra: A method based on time averaging over short, modified periodograms."
- Oppenheim, A. V., & Schafer, R. W. (2009). Discrete-Time Signal Processing. Prentice Hall.

### Software Documentation
- [Librosa Documentation](https://librosa.org/doc/latest/index.html)
- [Scipy Signal Processing](https://docs.scipy.org/doc/scipy/reference/signal.html)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)

### Related ADRs
- [ADR-0003: Bell Detection Function](../adr/0003-bell-detection-function.md)
- [ADR-0004: Bell Detection Improvements](../adr/0004-bell-detection-improvements.md)

## Conclusion

The spectral bell frequency analyzer provides a robust, scientific approach to determining optimal detection frequencies for boxing bell sounds. By combining spectral analysis with multi-criteria scoring, it adapts to different recording conditions and bell characteristics, improving the accuracy and reliability of round detection in boxing videos.

The modular design enables easy integration with existing tools while maintaining flexibility for future enhancements. Comprehensive testing and validation ensure reliable performance across different audio scenarios.

**Version**: 1.0
**Last Updated**: 2026-02-15
**Status**: Production-Ready