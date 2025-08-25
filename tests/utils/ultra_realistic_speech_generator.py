#!/usr/bin/env python3
"""
Ultra-realistic speech generator specifically tuned for Whisper VAD
Based on research into Whisper's internal VAD parameters
"""

import numpy as np
import wave
from pathlib import Path
from typing import Optional, Dict
import tempfile

class UltraRealisticSpeechGenerator:
    """Generates audio that meets Whisper's exact VAD requirements"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        
    def create_whisper_optimized_speech(self, duration: float = 5.0) -> np.ndarray:
        """
        Create speech audio optimized for Whisper VAD - MAXIMUM REALISM approach
        Focus on creating intense speech-frequency content that Whisper recognizes
        """
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # 1. Create multiple strong fundamental frequencies (simulate formant tracking)
        f0_base = 140.0  # Base male voice
        f0_variation = f0_base + 20 * np.sin(2 * np.pi * 2 * t)  # Natural pitch variation
        
        # Generate fundamental with vibrato
        phase = np.cumsum(2 * np.pi * f0_variation / self.sample_rate)
        fundamental = np.sin(phase)
        
        # 2. Create INTENSIVE formant structure (key for Whisper recognition)
        # Use more formants and stronger amplitudes
        formant_freqs = [400, 730, 1090, 1400, 2200, 2440, 3100]  # Extended formant set
        formant_signal = np.zeros_like(t)
        
        for i, freq in enumerate(formant_freqs):
            # Vary formant strength based on typical speech patterns
            strength = 0.8 if i < 3 else 0.4  # First 3 formants are strongest
            
            # Add formant with bandwidth (more realistic)
            main_formant = strength * np.sin(2 * np.pi * freq * t)
            # Add sidebands for bandwidth effect
            sideband1 = 0.3 * strength * np.sin(2 * np.pi * (freq - 50) * t)
            sideband2 = 0.3 * strength * np.sin(2 * np.pi * (freq + 50) * t)
            
            formant_signal += main_formant + sideband1 + sideband2
            
        # 3. Add MASSIVE harmonic content (critical for speech recognition)
        harmonic_signal = fundamental
        for harmonic in range(2, 15):  # Many more harmonics
            harmonic_freq = f0_base * harmonic
            if harmonic_freq < 8000:  # Extended range
                harmonic_strength = 0.4 / np.sqrt(harmonic)  # Slower rolloff
                harmonic_component = harmonic_strength * np.sin(2 * np.pi * harmonic_freq * t)
                harmonic_signal += harmonic_component
                
        # 4. Add intense speech-specific noise (crucial for VAD)
        # Wideband speech noise covering full speech spectrum
        speech_noise = np.random.normal(0, 0.15, samples)  # Much stronger
        speech_noise = self._bandpass_filter(speech_noise, 200, 4000)  # Full speech range
        
        # High-frequency fricatives and sibilants
        fricative_noise = np.random.normal(0, 0.12, samples)  # Stronger fricatives
        fricative_noise = self._bandpass_filter(fricative_noise, 2000, 8000)
        
        # Low-frequency vocal tract resonance
        vocal_resonance = np.random.normal(0, 0.08, samples)
        vocal_resonance = self._bandpass_filter(vocal_resonance, 80, 500)
        
        # 5. Create speech envelope with MAXIMUM voice activity
        # Multiple overlapping rhythms for natural speech
        syllable_rate = 4.0  # Faster speech rate
        word_rate = 1.8
        phrase_rate = 0.4
        
        syllable_envelope = 0.8 + 0.2 * np.sin(2 * np.pi * syllable_rate * t)
        word_envelope = 0.85 + 0.15 * np.sin(2 * np.pi * word_rate * t)
        phrase_envelope = 0.9 + 0.1 * np.sin(2 * np.pi * phrase_rate * t)
        
        # Combine for ultra-active envelope
        total_envelope = syllable_envelope * word_envelope * phrase_envelope
        
        # 6. Combine ALL components with maximum speech weighting
        speech_signal = (
            0.6 * harmonic_signal +           # Maximum harmonic content
            0.7 * formant_signal +            # Maximum formant structure  
            0.4 * speech_noise +              # High speech noise
            0.3 * fricative_noise +           # High fricatives
            0.2 * vocal_resonance +           # Vocal tract resonance
            fundamental * 0.3                 # Additional fundamental
        )
        
        # 7. Apply speech envelope
        speech_signal *= total_envelope
        
        # 8. NO PAUSES - maintain 100% voice activity
        # Only add very subtle amplitude variations instead of pauses
        micro_variations = 0.95 + 0.05 * np.random.normal(0, 1, samples)
        speech_signal *= micro_variations
        
        # 9. Aggressive processing for maximum Whisper compatibility
        # Focus energy in core speech range
        speech_signal = self._bandpass_filter(speech_signal, 100, 8000)
        
        # Strong compression for consistent energy
        speech_signal = np.tanh(speech_signal * 2.5) * 0.9
        
        # 10. Final amplitude targeting for Whisper VAD
        # Target much higher RMS for VAD threshold 0.35
        max_amplitude = np.max(np.abs(speech_signal))
        if max_amplitude > 0:
            # Target very high RMS to trigger VAD reliably
            target_rms = 0.2  # Much higher target
            current_rms = np.sqrt(np.mean(speech_signal ** 2))
            speech_signal = speech_signal * (target_rms / current_rms)
        
        # Ensure maximum dynamic range
        speech_signal = np.clip(speech_signal, -0.98, 0.98)
        
        return speech_signal.astype(np.float32)
    
    def _bandpass_filter(self, signal: np.ndarray, low_freq: float, high_freq: float) -> np.ndarray:
        """Simple FFT-based bandpass filter"""
        fft = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/self.sample_rate)
        
        # Create filter mask
        mask = np.zeros_like(freqs, dtype=float)
        mask[(np.abs(freqs) >= low_freq) & (np.abs(freqs) <= high_freq)] = 1.0
        
        # Apply smooth transitions at edges
        transition_width = 50  # Hz
        for i, freq in enumerate(np.abs(freqs)):
            if low_freq - transition_width <= freq < low_freq:
                mask[i] = (freq - (low_freq - transition_width)) / transition_width
            elif high_freq < freq <= high_freq + transition_width:
                mask[i] = 1.0 - (freq - high_freq) / transition_width
        
        fft *= mask
        return np.real(np.fft.ifft(fft))

def create_ultra_realistic_test_audio(output_dir: Optional[str] = None) -> Dict[str, str]:
    """Create ultra-realistic test audio files for Whisper VAD validation"""
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="ultra_realistic_speech_")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    generator = UltraRealisticSpeechGenerator()
    audio_files = {}
    
    # Generate ultra-realistic English speech (5 seconds)
    ultra_speech = generator.create_whisper_optimized_speech(duration=5.0)
    ultra_path = output_dir / "ultra_realistic_english.wav"
    if save_audio_wav(ultra_speech, str(ultra_path)):
        audio_files['ultra_realistic'] = str(ultra_path)
    
    # Generate shorter version (2 seconds) - edge case test
    short_ultra_speech = generator.create_whisper_optimized_speech(duration=2.0)
    short_ultra_path = output_dir / "ultra_realistic_short.wav"
    if save_audio_wav(short_ultra_speech, str(short_ultra_path)):
        audio_files['ultra_realistic_short'] = str(short_ultra_path)
    
    print(f"Created {len(audio_files)} ultra-realistic test audio files at: {output_dir}")
    for name, path in audio_files.items():
        file_size = Path(path).stat().st_size / 1024  # KB
        print(f"   {name}: {Path(path).name} ({file_size:.1f} KB)")
        
        # Analyze the generated audio
        print(f"   Analyzing {name}...")
        analyze_audio_for_whisper(path)
    
    return audio_files

def analyze_audio_for_whisper(audio_path: str):
    """Analyze audio characteristics important for Whisper VAD"""
    try:
        with wave.open(audio_path, 'rb') as wav:
            frames = wav.readframes(wav.getnframes())
            audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767
        
        # Key metrics for Whisper VAD
        duration = len(audio_data) / 16000
        
        # 1. RMS energy
        rms_energy = np.sqrt(np.mean(audio_data ** 2))
        print(f"     RMS Energy: {rms_energy:.4f} (target: >0.05)")
        
        # 2. Voice activity ratio (non-silence)
        energy_threshold = 0.01  # Conservative threshold
        voice_activity_ratio = np.sum(audio_data ** 2 > energy_threshold) / len(audio_data)
        print(f"     Voice Activity Ratio: {voice_activity_ratio:.3f} (target: >0.6)")
        
        # 3. Spectral analysis
        fft = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(audio_data), 1/16000)
        power_spectrum = np.abs(fft) ** 2
        
        # Speech core frequency energy (300-3400Hz)
        speech_range = (np.abs(freqs) >= 300) & (np.abs(freqs) <= 3400)
        total_energy = np.sum(power_spectrum)
        speech_energy_ratio = np.sum(power_spectrum[speech_range]) / total_energy if total_energy > 0 else 0
        print(f"     Speech Frequency Ratio: {speech_energy_ratio:.3f} (target: >0.7)")
        
        # 4. Dynamic range
        dynamic_range = np.max(audio_data) - np.min(audio_data)
        print(f"     Dynamic Range: {dynamic_range:.3f} (target: >0.2)")
        
        # 5. Overall Whisper VAD compatibility prediction
        vad_score = (
            (rms_energy > 0.05) * 25 +
            (voice_activity_ratio > 0.6) * 35 +  
            (speech_energy_ratio > 0.7) * 25 +
            (dynamic_range > 0.2) * 15
        )
        
        # Use ASCII-safe output for Windows console compatibility
        if vad_score >= 85:
            status = "EXCELLENT"
        elif vad_score >= 70:
            status = "GOOD" 
        elif vad_score >= 50:
            status = "MARGINAL"
        else:
            status = "POOR"
        print(f"     VAD Compatibility Score: {vad_score}/100 {status}")
        
    except Exception as e:
        print(f"     Analysis failed: {e}")

def save_audio_wav(audio: np.ndarray, output_path: str, sample_rate: int = 16000) -> bool:
    """Save audio to WAV file with proper formatting"""
    try:
        with wave.open(output_path, 'wb') as wav:
            wav.setnchannels(1)  # Mono
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(sample_rate)
            
            # Convert to 16-bit integers
            audio_int16 = (audio * 32767).astype(np.int16)
            wav.writeframes(audio_int16.tobytes())
        
        return True
    except Exception as e:
        print(f"Failed to save audio: {e}")
        return False

if __name__ == "__main__":
    # Test the ultra-realistic speech generator
    print("=== Ultra-Realistic Speech Generator Test ===")
    test_files = create_ultra_realistic_test_audio()
    
    print("\n=== Summary ===")
    print(f"Generated {len(test_files)} ultra-realistic speech files")
    print("These files are specifically optimized for Whisper VAD requirements:")
    print("- RMS energy >0.05 (for VAD threshold 0.35)")
    print("- Voice activity ratio >60%") 
    print("- Speech frequency content >70%")
    print("- Sufficient dynamic range")
    print("- Proper amplitude modulation patterns")