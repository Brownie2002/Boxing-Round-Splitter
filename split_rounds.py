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

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

TEMP_WAV = "temp_audio.wav"
TARGET_FREQ = 2050  # Hz
BANDWIDTH = 50  # Hz on each side
MIN_PEAK_HEIGHT = 0.04  # adjust based on recording amplitude
PEAKS_IN_ROW = 4
MAX_GAP = .6  # seconds between consecutive beeps
ROUND_TIME = 120 # seconds of the round

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
    video_files = sys.argv[1:]

    creation_date = get_video_metadata(video_files[0])

    logger.info(f"Creation Date: {creation_date}")

    # Create temp_video_list.txt
    with open("temp_video_list.txt", "w") as f:
        for video in video_files:
            f.write(f"file '{video}'\n")

    # Step 1: Extract the audio from the .lrv video using ffmpeg
    print("Extracting audio with ffmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",  "-f", "concat", "-safe", "0",
        "-i", "temp_video_list.txt", "-vn",      # no video
        "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1", TEMP_WAV
    ]
    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Step 2: Load the audio with librosa
    print("Loading audio...")
    y, sr = librosa.load(TEMP_WAV, sr=None)

    # Create a bandpass filter around 2000Hz
    low = (TARGET_FREQ - BANDWIDTH) / (sr / 2)
    high = (TARGET_FREQ + BANDWIDTH) / (sr / 2)
    b, a = butter(N=4, Wn=[low, high], btype='band')
    filtered_audio = filtfilt(b, a, y)

    # Compute amplitude envelope
    amplitude = np.abs(filtered_audio)

    # Detect peaks
    peaks, properties = find_peaks(amplitude, height=MIN_PEAK_HEIGHT, distance=sr*0.1)  # enforce 100ms min distance

    # Convert peak indices to time in seconds
    peak_times = peaks / sr

    valid_events = []
    current_group = [peak_times[0]]

    for t in peak_times[1:]:
        # If the current peak is close to the previous one, add to group
        if t - current_group[-1] <= MAX_GAP:
            current_group.append(t)
        else:
            # Check if the group has enough peaks
            if len(current_group) >= PEAKS_IN_ROW:
                valid_events.append(current_group)
            current_group = [t]

    # Check the last group
    if len(current_group) >= PEAKS_IN_ROW:
        valid_events.append(current_group)

    # Output formatted results
    print(f"{'Group':<6}  {'Size':<7} {'Start Time':<12} {'Δ Time From Prev':<15}")
    print("-" * 40)
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

                # Create the video segment
                cmd2 = [
                    "nice", "-n", "10",
                    "ffmpeg", "-y",
                    "-ss", f"{max(0, start_time):.3f}",
                    "-t", f"{delta_sec:.3f}",
                    "-f", "concat", "-safe", "0",
                    "-i", "temp_video_list.txt",
                    "-i", "logo.png",
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
                    "-movflags",  "+faststart",
                    output_file,
                ]

                cmd = [
                    "nice", "-n", "10",
                    "ffmpeg", "-y",
                    "-ss", f"{max(0, start_time):.3f}",  # Start 0.5s earlier
                    "-t", f"{delta_sec:.3f}",
                    "-f", "concat", "-safe", "0",
                    "-i", "temp_video_list.txt",
                    "-vf", f"drawtext=text='{creation_date}':fontsize=24:x=10:y=10:fontcolor=white:box=1:boxcolor=black@0.5",
                    "-c:v", "libx264",
                    "-b:v", "5M",
                    "-c:a", "aac",
                    "-b:a", "64k",
                    "-movflags", "+faststart",
                    output_file,
                ]

                print(f"Creating round {i+1}: {output_file} ({hh_mm_ss} for {delta_str})")
                result = subprocess.run(cmd2, capture_output=True, text=True)
                print(result.stdout)
                print(result.stderr)

        else:
            delta_str = "N/A (last group)"
            print(f"Round {i+1:<6} has no next group: {hh_mm_ss:<12} {delta_str:<15}")

if __name__ == "__main__":
    main()
