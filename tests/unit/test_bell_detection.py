import unittest
import os
import sys
import hashlib
import warnings

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from core.split_rounds import detect_bell_ringing


class TestBellDetection(unittest.TestCase):
    """Test cases for the bell detection function."""

    def test_detect_bell_ringing_with_10min_audio(self):
        """Test bell detection with the output_10min.wav file."""
        test_audio_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_bell_input.wav'))
        reference_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_bell_reference_timestamps.txt'))
        output_detection_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_bell_output_timestamps.txt'))

        # Call the function with warnings suppressed
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)
            valid_events = detect_bell_ringing(test_audio_path, output_detection_file)

        # Verify that the function returns a list
        self.assertIsInstance(valid_events, list, "The function should return a list of events.")

        # Verify that each event is a list of timestamps
        for event in valid_events:
            self.assertIsInstance(event, list, "Each event should be a list of timestamps.")
            for timestamp in event:
                self.assertIsInstance(timestamp, (int, float), "Each timestamp should be a number.")

        # Verify that the debug file was created
        self.assertTrue(os.path.exists(output_detection_file), "The debug file should be created.")
        
        if os.path.exists(reference_file):
            with open(reference_file, 'rb') as f:
                reference_md5 = hashlib.md5(f.read()).hexdigest()
            
            with open(output_detection_file, 'rb') as f:
                debug_md5 = hashlib.md5(f.read()).hexdigest()
            
            print("\nMD5 Checksums for comparison:")
            print("=" * 50)
            print(f"Reference file MD5: {reference_md5}")
            print(f"Debug file MD5:     {debug_md5}")
            
            # Assert that the MD5 checksums match
            self.assertEqual(reference_md5, debug_md5, "MD5 checksums do not match. Please inspect the files manually to identify discrepancies.")

if __name__ == '__main__':
    unittest.main()