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

# Configure logging (default to INFO level)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create a temp directory if it doesn't exist
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

TEMP_WAV = os.path.join(TEMP_DIR, "temp_audio.wav")
TEMP_VIDEO_LIST = os.path.join(TEMP_DIR, "temp_video_list.txt")

# ========== PARAMÈTRES COURANTS (modifiables facilement) ==========
# Temps d'un round en secondes (modifiable couramment)
ROUND_TIME = 120  # secondes

# ========== PARAMÈTRES EXPERTS (déconseillés à modifier) ==========
# Paramètres de détection de cloche - NE PAS MODIFIER SAUF SI VOUS SAVEZ CE QUE VOUS FAITES
TARGET_FREQ = 2080  # Hz - Fréquence cible de la cloche
BANDWIDTH = 50  # Hz - Bande passante autour de la fréquence cible
MIN_PEAK_HEIGHT = 0.03  # Niveau minimal pour détecter un pic
PEAKS_IN_ROW = 4  # Nombre minimal de pics consécutifs pour une détection
MAX_GAP = 0.6  # Secondes maximales entre pics consécutifs

def validate_logo_path(logo_path):
    """
    Validates the logo file path and converts relative paths to absolute paths.

    Args:
        logo_path (str): Path to the logo file (can be relative or absolute).

    Returns:
        str: Absolute path to the logo file if valid.

    Raises:
        FileNotFoundError: If the logo file does not exist.
        ValueError: If the logo file is not a supported image format.
    """
    if logo_path is None:
        return None

    # Convert relative path to absolute path
    abs_logo_path = os.path.abspath(logo_path)

    # Check if file exists
    if not os.path.exists(abs_logo_path):
        raise FileNotFoundError(f"Logo file not found: {abs_logo_path}")

    # Check if it's a file (not a directory)
    if not os.path.isfile(abs_logo_path):
        raise ValueError(f"Logo path is not a file: {abs_logo_path}")

    # Check file extension for supported image formats
    supported_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
    file_ext = os.path.splitext(abs_logo_path)[1].lower()
    if file_ext not in supported_extensions:
        raise ValueError(f"Unsupported logo file format: {file_ext}. Supported formats: {', '.join(supported_extensions)}")

    logger.info(f"Using logo file: {abs_logo_path}")
    return abs_logo_path

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

    # Only proceed if we have peaks
    if len(peak_times) > 0:
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

def get_video_creation_info(video_path):
    """
    Extracts creation metadata from a video file in a single FFprobe call.

    This optimized function retrieves both the formatted date (YYYY-MM-DD) and
    the full datetime object for sorting purposes in one FFprobe call.

    Args:
        video_path (str): Path to the video file.

    Returns:
        tuple: (formatted_date_str, datetime_obj) where:
            - formatted_date_str: Creation date as 'YYYY-MM-DD' or 'Not available'
            - datetime_obj: Full datetime object or None if not available

    Example:
        >>> formatted_date, datetime_obj = get_video_creation_info("video.mp4")
        >>> print(f"Date: {formatted_date}, Full datetime: {datetime_obj}")
    """
    try:
        # Single FFprobe call to get all metadata
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_format',
            '-print_format', 'json',
            video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        metadata = json.loads(result.stdout)

        creation_time = metadata['format'].get('tags', {}).get('creation_time', None)

        if creation_time:
            datetime_obj = datetime.strptime(creation_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            formatted_date = datetime_obj.strftime('%Y-%m-%d')
            return formatted_date, datetime_obj
        else:
            return 'Not available', None

    except Exception as e:
        logger.warning(f"Could not extract metadata from {video_path}: {e}")
        return f"An error occurred: {e}", None

def get_video_metadata(video_path):
    """
    Extracts metadata from the video file, including the creation date.

    This function uses FFprobe to retrieve video metadata in JSON format and extracts
    the creation date if available. The creation date is parsed and formatted as YYYY-MM-DD.

    Args:
        video_path (str): Path to the video file.

    Returns:
        str: The creation date of the video in the format 'YYYY-MM-DD' if available.
             Returns 'Not available' if creation date cannot be extracted.
             Returns an error message if an exception occurs during processing.

    Example:
        >>> creation_date = get_video_metadata("path/to/video.mp4")
        >>> print(f"Creation Date: {creation_date}")
        Creation Date: 2026-02-15

    Note:
        This function requires FFprobe to be installed and available in the system PATH.
        The creation date is extracted from the 'creation_time' tag in the video metadata.
    """
    # Use the optimized function and return just the formatted date
    formatted_date, _ = get_video_creation_info(video_path)
    return formatted_date

def sort_videos_by_creation_date(video_files):
    """
    Sorts a list of video files by their creation date and returns sorted list with first video's date.

    This optimized function extracts metadata once per video and returns both the sorted list
    and the creation date of the first video for output directory naming.

    Args:
        video_files (list): List of video file paths.

    Returns:
        tuple: (sorted_video_files, first_video_date, sorted_video_info) where:
            - sorted_video_files: List of video paths sorted by creation date (oldest first)
            - first_video_date: Creation date of the first video as 'YYYY-MM-DD'
            - sorted_video_info: List of tuples (video_path, formatted_date, datetime_obj) for display

    Example:
        >>> sorted_videos, first_date, video_info = sort_videos_by_creation_date(video_files)
        >>> print(f"First video date: {first_date}")
        >>> for video, date, _ in video_info:
        ...     print(f"{video}: {date}")
    """
    # Get creation info for all videos in one pass
    video_info = []
    for video in video_files:
        formatted_date, creation_datetime = get_video_creation_info(video)
        video_info.append((video, formatted_date, creation_datetime))

    # Sort by creation datetime (oldest first), videos without date go to the end
    sorted_videos = sorted(
        video_info,
        key=lambda x: (x[2] is None, x[2] if x[2] else datetime.max)
    )

    # Extract sorted video paths
    sorted_video_files = [video for video, _, _ in sorted_videos]

    # Get the first video's formatted date for output directory
    first_video_date = sorted_videos[0][1] if sorted_videos else 'Not available'

    return sorted_video_files, first_video_date, sorted_videos

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Split boxing videos into individual rounds based on bell sounds.')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--logo', type=str, help='Path to the logo file to overlay on output videos', default=None)
    parser.add_argument('--round-time', type=int, help='Duration of a round in seconds (default: 120)', default=ROUND_TIME)
    parser.add_argument('--expert-mode', action='store_true', help='Show expert parameters (use with caution)')
    parser.add_argument('--target-freq', type=int, help='Target frequency for bell detection (default: 2080)', default=TARGET_FREQ)
    parser.add_argument('--bandwidth', type=int, help='Bandwidth around target frequency (default: 50)', default=BANDWIDTH)
    parser.add_argument('--min-peak-height', type=float, help='Minimum peak height for detection (default: 0.03)', default=MIN_PEAK_HEIGHT)
    parser.add_argument('--peaks-in-row', type=int, help='Minimum peaks in row for detection (default: 4)', default=PEAKS_IN_ROW)
    parser.add_argument('--max-gap', type=float, help='Maximum gap between peaks (default: 0.6)', default=MAX_GAP)
    args = parser.parse_args()

    # Configure logging based on debug flag
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(log_level)

    # Declare global variables at the beginning of the function
    global ROUND_TIME, TARGET_FREQ, BANDWIDTH, MIN_PEAK_HEIGHT, PEAKS_IN_ROW, MAX_GAP

    # Update global parameters
    ROUND_TIME = args.round_time
    TARGET_FREQ = args.target_freq
    BANDWIDTH = args.bandwidth
    MIN_PEAK_HEIGHT = args.min_peak_height
    PEAKS_IN_ROW = args.peaks_in_row
    MAX_GAP = args.max_gap

    # Get video files from command line arguments
    video_files = args.video_files

    # Sort videos by creation date and get first video's date in one call
    sorted_video_files, creation_date, sorted_video_info = sort_videos_by_creation_date(video_files)

    if len(sorted_video_files) != len(video_files) or any(
        sorted_video_files[i] != video_files[i]
        for i in range(len(video_files))
    ):
        logger.info("Videos sorted by creation date:")
        for i, (video, formatted_date, _) in enumerate(sorted_video_info, 1):
            date_str = formatted_date if formatted_date and formatted_date != 'Not available' else 'Unknown'
            logger.info(f"  {i}. {os.path.basename(video)} - {date_str}")

    # Handle logo parameter - always ensure we have a logo
    if args.logo:
        try:
            logo_path = validate_logo_path(args.logo)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Logo error: {e}")
            sys.exit(1)
    else:
        # Use default logo if no logo is specified
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "logo.png")

        if not os.path.exists(logo_path):
            logger.error(f"Default logo not found at: {logo_path}")
            sys.exit(1)

        logger.info(f"Using default logo: {logo_path}")

    # Show expert parameters if requested
    if args.expert_mode:
        logger.warning("EXPERT MODE ENABLED - These parameters are advanced and should not be modified unless you understand their impact!")
        logger.warning(f"TARGET_FREQ: {TARGET_FREQ} Hz")
        logger.warning(f"BANDWIDTH: {BANDWIDTH} Hz")
        logger.warning(f"MIN_PEAK_HEIGHT: {MIN_PEAK_HEIGHT}")
        logger.warning(f"PEAKS_IN_ROW: {PEAKS_IN_ROW}")
        logger.warning(f"MAX_GAP: {MAX_GAP} seconds")

    logger.info(f"Creation Date: {creation_date}")
    logger.info(f"Round Time: {ROUND_TIME} seconds")

    # Create temp_video_list.txt with absolute paths (using sorted videos)
    with open(TEMP_VIDEO_LIST, "w") as f:
        for video in sorted_video_files:
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
