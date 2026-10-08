"""
SOLUCIÓ DE REFERÈNCIA — Sessió 3 (Bloc 3a): captura, playback i efectes offline
DOCENT — no distribuir als alumnes.

Implementació correcta de les dues funcions amb TODO de l'assignment:
  - echo        : amb barreja sec/processat (dry/wet) via paràmetre 'mix'
  - distortion  : saturació suau amb np.tanh (no retall dur)
Inclou un harness d'autotests que s'executa sense àudio real (només NumPy):
    python3 solucio.py
"""
import numpy as np


# ---------- Funcions amb TODO (solució) ----------

def echo(data, delay_seconds, decay=0.5, mix=0.5, sample_rate=44100):
    delay_samples = int(delay_seconds * sample_rate)
    wet = np.copy(data)                                  # còpia: el +=  modifica en el lloc
    wet[delay_samples:] += data[:-delay_samples] * decay  # senyal processat (original + eco)
    return (1 - mix) * data + mix * wet                   # barreja sec/processat


def distortion(data, drive=5.0):
    shaped = np.tanh(data * drive)                        # saturació suau (no clip dur)
    return shaped / np.max(np.abs(shaped))                # normalitza a amplitud 1


# ---------- Efectes ja donats a l'alumne (catàleg), per referència ----------

def reverse(data):
    return data[::-1]

def fade_in(data, duration, sample_rate=44100):
    n = min(int(duration * sample_rate), len(data))
    env = np.ones(len(data)); env[:n] = np.linspace(0, 1, n)
    return data * env

def fade_out(data, duration, sample_rate=44100):
    n = min(int(duration * sample_rate), len(data))
    env = np.ones(len(data)); env[-n:] = np.linspace(1, 0, n)
    return data * env

def delay_multi(data, delay_seconds, decay=0.5, n_repeats=4, sample_rate=44100):
    result = np.copy(data)
    d = int(delay_seconds * sample_rate)
    for i in range(1, n_repeats + 1):
        start = i * d
        if start >= len(data): break
        result[start:] += data[:len(data) - start] * (decay ** i)
    return result

def tremolo(data, rate=5.0, depth=0.5, sample_rate=44100):
    t = np.linspace(0, len(data)/sample_rate, len(data), endpoint=False)
    lfo = 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t))
    return data * lfo

def ring_modulation(data, carrier_freq=200.0, sample_rate=44100):
    t = np.linspace(0, len(data)/sample_rate, len(data), endpoint=False)
    return data * np.sin(2 * np.pi * carrier_freq * t)

def playback_speed(data, factor, sample_rate=44100):
    return data, int(sample_rate * factor)


# ---------- Autotests (harness sense hardware) ----------

if __name__ == "__main__":
    # Part 1 — echo (dry/wet)
    x = np.zeros(1000); x[0] = 1.0
    r = echo(x, 0.01, 0.5, mix=1.0)
    assert r is not None and len(r) == 1000
    assert np.isclose(r[0], 1.0)
    assert r[441] > 0.4
    assert np.isclose(echo(x, 0.01, 0.5, mix=0.0)[441], 0.0)
    xc = np.copy(x); _ = echo(x, 0.01, 0.5, mix=1.0)
    assert np.array_equal(x, xc)
    print("✅ Part 1 (echo dry/wet) OK")

    # Part 2 — distortion (tanh)
    td = np.array([0.1, 0.5, 0.9, -0.5, -0.9])
    rd = distortion(td, drive=3.0)
    assert len(rd) == 5
    assert np.isclose(np.max(np.abs(rd)), 1.0)
    assert np.isclose(rd[2], -rd[4])
    assert abs(rd[0]) < abs(rd[1]) < abs(rd[2])
    print("✅ Part 2 (distortion tanh) OK")

    print("\n✅ Totes les solucions passen els autotests.")
