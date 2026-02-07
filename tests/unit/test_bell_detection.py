import unittest
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from core.split_rounds import detect_bell_ringing


class TestBellDetection(unittest.TestCase):
    """Test cases for the bell detection function."""

    def test_detect_bell_ringing_with_test_audio(self):
        """Test bell detection with the test_audio.wav file."""
        test_audio_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../test_audio.wav'))
        debug_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../bell_detection_test_debug.txt'))

        # Check if the test audio file exists
        if not os.path.exists(test_audio_path):
            self.skipTest(f"Test audio file not found: {test_audio_path}")

        # Call the function
        valid_events = detect_bell_ringing(test_audio_path, debug_file)

        # Verify that the function returns a list
        self.assertIsInstance(valid_events, list, "The function should return a list of events.")

        # Verify that each event is a list of timestamps
        for event in valid_events:
            self.assertIsInstance(event, list, "Each event should be a list of timestamps.")
            for timestamp in event:
                self.assertIsInstance(timestamp, (int, float), "Each timestamp should be a number.")

        # Verify that the debug file was created
        self.assertTrue(os.path.exists(debug_file), "The debug file should be created.")

        # Read the debug file and verify the timestamps
        with open(debug_file, 'r') as f:
            debug_content = f.read()
            self.assertIn("Bell Ringing Detection Debug Info", debug_content, "Debug file should contain the header.")
            self.assertIn("Event", debug_content, "Debug file should contain event information.")

        # Calculate MD5 checksums for comparison
        import hashlib
        
        reference_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'reference_timestamps.txt'))
        if os.path.exists(reference_file):
            with open(reference_file, 'rb') as f:
                reference_md5 = hashlib.md5(f.read()).hexdigest()
            
            with open(debug_file, 'rb') as f:
                debug_md5 = hashlib.md5(f.read()).hexdigest()
            
            print("\nMD5 Checksums for comparison:")
            print("=" * 50)
            print(f"Reference file MD5: {reference_md5}")
            print(f"Debug file MD5:     {debug_md5}")
            
            # Assert that the MD5 checksums match
            self.assertEqual(reference_md5, debug_md5, "MD5 checksums do not match. Please inspect the files manually to identify discrepancies.")

        # Note: The debug file is not removed to allow manual inspection
        # If you want to clean up, uncomment the following lines:
        # if os.path.exists(debug_file):
        #     os.remove(debug_file)


if __name__ == '__main__':
    unittest.main()