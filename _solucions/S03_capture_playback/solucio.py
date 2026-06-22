"""
Solució de referència — S03: Efectes bàsics (echo, distortion, versió final)
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida els 5 TODOs del notebook S03 sense Colab ni àudio.
TODO 5 (versió final) s'exemplifica amb una combinació concreta de 2 efectes.
"""

import numpy as np

sample_rate = 44100

# Substitut del so d'entrada
np.random.seed(0)
data = (np.random.uniform(-0.4, 0.4, sample_rate * 2)).astype('float64')


# ── TODO 1 & 2 — echo ───────────────────────────────────────────────────────

def echo(data, delay_seconds, decay=0.5, sample_rate=44100):
    delay_samples = int(delay_seconds * sample_rate)
    # TODO 1: còpia (no referència!)
    result = np.copy(data)
    # TODO 2: suma l'eco retardat
    result[delay_samples:] += data[:-delay_samples] * decay
    return result


# Autotest 1
test_data = np.zeros(1000)
test_data[0] = 1.0
result = echo(test_data, delay_seconds=0.01, decay=0.5, sample_rate=44100)
assert len(result) == 1000
assert np.isclose(result[0], 1.0), "L'impuls original hauria de conservar-se"
assert result[441] > 0.4, f"Eco massa feble a 441 mostres: {result[441]:.3f}"

# Comprova que NO modifica l'original
original_copy = np.copy(test_data)
_ = echo(test_data, delay_seconds=0.01, decay=0.5)
assert np.array_equal(test_data, original_copy), "La funció modifica l'original! Usa np.copy()"
print("✅ TODO 1 & 2 (echo) correctes")


# ── TODO 3 & 4 — distortion ─────────────────────────────────────────────────

def distortion(data, drive=5.0, threshold=0.7):
    # TODO 3: amplifica i retalla
    clipped = np.clip(data * drive, -threshold, threshold)
    # TODO 4: normalitza
    return clipped / np.max(np.abs(clipped))


# Autotest 2
test_data = np.array([0.1, 0.5, 0.9, -0.5, -0.9])
result = distortion(test_data, drive=3.0, threshold=0.8)
assert np.isclose(np.max(np.abs(result)), 1.0), \
    f"Max absolut hauria de ser 1.0, és {np.max(np.abs(result)):.3f}"
assert np.isclose(abs(result[2]), abs(result[4])), \
    "Valors retallats haurien de tenir la mateixa amplitud absoluta"
print("✅ TODO 3 & 4 (distortion) correctes")


# ── TODO 5 — versió final (2+ efectes encadenats) ───────────────────────────
#
# Exemple de solució de referència: distorsió suau seguida d'eco curt.
# L'alumne pot triar qualsevol combinació; el criteri és que usa ≥2 efectes.
#
# Efectes auxiliars (proporcionats al notebook, repetits aquí per completesa):

def tremolo(data, rate=5.0, depth=0.5, sample_rate=44100):
    t = np.linspace(0, len(data)/sample_rate, len(data), endpoint=False)
    lfo = 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t))
    return data * lfo

def fade_out(data, duration, sample_rate=44100):
    n = min(int(duration * sample_rate), len(data))
    env = np.ones(len(data))
    env[-n:] = np.linspace(1, 0, n)
    return data * env


# Solució de referència per al TODO 5:
versio_final = distortion(data, drive=3.0, threshold=0.8)   # efecte 1
versio_final = echo(versio_final, delay_seconds=0.15, decay=0.4)  # efecte 2
versio_final = fade_out(versio_final, duration=0.5)                # opcional (bonus)

# Verificació mínima: el resultat és un array de la mateixa longitud
assert isinstance(versio_final, np.ndarray)
assert len(versio_final) == len(data)
print("✅ TODO 5 (versió final amb ≥2 efectes encadenats) correcte")

print("\n✅ Tots els TODOs de S03 validats correctament.")
print("\nNOTA DOCENT — TODO 5 és creatiu/obert: qualsevol combinació de ≥2 efectes")
print("del catàleg (echo, distortion, tremolo, delay_multi, reverse, ring_modulation...)")
print("és vàlida sempre que la variable 'versio_final' sigui un np.ndarray.")
