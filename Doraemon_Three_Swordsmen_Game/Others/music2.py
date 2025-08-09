import numpy as np
from scipy.io.wavfile import write

SAMPLE_RATE = 44100  # Hz
DURATION = 10  # seconds

def generate_fade_tone(frequency, duration, volume=0.5):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    fade = np.linspace(0.2, 1.0, len(t))  # slight fade-in
    wave = np.sin(2 * np.pi * frequency * t)
    return volume * wave * fade

# Dreamy arpeggio-like tones
melody_freqs = [392, 440, 494, 523, 587]  # G A B C D
melody = np.concatenate([generate_fade_tone(f, 1.0) for f in melody_freqs])

# Repeat softly
music = np.tile(melody, 1)

# Normalize to 16-bit PCM
music = np.int16(music / np.max(np.abs(music)) * 32767)

write("../assets/bgm_intro.wav", SAMPLE_RATE, music)
print("✅ Intro music exported: bgm_intro.wav")
