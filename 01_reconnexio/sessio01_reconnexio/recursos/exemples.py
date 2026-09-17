"""
Exemples — Bloc 1, Sessió 1 (versió Thonny)
El so com a array

Equivalent al notebook recursos/patches_bloc1.ipynb (Colab),
adaptat per executar-se localment amb Thonny + sounddevice.

Executa el fitxer per blocs (selecciona codi i fes "Run selection",
o comenta/descomenta seccions) per seguir la demo pas a pas.
"""

import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

sample_rate = 44100


# ---------------------------------------------------------------
# 1. L'eix de temps
# ---------------------------------------------------------------
duration = 1.0  # segons

t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

print("Nombre de mostres:", len(t))
print("Primers 10 valors de t:", t[:10])
print("Darrers 3 valors de t:", t[-3:])


# ---------------------------------------------------------------
# 2. Generar una ona sinusoidal
# ---------------------------------------------------------------
freq = 440  # Hz (un La4)

wave = np.sin(2 * np.pi * freq * t)

print("wave és un array de", len(wave), "valors")
print("Primers 10 valors:", wave[:10])


# ---------------------------------------------------------------
# 3. Visualitzar l'ona
# ---------------------------------------------------------------
n_samples_to_plot = 500  # uns ~11ms a 44100Hz

plt.plot(t[:n_samples_to_plot], wave[:n_samples_to_plot])
plt.xlabel("temps (s)")
plt.ylabel("amplitud")
plt.title(f"Ona sinusoidal a {freq} Hz")
plt.show()


# ---------------------------------------------------------------
# 4. Escoltar el resultat
# ---------------------------------------------------------------
sd.play(wave, sample_rate)
sd.wait()  # espera que acabi de sonar abans de continuar


# ---------------------------------------------------------------
# 5. DEMO EN DIRECTE — canviem la freqüència
#
# Pregunta a la classe abans d'executar: si canviem 'freq' a 220,
# sonarà més agut o més greu? I a 880?
# ---------------------------------------------------------------
freq = 220  # prova 220, després 880

wave = np.sin(2 * np.pi * freq * t)
sd.play(wave, sample_rate)
sd.wait()


# ---------------------------------------------------------------
# 6. DEMO EN DIRECTE — l'amplitud (volum)
#
# Pregunta: que passarà si multipliquem 'wave' per 0.1? I per 2.0?
# Recordeu el warm-up: array * número multiplica CADA element.
# ---------------------------------------------------------------
freq = 440
amplitude = 0.1  # prova 0.1, després 1.0, després 2.0 (atenció al clipping!)

wave = amplitude * np.sin(2 * np.pi * freq * t)
sd.play(wave, sample_rate)
sd.wait()

# Si amplitude > 1, el so es distorsiona ("clipping").
# L'àudio s'espera entre -1 i 1.


# ---------------------------------------------------------------
# 7. Empaquetar-ho en una funció
# ---------------------------------------------------------------
def generate_tone(freq, duration, amplitude=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * freq * t)
    return wave


my_tone = generate_tone(freq=330, duration=1.5, amplitude=0.3)
sd.play(my_tone, sample_rate)
sd.wait()


# ---------------------------------------------------------------
# 8. Preview — altres formes d'ona
# (Només per escoltar la diferència de timbre. Es treballa al Bloc 5.)
# ---------------------------------------------------------------
from scipy import signal

freq = 220
square_wave = 0.3 * signal.square(2 * np.pi * freq * t)
sawtooth_wave = 0.3 * signal.sawtooth(2 * np.pi * freq * t)
noise = 0.3 * np.random.uniform(-1, 1, len(t))

print("Quadrada:")
sd.play(square_wave, sample_rate)
sd.wait()

print("Serra:")
sd.play(sawtooth_wave, sample_rate)
sd.wait()

print("Soroll:")
sd.play(noise, sample_rate)
sd.wait()
