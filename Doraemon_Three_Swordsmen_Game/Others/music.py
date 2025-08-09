import numpy as np
from scipy.io.wavfile import write

SAMPLE_RATE = 44100  # Hz
DURATION = 10  # seconds

def generate_tone(frequency, duration, volume=0.5):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t)
    return volume * wave

# Simple fantasy-style melody
melody_freqs = [440, 523, 659, 587, 440, 698, 784]
melody = np.concatenate([generate_tone(f, 0.7) for f in melody_freqs])

# Repeat for loop
music = np.tile(melody, 2)

# Normalize to 16-bit PCM
music = np.int16(music / np.max(np.abs(music)) * 32767)

write("../assets/bgm_gameplay.wav", SAMPLE_RATE, music)
print("✅ Music exported: bgm_gameplay.wav")
