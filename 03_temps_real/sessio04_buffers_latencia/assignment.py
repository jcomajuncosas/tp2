"""
Assignment — Bloc 3b, Sessió 4
Mini-repte: Pass-through amb gain en temps real

IMPORTANT: executa amb Thonny (entorn local). NO funciona a Colab.
Un cop completat, puja aquest fitxer al Classroom.

Completa les seccions marcades amb # TODO.
Cada part té un test manual (escolta el resultat) i una comprovació de codi.
"""

import sounddevice as sd
import numpy as np
import time

sample_rate = 44100
blocksize = 1024


# ---------------------------------------------------------------
# PART 1 — Pass-through bàsic
#
# Implementa un callback que copiï l'entrada a la sortida
# sense cap modificació. Has de sentir la teva veu
# amb la latència del buffer (~23ms amb blocksize=1024).
# ---------------------------------------------------------------
print("=== PART 1: Pass-through ===")

def passthrough_callback(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    # TODO 1: copia indata a outdata
    # Pista: outdata[:] = ...
    pass  # <-- substitueix aquest 'pass'


# Comprovació funcional: simulem una crida amb arrays de prova
_in  = np.array([[0.1], [0.2], [0.3]], dtype='float32')
_out = np.zeros((3, 1), dtype='float32')
passthrough_callback(_in, _out, 3, None, None)
assert np.allclose(_out.flatten(), _in.flatten()), \
    "El callback no copia correctament l'entrada a la sortida"
print("✅ Part 1 correcta: el callback fa pass-through")

print("\nExecutant pass-through durant 6 segons. Parla o fes un so...")
try:
    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   callback=passthrough_callback):
        sd.sleep(6000)
except KeyboardInterrupt:
    pass
print("Part 1 feta.\n")


# ---------------------------------------------------------------
# PART 2 — Gain en temps real
#
# Implementa un callback que apliqui un gain variable.
# El gain es controla des del bucle principal (input).
# ---------------------------------------------------------------
print("=== PART 2: Gain en temps real ===")

# TODO 2: declara una variable global 'gain' amb valor inicial 0.5
gain = None  # <-- substitueix per gain = 0.5


def gain_callback(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    # TODO 3: aplica el gain a indata i assigna el resultat a outdata[:]
    pass  # <-- substitueix aquest 'pass'


# Comprovació funcional
assert gain is not None, "Declara la variable 'gain'"
assert gain == 0.5, f"El gain inicial ha de ser 0.5, és {gain}"
_in  = np.array([[0.4], [0.8], [-0.4]], dtype='float32')
_out = np.zeros((3, 1), dtype='float32')
gain_callback(_in, _out, 3, None, None)
assert np.allclose(_out.flatten(), (_in * 0.5).flatten()), \
    f"Amb gain=0.5, outdata hauria de ser indata*0.5. Resultat: {_out.flatten()}"
print("✅ Part 2 correcta: el callback aplica el gain")

print("\nEscriu un número entre 0.0 i 2.0 per canviar el gain.")
print("Escriu 'q' per passar a la Part 3.\n")

with sd.Stream(samplerate=sample_rate,
               blocksize=blocksize,
               channels=1,
               dtype='float32',
               callback=gain_callback):
    while True:
        try:
            entrada = input(f"Gain actual: {gain:.2f} → nou valor (o 'q'): ")
            if entrada.lower() == 'q':
                break
            nou_gain = float(entrada)
            if 0.0 <= nou_gain <= 2.0:
                gain = nou_gain
            else:
                print("Valor fora de rang (0.0 - 2.0)")
        except ValueError:
            print("Escriu un número vàlid")
        except KeyboardInterrupt:
            break

print("Part 2 feta.\n")


# ---------------------------------------------------------------
# PART 3 — Experimentar amb blocksize i latència
#
# Canvia el valor de 'blocksize' i observa com canvia la latència
# i el risc de glitch. Omple les observacions al final.
# ---------------------------------------------------------------
print("=== PART 3: Blocksize i latència ===")

for bs in [128, 512, 2048]:
    latència = bs / sample_rate * 1000
    print(f"blocksize={bs:4d} → latència teòrica: {latència:.1f} ms")

print("\nProva a canviar 'blocksize' al principi del fitxer a 256 i a 2048.")
print("Per a cada valor, executa la Part 2 i nota si la latència és perceptible.")

# TODO 4: Omple les teves observacions (edita el text entre cometes)
observacions = {
    'blocksize_256': {
        'latencia_ms': None,        # <-- substitueix per el valor calculat
        'latencia_perceptible': None,  # <-- True o False
        'glitches': None,           # <-- True, False o 'de vegades'
        'nota': '',                 # <-- comentari lliure
    },
    'blocksize_1024': {
        'latencia_ms': None,
        'latencia_perceptible': None,
        'glitches': None,
        'nota': '',
    },
    'blocksize_2048': {
        'latencia_ms': None,
        'latencia_perceptible': None,
        'glitches': None,
        'nota': '',
    },
}

# Comprovació mínima
assert observacions['blocksize_256']['latencia_ms'] is not None, \
    "Omple les observacions de blocksize=256"
assert observacions['blocksize_1024']['latencia_ms'] is not None, \
    "Omple les observacions de blocksize=1024"

print("\n✅ Observacions registrades")
for bs_key, obs in observacions.items():
    print(f"\n{bs_key}:")
    for k, v in obs.items():
        print(f"  {k}: {v}")


# ---------------------------------------------------------------
# PART 4 — Reflexió (edita el text)
# ---------------------------------------------------------------
print("\n=== PART 4: Reflexió ===")

# TODO 5: Respon a les preguntes editant les strings
reflexio = {
    'per_que_global_es_necessaria':
        '',  # Per qué la variable 'gain' ha de ser accessible des del callback?

    'per_que_global_es_lleig':
        '',  # Per qué dir que la variable global és "lleig" com a solució?

    'per_que_colab_no_funciona':
        '',  # Explica per qué el codi d'aquesta sessió no funciona a Colab
              # però sí que funciona WebAudio API al navegador.

    'trade_off_blocksize':
        '',  # Descriu el trade-off entre blocksize petit i blocksize gran
}

for pregunta, resposta in reflexio.items():
    if resposta:
        print(f"\n{pregunta}:\n  {resposta}")
    else:
        print(f"\n⚠️  {pregunta}: pendent de respondre")

print("\n--- Fi de l'assignment ---")
print("Puja aquest fitxer (.py) al Classroom un cop completat.")
