#!/usr/bin/env python3
"""
Create test audio for CPU optimization benchmarking
"""

import numpy as np
import wave
import os
from pathlib import Path

def create_test_audio(filename: str, duration: float = 15.0, sample_rate: int = 16000):
    """Create a simple synthetic audio file for testing"""
    
    # Generate synthetic audio with speech-like characteristics
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create speech-like waveform with multiple frequency components
    # Base frequency (fundamental)
    f1 = 120  # Typical male voice fundamental
    f2 = 240  # First harmonic
    f3 = 360  # Second harmonic
    
    # Generate complex waveform
    audio = (
        0.4 * np.sin(2 * np.pi * f1 * t) +
        0.2 * np.sin(2 * np.pi * f2 * t) +
        0.1 * np.sin(2 * np.pi * f3 * t)
    )
    
    # Add some noise for realism
    noise = 0.02 * np.random.randn(len(audio))
    audio = audio + noise
    
    # Add envelope to simulate speech patterns
    envelope = np.abs(np.sin(np.pi * t / duration * 5))  # 5 "speech bursts"
    audio = audio * envelope
    
    # Normalize to 16-bit range
    audio = np.clip(audio, -1.0, 1.0)
    audio = (audio * 32767).astype(np.int16)
    
    # Save as WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())
    
    print(f"Created test audio: {filename} ({duration}s)")
    return filename

def main():
    """Create test audio files"""
    
    # Create test audio directory
    test_dir = Path("test_audio")
    test_dir.mkdir(exist_ok=True)
    
    # Create different duration test files
    test_files = [
        (test_dir / "short_test.wav", 5.0),
        (test_dir / "medium_test.wav", 15.0),
        (test_dir / "long_test.wav", 30.0)
    ]
    
    created_files = []
    for filename, duration in test_files:
        created_file = create_test_audio(str(filename), duration)
        created_files.append(created_file)
    
    print(f"\nCreated {len(created_files)} test audio files:")
    for f in created_files:
        size_kb = os.path.getsize(f) / 1024
        print(f"  {f} ({size_kb:.1f} KB)")
    
    return created_files

if __name__ == "__main__":
    main()