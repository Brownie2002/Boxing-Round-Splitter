import unittest
import os
import sys
import json
import numpy as np
import warnings

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from core.spectral_analyzer import (
    analyze_spectral_response,
    evaluate_frequency,
    group_peaks_into_events,
    calculate_event_consistency,
    select_optimal_frequency
)
from core.split_rounds import detect_bell_ringing

class TestSpectralAnalysis(unittest.TestCase):
    """Test cases for the spectral bell frequency analyzer using real test audio."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test using real bell detection audio file."""
        # Use the real test audio file that contains actual bell sounds
        cls.test_audio_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_bell_input.wav'))
        
        # Verify the test file exists
        cls.assertTrue(os.path.exists(cls.test_audio_path), 
                      "Test audio file test_bell_input.wav should exist")
        
        # Run bell detection to get reference timestamps
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            cls.bell_events = detect_bell_ringing(cls.test_audio_path)
    
    def test_real_audio_file_properties(self):
        """Test properties of the real test audio file."""
        import librosa
        
        # Load audio file
        y, sr = librosa.load(self.test_audio_path, sr=None)
        
        # Verify it's a valid audio file
        self.assertGreater(len(y), 0, "Audio should have samples")
        self.assertGreater(sr, 0, "Sample rate should be positive")
        
        # Should be a reasonably long file (at least 1 minute)
        duration = len(y) / sr
        self.assertGreater(duration, 60, "Test audio should be at least 1 minute long")
    
    def test_bell_detection_on_real_audio(self):
        """Test that bell detection works on real audio and finds events."""
        # Should have detected some bell events
        self.assertIsInstance(self.bell_events, list, "Should return list of events")
        self.assertGreater(len(self.bell_events), 0, "Should detect at least one bell event")
        
        # Each event should be a list of timestamps
        for event in self.bell_events:
            self.assertIsInstance(event, list, "Each event should be a list")
            self.assertGreater(len(event), 0, "Each event should have timestamps")
            
            # Timestamps should be numeric and in order
            for i, timestamp in enumerate(event):
                self.assertIsInstance(timestamp, (int, float), "Timestamps should be numeric")
                if i > 0:
                    self.assertGreaterEqual(timestamp, event[i-1], "Timestamps should be in order")
    
    def test_spectral_analysis_on_real_audio(self):
        """Test spectral analysis on real bell detection audio."""
        # Run spectral analysis on the real audio file
        results = analyze_spectral_response(self.test_audio_path)
        
        # Should return a dictionary with analysis results
        self.assertIsInstance(results, dict, "Should return dictionary of analysis results")
        
        # Check structure of results
        self.assertIn('audio_file', results, "Should include audio file name")
        self.assertIn('sample_rate', results, "Should include sample rate")
        self.assertIn('analysis_band', results, "Should include analysis band")
        self.assertIn('spectral_peaks', results, "Should include spectral peaks")
        self.assertIn('recommended_frequency', results, "Should include recommended frequency")
        
        # Check spectral peaks structure
        self.assertGreater(len(results['spectral_peaks']), 0, "Should detect spectral peaks")
        
        for peak in results['spectral_peaks']:
            self.assertIn('frequency', peak, "Each peak should have frequency")
            self.assertIn('spectral_power', peak, "Each peak should have spectral power")
            self.assertIn('events_detected', peak, "Each peak should have event count")
            self.assertIn('consistency_score', peak, "Each peak should have consistency score")
        
        # Recommended frequency should be reasonable
        recommended = results['recommended_frequency']
        self.assertGreater(recommended, 1500, "Recommended frequency should be > 1500Hz")
        self.assertLess(recommended, 2500, "Recommended frequency should be < 2500Hz")
    
    def test_frequency_evaluation_with_real_bells(self):
        """Test frequency evaluation using known bell frequencies."""
        # Test common bell frequencies
        test_frequencies = [1900, 2000, 2050, 2100, 2200]
        
        results = []
        for freq in test_frequencies:
            result = evaluate_frequency(self.test_audio_path, freq)
            results.append(result)
            
            # Verify result structure (actual structure from the function)
            self.assertIn('frequency', result)
            self.assertIn('events_detected', result)
            self.assertIn('event_timestamps', result)
            self.assertIn('amplitude_stats', result)
            self.assertIn('consistency_score', result)
            
            # Verify amplitude stats
            stats = result['amplitude_stats']
            self.assertIn('mean', stats)
            self.assertIn('std', stats)
            self.assertIn('max', stats)
        
        # Should have results for all test frequencies
        self.assertEqual(len(results), len(test_frequencies), "Should have results for all test frequencies")
        
        # Find the frequency with most events detected
        best_result = max(results, key=lambda x: x['events_detected'])
        self.assertGreater(best_result['events_detected'], 0, "Best frequency should detect some events")
    
    def test_optimal_frequency_selection(self):
        """Test optimal frequency selection with real audio."""
        # Test multiple frequencies around expected bell range
        frequencies = list(range(1800, 2300, 50))  # 1800, 1850, 1900, ..., 2250
        
        # Create mock results in the format expected by select_optimal_frequency
        mock_results = []
        for freq in frequencies:
            result = evaluate_frequency(self.test_audio_path, freq)
            # Convert to format expected by select_optimal_frequency
            mock_result = {
                'frequency': freq,
                'power_percentage': result['consistency_score'],  # Use consistency as proxy
                'events_detected': result['events_detected'],
                'consistency_score': result['consistency_score']
            }
            mock_results.append(mock_result)
        
        # Select optimal frequency
        optimal_freq = select_optimal_frequency(mock_results)
        
        # Should return valid frequency
        self.assertIn(optimal_freq, frequencies, "Should return one of test frequencies")
        self.assertGreater(optimal_freq, 1800, "Optimal frequency should be reasonable")
    
    def test_event_consistency_analysis(self):
        """Test event consistency calculation with real bell events."""
        # Use the bell events detected from the real audio
        if len(self.bell_events) > 0:
            # Calculate consistency for the detected events
            consistency_score = calculate_event_consistency(self.bell_events)
            
            # Should return a single consistency score (not a list)
            self.assertIsInstance(consistency_score, (float, np.floating), 
                                "Should return a float consistency score")
            
            # Score should be reasonable
            self.assertGreaterEqual(consistency_score, 0, "Consistency score should be non-negative")
            self.assertLessEqual(consistency_score, 1.0, "Consistency score should be <= 1.0")
    
    def test_peak_grouping_with_real_data(self):
        """Test peak grouping functionality with realistic peak data."""
        # Create realistic peak data based on typical bell patterns
        # Simulate peaks that would come from real bell detection
        peaks = []
        
        # Add some clusters of peaks (simulating bell rings)
        base_times = [2.0, 5.0, 8.0, 12.0]  # Typical round start times
        
        for base_time in base_times:
            # Add 3-5 peaks around each base time (simulating multiple beeps per bell)
            num_peaks = np.random.randint(3, 6)
            for i in range(num_peaks):
                offset = np.random.uniform(-0.1, 0.1)  # Small variation
                peaks.append(base_time + offset)
        
        # Sort peaks by time
        peaks.sort()
        
        # Group peaks into events
        events = group_peaks_into_events(peaks, max_gap=0.3)
        
        # Should group into reasonable number of events
        self.assertGreater(len(events), 1, "Should group into multiple events")
        self.assertLess(len(events), len(base_times) + 2, "Should not create too many events")
        
        # Each event should have multiple peaks
        for event in events:
            self.assertGreater(len(event), 1, "Each event should have multiple peaks")
    
    def test_integration_bell_detection_and_spectral_analysis(self):
        """Test integration between bell detection and spectral analysis."""
        # We already have bell events from setUpClass
        self.assertGreater(len(self.bell_events), 0, "Should have detected bell events")
        
        # Run spectral analysis
        spectral_results = analyze_spectral_response(self.test_audio_path)
        
        # Find the best frequency from spectral analysis
        best_frequency = spectral_results['recommended_frequency']
        
        # The best frequency should be in reasonable bell range
        self.assertGreater(best_frequency, 1500, "Bell frequency should be > 1500Hz")
        self.assertLess(best_frequency, 2500, "Bell frequency should be < 2500Hz")
        
        # Check that we detected some spectral peaks
        self.assertGreater(len(spectral_results['spectral_peaks']), 0, 
                          "Should detect at least one spectral peak")
        
        # Find the peak with most events detected
        best_peak = max(spectral_results['spectral_peaks'], key=lambda x: x['events_detected'])
        self.assertGreater(best_peak['events_detected'], 0, 
                          "Best peak should detect some events")

if __name__ == '__main__':
    unittest.main()