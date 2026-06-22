"""
Solució de referència — S04: Pass-through i gain en temps real (sounddevice)
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida els 5 TODOs sense necessitar micròfon ni altaveu:
  - TODOs 1-3: callbacks provats amb arrays sintètics (mateixa lògica que l'autotest del fitxer)
  - TODO 4: observacions omplertes amb valors de referència
  - TODO 5: reflexió amb respostes de referència
La part interactiva (sd.Stream) no s'executa en mode validació.
"""

import numpy as np

sample_rate = 44100
blocksize = 1024


# ── TODO 1 — passthrough_callback ───────────────────────────────────────────

def passthrough_callback(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    # TODO 1: copia indata a outdata
    outdata[:] = indata


_in  = np.array([[0.1], [0.2], [0.3]], dtype='float32')
_out = np.zeros((3, 1), dtype='float32')
passthrough_callback(_in, _out, 3, None, None)
assert np.allclose(_out.flatten(), _in.flatten()), \
    "El callback no copia correctament l'entrada a la sortida"
print("✅ TODO 1 (passthrough_callback) correcte")


# ── TODO 2 — variable global 'gain' ─────────────────────────────────────────

# TODO 2: declara gain = 0.5
gain = 0.5

assert gain is not None, "Declara la variable 'gain'"
assert gain == 0.5, f"El gain inicial ha de ser 0.5, és {gain}"
print("✅ TODO 2 (gain = 0.5) correcte")


# ── TODO 3 — gain_callback ──────────────────────────────────────────────────

def gain_callback(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    # TODO 3: aplica gain a indata
    outdata[:] = indata * gain


_in  = np.array([[0.4], [0.8], [-0.4]], dtype='float32')
_out = np.zeros((3, 1), dtype='float32')
gain_callback(_in, _out, 3, None, None)
assert np.allclose(_out.flatten(), (_in * 0.5).flatten()), \
    f"Amb gain=0.5, outdata hauria de ser indata*0.5. Resultat: {_out.flatten()}"
print("✅ TODO 3 (gain_callback) correcte")


# ── TODO 4 — observacions blocksize ─────────────────────────────────────────
#
# Valors de referència (depenen de l'ordinador, però les tendències són fixes):
#   blocksize=256  → latència ~5.8 ms, perceptible=False (límit ~10ms), glitches possibles
#   blocksize=1024 → latència ~23.2 ms, perceptible=True, glitches=False (el més estable)
#   blocksize=2048 → latència ~46.4 ms, perceptible=True, glitches=False

observacions = {
    'blocksize_256': {
        'latencia_ms': round(256 / sample_rate * 1000, 1),    # 5.8
        'latencia_perceptible': False,
        'glitches': 'de vegades',
        'nota': 'Latència mínima però risc de glitch en ordinadors lents',
    },
    'blocksize_1024': {
        'latencia_ms': round(1024 / sample_rate * 1000, 1),   # 23.2
        'latencia_perceptible': True,
        'glitches': False,
        'nota': 'Bon equilibri entre latència i estabilitat (valor per defecte del curs)',
    },
    'blocksize_2048': {
        'latencia_ms': round(2048 / sample_rate * 1000, 1),   # 46.4
        'latencia_perceptible': True,
        'glitches': False,
        'nota': 'Molt estable, latència notòria però acceptable per a efectes no en viu',
    },
}

assert observacions['blocksize_256']['latencia_ms'] is not None
assert observacions['blocksize_1024']['latencia_ms'] is not None
print("✅ TODO 4 (observacions blocksize) omplertes")
for k, v in observacions.items():
    print(f"  {k}: latencia={v['latencia_ms']} ms, "
          f"perceptible={v['latencia_perceptible']}, glitches={v['glitches']}")


# ── TODO 5 — reflexió ───────────────────────────────────────────────────────

reflexio = {
    'per_que_global_es_necessaria':
        "El callback és cridat per un fil separat de l'àudio. La variable "
        "'gain' ha d'existir en un àmbit compartit (global o closure) perquè "
        "tant el callback com el bucle principal hi puguin accedir.",

    'per_que_global_es_lleig':
        "Les variables globals creen acoblament ocult: qualsevol part del codi "
        "pot modificar-les sense que el callback ho sàpiga. Amb classes o "
        "closures el state és encapsulat i és més fàcil raonar sobre qui el canvia.",

    'per_que_colab_no_funciona':
        "Colab corre el codi Python en un servidor remot sense accés al hardware "
        "d'àudio local. sounddevice necessita accés directe als drivers d'àudio "
        "del sistema operatiu (PortAudio). La WebAudio API del navegador sí que "
        "pot accedir al micròfon/altaveu del client via JavaScript perquè "
        "s'executa localment al navegador.",

    'trade_off_blocksize':
        "Blocksize petit → menys mostres per crida → latència menor (temps entre "
        "captura i reproducció), però el sistema operatiu ha de cridar el callback "
        "molt sovint. Si el callback tarda més que el blocksize en processar, "
        "el buffer s'esgota i es produeix un glitch (dropout). Blocksize gran → "
        "latència major però més marge de temps per al processament → menys glitches.",
}

for p, r in reflexio.items():
    assert r, f"Reflexió buida: {p}"
    print(f"✅ reflexio['{p}']: ✓")

print("\n✅ Tots els TODOs de S04 validats correctament.")
print("\nNOTA DOCENT — La Part 4 (reflexió) i Part 3 (observacions) admeten variació")
print("en la resposta de l'alumne; el criteri és la comprensió del trade-off latència/glitch.")
