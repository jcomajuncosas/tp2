"""
Assignment — Bloc 3b, Sessió 4
Mini-repte: callbacks en temps real (pass-through, gain, distorsió)

⚠️  AURICULARS OBLIGATORIS. Micròfon + altaveus = realimentació (Larsen).

IMPORTANT: executa amb Thonny (entorn local). NO funciona a Colab.
Un cop completat, puja aquest fitxer al Classroom.

COM TREBALLAR-HI A THONNY:
  1. Completa un TODO.
  2. Prem F5 (Run). Això només DEFINEIX les funcions; no sona res.
  3. A la consola (Shell), crida la funció d'escolta d'aquella part:
         >>> escolta_part1()
     Cada escolta_partN() primer comprova la teva callback i, si és
     correcta, obre l'stream perquè la sentis.
  4. Passa al TODO següent. Pots tornar a cridar qualsevol part quan vulguis.

Parts:  1 pass-through · 2 gain · 3 distorsió (la fas tu sencera)
        4 latència (mesures) · 5 reflexió · BONUS vúmetre
"""

import sounddevice as sd
import numpy as np
import time

sample_rate = 44100
blocksize = 1024


# ===============================================================
# PART 1 — Pass-through
#   Copia l'entrada a la sortida sense modificar-la.
# ===============================================================

def passthrough_callback(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    # TODO 1: copia indata a outdata
    # Pista: outdata[:] = ...
    pass  # <-- substitueix aquest 'pass'


def escolta_part1(segons=6):
    comprova_part1()
    print(f"Pass-through durant {segons} s. Parla o fes un so...")
    try:
        with sd.Stream(samplerate=sample_rate,
                       blocksize=blocksize,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=passthrough_callback):   # ← la teva callback
            sd.sleep(segons * 1000)    # el programa dorm; l'stream crida la callback
    except KeyboardInterrupt:
        pass
    print("Stream tancat.")


def comprova_part1():
    # Fem a mà el que farà l'stream ~43 vegades per segon:
    # cridar la callback amb un bloc d'entrada i un bloc de sortida buit.
    # (Aquí el bloc és de només 3 mostres, per poder-lo comprovar.)
    entrada = np.array([[0.1], [0.2], [0.3]], dtype='float32')
    sortida = np.zeros((3, 1), dtype='float32')
    passthrough_callback(entrada, sortida, 3, None, None)
    assert np.allclose(sortida, entrada), \
        f"La sortida hauria de ser igual a l'entrada. Resultat: {sortida.flatten()}"
    print("✅ Part 1: la callback fa pass-through")


# ===============================================================
# PART 2 — Gain en temps real
#   La callback llegeix 'gain'; el bucle principal la canvia.
# ===============================================================

# TODO 2: declara una variable global 'gain' amb valor inicial 0.5
gain = None  # <-- substitueix per gain = 0.5


def gain_callback(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    # TODO 3: aplica el gain a indata i assigna el resultat a outdata[:]
    pass  # <-- substitueix aquest 'pass'


def escolta_part2():
    global gain    # assignem 'gain' des de dins d'una funció → cal `global`
    comprova_part2()
    print("Escriu un número entre 0.0 i 2.0 per canviar el gain. 'q' per sortir.\n")
    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   latency='low',
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
    print("Stream tancat.")


def comprova_part2():
    global gain
    assert gain is not None, "Declara la variable 'gain' (TODO 2)"
    gain = 0.5   # partim sempre del valor inicial
    entrada = np.array([[0.4], [0.8], [-0.4]], dtype='float32')
    sortida = np.zeros((3, 1), dtype='float32')
    gain_callback(entrada, sortida, 3, None, None)
    assert np.allclose(sortida, entrada * 0.5), \
        f"Amb gain=0.5, la sortida hauria de ser entrada*0.5. Resultat: {sortida.flatten()}"
    print("✅ Part 2: la callback aplica el gain")


# ===============================================================
# PART 3 — Distorsió en temps real (LA FAS TU SENCERA)
#
#   A la S03 vas distorsionar un fitxer sencer amb np.tanh.
#   Ara ho faràs en directe, bloc a bloc, amb un 'drive'
#   que es pot canviar mentre sona (com el gain de la Part 2).
#
#   Distorsió: sortida = tanh(entrada * drive)
#     drive = 1   → gairebé net
#     drive = 20  → molt saturat
# ===============================================================

# TODO 4: declara una variable global 'drive' amb valor inicial 1.0
drive = None  # <-- substitueix


def disto_callback(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    # TODO 5: omple outdata[:] amb la distorsió de indata, usant 'drive'
    pass  # <-- substitueix aquest 'pass'


def escolta_part3():
    global drive
    comprova_part3()
    # TODO 6: escriu aquí, tu, l'stream i el bucle de control.
    #   - Obre un sd.Stream amb `with`, com a la Part 2, però amb disto_callback.
    #   - Dins, un bucle que demani un nou 'drive' amb input()
    #     (rang vàlid: 1.0 a 50.0) i surti amb 'q'.
    #   - Controla ValueError i KeyboardInterrupt.
    #   Mira la Part 2 com a model, però NO la copiïs sense entendre-la:
    #   cada línia que escriguis, has de saber per què hi és.
    print("TODO 6: encara no has escrit l'stream de la Part 3")


def comprova_part3():
    global drive
    assert drive is not None, "Declara la variable 'drive' (TODO 4)"
    entrada = np.array([[0.1], [0.5], [-0.9]], dtype='float32')
    for d in (1.0, 10.0):
        drive = d
        sortida = np.zeros((3, 1), dtype='float32')
        disto_callback(entrada, sortida, 3, None, None)
        assert np.allclose(sortida, np.tanh(entrada * d), atol=1e-6), \
            f"Amb drive={d}, la sortida hauria de ser tanh(entrada*{d}). " \
            f"Resultat: {sortida.flatten()}"
    drive = 1.0
    print("✅ Part 3: la callback distorsiona correctament")


# ===============================================================
# PART 4 — Latència: teoria vs. mesura
#
#   Crida des de la consola:
#       >>> mesura_latencia(256)
#       >>> mesura_latencia(1024)
#       >>> mesura_latencia(2048)
#   i omple les observacions amb el que veus i sents.
# ===============================================================

def mesura_latencia(bs, segons=5):
    teorica = bs / sample_rate * 1000
    try:
        with sd.Stream(samplerate=sample_rate,
                       blocksize=bs,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=passthrough_callback) as stream:
            lat_in, lat_out = stream.latency            # en segons
            print(f"blocksize={bs}: durada del bloc {teorica:.1f} ms · "
                  f"latència reportada {(lat_in + lat_out)*1000:.1f} ms")
            print("Parla, pica de mans... escolta el retard i si hi ha talls.")
            sd.sleep(segons * 1000)
    except KeyboardInterrupt:
        pass


# TODO 7: omple les observacions
observacions = {
    'blocksize_256': {
        'durada_bloc_ms': None,         # bs / sample_rate * 1000
        'latencia_reportada_ms': None,  # el que imprimeix mesura_latencia
        'retard_perceptible': None,     # True o False
        'glitches': None,               # True, False o 'de vegades'
        'nota': '',
    },
    'blocksize_1024': {
        'durada_bloc_ms': None,
        'latencia_reportada_ms': None,
        'retard_perceptible': None,
        'glitches': None,
        'nota': '',
    },
    'blocksize_2048': {
        'durada_bloc_ms': None,
        'latencia_reportada_ms': None,
        'retard_perceptible': None,
        'glitches': None,
        'nota': '',
    },
}


# ===============================================================
# PART 5 — Reflexió (edita les strings)
# ===============================================================

# TODO 8
reflexio = {
    'per_que_global_es_necessaria':
        '',  # Per què 'gain' ha de ser accessible des de la callback I des del bucle?

    'per_que_global_es_lleig':
        '',  # Per què es diu que la variable global és una solució "lletja"?

    'per_que_colab_no_funciona':
        '',  # Per què aquest codi no funciona a Colab,
             # però la WebAudio API sí que funciona al navegador?

    'trade_off_blocksize':
        '',  # Trade-off entre blocksize petit i blocksize gran.
             # La latència reportada coincideix amb la durada del bloc? Per què?

    'echo_al_callback':
        '',  # Per què la funció echo() de la S03 NO es pot posar tal qual
             # dins d'una callback? (Pista: què "veu" la callback a cada crida?)
}


# ===============================================================
# BONUS — Vúmetre de text
#
#   Fins ara la informació anava del bucle cap a la callback (gain).
#   Ara al revés: la callback MESURA el nivell de cada bloc i el
#   bucle principal el MOSTRA.
#
#   Nivell RMS d'un bloc: np.sqrt(np.mean(indata ** 2))
# ===============================================================

nivell = 0.0


def vumetre_callback(indata, outdata, frames, time_info, status):
    # BONUS a: calcula el RMS de indata i desa'l a la global 'nivell'.
    #          (Atenció: aquí ESCRIUS una global des de dins d'una funció...)
    #          Fes també pass-through, perquè se senti el so.
    pass


def escolta_bonus():
    # BONUS b: obre l'stream amb vumetre_callback i, dins, un bucle que
    #          cada 0.1 s (time.sleep(0.1)) imprimeixi una barra
    #          proporcional al nivell, per exemple:  '#' * int(nivell * 200)
    #          Surt amb Ctrl+C.
    print("BONUS: encara no l'has fet")


# ===============================================================
def comprova_tot():
    comprova_part1()
    comprova_part2()
    comprova_part3()
    for k in observacions:
        assert observacions[k]['durada_bloc_ms'] is not None, f"Omple observacions['{k}']"
        assert observacions[k]['latencia_reportada_ms'] is not None, f"Omple observacions['{k}']"
    print("✅ Part 4: observacions omplertes")
    pendents = [p for p, r in reflexio.items() if not r.strip()]
    if pendents:
        print("⚠️  Reflexió pendent:", ", ".join(pendents))
    else:
        print("✅ Part 5: reflexió completa")


print("Funcions definides. Crida-les des de la consola, per exemple:")
print("  escolta_part1()   escolta_part2()   escolta_part3()")
print("  mesura_latencia(256)   escolta_bonus()   comprova_tot()")
print("⚠️  Auriculars posats!")
