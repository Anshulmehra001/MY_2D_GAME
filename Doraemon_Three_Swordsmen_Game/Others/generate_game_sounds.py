import numpy as np
from scipy.io.wavfile import write
import os

ASSETS = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')
os.makedirs(ASSETS, exist_ok=True)

SAMPLE_RATE = 44100

def save_wav(filename, data):
    data = np.int16(data / np.max(np.abs(data)) * 32767)
    write(filename, SAMPLE_RATE, data)

# 1. Gameplay BGM (bgm.mp3 - save as .wav and rename)
def generate_bgm():
    freqs = [262, 330, 392, 440, 392, 330]  # C E G A G E
    tone = np.concatenate([np.sin(2 * np.pi * f * np.linspace(0, 0.3, int(SAMPLE_RATE * 0.3))) for f in freqs])
    save_wav(os.path.join(ASSETS, 'bgm.wav'), tone)

# 2. Slash sound (short high-frequency sweep)
def generate_slash():
    t = np.linspace(0, 0.2, int(SAMPLE_RATE * 0.2), False)
    wave = np.sin(2 * np.pi * 800 * t) * (1 - t)  # quick fade-out
    save_wav(os.path.join(ASSETS, 'slash.wav'), wave)

# 3. Hit sound (short impact burst)
def generate_hit():
    t = np.linspace(0, 0.1, int(SAMPLE_RATE * 0.1), False)
    burst = np.random.rand(len(t)) * 2 - 1
    envelope = np.exp(-30 * t)
    hit = burst * envelope
    save_wav(os.path.join(ASSETS, 'hit.wav'), hit)

# Generate all
generate_bgm()
generate_slash()
generate_hit()

print("✅ Sounds generated in: assets/sounds/")
