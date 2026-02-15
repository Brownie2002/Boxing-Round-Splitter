import unittest
import os
import sys
import hashlib
import warnings
import numpy as np
import librosa

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from core.split_rounds import detect_bell_ringing


class TestBellDetection(unittest.TestCase):
    """Test cases for the bell detection function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_audio_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_bell_input.wav'))
        self.reference_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_bell_reference_timestamps.txt'))
        self.output_detection_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_bell_output_timestamps.txt'))
        
        # Create temp directory for test files
        self.temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'temp_test_files'))
        os.makedirs(self.temp_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test files."""
        # Remove temporary test files
        for file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception:
                pass

    def test_detect_bell_ringing_with_10min_audio(self):
        """Test bell detection with the output_10min.wav file."""
        # Call the function with warnings suppressed
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(self.test_audio_path, self.output_detection_file)

        # Verify that the function returns a list
        self.assertIsInstance(valid_events, list, "The function should return a list of events.")

        # Verify that each event is a list of timestamps
        for event in valid_events:
            self.assertIsInstance(event, list, "Each event should be a list of timestamps.")
            for timestamp in event:
                self.assertIsInstance(timestamp, (int, float), "Each timestamp should be a number.")

        # Verify that the debug file was created
        self.assertTrue(os.path.exists(self.output_detection_file), "The debug file should be created.")
        
        if os.path.exists(self.reference_file):
            with open(self.reference_file, 'rb') as f:
                reference_md5 = hashlib.md5(f.read()).hexdigest()
            
            with open(self.output_detection_file, 'rb') as f:
                debug_md5 = hashlib.md5(f.read()).hexdigest()
            
            print("\nMD5 Checksums for comparison:")
            print("=" * 50)
            print(f"Reference file MD5: {reference_md5}")
            print(f"Debug file MD5:     {debug_md5}")
            
            # Assert that the MD5 checksums match
            self.assertEqual(reference_md5, debug_md5, "MD5 checksums do not match. Please inspect the files manually to identify discrepancies.")

    def test_empty_audio_file(self):
        """Test bell detection with an empty audio file."""
        # Create an empty audio file
        empty_audio_path = os.path.join(self.temp_dir, 'empty_audio.wav')
        
        # Create a very short silent audio file
        y = np.zeros(44100)  # 1 second of silence
        try:
            import soundfile as sf
            sf.write(empty_audio_path, y, 44100)
        except ImportError:
            # Fallback for older librosa versions
            try:
                librosa.output.write_wav(empty_audio_path, y, 44100)
            except AttributeError:
                from scipy.io.wavfile import write
                y_int16 = (y * 32767).astype(np.int16)
                write(empty_audio_path, 44100, y_int16)
        
        # Test with empty audio
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(empty_audio_path)
        
        # Should return empty list for no bell events
        self.assertEqual(len(valid_events), 0, "Empty audio should return no bell events")

    def test_audio_with_no_bell_sounds(self):
        """Test bell detection with audio containing no bell sounds."""
        # Create audio with no bell sounds (just noise)
        no_bell_path = os.path.join(self.temp_dir, 'no_bell_audio.wav')
        
        # Generate pure noise
        np.random.seed(42)  # For reproducibility
        noise = np.random.normal(0, 0.1, 44100 * 5)  # 5 seconds of noise
        
        try:
            import soundfile as sf
            sf.write(no_bell_path, noise, 44100)
        except ImportError:
            try:
                librosa.output.write_wav(no_bell_path, noise, 44100)
            except AttributeError:
                from scipy.io.wavfile import write
                noise_int16 = (noise * 32767).astype(np.int16)
                write(no_bell_path, 44100, noise_int16)
        
        # Test with no bell sounds
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(no_bell_path)
        
        # Should return empty list or very few events
        self.assertLessEqual(len(valid_events), 1, "Audio with no bells should return few or no events")

    def test_different_sample_rates(self):
        """Test bell detection with different sample rates."""
        # Test with 22050Hz sample rate
        low_sr_path = os.path.join(self.temp_dir, 'low_sr_audio.wav')
        
        # Generate test audio at 22050Hz
        y_22k = np.zeros(22050 * 3)  # 3 seconds
        # Add a simple bell-like sound
        t = np.linspace(0, 0.5, 11025)  # 0.5 seconds at 22050Hz
        bell = 0.5 * np.sin(2 * np.pi * 2050 * t) * np.exp(-t * 5)
        y_22k[11025:22050] = bell
        
        try:
            import soundfile as sf
            sf.write(low_sr_path, y_22k, 22050)
        except ImportError:
            try:
                librosa.output.write_wav(low_sr_path, y_22k, 22050)
            except AttributeError:
                from scipy.io.wavfile import write
                y_22k_int16 = (y_22k * 32767).astype(np.int16)
                write(low_sr_path, 22050, y_22k_int16)
        
        # Test with 22050Hz audio
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(low_sr_path)
        
        # Should still detect the bell sound
        self.assertGreaterEqual(len(valid_events), 1, "Should detect bell at 22050Hz sample rate")

    def test_debug_file_generation(self):
        """Test debug file generation with different scenarios."""
        debug_file_path = os.path.join(self.temp_dir, 'debug_test.txt')
        
        # Test with normal audio
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(self.test_audio_path, debug_file_path)
        
        # Verify debug file was created and contains expected content
        self.assertTrue(os.path.exists(debug_file_path), "Debug file should be created")
        
        with open(debug_file_path, 'r') as f:
            content = f.read()
            self.assertIn("Bell Ringing Detection Debug Info", content)
            self.assertIn("Event", content)
            
            # Count number of events in debug file
            event_count = content.count("Event")
            self.assertEqual(event_count, len(valid_events), "Debug file should contain all detected events")

    def test_edge_case_short_audio(self):
        """Test bell detection with very short audio files."""
        short_audio_path = os.path.join(self.temp_dir, 'short_audio.wav')
        
        # Create a very short audio file (0.5 seconds)
        y_short = np.zeros(22050)  # 0.5 seconds at 44100Hz would be 22050 samples
        
        try:
            import soundfile as sf
            sf.write(short_audio_path, y_short, 44100)
        except ImportError:
            try:
                librosa.output.write_wav(short_audio_path, y_short, 44100)
            except AttributeError:
                from scipy.io.wavfile import write
                y_short_int16 = (y_short * 32767).astype(np.int16)
                write(short_audio_path, 44100, y_short_int16)
        
        # Test with very short audio
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(short_audio_path)
        
        # Should return empty list for such short audio
        self.assertEqual(len(valid_events), 0, "Very short audio should return no bell events")

    def test_return_value_structure(self):
        """Test the structure and content of the return value."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(self.test_audio_path)
        
        # Test return value structure
        self.assertIsInstance(valid_events, list, "Should return a list")
        
        if len(valid_events) > 0:
            # Test first event structure
            first_event = valid_events[0]
            self.assertIsInstance(first_event, list, "Each event should be a list")
            self.assertGreater(len(first_event), 0, "Each event should contain timestamps")
            
            # Test timestamp values
            for timestamp in first_event:
                self.assertIsInstance(timestamp, (int, float), "Timestamps should be numeric")
                self.assertGreaterEqual(timestamp, 0, "Timestamps should be non-negative")
            
            # Test that timestamps are in order
            sorted_timestamps = sorted(first_event)
            self.assertEqual(first_event, sorted_timestamps, "Timestamps should be in chronological order")

    def test_multiple_bell_events(self):
        """Test detection of multiple bell events in sequence."""
        # Use the main test file which should have multiple bell events
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(self.test_audio_path)
        
        # Should detect multiple events
        self.assertGreater(len(valid_events), 1, "Should detect multiple bell events")
        
        # Test that events are properly separated
        if len(valid_events) >= 2:
            first_event_end = valid_events[0][-1]
            second_event_start = valid_events[1][0]
            gap = second_event_start - first_event_end
            
            # Events should be separated by some gap
            self.assertGreater(gap, 0.1, "Consecutive events should have some separation")

if __name__ == '__main__':
    unittest.main()