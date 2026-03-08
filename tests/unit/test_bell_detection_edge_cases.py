import unittest
import os
import sys
import warnings
import numpy as np
import librosa

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from core.split_rounds import detect_bell_ringing

class TestBellDetectionEdgeCases(unittest.TestCase):
    """Additional test cases for edge cases in bell detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_audio_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_bell_input.wav'))
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

    def test_corrupted_audio_file(self):
        """Test bell detection with a corrupted audio file."""
        corrupted_path = os.path.join(self.temp_dir, 'corrupted_audio.wav')

        # Create a file with invalid WAV header
        with open(corrupted_path, 'wb') as f:
            f.write(b'This is not a valid WAV file')

        # Test with corrupted audio - should handle gracefully
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(corrupted_path)

        # Should return empty list for corrupted audio
        self.assertEqual(len(valid_events), 0, "Corrupted audio should return no bell events")

    def test_unsupported_audio_format(self):
        """Test bell detection with unsupported audio format."""
        unsupported_path = os.path.join(self.temp_dir, 'unsupported.mp3')

        # Create a dummy MP3 file (not actually valid, but for testing)
        with open(unsupported_path, 'wb') as f:
            f.write(b'This is not a WAV file')

        # Test with unsupported format - should handle gracefully
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(unsupported_path)

        # Should return empty list for unsupported format
        self.assertEqual(len(valid_events), 0, "Unsupported format should return no bell events")

    def test_extremely_long_audio(self):
        """Test bell detection with extremely long audio (simulated)."""
        # Create a very long audio file (simulated with zeros)
        long_audio_path = os.path.join(self.temp_dir, 'long_audio.wav')
        y = np.zeros(44100 * 60 * 60)  # 1 hour of silence

        try:
            import soundfile as sf
            sf.write(long_audio_path, y, 44100)
        except ImportError:
            try:
                librosa.output.write_wav(long_audio_path, y, 44100)
            except AttributeError:
                from scipy.io.wavfile import write
                y_int16 = (y * 32767).astype(np.int16)
                write(long_audio_path, 44100, y_int16)

        # Test with long audio
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(long_audio_path)

        # Should return empty list for silent long audio
        self.assertEqual(len(valid_events), 0, "Long silent audio should return no bell events")

    def test_invalid_parameters(self):
        """Test bell detection with invalid parameters."""
        # Test with None as audio path
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(None)

        # Should handle None gracefully
        self.assertEqual(len(valid_events), 0, "None as audio path should return no bell events")

        # Test with empty string as audio path
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing("")

        # Should handle empty string gracefully
        self.assertEqual(len(valid_events), 0, "Empty string as audio path should return no bell events")

    def test_consistency_across_runs(self):
        """Test that detection results are consistent across multiple runs."""
        # Run detection multiple times
        results = []
        for _ in range(3):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=DeprecationWarning)
                valid_events = detect_bell_ringing(self.test_audio_path)
            results.append(valid_events)

        # All runs should produce the same number of events
        event_counts = [len(r) for r in results]
        self.assertEqual(len(set(event_counts)), 1, "Detection should be consistent across runs")

        # All runs should produce events with the same structure
        for result in results:
            self.assertIsInstance(result, list, "Should return a list")
            for event in result:
                self.assertIsInstance(event, list, "Each event should be a list")
                for timestamp in event:
                    self.assertIsInstance(timestamp, (int, float), "Timestamps should be numeric")

if __name__ == '__main__':
    unittest.main()
