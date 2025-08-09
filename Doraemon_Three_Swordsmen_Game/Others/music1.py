from pydub.generators import Sine
from pydub import AudioSegment
import numpy as np

# Settings
duration_ms = 8000  # 8 seconds
volume_db = -10

# Notes (frequencies in Hz)
notes = [440, 493, 523, 587, 659, 698, 784]  # A, B, C, D, E, F, G
music = AudioSegment.silent(duration=0)

for i in range(len(notes)):
    freq = notes[i]
    tone = Sine(freq).to_audio_segment(duration=800).apply_gain(volume_db)
    music += tone.fade_in(200).fade_out(200)

# Repeat once for 16s total
music = music * 2

# Export
music.export("bgm_intro.wav", format="wav")
print("✅ Exported: bgm_intro.wav")
