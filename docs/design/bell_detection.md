# Bell Detection Design

## Overview

The `detect_bell_ringing` function is designed to detect bell ringing events in an audio file, typically used in the context of boxing videos to identify the start and end of rounds. This document explains the design choices and parameters used in the bell detection algorithm.

## Function Signature

```python
def detect_bell_ringing(audio_path, output_debug_file=None):
    """
    Detects bell ringing events in an audio file and returns their timestamps.

    Args:
        audio_path (str): Path to the audio file (WAV format).
        output_debug_file (str, optional): Path to a file where debug information will be written.

    Returns:
        list: A list of lists, where each sublist contains timestamps of a detected bell ringing event.
    """
```

## Parameters

### `TARGET_FREQ`
- **Description**: The target frequency for bell detection.
- **Value**: `2050` Hz
- **Rationale**: Boxing bells typically ring at around 2000 Hz. This frequency is chosen to isolate the bell sound from other noises in the audio.

### `BANDWIDTH`
- **Description**: The bandwidth around the target frequency for the bandpass filter.
- **Value**: `50` Hz
- **Rationale**: A bandwidth of 50 Hz on each side of the target frequency allows for slight variations in the bell's frequency while still filtering out most other sounds.

### `MIN_PEAK_HEIGHT`
- **Description**: The minimum height of a peak to be considered a bell ring.
- **Value**: `0.03`
- **Rationale**: This threshold is set to filter out background noise and only detect significant peaks that correspond to bell rings. Lowering this value can help detect weaker bell rings but may also increase false positives.

### `PEAKS_IN_ROW`
- **Description**: The minimum number of consecutive peaks required to validate a bell ringing event.
- **Value**: `4`
- **Rationale**: Boxing bells typically ring multiple times in quick succession. Requiring at least 4 consecutive peaks helps distinguish bell rings from other transient noises.

### `MAX_GAP`
- **Description**: The maximum time gap between consecutive peaks to be considered part of the same event.
- **Value**: `0.6` seconds
- **Rationale**: This value is chosen based on the typical ringing pattern of boxing bells, where individual rings are close together but distinct.

## Algorithm

### Step 1: Load Audio
The audio file is loaded using `librosa`, which provides a simple interface for reading audio files and extracting the audio data and sample rate.

### Step 2: Bandpass Filter
A bandpass filter is applied around the target frequency to isolate the bell sound. This is done using a Butterworth filter of order 4, which provides a good balance between roll-off steepness and computational efficiency.

### Step 3: Compute Amplitude Envelope
The amplitude envelope of the filtered audio is computed to highlight the peaks corresponding to bell rings.

### Step 4: Detect Peaks
Peaks in the amplitude envelope are detected using `scipy.signal.find_peaks`. The `height` parameter is set to `MIN_PEAK_HEIGHT` to filter out small peaks, and the `distance` parameter is set to ensure peaks are at least 100ms apart.

### Step 5: Convert Peak Indices to Time
The indices of the detected peaks are converted to timestamps in seconds by dividing by the sample rate.

### Step 6: Group Peaks into Events
Peaks are grouped into bell ringing events based on their temporal proximity. Peaks that are within `MAX_GAP` seconds of each other are considered part of the same event. An event is only valid if it contains at least `PEAKS_IN_ROW` peaks.

### Step 7: Write Debug Information
If an `output_debug_file` is provided, the detected events are written to this file in a human-readable format, with timestamps converted to `hh:mm:ss.ssss` for easy inspection.

## Output

The function returns a list of lists, where each sublist contains the timestamps (in seconds) of a detected bell ringing event. For example:

```python
[
    [123.456, 124.567, 125.678, 126.789],  # Event 1
    [345.678, 346.789, 347.890, 348.901]   # Event 2
]
```

## Debug File

The debug file, if generated, contains the detected events in a formatted manner:

```
Bell Ringing Detection Debug Info
========================================
Event 1: ['00:02:03.456', '00:02:04.567', '00:02:05.678', '00:02:06.789']
Event 2: ['00:05:45.678', '00:05:46.789', '00:05:47.890', '00:05:48.901']
========================================
```

## Performance Considerations

- **Computational Efficiency**: The algorithm is designed to be efficient, with a time complexity dominated by the bandpass filtering and peak detection steps.
- **Memory Usage**: The algorithm loads the entire audio file into memory, which may be a consideration for very long videos. However, this is typically not an issue for standard boxing videos.
- **Accuracy**: The accuracy of the detection depends heavily on the choice of parameters. Adjusting `MIN_PEAK_HEIGHT`, `PEAKS_IN_ROW`, and `MAX_GAP` can help fine-tune the detection for different types of videos.

## Future Improvements

- **Adaptive Thresholding**: Implement adaptive thresholding for `MIN_PEAK_HEIGHT` to better handle varying audio qualities.
- **Machine Learning**: Explore the use of machine learning models to improve detection accuracy, especially in noisy environments.
- **Real-time Processing**: Adapt the algorithm for real-time processing of audio streams.

## References

- [Librosa Documentation](https://librosa.org/doc/latest/index.html)
- [Scipy Signal Processing](https://docs.scipy.org/doc/scipy/reference/signal.html)
- [ADR-0003 — Bell Detection Function](../adr/0003-bell-detection-function.md)
- [ADR-0004 — Bell Detection Improvements](../adr/0004-bell-detection-improvements.md)