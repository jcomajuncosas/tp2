"""
Exemples — Bloc 2, Sessió 2 (versió Thonny)
El so com a fitxer: WAV, mixing i loops

Equivalent al notebook recursos/patches_bloc2.ipynb (Colab),
adaptat per executar-se localment amb Thonny + soundfile + sounddevice.

Necessites un fitxer 'perc_loop.wav' a la mateixa carpeta que aquest script
(descarrega'l de recursos/audio/perc_loop.wav).
"""

import numpy as np
import soundfile as sf
import sounddevice as sd
import librosa
import librosa.display
import matplotlib.pyplot as plt

sample_rate = 44100


# ---------------------------------------------------------------
# 1. Recordatori Sessió 1 — generar un to
# ---------------------------------------------------------------
def generate_tone(freq, duration, amplitude=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * freq * t)
    return wave


tone = generate_tone(freq=440, duration=1.0, amplitude=0.5)
sd.play(tone, sample_rate)
sd.wait()


# ---------------------------------------------------------------
# 2. Escriure un WAV
# ---------------------------------------------------------------
sf.write("el_meu_to.wav", tone, sample_rate)
print("Fitxer escrit!")


# ---------------------------------------------------------------
# 3. Llegir-lo de nou
#
# Pregunta: si comparem 'tone' (l'original) amb 'data' (el llegit),
# seran exactament iguals?
# ---------------------------------------------------------------
data, sr = sf.read("el_meu_to.wav")

print("Sample rate:", sr)
print("Longitud original:", len(tone), "  Longitud llegida:", len(data))
print("Són (gairebé) iguals?", np.allclose(tone, data, atol=1e-4))

sd.play(data, sr)
sd.wait()


# ---------------------------------------------------------------
# 4. Carregar i visualitzar el loop de percussió
#
# Assegura't que 'perc_loop.wav' esta a la mateixa carpeta
# ---------------------------------------------------------------
perc, sr_perc = librosa.load("perc_loop.wav", sr=None)

print("Durada:", len(perc) / sr_perc, "segons")

librosa.display.waveshow(perc, sr=sr_perc)
plt.title("Loop de percussió")
plt.show()

sd.play(perc, sr_perc)
sd.wait()


# ---------------------------------------------------------------
# 5. DEMO EN DIRECTE — Mixing
#
# Pregunta: 'perc' te 88200 mostres (2s). El 'tone' en te 44100 (1s).
# Que passara si fem 'perc + tone' directament? (Error: longituds diferents)
# ---------------------------------------------------------------
print("len(perc):", len(perc))
print("len(tone):", len(tone))

n = min(len(perc), len(tone))
mix = perc[:n] + tone[:n]
mix = mix / np.max(np.abs(mix))

sd.play(mix, sample_rate)
sd.wait()


# ---------------------------------------------------------------
# 6. DEMO EN DIRECTE — Loop amb np.tile
#
# Pregunta: si 'perc' dura 2 segons, quant durara np.tile(perc, 4)?
# ---------------------------------------------------------------
perc_x4 = np.tile(perc, 4)

print("Durada x4:", len(perc_x4) / sr_perc, "segons")

sd.play(perc_x4, sr_perc)
sd.wait()


# ---------------------------------------------------------------
# 7. Tot junt: loop + to per sobre, amb fade
#
# Assegura't que 'example_pad.wav' esta a la mateixa carpeta
# ---------------------------------------------------------------
pad, sr_pad = librosa.load("example_pad.wav", sr=None)

n_repeats = int(np.ceil(len(pad) / len(perc)))
perc_repeated = np.tile(perc, n_repeats)[:len(pad)]

perc_repeated = perc_repeated * 0.6

mix_final = perc_repeated + pad
mix_final = mix_final / np.max(np.abs(mix_final))

librosa.display.waveshow(mix_final, sr=sr_pad)
plt.title("Mix final")
plt.show()

sd.play(mix_final, sr_pad)
sd.wait()
