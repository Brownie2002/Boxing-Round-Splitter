#!/usr/bin/env python3
"""
Bell Frequency Analyzer - Find optimal frequency for bell detection in boxing videos.
This tool analyzes the spectral content of audio files to determine the best frequency
for bell detection, improving the accuracy of round splitting.
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta
import logging
import numpy as np

# Add src to path
sys.path.insert(0, os.path.abspath('src'))

from core.spectral_analyzer import analyze_spectral_response

# Optional import for visualization
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    plt = None

# Configure logging (similar to split_rounds.py)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS.ss format for easy media player navigation."""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 10000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}"

def generate_visualization(results, audio_path, output_dir="visualizations"):
    """Generate visualizations of the spectral analysis."""
    if not HAS_MATPLOTLIB:
        logger.warning("matplotlib not available - skipping visualization")
        return None
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load audio for visualization
    import librosa
    y, sr = librosa.load(audio_path, sr=None)
    times = np.arange(len(y)) / sr
    
    # Create figure
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Full audio waveform
    plt.subplot(3, 1, 1)
    plt.plot(times, y, alpha=0.7, color='blue')
    plt.title('Full Audio Waveform')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Spectral peaks overlay
    plt.subplot(3, 1, 2)
    plt.plot(times, y, alpha=0.3, color='gray', label='Original')
    
    # Plot each spectral peak's events
    colors = plt.cm.rainbow(np.linspace(0, 1, len(results['spectral_peaks'])))
    
    for i, (peak, color) in enumerate(zip(results['spectral_peaks'], colors)):
        freq = peak['frequency']
        for event in peak['event_timestamps']:
            for timestamp in event:
                # Find closest index
                idx = int(timestamp * sr)
                if 0 <= idx < len(y):
                    plt.scatter(timestamp, y[idx], 
                               color=color, s=50, alpha=0.7, 
                               label=f'{freq:.1f}Hz' if i == 0 else "")
    
    plt.title('Detected Bell Events (Spectral Peaks Overlay)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Zoom on detected events
    plt.subplot(3, 1, 3)
    
    for i, (peak, color) in enumerate(zip(results['spectral_peaks'], colors)):
        freq = peak['frequency']
        for event in peak['event_timestamps']:
            if event:  # If we have timestamps
                start_time = event[0] - 0.1  # 100ms before
                end_time = event[-1] + 0.1  # 100ms after
                mask = (times >= start_time) & (times <= end_time)
                plt.plot(times[mask], y[mask], color=color, alpha=0.7,
                        label=f'{freq:.1f}Hz at {format_timestamp(event[0])}')
    
    plt.title('Zoom on Detected Bell Events')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save visualization
    viz_path = os.path.join(output_dir, f"spectral_analysis_{os.path.basename(audio_path)}.png")
    plt.savefig(viz_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return viz_path

def main():
    # Parse command line arguments (homogeneous with split_rounds.py)
    parser = argparse.ArgumentParser(
        description='Bell Frequency Analyzer - Find optimal frequency for bell detection in boxing videos'
    )
    
    parser.add_argument('audio_file', help='Path to the WAV audio file to analyze')
    parser.add_argument('--output', help='Save detailed analysis report to JSON file')
    parser.add_argument('--band', nargs=2, type=int, default=[1500, 2500],
                       help='Frequency analysis band in Hz (default: 1500 2500)')
    parser.add_argument('--peaks', type=int, default=5,
                       help='Number of spectral peaks to analyze (default: 5)')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate visualization graphs')
    parser.add_argument('--viz-dir', default='visualizations',
                       help='Directory to save visualizations (default: visualizations)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Validate audio file
    if not os.path.exists(args.audio_file):
        logger.error(f"Audio file '{args.audio_file}' not found.")
        sys.exit(1)
    
    if not args.audio_file.lower().endswith('.wav'):
        logger.warning(f"File '{args.audio_file}' may not be a WAV file.")
    
    logger.info("=" * 60)
    logger.info("Bell Frequency Analyzer")
    logger.info("=" * 60)
    logger.info(f"Audio file: {args.audio_file}")
    logger.info(f"Analysis band: {args.band[0]}-{args.band[1]} Hz")
    logger.info(f"Peaks to analyze: {args.peaks}")
    logger.info("-" * 60)
    
    # Perform spectral analysis
    logger.info("Analyzing spectral content...")
    results = analyze_spectral_response(
        args.audio_file,
        analysis_band=tuple(args.band),
        output_report=args.output,
        n_peaks=args.peaks
    )
    
    # Display results using logging
    logger.info(f"\nAnalysis complete!")
    logger.info(f"Recommended frequency: {results['recommended_frequency']:.1f} Hz")
    
    logger.info(f"\nDetected {len(results['spectral_peaks'])} significant spectral peaks:")
    logger.info("-" * 80)
    
    # Sort peaks by score (descending)
    scored_peaks = []
    for peak in results['spectral_peaks']:
        power_score = peak['power_percentage']
        event_score = min(1.0, peak['events_detected'] / 10.0)
        consistency_score = peak['consistency_score']
        total_score = 0.4 * power_score + 0.3 * event_score + 0.3 * consistency_score
        
        # Format event timestamps
        formatted_events = []
        for event in peak['event_timestamps']:
            if event:  # If we have timestamps
                formatted_events.append({
                    'timestamp_sec': event[0],
                    'timestamp_str': format_timestamp(event[0]),
                    'amplitude': peak['amplitude_stats']['max']
                })
        
        scored_peaks.append({
            'frequency': peak['frequency'],
            'score': total_score,
            'events': peak['events_detected'],
            'power': peak['power_percentage'],
            'consistency': peak['consistency_score'],
            'formatted_events': formatted_events
        })
    
    # Sort by score (descending)
    scored_peaks.sort(key=lambda x: x['score'], reverse=True)
    
    for i, peak in enumerate(scored_peaks, 1):
        marker = "✓" if abs(peak['frequency'] - results['recommended_frequency']) < 10 else " "
        logger.info(f"{marker} {i}. {peak['frequency']:6.1f} Hz | " +
                   f"Score: {peak['score']:.2f} | " +
                   f"Events: {peak['events']} | " +
                   f"Power: {peak['power']:.2f} | " +
                   f"Consistency: {peak['consistency']:.2f}")
        
        # Show event details with formatted timestamps
        for j, event in enumerate(peak['formatted_events'], 1):
            logger.info(f"    Event {j}: {event['timestamp_str']} | " +
                      f"Amplitude: {event['amplitude']:.3f}")
    
    logger.info("-" * 60)
    
    # Show scoring explanation
    logger.info("\nScoring breakdown (weighted):")
    logger.info(f"  Power: 40% - Spectral energy at frequency")
    logger.info(f"  Events: 30% - Number of bell events detected")
    logger.info(f"  Consistency: 30% - Regularity of event timing")
    
    # Generate visualization if requested
    viz_path = None
    if args.visualize:
        try:
            viz_path = generate_visualization(results, args.audio_file, args.viz_dir)
            logger.info(f"\n✓ Visualization saved to: {viz_path}")
        except Exception as e:
            logger.warning(f"Could not generate visualization: {e}")
    
    # Save report if requested
    if args.output:
        logger.info(f"\n✓ Detailed report saved to: {args.output}")
        
        # Add metadata to report
        results['analysis_metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'command': ' '.join(sys.argv),
            'analysis_parameters': {
                'band': args.band,
                'peaks': args.peaks,
                'visualization': viz_path if viz_path else None
            }
        }
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
    
    logger.info("\nSuggested usage:")
    logger.info(f"  For future analysis, use --target-freq {results['recommended_frequency']:.0f}")
    logger.info("  Open in VLC: vlc {args.audio_file} --start-time=<timestamp>")
    logger.info("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)