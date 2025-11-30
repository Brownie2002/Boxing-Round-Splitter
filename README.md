# 🥊 Boxing Round Splitter 🥊

Welcome to the Boxing Round Splitter! 🎉 This Python script is designed to split boxing videos into individual rounds based on the sound of the boxing bell. 🎵 Whether you're a coach, analyst, or just a boxing fan, this tool will help you break down matches into manageable segments for analysis or review. 📊

## 🌟 Features

- **🎵 Automatic Round Detection**: Uses audio analysis to detect the boxing bell sound and identify the start of each round.
- **✂️ Video Splitting**: Splits the input video into individual rounds and saves them as separate files.
- **📅 Metadata Handling**: Extracts and uses video metadata to organize the output files.

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

3. **Output**: The script will create a directory with the name of the video's creation date and save each round as a separate MP4 file. 🎉

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

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📧 Contact

For any questions or feedback, please open an issue on GitHub or contact the maintainer at your.email@example.com. 📩

Let's make boxing analysis fun and easy! 🥊🎉