# 🥊 Boxing Round Splitter 🥊

Welcome to the Boxing Round Splitter! 🎉 This **Python** project is designed to split boxing videos into individual rounds based on the sound of the boxing bell. 🎵 Whether you're a coach, analyst, or just a boxing fan, this tool will help you break down matches into manageable segments for analysis or review. 📊

## 🌟 Features

- **🎵 Automatic Round Detection**: Uses audio analysis to detect the boxing bell sound and identify the start of each round.
- **✂️ Video Splitting**: Splits the input video into individual rounds and saves them as separate files.
- **📅 Metadata Handling**: Extracts and uses video metadata to organize the output files.
- **📊 Debug Information**: Generates a debug file with timestamps of detected bell ringing events for easy inspection.
- **📚 Comprehensive Documentation**: Includes detailed design documentation and ADRs for better understanding and maintenance.

## 🚀 Installation

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yourusername/boxing-round-splitter.git
    cd boxing-round-splitter
    ```

2. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

## 📌 Usage

1. **Prepare Your Video**: Ensure your video file is in a supported format (e.g., MP4).

2. **Run the Script**:
    ```sh
    python split_rounds.py path/to/your/video.mp4
    ```

   **With Debug Option**:
    ```sh
    python split_rounds.py --debug path/to/your/video.mp4
    ```

3. **Output**: The script will create a directory with the name of the video's creation date and save each round as a separate MP4 file. 🎉

## 🧪 Running Tests

To run the unit tests, use the following commands:

### List all available tests:
```bash
python -m unittest discover -s tests/unit -p "test_*.py" -v
```

### Run all unit tests:
```bash
python -m unittest discover tests/unit
```

### Run a specific test:
```bash
python -m unittest tests.unit.test_bell_detection
```

## 📚 Documentation

### Design Documentation
- **Bell Detection Design**: Detailed explanation of the bell detection algorithm, parameters, and design choices. See [docs/design/bell_detection.md](docs/design/bell_detection.md).

### Architecture Decision Records (ADRs)
- **ADR-0001**: Structure de la documentation pyramidale. See [docs/adr/0001-structure-documentation-pyramidale.md](docs/adr/0001-structure-documentation-pyramidale.md).
- **ADR-0002**: Format des ADRs. See [docs/adr/0002-format-adr.md](docs/adr/0002-format-adr.md).
- **ADR-0003**: Bell Detection Function. See [docs/adr/0003-bell-detection-function.md](docs/adr/0003-bell-detection-function.md).
- **ADR-0004**: Bell Detection Improvements. See [docs/adr/0004-bell-detection-improvements.md](docs/adr/0004-bell-detection-improvements.md).

## 🔊 Bell Frequency Analyzer

The project includes a spectral analysis tool to determine the optimal bell frequency for detection.

### Usage

```bash
# Basic analysis
python src/tools/analyze_bell_frequency.py fight1.wav

# With debug logging
python src/tools/analyze_bell_frequency.py fight1.wav --debug

# Save results to JSON report
python src/tools/analyze_bell_frequency.py fight1.wav --output report.json

# Generate visualizations (requires matplotlib)
python src/tools/analyze_bell_frequency.py fight1.wav --visualize

# Custom frequency band and step size
python src/tools/analyze_bell_frequency.py fight1.wav --band 1800 2200 --step 50.0
```

### Features

- **Automatic frequency detection**: Analyzes spectral content to find optimal bell frequency
- **Detailed reporting**: JSON output with complete analysis metadata
- **Visualizations**: Generates PNG images of spectral analysis (with matplotlib)
- **Timestamp navigation**: Outputs VLC-compatible timestamps for easy verification
- **Customizable parameters**: Adjust analysis band, frequency step size, etc.

### Example Output

```
============================================================
Bell Frequency Analyzer
============================================================
Audio file: fight1.wav
Analysis band: 1500-2500 Hz
Peaks analyzed: 5
------------------------------------------------------------
Analyzing spectral content...

✓ Recommended frequency: 2196.4 Hz
✓ Detected 3 significant spectral peaks
✓ Visualization saved: visualizations/spectral_analysis_fight1.wav.png
✓ Report saved: report.json

Top frequencies:
1. 2196.4 Hz | Score: 0.43 | Events: 1 | Timestamp: 00:00:08.00
2. 2045.7 Hz | Score: 0.42 | Events: 1 | Timestamp: 00:00:05.00
3. 1894.9 Hz | Score: 0.41 | Events: 1 | Timestamp: 00:00:02.00

Usage suggestion:
  python src/core/split_rounds.py fight1.mp4 --target-freq 2196
  vlc fight1.wav --start-time=00:00:08.00
============================================================
```

### JSON Report Structure

The tool generates detailed JSON reports with:
- Audio metadata and analysis parameters
- Complete spectral peak analysis
- Event timestamps and amplitudes
- Scoring breakdown (power, events, consistency)

### Visualizations

When using `--visualize`, three plots are generated:
1. Full audio waveform
2. Spectral peaks overlay
3. Zoom on detected events

## 📚 Functions

### `get_video_metadata(video_path)`

**Description**: Extracts metadata from the video file, including the creation date.

**Parameters**:
- `video_path` (str): Path to the video file.

**Returns**:
- `str`: The creation date of the video in the format `YYYY-MM-DD`.

**Example**:
```python
creation_date = get_video_metadata("path/to/video.mp4")
print(f"Creation Date: {creation_date}")
```

### `detect_bell_ringing(audio_path, output_debug_file=None)`

**Description**: Detects bell ringing events in an audio file and returns their timestamps.

**Parameters**:
- `audio_path` (str): Path to the audio file (WAV format).
- `output_debug_file` (str, optional): Path to a file where debug information will be written.

**Returns**:
- `list`: A list of lists, where each sublist contains timestamps of a detected bell ringing event.

**Example**:
```python
valid_events = detect_bell_ringing("test_audio.wav", "bell_detection_debug.txt")
print(f"Detected events: {valid_events}")
```

### `split_rounds(video_path)`

**Description**: Splits the video into individual rounds based on the boxing bell sound.

**Parameters**:
- `video_path` (str): Path to the video file.

**Returns**:
- `None`: Saves the individual rounds as separate files in a directory named after the video's creation date.

**Example**:
```python
split_rounds("path/to/video.mp4")
```

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. 🎉


Let's make boxing analysis fun and easy! 🥊🎉