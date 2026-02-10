import argparse
import librosa
import numpy as np
import matplotlib.pyplot as plt
import os

def analyze_frequency(audio_path, output_image_path="frequency_spectrum.png"):
    """
    Analyzes the frequency spectrum of an audio file and saves a plot.

    Args:
        audio_path (str): Path to the input audio file.
        output_image_path (str): Path to save the frequency spectrum plot.
    """
    y, sr = librosa.load(audio_path, sr=None)

    # Compute FFT
    N = len(y)
    T = 1.0 / sr
    yf = np.fft.fft(y)
    xf = np.fft.fftfreq(N, T)[:N//2]

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
    plt.title("Frequency Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.xlim(0, 5000) # Limit to a reasonable frequency range for bell sounds
    plt.savefig(output_image_path)
    plt.close()
    print(f"Frequency spectrum plot saved to {output_image_path}")

def main():
    parser = argparse.ArgumentParser(description='Analyze the frequency spectrum of an audio file.')
    parser.add_argument('audio_file', help='Path to the input audio file.')
    parser.add_argument('--output', default='frequency_spectrum.png',
                        help='Path to save the frequency spectrum plot (default: frequency_spectrum.png).')
    args = parser.parse_args()

    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found at {args.audio_file}")
        return

    analyze_frequency(args.audio_file, args.output)

if __name__ == "__main__":
    main()
