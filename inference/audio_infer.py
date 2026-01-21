"""
Heuristic Audio Deepfake Detector
NO MODEL REQUIRED - Uses signal processing to detect AI voice artifacts
Size: 0MB (just uses librosa + numpy)
"""

import librosa
import numpy as np
from typing import Dict, List, Tuple


class HeuristicAudioDetector:
    """
    Detects audio deepfakes using acoustic analysis.
    
    Detection Signals:
    1. Spectral inconsistency - AI voices have unnatural frequency patterns
    2. Pitch abnormalities - Robotic pitch contours
    3. Energy gaps - Unnatural pauses/breathing
    4. High-frequency artifacts - AI struggles with fine details
    5. Temporal discontinuities - Spliced audio segments
    """
    
    def __init__(self):
        self.sample_rate = 16000
        
    def analyze_audio(self, audio_path: str) -> Dict:
        """
        Analyzes audio and returns deepfake probability + explanations.
        
        Returns:
            {
                'score': 0.0-1.0,  # Probability of deepfake
                'confidence': 0.0-1.0,
                'signals': {...},  # Individual signal scores
                'explanation': str
            }
        """
        # Load audio
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        # Run all detection signals
        signals = {
            'spectral_inconsistency': self._check_spectral_consistency(y),
            'pitch_abnormality': self._check_pitch_naturalness(y),
            'energy_gaps': self._check_energy_continuity(y),
            'high_freq_artifacts': self._check_high_frequency_quality(y),
            'temporal_discontinuity': self._check_temporal_consistency(y),
        }
        
        # Aggregate scores (weighted average)
        weights = {
            'spectral_inconsistency': 0.25,
            'pitch_abnormality': 0.20,
            'energy_gaps': 0.15,
            'high_freq_artifacts': 0.25,
            'temporal_discontinuity': 0.15,
        }
        
        final_score = sum(signals[k] * weights[k] for k in weights)
        
        # Generate explanation
        explanation = self._generate_explanation(signals, final_score)
        
        return {
            'score': float(final_score),
            'confidence': self._calculate_confidence(signals),
            'signals': signals,
            'explanation': explanation
        }
    
    def _check_spectral_consistency(self, y: np.ndarray) -> float:
        """
        Real voices have natural spectral variation.
        AI voices often have overly smooth or sharp transitions.
        """
        # Compute STFT
        stft = librosa.stft(y, n_fft=2048, hop_length=512)
        mag = np.abs(stft)
        
        # Check spectral flux (frame-to-frame change)
        spectral_flux = np.mean(np.diff(mag, axis=1) ** 2)
        
        # AI voices tend to have either:
        # - Too smooth (low flux) - overly processed
        # - Too sharp (high flux) - artifacts
        
        # Normalize to 0-1 range (empirically tuned)
        if spectral_flux < 0.01:  # Too smooth
            return 0.8
        elif spectral_flux > 0.5:  # Too sharp
            return 0.7
        else:  # Natural range
            return 0.1
    
    def _check_pitch_naturalness(self, y: np.ndarray) -> float:
        """
        Human pitch varies naturally. AI pitch can be robotic or jumpy.
        """
        # Extract pitch using YIN algorithm
        f0 = librosa.yin(y, fmin=50, fmax=500, sr=self.sample_rate)
        
        # Remove unvoiced frames (pitch = inf or 0)
        f0_voiced = f0[(f0 > 0) & (f0 < 500)]
        
        if len(f0_voiced) < 10:
            return 0.5  # Not enough data
        
        # Check pitch variation
        pitch_std = np.std(f0_voiced)
        pitch_range = np.ptp(f0_voiced)  # peak-to-peak
        
        # Natural speech: moderate variation
        # AI: either too flat or too jumpy
        if pitch_std < 5 or pitch_range < 20:  # Too flat
            return 0.75
        elif pitch_std > 80:  # Too variable
            return 0.65
        else:
            return 0.15
    
    def _check_energy_continuity(self, y: np.ndarray) -> float:
        """
        Natural speech has gradual energy changes (breathing, pauses).
        AI often has abrupt starts/stops.
        """
        # Compute RMS energy per frame
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
        
        # Check for abrupt energy changes
        energy_diff = np.abs(np.diff(rms))
        abrupt_changes = np.sum(energy_diff > 0.1)
        
        # Normalize by total frames
        abruptness_ratio = abrupt_changes / len(rms)
        
        if abruptness_ratio > 0.3:  # Too many abrupt changes
            return 0.7
        else:
            return 0.2
    
    def _check_high_frequency_quality(self, y: np.ndarray) -> float:
        """
        AI struggles to synthesize high frequencies (8kHz+).
        Real voices have rich high-frequency content.
        """
        # Compute mel spectrogram
        mel = librosa.feature.melspectrogram(
            y=y, sr=self.sample_rate, n_mels=128, fmax=8000
        )
        mel_db = librosa.power_to_db(mel)
        
        # Compare energy in high vs low frequencies
        low_freq_energy = np.mean(mel_db[:64])  # 0-4kHz
        high_freq_energy = np.mean(mel_db[64:])  # 4-8kHz
        
        ratio = high_freq_energy / (low_freq_energy + 1e-8)
        
        # AI voices: weak high frequencies (ratio < -20dB)
        if ratio < -20:
            return 0.8
        elif ratio < -15:
            return 0.5
        else:
            return 0.1
    
    def _check_temporal_consistency(self, y: np.ndarray) -> float:
        """
        Spliced/edited audio has discontinuities.
        Check for sudden timbre changes.
        """
        # Extract MFCCs (timbre representation)
        mfcc = librosa.feature.mfcc(y=y, sr=self.sample_rate, n_mfcc=13)
        
        # Compute frame-to-frame distance
        mfcc_diff = np.sum(np.diff(mfcc, axis=1) ** 2, axis=0)
        
        # Find large jumps (potential splice points)
        threshold = np.percentile(mfcc_diff, 95)
        large_jumps = np.sum(mfcc_diff > threshold * 2)
        
        if large_jumps > 5:  # Multiple discontinuities
            return 0.75
        elif large_jumps > 2:
            return 0.4
        else:
            return 0.1
    
    def _calculate_confidence(self, signals: Dict) -> float:
        """
        Confidence is high when multiple signals agree.
        """
        scores = list(signals.values())
        agreement = 1.0 - np.std(scores)  # Low std = high agreement
        return float(np.clip(agreement, 0.3, 0.95))
    
    def _generate_explanation(self, signals: Dict, final_score: float) -> str:
        """Generate human-readable explanation."""
        if final_score > 0.7:
            verdict = "LIKELY DEEPFAKE"
            reasons = []
            if signals['spectral_inconsistency'] > 0.6:
                reasons.append("unnatural spectral patterns")
            if signals['pitch_abnormality'] > 0.6:
                reasons.append("robotic pitch contours")
            if signals['high_freq_artifacts'] > 0.6:
                reasons.append("weak high-frequency content")
            
            return f"{verdict}: Detected {', '.join(reasons)}."
        
        elif final_score > 0.4:
            return "UNCERTAIN: Some suspicious artifacts detected, but inconclusive."
        
        else:
            return "LIKELY AUTHENTIC: Audio shows natural speech characteristics."


def run_audio_inference(audio_path: str) -> float:
    """
    Drop-in replacement for your current audio inference.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        float: Deepfake probability (0-1)
    """
    detector = HeuristicAudioDetector()
    result = detector.analyze_audio(audio_path)
    
    print(f"\n{'='*60}")
    print(f"HEURISTIC AUDIO ANALYSIS")
    print(f"{'='*60}")
    print(f"Final Score: {result['score']*100:.1f}%")
    print(f"Confidence: {result['confidence']*100:.1f}%")
    print(f"\nIndividual Signals:")
    for signal, score in result['signals'].items():
        print(f"  • {signal}: {score*100:.0f}%")
    print(f"\n{result['explanation']}")
    print(f"{'='*60}\n")
    
    return result['score']