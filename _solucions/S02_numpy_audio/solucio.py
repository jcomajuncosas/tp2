"""
Solució de referència — S02: Audio Manipulator (loop + efectes bàsics)
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida els 4 TODOs (4c comptats) del notebook S02 sense Colab ni àudio.
Substituïm la càrrega de fitxer real per un array sintètic.
"""

import numpy as np

sample_rate = 44100

# Substitut del so d'entrada (en lloc de librosa.load)
np.random.seed(42)
input_data = np.random.uniform(-0.3, 0.3, sample_rate * 2).astype('float32')
perc = np.random.uniform(-0.4, 0.4, sample_rate).astype('float32')


# ── TODO 1 — apply_gain ─────────────────────────────────────────────────────

def apply_gain(data, factor):
    return data * factor


# Autotest 1
test_data = np.array([0.4, -0.4, 0.2])
result = apply_gain(test_data, 0.5)
assert np.allclose(result, np.array([0.2, -0.2, 0.1])), f"Resultat incorrecte: {result}"
print("✅ TODO 1 (apply_gain) correcte")


# ── TODO 2 — apply_fade_out ──────────────────────────────────────────────────

def apply_fade_out(data, fade_duration, sample_rate=44100):
    fade_samples = int(fade_duration * sample_rate)
    fade_samples = min(fade_samples, len(data))
    envelope = np.ones(len(data))
    # TODO 2: substitueix els últims fade_samples per linspace(1,0)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    return data * envelope


# Autotest 2
test_data = np.ones(1000)
result = apply_fade_out(test_data, fade_duration=0.01, sample_rate=44100)
assert len(result) == 1000
assert np.isclose(result[0], 1.0)
assert result[-1] < 0.01
assert result[500] > result[-1]
print("✅ TODO 2 (apply_fade_out) correcte")


# ── TODO 3 — make_loop ──────────────────────────────────────────────────────

def make_loop(data, n_repeats):
    return np.tile(data, n_repeats)


# Autotest 3
test_data = np.array([1, 2, 3])
result = make_loop(test_data, 3)
assert len(result) == 9
assert np.array_equal(result, np.array([1, 2, 3, 1, 2, 3, 1, 2, 3]))
print("✅ TODO 3 (make_loop) correcte")


# ── TODO 4a-4c — mix_sounds ─────────────────────────────────────────────────

def mix_sounds(data1, data2):
    # TODO 4a: mínima longitud
    n = min(len(data1), len(data2))
    # TODO 4b: suma retallada
    mix = data1[:n] + data2[:n]
    # TODO 4c: normalitza
    mix = mix / np.max(np.abs(mix))
    return mix


# Autotest 4
test_a = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
test_b = np.array([0.5, 0.5, 0.5])
result = mix_sounds(test_a, test_b)
assert len(result) == 3, f"Longitud incorrecta: {len(result)}"
assert np.isclose(np.max(np.abs(result)), 1.0), f"Max hauria de ser 1.0, és {np.max(np.abs(result))}"
print("✅ TODO 4a-4c (mix_sounds) correcte")

# Integració: apliquem tot el pipeline
my_loop   = make_loop(input_data, 2)
perc_loop = make_loop(perc, 2)
final_mix = mix_sounds(apply_gain(my_loop, 1.0), apply_gain(perc_loop, 0.7))
final_mix = apply_fade_out(final_mix, fade_duration=1.0, sample_rate=sample_rate)
assert np.max(np.abs(final_mix)) <= 1.0 + 1e-6
print("✅ Pipeline complet (loop + mix + fade) correcte")

print("\n✅ Tots els TODOs de S02 validats correctament.")
