import librosa
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
from datetime import timedelta
import subprocess
import os
import sys
import json
from datetime import datetime
import logging
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Split boxing videos into individual rounds based on bell sounds.')
parser.add_argument('--debug', action='store_true', help='Enable debug logging')
parser.add_argument('video_files', nargs='+', help='Paths to the video files to process')
args = parser.parse_args()

# Configure logging
log_level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(level=log_level,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create a temp directory if it doesn't exist
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

TEMP_WAV = os.path.join(TEMP_DIR, "temp_audio.wav")
TEMP_VIDEO_LIST = os.path.join(TEMP_DIR, "temp_video_list.txt")
TARGET_FREQ = 2050  # Hz
BANDWIDTH = 50  # Hz on each side
MIN_PEAK_HEIGHT = 0.03  # adjust based on recording amplitude
PEAKS_IN_ROW = 4
MAX_GAP = .6  # seconds between consecutive beeps
ROUND_TIME = 120 # seconds of the round


def detect_bell_ringing(audio_path, output_debug_file=None):
    """
    Detects bell ringing events in an audio file and returns their timestamps.

    Further details in /docs/design/bell_detection.md

    Args:
        audio_path (str): Path to the audio file (WAV format).
        output_debug_file (str, optional): Path to a file where debug information will be written.

    Returns:
        list: A list of lists, where each sublist contains timestamps of a detected bell ringing event.
    """
    # Load the audio with librosa
    y, sr = librosa.load(audio_path, sr=None)

    # Create a bandpass filter around TARGET_FREQ
    low = (TARGET_FREQ - BANDWIDTH) / (sr / 2)
    high = (TARGET_FREQ + BANDWIDTH) / (sr / 2)
    b, a = butter(N=4, Wn=[low, high], btype='band')
    filtered_audio = filtfilt(b, a, y)

    # Compute amplitude envelope
    amplitude = np.abs(filtered_audio)

    # Detect peaks
    peaks, properties = find_peaks(amplitude, height=MIN_PEAK_HEIGHT, distance=sr*0.1)

    # Convert peak indices to time in seconds
    peak_times = peaks / sr

    # Group peaks into bell ringing events
    valid_events = []
    current_group = [peak_times[0]]

    for t in peak_times[1:]:
        if t - current_group[-1] <= MAX_GAP:
            current_group.append(t)
        else:
            if len(current_group) >= PEAKS_IN_ROW:
                valid_events.append(current_group)
            current_group = [t]

    # Check the last group
    if len(current_group) >= PEAKS_IN_ROW:
        valid_events.append(current_group)

    # Write debug information if requested
    if output_debug_file:
        with open(output_debug_file, 'w') as f:
            f.write("Bell Ringing Detection Debug Info\n")
            f.write("=" * 40 + "\n")
            for i, group in enumerate(valid_events):
                # Convert timestamps to hh:mm:ss.ssss format
                formatted_times = [f"{int(t // 3600):02d}:{int((t % 3600) // 60):02d}:{int(t % 60):02d}.{int((t % 1) * 1000):03d}" for t in group]
                f.write(f"Event {i+1}: {formatted_times}\n")
            f.write("=" * 40 + "\n")

    return valid_events

def get_video_metadata(video_path):
    try:
        # Run FFprobe to get video metadata in JSON format
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_format',
            '-print_format', 'json',
            video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        metadata = json.loads(result.stdout)

        # Extract the creation date if available
        creation_date = metadata['format'].get('tags', {}).get('creation_time', 'Not available')
        if creation_date != 'Not available':
            # Parse the creation date and format it to year, month, day
            date_obj = datetime.strptime(creation_date, '%Y-%m-%dT%H:%M:%S.%fZ')
            formatted_date = date_obj.strftime('%Y-%m-%d')
            return formatted_date
        else:
            return creation_date
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    # Get video files from command line arguments
    video_files = args.video_files

    creation_date = get_video_metadata(video_files[0])
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "logo.png")
    logger.info(f"Creation Date: {creation_date}")

    # Create temp_video_list.txt with absolute paths
    with open(TEMP_VIDEO_LIST, "w") as f:
        for video in video_files:
            # Convert relative paths to absolute paths
            abs_video_path = os.path.abspath(video)
            f.write(f"file '{abs_video_path}'\n")

    # Step 1: Extract the audio from the .lrv video using ffmpeg
    logger.info("Extracting audio with ffmpeg to %s", TEMP_WAV)
    ffmpeg_cmd = [
        "ffmpeg", "-v", "debug", "-y",  "-f", "concat", "-safe", "0",
        "-i", TEMP_VIDEO_LIST, "-vn",      # no video
        "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1", TEMP_WAV
    ]
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    logger.debug("FFmpeg stdout: %s", result.stdout)
    logger.debug("FFmpeg stderr: %s", result.stderr)

    # Step 2: Detect bell ringing events
    logger.info("Detecting bell ringing events...")
    bell_ringing_file = os.path.join(TEMP_DIR, "bell_ringing_debug.txt")
    valid_events = detect_bell_ringing(TEMP_WAV, bell_ringing_file)
    logger.info("Debug information written to %s", bell_ringing_file)

    # Output formatted results

    prev_time = None

    output_dir = f"{creation_date}-boxing"
    os.makedirs(output_dir, exist_ok=True)
    round = 0

    for i, group in enumerate(valid_events):
        start_time = group[0] - 0.5
        td = timedelta(seconds=start_time)
        hh_mm_ss = str(td).split(".")[0]

        # Look ahead for the next group
        if i + 1 < len(valid_events):
            next_start = valid_events[i + 1][0]
            delta_sec = next_start - start_time + 1
            delta_td = timedelta(seconds=delta_sec)
            delta_str = str(delta_td).split(".")[0].rjust(8, "0")

            # Check if delta is about 2 minutes +- 2 seconds
            if ROUND_TIME - 2 <= delta_sec <= ROUND_TIME + 2:
                # Output file name
                round = round + 1
                output_file = os.path.join(output_dir, f"{creation_date}_round_{round:02d}.mp4")

                cmd = [
                    "nice", "-n", "10",
                    "ffmpeg", "-y",
                    "-ss", f"{max(0, start_time):.3f}",
                    "-t", f"{delta_sec:.3f}",
                    "-f", "concat", "-safe", "0",
                    "-i", TEMP_VIDEO_LIST,
                    "-i", logo_path,
                    "-filter_complex",
                    (
                        "[0:v]drawtext=text='{}':"
                        "fontsize=24:x=10:y=10:fontcolor=white:box=1:boxcolor=black@0.5[text];"
                        "[text][1:v]overlay=W-w-10:10[outv]"
                    ).format(creation_date),
                    "-map", "[outv]",
                    "-map", "0:a?",
                    "-c:a", "aac", "-b:a", "48k",
                    "-c:v", "libx264",
                    "-b:v", "4M",
                    "-preset", "fast",
                    "-movflags",  "+faststart",
                    output_file,
                ]

                logger.info(f"Creating round for event {i+1}: {output_file} ({hh_mm_ss} for {delta_str})")
                result = subprocess.run(cmd, capture_output=True, text=True)
                logger.debug("FFmpeg stdout: %s", result.stdout)
                logger.debug("FFmpeg stderr: %s", result.stderr)

        else:
            delta_str = "N/A (last group)"
            logger.info(f"Event {i+1:<6} has no next group: {hh_mm_ss:<12} {delta_str:<15}")

if __name__ == "__main__":
    main()
