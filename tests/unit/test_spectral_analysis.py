import unittest
import os
import sys
import json
import numpy as np

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from core.spectral_analyzer import (
    generate_test_audio,
    analyze_spectral_response,
    evaluate_frequency,
    group_peaks_into_events,
    calculate_event_consistency,
    select_optimal_frequency
)

class TestSpectralAnalysis(unittest.TestCase):
    """Test cases for the spectral bell frequency analyzer."""
    
    @classmethod
    def setUpClass(cls):
        """Generate test audio file once for all tests."""
        cls.test_audio_path = "temp_audio.wav"
        cls.report_path = "test_spectral_report.json"
        
        # Generate test audio with bells at 1900Hz, 2050Hz, 2200Hz
        generate_test_audio(
            cls.test_audio_path,
            bell_frequencies=[1900, 2050, 2200],
            bell_times=[2.0, 5.0, 8.0]
        )
        
        # Verify file was created
        cls.assertTrue(os.path.exists(cls.test_audio_path), 
                      "Test audio file should be created")
    
    def test_generate_test_audio(self):
        """Test that test audio generation works correctly."""
        # File should exist (already tested in setUpClass)
        self.assertTrue(os.path.exists(self.test_audio_path))
        
        # Verify it's a valid WAV file
        import librosa
        y, sr = librosa.load(self.test_audio_path, sr=None)
        self.assertEqual(sr, 44100, "Sample rate should be 44100Hz")
        self.assertEqual(len(y), 441000, "10 seconds at 44100Hz should be 441000 samples")
    
    def test_group_peaks_into_events(self):
        """Test peak grouping functionality."""
        # Test with no peaks
        result = group_peaks_into_events([])
        self.assertEqual(result, [], "Empty input should return empty list")
        
        # Test with peaks that form one event
        peaks = [1.0, 1.2, 1.4, 1.5]  # All within 0.6s of each other
        events = group_peaks_into_events(peaks)
        self.assertEqual(len(events), 1, "Should form one event")
        self.assertEqual(len(events[0]), 4, "Event should contain all 4 peaks")
        
        # Test with peaks that form multiple events (need at least 4 peaks per event)
        peaks = [1.0, 1.2, 1.4, 1.5, 2.2, 2.4, 2.6, 2.7]  # Two groups of 4 peaks each
        events = group_peaks_into_events(peaks)
        self.assertEqual(len(events), 2, "Should form two events")
        self.assertEqual(len(events[0]), 4, "First event should have 4 peaks")
        self.assertEqual(len(events[1]), 4, "Second event should have 4 peaks")
        
        # Test with insufficient peaks per event
        peaks = [1.0, 1.2]  # Only 2 peaks (need 4 minimum)
        events = group_peaks_into_events(peaks)
        self.assertEqual(len(events), 0, "Should not form event with <4 peaks")
    
    def test_calculate_event_consistency(self):
        """Test event consistency calculation."""
        # Test with no events
        consistency = calculate_event_consistency([])
        self.assertEqual(consistency, 0.0, "No events should return 0 consistency")
        
        # Test with one event
        events = [[1.0, 1.1, 1.2, 1.3]]
        consistency = calculate_event_consistency(events)
        self.assertEqual(consistency, 0.0, "Single event should return 0 consistency")
        
        # Test with perfectly consistent events (exactly 2 seconds apart)
        events = [
            [10.0, 10.1, 10.2, 10.3],
            [12.0, 12.1, 12.2, 12.3],
            [14.0, 14.1, 14.2, 14.3]
        ]
        consistency = calculate_event_consistency(events)
        self.assertGreater(consistency, 0.9, "Perfect consistency should be >0.9")
        
        # Test with inconsistent events
        events = [
            [10.0, 10.1, 10.2, 10.3],
            [11.0, 11.1, 11.2, 11.3],  # Only 1 second after first
            [15.0, 15.1, 15.2, 15.3]   # 4 seconds after second
        ]
        consistency = calculate_event_consistency(events)
        self.assertLess(consistency, 0.5, "Inconsistent events should have low score")
    
    def test_evaluate_frequency(self):
        """Test frequency evaluation functionality."""
        # Test with a frequency that should detect bells (2050Hz)
        result = evaluate_frequency(self.test_audio_path, 2050)
        
        self.assertIsInstance(result, dict, "Should return a dictionary")
        self.assertEqual(result['frequency'], 2050, "Should return correct frequency")
        self.assertGreaterEqual(result['events_detected'], 1, 
                               "Should detect at least one bell event")
        self.assertIn('amplitude_stats', result, "Should include amplitude stats")
        self.assertIn('consistency_score', result, "Should include consistency score")
        
        # Verify amplitude stats are reasonable
        stats = result['amplitude_stats']
        self.assertGreater(stats['max'], 0, "Max amplitude should be >0")
        self.assertGreaterEqual(stats['mean'], 0, "Mean amplitude should be >=0")
        self.assertGreaterEqual(stats['std'], 0, "Std amplitude should be >=0")
        
        # Test with a frequency that shouldn't detect much (1000Hz - outside bell range)
        result_low = evaluate_frequency(self.test_audio_path, 1000)
        self.assertLessEqual(result_low['events_detected'], 
                           result['events_detected'], 
                           "Lower frequency should detect fewer events")
    
    def test_analyze_spectral_response(self):
        """Test complete spectral analysis workflow."""
        # Perform spectral analysis
        results = analyze_spectral_response(self.test_audio_path, 
                                          output_report=self.report_path)
        
        # Verify basic structure
        self.assertIn('audio_file', results, "Should include audio file name")
        self.assertIn('sample_rate', results, "Should include sample rate")
        self.assertIn('analysis_band', results, "Should include analysis band")
        self.assertIn('spectral_peaks', results, "Should include spectral peaks")
        self.assertIn('recommended_frequency', results, "Should include recommended frequency")
        
        # Verify spectral peaks
        self.assertGreater(len(results['spectral_peaks']), 0, 
                          "Should detect at least one spectral peak")
        
        for peak in results['spectral_peaks']:
            self.assertIn('frequency', peak, "Each peak should have frequency")
            self.assertIn('spectral_power', peak, "Each peak should have spectral power")
            self.assertIn('events_detected', peak, "Each peak should have event count")
            self.assertIn('consistency_score', peak, "Each peak should have consistency score")
        
        # Verify recommended frequency is reasonable (should be around our test frequencies)
        recommended = results['recommended_frequency']
        self.assertGreater(recommended, 1800, "Recommended freq should be >1800Hz")
        self.assertLess(recommended, 2300, "Recommended freq should be <2300Hz")
        
        # Verify report file was created
        self.assertTrue(os.path.exists(self.report_path), 
                       "Report file should be created")
        
        # Verify report file is valid JSON
        with open(self.report_path, 'r') as f:
            report_data = json.load(f)
            self.assertEqual(report_data['recommended_frequency'], 
                            results['recommended_frequency'], 
                            "Report should match return value")
    
    def test_select_optimal_frequency(self):
        """Test optimal frequency selection logic."""
        # Create mock frequency results
        freq_results = [
            {
                'frequency': 1900,
                'power_percentage': 0.8,
                'events_detected': 6,
                'consistency_score': 0.7
            },
            {
                'frequency': 2050,
                'power_percentage': 0.9,
                'events_detected': 8,
                'consistency_score': 0.85
            },
            {
                'frequency': 2200,
                'power_percentage': 0.7,
                'events_detected': 5,
                'consistency_score': 0.6
            }
        ]
        
        # 2050Hz should be selected (highest weighted score)
        optimal = select_optimal_frequency(freq_results)
        self.assertEqual(optimal, 2050, "Should select 2050Hz as optimal")
        
        # Test with clear winner on power (adjust weights to favor power more)
        freq_results_power = [
            {
                'frequency': 1900,
                'power_percentage': 0.95,  # Much higher power
                'events_detected': 8,      # More events than before
                'consistency_score': 0.7   # Better consistency
            },
            {
                'frequency': 2050,
                'power_percentage': 0.6,
                'events_detected': 6,
                'consistency_score': 0.8
            }
        ]
        
        optimal_power = select_optimal_frequency(freq_results_power)
        self.assertEqual(optimal_power, 1900, "Should select 1900Hz (higher power and events)")
    
    def test_integration_with_real_audio(self):
        """Test with the generated audio file containing multiple bell frequencies."""
        results = analyze_spectral_response(self.test_audio_path)
        
        # Should detect multiple spectral peaks
        self.assertGreaterEqual(len(results['spectral_peaks']), 2, 
                               "Should detect multiple frequency peaks")
        
        # Should recommend a frequency near our test frequencies
        recommended = results['recommended_frequency']
        self.assertTrue(1850 < recommended < 2250, 
                       f"Recommended frequency {recommended} should be near test frequencies")
        
        # Verify we can find frequencies close to our generated bells
        detected_freqs = [peak['frequency'] for peak in results['spectral_peaks']]
        
        # At least one should be close to 2050Hz (our main test frequency)
        close_to_2050 = any(1950 < f < 2150 for f in detected_freqs)
        self.assertTrue(close_to_2050, 
                       "Should detect frequency close to 2050Hz")

if __name__ == '__main__':
    # Run tests and generate test audio if needed
    unittest.main(verbosity=2)