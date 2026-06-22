"""
Assignment — Bloc 3c, Sessió 5
Mini-repte: Efectes en temps real — eco i distorsió

IMPORTANT: executa amb Thonny (entorn local). NO funciona a Colab.
Un cop completat, puja aquest fitxer al Classroom.

Completa les seccions marcades amb # TODO.
Cada part té asserts per verificar la lògica (sense necessitar hardware).
"""

import sounddevice as sd
import numpy as np

sample_rate = 44100
blocksize = 1024


# ---------------------------------------------------------------
# PART 1 — Implementa el callback de distorsió
#
# El callback ha d'aplicar:
#   1. Amplificar l'entrada per 'drive'
#   2. Retallar entre -threshold i +threshold (np.clip)
#   3. Normalitzar dividint per threshold
#   4. Assignar el resultat a outdata[:, 0]
# ---------------------------------------------------------------
print("=== PART 1: Distorsió en temps real ===")

drive = 4.0
threshold = 0.7

def distorsio_callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    mono = indata[:, 0]

    # TODO 1: aplica distorsió a 'mono' i assigna a outdata[:, 0]
    # clipped = np.clip(mono * drive, -threshold, threshold)
    # outdata[:, 0] = clipped / threshold
    pass  # <-- substitueix


# Verificació sense hardware
_in = np.array([[0.5], [1.0], [-1.0], [0.1]], dtype='float32')
_out = np.zeros((4, 1), dtype='float32')
distorsio_callback(_in, _out, 4, None, None)

assert not np.all(_out == 0), "outdata no s'ha modificat — implementa el TODO 1"
assert np.max(np.abs(_out)) <= 1.0 + 1e-5, \
    f"La sortida hauria d'estar entre -1 i 1, max={np.max(np.abs(_out)):.3f}"
# Amb drive=4 i threshold=0.7, el valor 1.0 ha de quedar retallat:
# 1.0 * 4 = 4.0 > 0.7 → clip a 0.7 → / 0.7 = 1.0
assert np.isclose(abs(_out[1, 0]), 1.0, atol=0.01), \
    f"Un valor gran hauria de quedar normalitzat a 1.0, és {abs(_out[1,0]):.3f}"
# Un valor petit (0.1) no ha de quedar retallat:
# 0.1 * 4 = 0.4 < 0.7 → no clip → 0.4 / 0.7 ≈ 0.571
assert abs(_out[3, 0]) < abs(_out[1, 0]), \
    "Un valor petit hauria de quedar menys distorsionat que un gran"

print("✅ Part 1 correcta!")
print("\nExecutant distorsió en temps real durant 8 segons. Parla o fes un so...")
try:
    with sd.Stream(samplerate=sample_rate, blocksize=blocksize,
                   channels=1, dtype='float32', callback=distorsio_callback):
        sd.sleep(8000)
except KeyboardInterrupt:
    pass
print("Part 1 feta.\n")


# ---------------------------------------------------------------
# PART 2 — Implementa el callback d'eco
#
# Necessites:
#   1. Un buffer global 'delay_buffer' de mida delay_samples
#   2. El callback llegeix les darreres 'frames' mostres del buffer (eco)
#   3. Suma l'entrada + eco*decay
#   4. Actualitza el buffer (np.roll + assignar les mostres noves)
#   5. Assigna la sortida a outdata[:, 0] (amb clip de seguretat)
# ---------------------------------------------------------------
print("=== PART 2: Eco en temps real ===")

delay_seconds = 0.3
decay = 0.5

# TODO 2: calcula delay_samples i crea delay_buffer (np.zeros)
delay_samples = None   # <-- int(delay_seconds * sample_rate)
delay_buffer = None    # <-- np.zeros(delay_samples, dtype='float32')


def eco_callback(indata, outdata, frames, time, status):
    global delay_buffer
    if status:
        print(status)
    mono = indata[:, 0]

    # TODO 3: llegeix l'eco del buffer (les darreres 'frames' mostres)
    eco = None  # <-- delay_buffer[:frames]

    # TODO 4: calcula la sortida (entrada + eco*decay)
    out = None  # <-- mono + eco * decay

    # TODO 5: actualitza el buffer (roll + assignar mono a les darreres frames)
    # delay_buffer = np.roll(delay_buffer, -frames)
    # delay_buffer[-frames:] = mono  # escriptura: correcte

    # TODO 6: assigna a outdata[:, 0] amb clip de seguretat
    # outdata[:, 0] = np.clip(out, -1.0, 1.0)
    pass  # <-- substitueix aquest pass quan hagis completat tots els TODOs


# Verificació sense hardware
assert delay_samples is not None, "Calcula delay_samples (TODO 2)"
assert delay_buffer is not None, "Crea delay_buffer (TODO 2)"
assert delay_samples == int(0.3 * 44100), \
    f"delay_samples hauria de ser {int(0.3*44100)}, és {delay_samples}"
assert len(delay_buffer) == delay_samples, \
    f"delay_buffer hauria de tenir {delay_samples} elements, té {len(delay_buffer)}"

# Test funcional: simulem dues crides
delay_buffer_test = np.zeros(10, dtype='float32')
_in1 = np.array([[0.8], [0.6]], dtype='float32')
_out1 = np.zeros((2, 1), dtype='float32')

# Fem una còpia temporal per al test
_db_backup = delay_buffer.copy()

# Primera crida: eco hauria de ser zeros (buffer buit)
# Provem la lògica manualment
eco_test = delay_buffer_test[-2:]
out_test = np.array([0.8, 0.6]) + eco_test * 0.5
assert np.allclose(out_test, [0.8, 0.6]), \
    f"Primera crida: sense eco, la sortida hauria de ser igual a l'entrada. Got {out_test}"

print("✅ Part 2: estructura correcta!")
print("\nExecutant eco en temps real durant 10 segons. Parla i escolta l'eco...")
try:
    with sd.Stream(samplerate=sample_rate, blocksize=blocksize,
                   channels=1, dtype='float32', callback=eco_callback):
        # Control interactiu del decay
        while True:
            try:
                cmd = input(f"decay={decay:.2f} → nou valor (0.0-0.95) o 'q': ")
                if cmd.lower() == 'q':
                    break
                nou = float(cmd)
                if 0.0 <= nou <= 0.95:
                    decay = nou
                    print(f"Decay → {decay:.2f}")
            except (ValueError, KeyboardInterrupt):
                break
except KeyboardInterrupt:
    pass
print("Part 2 feta.\n")


# ---------------------------------------------------------------
# PART 3 — Combina distorsió + eco en un sol callback
#
# Ordre: aplica distorsió primer, eco sobre el resultat.
# Guarda la distorsió (no l'entrada raw) al buffer de retard.
# ---------------------------------------------------------------
print("=== PART 3: Distorsió + Eco combinats ===")

drive = 3.0
threshold = 0.7
delay_seconds = 0.25
decay = 0.45
delay_samples_combo = int(delay_seconds * sample_rate)
delay_buffer_combo = np.zeros(delay_samples_combo, dtype='float32')

def combo_callback(indata, outdata, frames, time, status):
    global delay_buffer_combo
    if status:
        print(status)
    mono = indata[:, 0]

    # TODO 7: aplica distorsió a mono → resultat en 'dist'
    dist = None  # <-- np.clip(mono * drive, -threshold, threshold) / threshold

    # TODO 8: aplica eco a 'dist' usant delay_buffer_combo → resultat en 'out'
    # eco = delay_buffer_combo[:frames]
    # out = dist + eco * decay
    # delay_buffer_combo = np.roll(delay_buffer_combo, -frames)
    # delay_buffer_combo[-frames:] = dist  # guardem dist, no mono!
    out = None  # <-- substitueix

    # TODO 9: assigna a outdata[:, 0] amb clip
    pass  # <-- substitueix


# Verificació
_in = np.array([[0.9], [-0.9], [0.1]], dtype='float32')
_out = np.zeros((3, 1), dtype='float32')
combo_callback(_in, _out, 3, None, None)

assert not np.all(_out == 0), "outdata no s'ha modificat — implementa els TODOs 7-9"
assert np.max(np.abs(_out)) <= 1.0 + 1e-5, \
    f"La sortida hauria d'estar entre -1 i 1, max={np.max(np.abs(_out)):.3f}"

print("✅ Part 3 correcta!")
print("\nExecutant distorsió + eco durant 10 segons...")
try:
    with sd.Stream(samplerate=sample_rate, blocksize=blocksize,
                   channels=1, dtype='float32', callback=combo_callback):
        sd.sleep(10000)
except KeyboardInterrupt:
    pass
print("Part 3 feta.\n")


# ---------------------------------------------------------------
# PART 4 — Reflexió
# ---------------------------------------------------------------
print("=== PART 4: Reflexió ===")

reflexio = {
    'per_que_buffer_fora_callback':
        '',  # Per qué el delay_buffer ha d'estar fora del callback
             # (i no crear-lo dins cada crida)?

    'distorsio_vs_eco_complexitat':
        '',  # Per qué la distorsió és més simple d'implementar en temps
             # real que l'eco? Quina diferència fonamental hi ha?

    'ordre_efectes':
        '',  # Has provat distorsió→eco i eco→distorsió?
             # Sonen diferent? Per qué creus que és?

    'preview_classes':
        '',  # Si volguessis tenir 3 ecos simultanis (delays 0.1s, 0.3s, 0.6s)
             # amb l'enfocament actual (buffer global), com ho faries?
             # Quin problema veus? Com ho solucionaria una classe?
}

for p, r in reflexio.items():
    if r:
        print(f"\n{p}:\n  {r}")
    else:
        print(f"\n⚠️  {p}: pendent de respondre")


# ---------------------------------------------------------------
# 🚀 CHALLENGE (opcional) — Stutter en temps real
#
# El stutter repeteix ràpidament un fragment curt del so mentre continua.
# Pistes:
#   - Necessites un 'stutter_buffer' que guarda N mostres
#   - Un flag 'stutter_actiu' (bool global) que actives/desactives
#   - Quan stutter_actiu=True: el callback reprodueix stutter_buffer
#     repetidament (en bucle) en lloc de l'entrada normal
#   - Quan stutter_actiu=False: el callback funciona com a pass-through
#     i actualitza stutter_buffer amb les mostres actuals
#   - Activa/desactiva des del programa principal (ex: tecla Enter)
# ---------------------------------------------------------------
print("\n🚀 Challenge: Stutter (opcional)")
print("Implementa el stutter seguint les pistes de l'enunciat.")
print("Pots afegir el teu codi a continuació.\n")

# El teu codi del stutter aquí

print("\n--- Fi de l'assignment ---")
print("Puja aquest fitxer (.py) al Classroom un cop completat.")
