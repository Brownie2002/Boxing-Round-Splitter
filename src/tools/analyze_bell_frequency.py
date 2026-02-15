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
import shutil
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

def analyze_spectral_response_with_steps(audio_path, analysis_band=(1500, 2500), 
                                       step_size=50.0, output_report=None, main_output_dir=None):
    """
    Perform spectral analysis with frequency scanning using step size.
    
    Args:
        audio_path: Path to WAV file
        analysis_band: Frequency range to analyze (Hz)
        step_size: Frequency step size in Hz for scanning
        output_report: Path to save analysis report (JSON)
        main_output_dir: Main output directory for README generation
        
    Returns:
        dict: Spectral analysis results
    """
    import librosa
    import json
    from core.spectral_analyzer import evaluate_frequency
    
    # Initialize results structure
    results = {
        'audio_file': os.path.basename(audio_path),
        'analysis_band': analysis_band,
        'step_analysis': {
            'step_size': step_size,
            'scanned_frequencies': [],
            'optimal_frequency_by_step': None
        },
        'recommended_frequency': None
    }
    
    # Get sample rate for reference
    y, sr = librosa.load(audio_path, sr=None)
    results['sample_rate'] = sr
    
    # Scan the frequency band with the specified step size
    start_freq = analysis_band[0]
    end_freq = analysis_band[1]
    current_freq = start_freq
    
    frequency_results = []
    
    logger.info(f"Scanning frequencies from {start_freq}Hz to {end_freq}Hz with {step_size}Hz steps...")
    
    while current_freq <= end_freq:
        freq_result = evaluate_frequency(audio_path, current_freq)
        frequency_results.append(freq_result)
        
        # Add to scanned frequencies list
        results['step_analysis']['scanned_frequencies'].append({
            'frequency': current_freq,
            'events_detected': freq_result['events_detected'],
            'consistency_score': freq_result['consistency_score'],
            'amplitude_stats': freq_result['amplitude_stats']
        })
        
        current_freq += step_size
    
    logger.info(f"Scanned {len(frequency_results)} frequencies")
    
    # Find optimal frequency from step scanning
    if frequency_results:
        # Use scoring logic similar to select_optimal_frequency
        scored_freqs = []
        
        # Find max amplitude for normalization
        max_amplitude = max(result['amplitude_stats']['max'] for result in frequency_results)
        
        for result in frequency_results:
            # Normalize power score (0-1)
            power_score = result['amplitude_stats']['max'] / max_amplitude if max_amplitude > 0 else 0
            
            # Normalize event score (0-1, capped at 10 events)
            event_score = min(1.0, result['events_detected'] / 10.0)
            
            # Use consistency score directly
            consistency_score = result['consistency_score']
            
            # Weighted score (power 40%, events 30%, consistency 30%)
            total_score = (0.4 * power_score + 0.3 * event_score + 0.3 * consistency_score)
            
            scored_freqs.append({
                'frequency': result['frequency'],
                'score': total_score,
                'power_score': power_score,
                'event_score': event_score,
                'consistency_score': consistency_score,
                'events_detected': result['events_detected']
            })
        
        # Find frequency with highest score
        optimal_step_freq = max(scored_freqs, key=lambda x: x['score'])
        results['step_analysis']['optimal_frequency_by_step'] = optimal_step_freq['frequency']
        results['recommended_frequency'] = optimal_step_freq['frequency']
        
        # Add detailed scoring information
        results['step_analysis']['scoring_details'] = scored_freqs
        
        logger.info(f"Optimal frequency found: {optimal_step_freq['frequency']:.1f}Hz (score: {optimal_step_freq['score']:.2f})")
    
    # Save report if requested
    if output_report:
        # Enhance the report with detailed event timestamps for top 3 frequencies
        enhanced_results = results.copy()
        
        # Get frequency_results from the step analysis function
        # We need to re-run the frequency evaluation for top frequencies
        from core.spectral_analyzer import evaluate_frequency
        
        # Get top 3 frequencies from step analysis
        step_events = results.get('step_analysis', {}).get('scanned_frequencies', [])
        top_3_freqs = sorted(step_events, key=lambda x: x['events_detected'], reverse=True)[:3]
        
        enhanced_results['top_candidates'] = []
        

        
        for freq_info in top_3_freqs:
            freq = freq_info['frequency']

            # Re-evaluate this frequency to get full details including timestamps
            freq_result = evaluate_frequency(audio_path, freq)
            
            candidate_info = {
                'frequency': freq,
                'events_detected': freq_result['events_detected'],
                'consistency_score': freq_result['consistency_score'],
                'amplitude_stats': freq_result['amplitude_stats']
            }
            
            enhanced_results['top_candidates'].append(candidate_info)
        

        
        # Generate individual frequency debug files
        output_dir = os.path.join(os.path.dirname(output_report), 'frequency_files')
        generate_frequency_debug_files(audio_path, step_events, output_report, output_dir, main_output_dir, results, frequency_results)
        
        with open(output_report, 'w') as f:
            json.dump(enhanced_results, f, indent=2)
    
    return results, frequency_results


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
    
    # Plot 2: Step analysis events overlay
    plt.subplot(3, 1, 2)
    plt.plot(times, y, alpha=0.3, color='gray', label='Original')
    
    # Plot events from step analysis (top 3 frequencies)
    step_events = results.get('step_analysis', {}).get('scanned_frequencies', [])
    
    # Get top 3 frequencies by event count
    top_freqs = sorted(step_events, key=lambda x: x['events_detected'], reverse=True)[:3]
    colors = plt.cm.rainbow(np.linspace(0, 1, len(top_freqs)))
    
    for i, (freq_info, color) in enumerate(zip(top_freqs, colors)):
        freq = freq_info['frequency']
        # Find the full frequency result with timestamps
        for freq_result in frequency_results:
            if abs(freq_result['frequency'] - freq) < 1 and 'event_timestamps' in freq_result:
                for event in freq_result['event_timestamps']:
                    for timestamp in event:
                        # Find closest index
                        idx = int(timestamp * sr)
                        if 0 <= idx < len(y):
                            plt.scatter(timestamp, y[idx], 
                                       color=color, s=50, alpha=0.7, 
                                       label=f'{freq:.1f}Hz' if i == 0 else "")
                break
    
    plt.title('Detected Bell Events (Step Analysis Overlay)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Zoom on detected events
    plt.subplot(3, 1, 3)
    
    for i, (freq_info, color) in enumerate(zip(top_freqs, colors)):
        freq = freq_info['frequency']
        # Find the full frequency result with timestamps
        for freq_result in frequency_results:
            if abs(freq_result['frequency'] - freq) < 1 and 'event_timestamps' in freq_result:
                for event in freq_result['event_timestamps']:
                    if event:  # If we have timestamps
                        start_time = event[0] - 0.1  # 100ms before
                        end_time = event[-1] + 0.1  # 100ms after
                        mask = (times >= start_time) & (times <= end_time)
                        plt.plot(times[mask], y[mask], color=color, alpha=0.7,
                                label=f'{freq:.1f}Hz at {format_timestamp(event[0])}')
                break
    
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

def generate_frequency_debug_files(audio_path, step_events, output_report, output_dir=None, main_output_dir=None, results=None, frequency_results=None):
    """
    Generate individual debug files for each frequency analyzed.
    
    Args:
        audio_path: Path to the audio file
        step_events: List of frequency analysis results
        output_report: Path to the main JSON report
        output_dir: Directory to save debug files (default: frequency_files subdirectory)
        main_output_dir: Main output directory for README and organization
        results: Analysis results dictionary for README generation
        frequency_results: Full frequency evaluation results for README generation
    """
    from core.spectral_analyzer import evaluate_frequency
    
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(output_report), 'frequency_files')
    
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Generating individual frequency debug files in: {output_dir}/")
    
    generated_files = []
    
    for freq_info in step_events:
        freq = freq_info['frequency']
        # Re-evaluate this frequency to get full details including timestamps
        freq_result = evaluate_frequency(audio_path, freq)
        
        # Generate individual debug file for this frequency
        debug_filename = f"bell_events_{int(freq)}Hz.txt"
        debug_filepath = os.path.join(output_dir, debug_filename)
        
        with open(debug_filepath, 'w') as debug_file:
            debug_file.write(f"Bell Ringing Detection Debug Info - Frequency: {freq}Hz\n")
            debug_file.write("=" * 60 + "\n")
            debug_file.write(f"Events detected: {freq_result['events_detected']}\n")
            debug_file.write(f"Consistency score: {freq_result['consistency_score']:.4f}\n")
            debug_file.write(f"Max amplitude: {freq_result['amplitude_stats']['max']:.6f}\n")
            debug_file.write("=" * 60 + "\n")
            
            # Add timestamps for each event
            if 'event_timestamps' in freq_result:
                for event_idx, event in enumerate(freq_result['event_timestamps'], 1):
                    if event and len(event) > 0:
                        # Format all timestamps in this event
                        formatted_times = []
                        for ts in event:
                            formatted_times.append(format_timestamp(ts))
                        
                        debug_file.write(f"Event {event_idx}: {formatted_times}\n")
            
            debug_file.write("=" * 60 + "\n")
        
        generated_files.append(debug_filepath)
        logger.info(f"✓ Generated debug file: {debug_filepath}")
    
    logger.info(f"✓ Generated {len(generated_files)} individual frequency debug files")
    logger.info("  Use: meld {}/ or vimdiff to compare files".format(output_dir))
    
    # Generate README file if we have a main output directory and results
    if main_output_dir and results and frequency_results:
        readme_path = os.path.join(main_output_dir, "README_ANALYSIS_RESULTS.md")
        with open(readme_path, 'w') as readme_file:
            readme_file.write("# Bell Frequency Analysis Results\n\n")
            readme_file.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            readme_file.write(f"**Audio File:** {os.path.basename(audio_path)}\n\n")
            readme_file.write(f"**Frequency Band:** {results['analysis_band'][0]}-{results['analysis_band'][1]} Hz\n\n")
            readme_file.write(f"**Step Size:** {results['step_analysis']['step_size']} Hz\n\n")
            readme_file.write(f"**Frequencies Scanned:** {len(step_events)}\n\n")
            
            readme_file.write("## 🎯 Analysis Results\n\n")
            readme_file.write(f"**Recommended Frequency:** {results['recommended_frequency']:.1f} Hz\n\n")
            
            readme_file.write("### Top 3 Candidates\n\n")
            readme_file.write("| Frequency | Events | Consistency | Power Score |\n")
            readme_file.write("|-----------|--------|-------------|-------------|\n")
            
            top_3 = sorted(step_events, key=lambda x: x['events_detected'], reverse=True)[:3]
            for freq_info in top_3:
                freq = freq_info['frequency']
                readme_file.write(f"| {freq:.1f} Hz | {freq_info['events_detected']} | {freq_info['consistency_score']:.4f} | {freq_info['amplitude_stats']['max']:.4f} |\n")
            
            readme_file.write("\n## 📁 Files Generated\n\n")
            readme_file.write(f"- `analysis_results.json` - Complete analysis report (JSON)\n")
            readme_file.write(f"- `{os.path.basename(audio_path)}` - Copy of analyzed audio file\n")
            readme_file.write(f"- `frequency_files/` - Individual frequency debug files\n")
            
            readme_file.write("\n## 🔍 How to Use These Results\n\n")
            readme_file.write("### Compare Frequency Files\n")
            readme_file.write("```bash\n")
            readme_file.write(f"meld frequency_files/\n")
            readme_file.write(f"vimdiff frequency_files/bell_events_{{{{int(results['recommended_frequency'])}}}}Hz.txt frequency_files/bell_events_{{{{int(top_3[1]['frequency'])}}}}Hz.txt\n")
            readme_file.write("```\n\n")
            
            readme_file.write("### Test Specific Events with VLC\n")
            readme_file.write("```bash\n")
            # Get first few events from recommended frequency
            recommended_freq = results['recommended_frequency']
            for freq_result in frequency_results:
                if abs(freq_result['frequency'] - recommended_freq) < 1:
                    events = freq_result.get('event_timestamps', [])[:3]
                    for i, event in enumerate(events, 1):
                        if event:
                            timestamp = event[0]
                            readme_file.write(f"vlc {os.path.basename(audio_path)} --start-time={timestamp:.2f}  # Event {i}\n")
                    break
            readme_file.write("```\n\n")
            
            readme_file.write("### Quick Analysis Summary\n")
            readme_file.write(f"- **Total events at recommended frequency:** {top_3[0]['events_detected']}\n")
            readme_file.write(f"- **Consistency score:** {top_3[0]['consistency_score']:.3f}\n")
            readme_file.write(f"- **Frequency range tested:** {len(step_events)} frequencies from {results['analysis_band'][0]}-{results['analysis_band'][1]} Hz\n")
            
            readme_file.write("\n## 📊 Detailed Statistics\n\n")
            readme_file.write("### All Scanned Frequencies\n\n")
            readme_file.write("| Freq | Events | Consistency | Power |\n")
            readme_file.write("|------|-------|-------------|-------|\n")
            
            for freq_info in step_events:
                freq = freq_info['frequency']
                marker = "✓" if abs(freq - results['recommended_frequency']) < 1 else " "
                readme_file.write(f"| {marker}{freq:.1f} | {freq_info['events_detected']} | {freq_info['consistency_score']:.3f} | {freq_info['amplitude_stats']['max']:.4f} |\n")
        
        logger.info(f"✓ Generated README: {readme_path}")
    
    return generated_files


def main():
    # Parse command line arguments (homogeneous with split_rounds.py)
    parser = argparse.ArgumentParser(
        description='Bell Frequency Analyzer - Find optimal frequency for bell detection in boxing videos'
    )
    
    parser.add_argument('audio_file', help='Path to the WAV audio file to analyze')
    parser.add_argument('--band', nargs=2, type=int, default=[1500, 2500],
                       help='Frequency analysis band in Hz (default: 1500 2500)')
    parser.add_argument('--step', type=float, default=50.0,
                       help='Frequency step size in Hz for scanning the band (default: 50.0)')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate visualization graphs')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--output-dir', 
                       help='Output directory for all analysis files. If not specified, automatically creates "analysis_[timestamp]_[audio_name]"')
    
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
    logger.info(f"Frequency step: {args.step} Hz")
    logger.info("-" * 60)
    
    # Set up output directory - create automatically if not specified
    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
    else:
        # Create automatic output directory name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        audio_name = os.path.splitext(os.path.basename(args.audio_file))[0]
        output_dir = os.path.abspath(f"analysis_{timestamp}_{audio_name}")
    
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Using output directory: {output_dir}")
    
    # Copy audio file to output directory
    audio_filename = os.path.basename(args.audio_file)
    copied_audio_path = os.path.join(output_dir, audio_filename)
    if not os.path.exists(copied_audio_path):
        shutil.copy2(args.audio_file, copied_audio_path)
        logger.info(f"✓ Copied audio file to: {copied_audio_path}")
    
    # Set default output paths within the output directory
    # Set output report path
        output_report = os.path.join(output_dir, 'analysis_results.json')
    
    viz_dir = os.path.join(output_dir, 'visualizations')
    
    # Perform spectral analysis with frequency scanning
    logger.info("Analyzing spectral content...")
    results, frequency_results = analyze_spectral_response_with_steps(
        args.audio_file,
        analysis_band=tuple(args.band),
        step_size=args.step,
        output_report=output_report,
        main_output_dir=output_dir  # Use the actual output_dir path
    )
    
    # Display results using logging
    logger.info(f"\nAnalysis complete!")
    logger.info(f"Recommended frequency: {results['recommended_frequency']:.1f} Hz")
    
    # Show step analysis results
    step_optimal = results['step_analysis']['optimal_frequency_by_step']
    logger.info(f"Step analysis optimal: {step_optimal:.1f} Hz")
    logger.info(f"Step size used: {results['step_analysis']['step_size']} Hz")
    logger.info(f"Frequencies scanned: {len(results['step_analysis']['scanned_frequencies'])}")
    
    logger.info(f"\nTop frequencies from step analysis:")
    logger.info("-" * 80)
    
    # Get top frequencies from step analysis
    scored_freqs = results['step_analysis']['scoring_details']
    
    # Sort by score (descending)
    scored_freqs.sort(key=lambda x: x['score'], reverse=True)
    
    # Show top 10 frequencies
    top_freqs = scored_freqs[:10]
    
    for i, freq_data in enumerate(top_freqs, 1):
        marker = "✓" if abs(freq_data['frequency'] - results['recommended_frequency']) < 1 else " "
        logger.info(f"{marker} {i}. {freq_data['frequency']:6.1f} Hz | " +
                   f"Score: {freq_data['score']:.2f} | " +
                   f"Events: {freq_data['events_detected']} | " +
                   f"Power: {freq_data['power_score']:.2f} | " +
                   f"Consistency: {freq_data['consistency_score']:.2f}")
        
        # Show detailed event timestamps for the recommended frequency
        if abs(freq_data['frequency'] - results['recommended_frequency']) < 1:
            # Find the full frequency result with event timestamps
            for scanned_freq in results['step_analysis']['scanned_frequencies']:
                if abs(scanned_freq['frequency'] - freq_data['frequency']) < 1:
                    # Get the full evaluation result for this frequency
                    full_result = next(
                        (result for result in frequency_results 
                         if abs(result['frequency'] - freq_data['frequency']) < 1), None
                    )
                    if full_result and 'event_timestamps' in full_result:
                        logger.info(f"    🔔 Detected bell events at {freq_data['frequency']:.1f}Hz:")
                        event_count = 0
                        for event_idx, event in enumerate(full_result['event_timestamps'], 1):
                            if event and len(event) > 0:
                                timestamp = event[0]  # First timestamp of the event
                                formatted_time = format_timestamp(timestamp)
                                logger.info(f"    Event {event_idx}: {formatted_time} ({timestamp:.2f}s)")
                                event_count += 1
                                if event_count >= 5:  # Show first 5 events
                                    logger.info(f"    ... and {len(full_result['event_timestamps']) - 5} more events")
                                    break
                    break
    
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
    
    # Save report
    logger.info(f"\n✓ Detailed report saved to: {output_report}")

    # Add metadata to report
    results['analysis_metadata'] = {
        'timestamp': datetime.now().isoformat(),
        'command': ' '.join(sys.argv),
        'analysis_parameters': {
            'band': args.band,
            'step': args.step,
            'visualization': viz_path if viz_path else None
        }
    }

    # with open(output_report, 'w') as f:
        #     json.dump(results, f, indent=2)
        # Note: Report generation moved to analyze_spectral_response_with_steps for enhanced features
    
    # Show summary of all events for recommended frequency
    logger.info("\n📋 Event Summary for Recommended Frequency:")
    logger.info("-" * 60)
    
    # Find the recommended frequency result from step analysis
    recommended_freq = results['recommended_frequency']
    all_events = []
    
    # Get events from the frequency results
    for result in frequency_results:
        if abs(result['frequency'] - recommended_freq) < 1 and 'event_timestamps' in result:
            all_events = result['event_timestamps']
            break
    
    if all_events:
        logger.info(f"Total events detected at {recommended_freq:.1f}Hz: {len(all_events)}")
        logger.info("First 10 events (use with VLC --start-time):")
        
        for i, event in enumerate(all_events[:10], 1):
            if event and len(event) > 0:
                timestamp = event[0]
                formatted_time = format_timestamp(timestamp)
                logger.info(f"  {i:2d}. {formatted_time} (--start-time={timestamp:.2f})")
        
        if len(all_events) > 10:
            logger.info(f"  ... and {len(all_events) - 10} more events")
    else:
        logger.info("No events detected at recommended frequency")
    
    logger.info("\n🎯 Quick Test Commands:")
    if all_events:
        for i, event in enumerate(all_events[:3], 1):
            if event and len(event) > 0:
                timestamp = event[0]
                logger.info(f"  vlc {args.audio_file} --start-time={timestamp:.2f}")
    
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