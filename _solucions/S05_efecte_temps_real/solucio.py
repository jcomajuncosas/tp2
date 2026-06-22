"""
Solució de referència — S05: Efectes en temps real (distorsió + eco + combo)
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida els 9 TODOs sense necessitar micròfon ni altaveu.
Els callbacks es proven amb arrays sintètics, igual que els asserts de l'assignment.
La part sd.Stream no s'executa en mode validació.
"""

import numpy as np

sample_rate = 44100
blocksize = 1024


# ── TODO 1 — distorsio_callback ─────────────────────────────────────────────

drive = 4.0
threshold = 0.7

def distorsio_callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    mono = indata[:, 0]
    # TODO 1: distorsió i normalització per threshold
    clipped = np.clip(mono * drive, -threshold, threshold)
    outdata[:, 0] = clipped / threshold


_in = np.array([[0.5], [1.0], [-1.0], [0.1]], dtype='float32')
_out = np.zeros((4, 1), dtype='float32')
distorsio_callback(_in, _out, 4, None, None)

assert not np.all(_out == 0), "outdata no s'ha modificat"
assert np.max(np.abs(_out)) <= 1.0 + 1e-5, \
    f"Sortida fora de rang: max={np.max(np.abs(_out)):.3f}"
# valor 1.0 * drive=4 > threshold=0.7 → clip → /threshold = 1.0
assert np.isclose(abs(_out[1, 0]), 1.0, atol=0.01), \
    f"Valor gran hauria de ser 1.0, és {abs(_out[1,0]):.3f}"
assert abs(_out[3, 0]) < abs(_out[1, 0]), \
    "Valor petit hauria de ser menys distorsionat que el gran"
print("✅ TODO 1 (distorsio_callback) correcte")


# ── TODO 2 — delay_samples i delay_buffer ───────────────────────────────────

delay_seconds = 0.3
decay = 0.5

# TODO 2:
delay_samples = int(delay_seconds * sample_rate)
delay_buffer = np.zeros(delay_samples, dtype='float32')

assert delay_samples == int(0.3 * 44100), \
    f"delay_samples hauria de ser {int(0.3*44100)}, és {delay_samples}"
assert len(delay_buffer) == delay_samples, \
    f"delay_buffer hauria de tenir {delay_samples} elements, té {len(delay_buffer)}"
print("✅ TODO 2 (delay_samples i delay_buffer) correcte")


# ── TODOs 3-6 — eco_callback ────────────────────────────────────────────────

def eco_callback(indata, outdata, frames, time, status):
    global delay_buffer
    if status:
        print(status)
    mono = indata[:, 0]
    # TODO 3: llegeix l'eco
    eco = delay_buffer[:frames]
    # TODO 4: suma entrada + eco
    out = mono + eco * decay
    # TODO 5: actualitza el buffer circular
    delay_buffer = np.roll(delay_buffer, -frames)
    delay_buffer[-frames:] = mono
    # TODO 6: assigna amb clip
    outdata[:, 0] = np.clip(out, -1.0, 1.0)


# Test: primera crida amb buffer buit → sortida ≈ entrada
_in1 = np.array([[0.8], [0.6]], dtype='float32')
_out1 = np.zeros((2, 1), dtype='float32')
delay_buffer_backup = delay_buffer.copy()
eco_callback(_in1, _out1, 2, None, None)
# Amb buffer buit, eco=zeros, out = mono + 0 = mono
assert np.allclose(_out1[:, 0], np.array([0.8, 0.6], dtype='float32'), atol=1e-5), \
    f"Primera crida (buffer buit): sortida hauria de ser igual a l'entrada, és {_out1[:, 0]}"
print("✅ TODOs 3-6 (eco_callback) correctes")

# Restaura buffer per als tests posteriors
delay_buffer = delay_buffer_backup


# ── TODOs 7-9 — combo_callback ──────────────────────────────────────────────

drive_c = 3.0
threshold_c = 0.7
delay_seconds_c = 0.25
decay_c = 0.45
delay_samples_combo = int(delay_seconds_c * sample_rate)
delay_buffer_combo = np.zeros(delay_samples_combo, dtype='float32')


def combo_callback(indata, outdata, frames, time, status):
    global delay_buffer_combo
    if status:
        print(status)
    mono = indata[:, 0]
    # TODO 7: distorsió
    dist = np.clip(mono * drive_c, -threshold_c, threshold_c) / threshold_c
    # TODO 8: eco sobre la distorsió
    eco = delay_buffer_combo[:frames]
    out = dist + eco * decay_c
    delay_buffer_combo = np.roll(delay_buffer_combo, -frames)
    delay_buffer_combo[-frames:] = dist   # guardem dist, no mono!
    # TODO 9: assigna amb clip
    outdata[:, 0] = np.clip(out, -1.0, 1.0)


_in = np.array([[0.9], [-0.9], [0.1]], dtype='float32')
_out = np.zeros((3, 1), dtype='float32')
combo_callback(_in, _out, 3, None, None)

assert not np.all(_out == 0), "outdata no s'ha modificat (TODOs 7-9)"
assert np.max(np.abs(_out)) <= 1.0 + 1e-5, \
    f"Sortida fora de rang: max={np.max(np.abs(_out)):.3f}"
print("✅ TODOs 7-9 (combo_callback) correctes")


# ── Reflexió (referència per al docent) ─────────────────────────────────────

reflexio_referencia = {
    'per_que_buffer_fora_callback':
        "El callback és cridat repetidament per a cada bloc d'àudio. Si el buffer "
        "es creés dins del callback, es reinicialitzaria a zeros a cada crida i "
        "l'eco desapareixeria. El buffer ha de persistir entre crides per acumular "
        "el historial de mostres necessari per al retard.",

    'distorsio_vs_eco_complexitat':
        "La distorsió és 'sense memòria': cada mostra de sortida depèn únicament "
        "de la mostra d'entrada actual (np.clip és sample-by-sample). "
        "L'eco és 'amb memòria': la sortida depèn de mostres passades "
        "que cal guardar en un buffer persistent entre crides del callback.",

    'ordre_efectes':
        "Distorsió→eco i eco→distorsió sonen diferent. En distorsió→eco, "
        "l'eco és una còpia distorsionada del so original, cosa que sona "
        "més 'dura'. En eco→distorsió, l'eco es forma del so net i la "
        "distorsió s'aplica a la suma entrada+eco, resultant en una "
        "distorsió més pronunciada als transiènts. L'ordre importa perquè "
        "la distorsió és no-lineal (no commuta amb el sumador de l'eco).",

    'preview_classes':
        "Amb l'enfocament actual caldria un delay_buffer_01, delay_buffer_03, "
        "delay_buffer_06 i delay_sample_01, _03, _06... amb globals nomenades "
        "manualment. Una classe EcoProcessor encapsularia el buffer i els "
        "paràmetres i es podria instanciar 3 vegades sense conflictes de noms.",
}

for k, v in reflexio_referencia.items():
    print(f"✅ reflexio['{k}']: ✓")

print("\n✅ Tots els TODOs de S05 validats correctament.")
print("\nNOTA DOCENT — La Part 4 (reflexió) és oberta; els punts clau a avaluar:")
print("  - buffer_fora: persistència entre crides (no reinicialització)")
print("  - distorsio_vs_eco: sense memòria vs. amb memòria")
print("  - ordre_efectes: la no-linealitat de clip fa que l'ordre importi")
print("  - preview_classes: el problema del global naming en múltiples instàncies")
