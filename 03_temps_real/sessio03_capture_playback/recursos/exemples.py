"""
Exemples — Bloc 3a, Sessió 3 (versió Thonny)
Captura, playback i efectes offline (model blocking)

Equivalent al notebook recursos/patches_bloc3a.ipynb (Colab),
adaptat per executar-se localment amb Thonny + sounddevice.
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
import librosa
import librosa.display
import matplotlib.pyplot as plt

sample_rate = 44100
duration = 3.0


# ---------------------------------------------------------------
# 1. Gravar amb el micròfon (model blocking)
# ---------------------------------------------------------------
print("Gravant 3 segons... fes un so ara!")
recording = sd.rec(int(duration * sample_rate),
                   samplerate=sample_rate,
                   channels=1,
                   dtype='float32')
sd.wait()  # espera que acabi — el programa S'ATURA aqui
print("Gravació acabada!")

# sd.rec retorna shape (n_mostres, 1) — cal aplanar per a mono
data = recording.flatten()

print("Shape original:", recording.shape)
print("Shape aplanat:", data.shape)
print("Durada:", len(data)/sample_rate, "s")

librosa.display.waveshow(data, sr=sample_rate)
plt.title("La teva gravació")
plt.show()

# Reprodueix el que has gravat
sd.play(data, sample_rate)
sd.wait()


# ---------------------------------------------------------------
# 2. Les funcions d'efectes (totes offline: array -> array)
# ---------------------------------------------------------------

def reverse(data):
    return data[::-1]

def fade_in(data, duration, sample_rate=44100):
    n = min(int(duration * sample_rate), len(data))
    env = np.ones(len(data))
    env[:n] = np.linspace(0, 1, n)
    return data * env

def fade_out(data, duration, sample_rate=44100):
    n = min(int(duration * sample_rate), len(data))
    env = np.ones(len(data))
    env[-n:] = np.linspace(1, 0, n)
    return data * env

def echo(data, delay_seconds, decay=0.5, sample_rate=44100):
    delay_samples = int(delay_seconds * sample_rate)
    result = np.copy(data)  # IMPORTANT: copia, no referencia!
    result[delay_samples:] += data[:-delay_samples] * decay
    return result

def delay_multi(data, delay_seconds, decay=0.5, n_repeats=4, sample_rate=44100):
    result = np.copy(data)
    delay_samples = int(delay_seconds * sample_rate)
    for i in range(1, n_repeats + 1):
        start = i * delay_samples
        if start >= len(data):
            break
        result[start:] += data[:len(data)-start] * (decay ** i)
    return result

def distortion(data, drive=5.0, threshold=0.7):
    clipped = np.clip(data * drive, -threshold, threshold)
    return clipped / np.max(np.abs(clipped))

def tremolo(data, rate=5.0, depth=0.5, sample_rate=44100):
    t = np.linspace(0, len(data)/sample_rate, len(data), endpoint=False)
    lfo = 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t))
    return data * lfo

def ring_modulation(data, carrier_freq=200.0, sample_rate=44100):
    t = np.linspace(0, len(data)/sample_rate, len(data), endpoint=False)
    return data * np.sin(2 * np.pi * carrier_freq * t)

def playback_speed(data, factor, sample_rate=44100):
    """Canvia velocitat (i to i durada). NO es pitch shift real."""
    new_sr = int(sample_rate * factor)
    return data, new_sr


# ---------------------------------------------------------------
# 3. DEMO — provar cada efecte
# (descomenta/comenta les seccions per provar-les una a una)
# ---------------------------------------------------------------

print("\n--- Reverse ---")
sd.play(reverse(data), sample_rate)
sd.wait()

print("\n--- Echo (delay=0.2s, decay=0.5) ---")
sd.play(echo(data, delay_seconds=0.2, decay=0.5), sample_rate)
sd.wait()

print("\n--- Distorsio (drive=5.0) ---")
sd.play(distortion(data, drive=5.0), sample_rate)
sd.wait()

print("\n--- Tremolo (rate=5Hz, depth=0.7) ---")
sd.play(tremolo(data, rate=5.0, depth=0.7), sample_rate)
sd.wait()

print("\n--- Ring modulation (carrier=200Hz) ---")
sd.play(ring_modulation(data, carrier_freq=200.0), sample_rate)
sd.wait()

print("\n--- Playback speed x0.5 (mes lent i mes greu) ---")
data_slow, sr_slow = playback_speed(data, factor=0.5)
sd.play(data_slow, sr_slow)
sd.wait()

print("\n--- Playback speed x2.0 (mes rapid i mes agut) ---")
data_fast, sr_fast = playback_speed(data, factor=2.0)
sd.play(data_fast, sr_fast)
sd.wait()


# ---------------------------------------------------------------
# 4. DEMO — encadenar efectes
# ---------------------------------------------------------------
print("\n--- Cadena: distorsio + echo + fade out ---")
cadena = data
cadena = distortion(cadena, drive=4.0)
cadena = echo(cadena, delay_seconds=0.15, decay=0.4)
cadena = fade_out(cadena, duration=0.5)

sd.play(cadena, sample_rate)
sd.wait()

# Desar el resultat
sf.write("resultat_final.wav", cadena, sample_rate)
print("Desat com resultat_final.wav")


# ---------------------------------------------------------------
# 5. DEMO — l'error de referencia vs. copia
# ---------------------------------------------------------------
original = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

# MAL: referencia — modifica l'original!
result_mal = original
result_mal[0] = 999
print("\noriginal despres de modificar result_mal:", original)

original = np.array([1.0, 2.0, 3.0, 4.0, 5.0])  # reset

# BE: copia independent
result_be = np.copy(original)
result_be[0] = 999
print("original despres de modificar result_be:", original)
