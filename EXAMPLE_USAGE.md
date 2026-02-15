# Example Usage - Bell Frequency Analyzer

This document shows how to use the spectral bell frequency analyzer tool.

## Basic Usage

```bash
# Analyze a WAV file and get recommended frequency
python src/tools/analyze_bell_frequency.py fight1.wav

# With debug logging
python src/tools/analyze_bell_frequency.py fight1.wav --debug

# Save results to JSON report
python src/tools/analyze_bell_frequency.py fight1.wav --output report.json

# Generate visualizations (requires matplotlib)
python src/tools/analyze_bell_frequency.py fight1.wav --visualize

# Custom frequency band and number of peaks
python src/tools/analyze_bell_frequency.py fight1.wav --band 1800 2200 --peaks 3

# All options combined
python src/tools/analyze_bell_frequency.py fight1.wav \
    --output detailed_report.json \
    --band 1800 2200 \
    --peaks 5 \
    --visualize \
    --viz-dir my_visualizations
```

## Example Output

```
============================================================
Bell Frequency Analyzer
============================================================
Audio file: temp_audio.wav
Analysis band: 1500-2500 Hz
Peaks to analyze: 5
------------------------------------------------------------
Analyzing spectral content...

Analysis complete!
Recommended frequency: 2196.4 Hz

Detected 3 significant spectral peaks:
----------------------------------------------------------------------------
✓ 1. 2196.4 Hz | Score: 0.43 | Events: 1 | Power: 1.00 | Consistency: 0.00
    Event 1: 00:00:08.00 | Amplitude: 0.816
  2. 2045.7 Hz | Score: 0.42 | Events: 1 | Power: 0.99 | Consistency: 0.00
    Event 1: 00:00:05.00 | Amplitude: 0.815
  3. 1894.9 Hz | Score: 0.41 | Events: 1 | Power: 0.96 | Consistency: 0.00
    Event 1: 00:00:02.00 | Amplitude: 0.815
----------------------------------------------------------------------------

Scoring breakdown (weighted):
  Power: 40% - Spectral energy at frequency
  Events: 30% - Number of bell events detected
  Consistency: 30% - Regularity of event timing

✓ Visualization saved to: visualizations/spectral_analysis_temp_audio.wav.png
✓ Detailed report saved to: report.json

Suggested usage:
  For future analysis, use --target-freq 2196
  Open in VLC: vlc temp_audio.wav --start-time=<timestamp>
============================================================
```

## Understanding the Output

### Timestamps Format
Timestamps are displayed in `HH:MM:SS.ss` format for easy navigation in media players:
- `00:00:02.00` = 2 seconds into the audio
- `00:00:05.00` = 5 seconds into the audio
- `00:00:08.00` = 8 seconds into the audio

You can open the audio file in VLC and jump to these exact timestamps:
```bash
vlc temp_audio.wav --start-time=00:00:08.00
```

### Scoring System
Each frequency is scored based on three criteria:
1. **Power (40%)**: Spectral energy at the frequency
2. **Events (30%)**: Number of bell events detected
3. **Consistency (30%)**: Regularity of event timing

The frequency with the highest weighted score is recommended.

### Amplitude Values
Amplitude values (0.0 to 1.0) indicate the strength of the detected bell sound:
- `0.816` = Strong bell detection
- `0.500` = Moderate detection
- `0.200` = Weak detection

## JSON Report Structure

The JSON report contains detailed information about the analysis:

```json
{
  "audio_file": "temp_audio.wav",
  "sample_rate": 44100,
  "analysis_band": [1500, 2500],
  "analysis_date": "2026-02-15T15:34:16.633824",
  "spectral_peaks": [
    {
      "frequency": 2196.38671875,
      "events_detected": 1,
      "event_timestamps": [[8.009433106575964, 8.109433106575963, ...]],
      "amplitude_stats": {"mean": 0.0095, "std": 0.0553, "max": 0.8162},
      "consistency_score": 0.0,
      "spectral_power": 9.116284289827778e-05,
      "power_percentage": 1.0
    },
    ...
  ],
  "recommended_frequency": 2196.38671875,
  "analysis_metadata": {
    "timestamp": "2026-02-15T15:34:20.302260",
    "command": "src/tools/analyze_bell_frequency.py temp_audio.wav --output report.json --visualize",
    "analysis_parameters": {
      "band": [1500, 2500],
      "peaks": 5,
      "visualization": "visualizations/spectral_analysis_temp_audio.wav.png"
    }
  }
}
```

## Visualizations

When using the `--visualize` option, the tool generates a PNG image with three plots:

1. **Full Audio Waveform**: Complete audio signal
2. **Spectral Peaks Overlay**: Detected bell events marked on the waveform
3. **Zoom on Detected Events**: Detailed view of each bell detection

The visualization helps you:
- See where bells were detected in the audio
- Compare different frequencies' performance
- Verify the accuracy of detections

## Practical Usage

1. **Find optimal frequency** for a new boxing video:
   ```bash
   python src/tools/analyze_bell_frequency.py new_fight.wav --output report.json
   ```

2. **Use the recommended frequency** in your main analysis:
   ```bash
   python src/core/split_rounds.py new_fight.mp4 --target-freq 2196
   ```

3. **Verify detections** by opening timestamps in VLC:
   ```bash
   vlc new_fight.wav --start-time=00:00:08.00
   ```

4. **Compare different frequency bands** if needed:
   ```bash
   python src/tools/analyze_bell_frequency.py fight1.wav --band 1800 2200
   python src/tools/analyze_bell_frequency.py fight1.wav --band 1900 2100
   ```

## Requirements

For full functionality including visualizations:
```bash
pip install matplotlib
```

The tool will work without matplotlib, but visualizations will be skipped.

## Notes

- Works best with WAV files (16-bit PCM recommended)
- Analysis band 1500-2500Hz covers typical boxing bell frequencies
- Higher `--peaks` values may detect more frequencies but increase processing time
- Use `--debug` for troubleshooting and detailed logging