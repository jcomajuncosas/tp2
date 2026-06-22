"""
Solució de referència — S01: Generar un to pur i modular-ne freqüència i amplitud
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida els 6 TODOs del notebook S01 sense necessitar Colab ni àudio.
"""

import numpy as np

sample_rate = 44100

# ── TODO 1 & 2 — generate_tone ──────────────────────────────────────────────

def generate_tone(freq, duration, amplitude=0.5, sample_rate=44100):
    # TODO 1: eix de temps
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # TODO 2: ona sinusoïdal
    wave = amplitude * np.sin(2 * np.pi * freq * t)
    return wave


# Autotest 1
test_wave = generate_tone(freq=440, duration=1.0, amplitude=0.5, sample_rate=44100)
assert isinstance(test_wave, np.ndarray)
assert len(test_wave) == 44100, f"S'esperaven 44100 mostres, n'hi ha {len(test_wave)}"
assert np.max(np.abs(test_wave)) <= 0.5 + 1e-6
assert np.max(np.abs(test_wave)) > 0.4
print("✅ TODO 1 & 2 (generate_tone) correctes")


# ── TODO 3 & 4 — generate_sweep ─────────────────────────────────────────────

def generate_sweep(freq_start, freq_end, duration, amplitude=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # TODO 3: freqüència variable lineal
    freq = np.linspace(freq_start, freq_end, len(t))
    # TODO 4: ona amb freq variable
    wave = amplitude * np.sin(2 * np.pi * freq * t)
    return wave


# Autotest 2
sweep_wave = generate_sweep(freq_start=220, freq_end=880, duration=2.0, amplitude=0.5)
assert len(sweep_wave) == 44100 * 2
zero_crossings = np.where(np.diff(np.sign(sweep_wave)))[0]
first_half_density  = np.sum(zero_crossings < len(sweep_wave) // 2)
second_half_density = np.sum(zero_crossings >= len(sweep_wave) // 2)
assert second_half_density > first_half_density, \
    "La freqüència no augmenta — revisa l'array 'freq'"
print("✅ TODO 3 & 4 (generate_sweep) correctes")


# ── TODO 5 & 6 — generate_tone_with_envelope ────────────────────────────────

def generate_tone_with_envelope(freq, duration, amplitude=0.5, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    half = n_samples // 2
    # TODO 5: envolvent triangular
    rise = np.linspace(0, amplitude, half)
    fall = np.linspace(amplitude, 0, n_samples - half)
    envelope = np.concatenate([rise, fall])
    # TODO 6: aplica envolvent
    wave = envelope * np.sin(2 * np.pi * freq * t)
    return wave


# Autotest 3
env_wave = generate_tone_with_envelope(freq=440, duration=2.0, amplitude=0.5)
assert len(env_wave) == 44100 * 2
start_amp  = np.max(np.abs(env_wave[:100]))
middle_amp = np.max(np.abs(env_wave[44090:44190]))
end_amp    = np.max(np.abs(env_wave[-100:]))
assert start_amp  < 0.05, f"Inici no és silenci: {start_amp:.3f}"
assert end_amp    < 0.05, f"Final no és silenci: {end_amp:.3f}"
assert middle_amp > 0.30, f"Centre massa baix: {middle_amp:.3f}"
print("✅ TODO 5 & 6 (generate_tone_with_envelope) correctes")

print("\n✅ Tots els TODOs de S01 validats correctament.")
