"""
Exemples — Bloc 3b, Sessió 4 (Thonny)
El model callback: àudio en temps real

⚠️  AURICULARS OBLIGATORIS. Micròfon + altaveus = realimentació (Larsen).

IMPORTANT: aquest fitxer requereix Thonny + sounddevice instal·lat localment.
NO funciona a Colab: el codi s'executaria en un servidor remot, sense accés
al micròfon ni als altaveus del teu ordinador.

─────────────────────────────────────────────────────────────────────
QUÈ ÉS UN STREAM?

Un sd.Stream és una connexió oberta amb la targeta de so. Mentre està
oberta, la targeta va demanant blocs de mostres — un cada
blocksize / sample_rate segons (~23 ms amb blocksize=1024) — i, cada
vegada, l'stream crida la teva funció CALLBACK per obtenir-lo:
li passa el bloc que acaba d'entrar pel micròfon (indata) i un bloc
buit que has d'omplir (outdata).

Tu no crides mai la callback: només la defineixes i la lliures a
l'stream (callback=...). Tot això passa "per darrere", en paral·lel
al teu programa (en un altre FIL d'execució, un thread). Per això el
programa principal pot quedar-se adormit (sleep) o esperant que
escriguis (input) i el so no s'atura.

El `with` obre l'stream en entrar al bloc i el tanca en sortir-ne,
passi el que passi: EL SO DURA EL QUE DURA EL BLOC INDENTAT.

El `try/except KeyboardInterrupt` serveix perquè, si prems Ctrl+C,
el programa tanqui l'stream i continuï net, en comptes d'aturar-se
amb un missatge d'error vermell. (`pass` vol dir "no facis res".)
─────────────────────────────────────────────────────────────────────

COM S'USA AQUEST FITXER A THONNY (no hi ha cel·les com a Colab):
  1. Prem F5 (Run). Això només DEFINEIX les funcions; no sona res.
  2. A la consola (Shell) de baix, crida la demo que vulguis:
         >>> demo_passthrough()
         >>> demo_gain()
     Pots repetir-les tantes vegades com vulguis, en l'ordre que vulguis.
  3. Ctrl+C atura l'stream actiu.
"""

import sounddevice as sd
import numpy as np
import time

sample_rate = 44100
blocksize = 1024        # durada d'un bloc: 1024 / 44100 ≈ 23 ms


# ---------------------------------------------------------------
# DEMO 1 — El callback més simple: pass-through
#   Copia l'entrada directament a la sortida, sense modificar res.
# ---------------------------------------------------------------

def passthrough(indata, outdata, frames, time_info, status):
    if status:                     # l'stream ens avisa si hi ha hagut glitch
        print("STATUS:", status)
    outdata[:] = indata            # copia entrada → sortida, sense canvis


def demo_passthrough(segons=8):
    print("Parla o fes un so. Hauries de sentir-te amb un petit retard.")
    print("Ctrl+C per aturar abans d'hora.\n")
    try:
        with sd.Stream(samplerate=sample_rate,   # ← obre l'stream...
                       blocksize=blocksize,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=passthrough):     # ← ...i li dona la callback
            sd.sleep(segons * 1000)               # el programa dorm; el so continua
        # ← aquí el bloc `with` s'ha acabat: l'stream ja està tancat
    except KeyboardInterrupt:
        pass                                      # Ctrl+C: sortim sense error
    print("Stream tancat.")


# ---------------------------------------------------------------
# DEMO 2 — Gain en temps real amb variable global
#   El callback LLEGEIX 'gain' a cada bloc (cada ~23 ms).
#   El bucle principal l'ESCRIU quan tu teclejes un valor.
#   Tots dos treballen alhora, en fils diferents.
# ---------------------------------------------------------------

gain = 0.5   # global: la veuen la callback i el bucle principal


def gain_control(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)
    outdata[:] = indata * gain     # només LLEGIR una global: no cal `global`


def demo_gain():
    global gain    # aquí sí: ASSIGNEM 'gain' des de dins d'una funció
    print("Escriu un número entre 0.0 i 2.0 i prem Enter. 'q' per sortir.\n")

    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   latency='low',
                   callback=gain_control):
        # En comptes de sleep, un bucle que manté viu el bloc `with`
        # i a més fa feina útil: llegir el teclat.
        while True:
            try:
                # input() espera que premis Enter. Mentre espera, el so continua.
                # Si prems Ctrl+C mentre espera, input() NO retorna cap text:
                # llença KeyboardInterrupt i saltem directament a l'except.
                entrada = input(f"Gain actual: {gain:.2f} → nou valor: ")
                if entrada.lower() == 'q':
                    break                          # surt del while → surt del with
                nou_gain = float(entrada)          # "hola" → llença ValueError
                if 0.0 <= nou_gain <= 2.0:
                    gain = nou_gain
                    print(f"Gain canviat a {gain:.2f}")
                else:
                    print("Valor fora de rang (0.0 - 2.0)")
            except ValueError:                     # text no numèric
                print("Escriu un número vàlid")    # ...i el while continua
            except KeyboardInterrupt:              # Ctrl+C
                break
    print("Stream tancat.")


# ---------------------------------------------------------------
# DEMO 3 — Quantes vegades es crida la callback?
#   Aquí la callback ESCRIU una global → necessita `global`.
#
#   Nota: en sistemes professionals s'usarien cues (queue.Queue) o
#   variables atòmiques. Per a un número simple, la global funciona
#   a la pràctica (gràcies al GIL de Python).
# ---------------------------------------------------------------

comptador = 0


def compta_blocs(indata, outdata, frames, time_info, status):
    global comptador
    comptador += 1
    outdata[:] = indata


def demo_compta_blocs(segons=3):
    global comptador
    comptador = 0
    print(f"Comptant crides a la callback durant {segons} segons...")
    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   latency='low',
                   callback=compta_blocs):
        sd.sleep(segons * 1000)

    real = comptador / segons
    esperada = sample_rate / blocksize
    print(f"Crides: {comptador}  →  {real:.1f} per segon")
    print(f"Esperades: {esperada:.1f} per segon (sample_rate / blocksize)")


# ---------------------------------------------------------------
# DEMO 4 — Callback lenta → glitch (deliberat)
#   La callback triga 50 ms, però el bloc dura ~23 ms:
#   la targeta no pot esperar i el so es trenca.
# ---------------------------------------------------------------

def callback_lenta(indata, outdata, frames, time_info, status):
    if status:
        print("STATUS:", status)   # aquí sí que veuràs avisos!
    time.sleep(0.05)               # 50 ms — més del doble del bloc (~23 ms)
    outdata[:] = indata


def demo_glitch(segons=4):
    print("Hauràs de sentir talls i artefactes. És el que volem demostrar.\n")
    try:
        with sd.Stream(samplerate=sample_rate,
                       blocksize=blocksize,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=callback_lenta):
            sd.sleep(segons * 1000)
    except KeyboardInterrupt:
        pass
    print("\nAixò és un glitch: el sistema no pot esperar que la callback acabi.")
    print("Regla d'or: dins la callback, fes el mínim possible.")


# ---------------------------------------------------------------
# DEMO 5 — Latència: teoria vs. realitat
#   blocksize / sample_rate és només la durada d'UN bloc.
#   La latència real inclou més buffers (entrada, sortida, sistema
#   operatiu...). `stream.latency` ens diu la que reporta el sistema.
#   Fixa't en el `as stream`: guardem l'stream en una variable
#   per poder-li preguntar coses.
# ---------------------------------------------------------------

def demo_latencia(bs=1024, segons=4):
    teorica = bs / sample_rate * 1000
    print(f"blocksize = {bs}")
    print(f"Durada d'un bloc (teòrica): {teorica:.1f} ms")
    try:
        with sd.Stream(samplerate=sample_rate,
                       blocksize=bs,
                       channels=1,
                       dtype='float32',
                       latency='low',
                       callback=passthrough) as stream:
            lat_in, lat_out = stream.latency       # en segons: (entrada, sortida)
            print(f"Latència reportada: entrada {lat_in*1000:.1f} ms"
                  f" + sortida {lat_out*1000:.1f} ms"
                  f" = {(lat_in + lat_out)*1000:.1f} ms")
            print("Parla i escolta el retard...")
            sd.sleep(segons * 1000)
    except KeyboardInterrupt:
        pass
    print("Prova també: demo_latencia(256)  i  demo_latencia(2048)")


# ---------------------------------------------------------------
print("Funcions definides. Crida-les des de la consola:")
print("  demo_passthrough()   demo_gain()   demo_compta_blocs()")
print("  demo_glitch()        demo_latencia(256)")
print("⚠️  Auriculars posats!")
