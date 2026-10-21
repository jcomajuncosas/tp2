"""
SOLUCIÓ (docent) — Challenge Sessió 5: Stutter en temps real

F5 i després, a la Shell:
    >>> comprova_stutter()     # sense hardware
    >>> escolta_stutter()      # Enter = enganxa / deixa anar, 'q' = sortir

Idees que posa en joc (i per què és un bon tancament del Bloc 3):
  · DUES memòries diferents: la cinta (què s'ha gravat) i la posició de
    lectura (per on anem del bucle). Totes dues han de sobreviure entre crides.
  · En mode stutter la cinta es CONGELA: deixem d'escriure-hi.
  · Lectura en bucle amb %: és la primera vegada que es mou un ÍNDEX en lloc
    de moure les dades — l'avantsala del buffer circular de veritat.
  · Comunicació bucle → callback amb una bool global (com el gain de la S04).

Limitació honesta: al punt de bucle hi ha un salt (clic). És part del so
típic d'un stutter; un fade curt als extrems seria l'extensió natural.
"""

import sounddevice as sd
import numpy as np

sample_rate = 44100
blocksize = 1024

stutter_s = 0.12
N = int(stutter_s * sample_rate)       # ha de ser >= blocksize
stutter_buffer = np.zeros(N, dtype='float32')
stutter_actiu = False                  # el bucle principal l'escriu, la callback la llegeix
posicio = 0                            # per on llegim el bucle (només la callback la toca)


def stutter_callback(indata, outdata, frames, time_info, status):
    global stutter_buffer, posicio
    if status:
        print("STATUS:", status)
    mono = indata[:, 0]

    if stutter_actiu:
        # Cinta congelada: la reproduïm en bucle des de 'posicio'
        index = (posicio + np.arange(frames)) % N
        outdata[:, 0] = stutter_buffer[index]
        posicio = (posicio + frames) % N
    else:
        # Mode normal: pass-through i anem gravant els últims N
        outdata[:, 0] = mono
        stutter_buffer = np.roll(stutter_buffer, -frames)
        stutter_buffer[-frames:] = mono
        posicio = 0                    # el proper stutter començarà pel principi


def escolta_stutter():
    global stutter_actiu, stutter_buffer, posicio
    stutter_buffer = np.zeros(N, dtype='float32')
    stutter_actiu = False
    posicio = 0
    print(f"Stutter de {stutter_s} s. Parla i prem Enter per enganxar / deixar anar.")
    print("'q' + Enter per sortir.\n")
    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   latency='low',
                   callback=stutter_callback):
        while True:
            try:
                entrada = input("STUTTER ▶ " if stutter_actiu else "normal  ▷ ")
            except KeyboardInterrupt:
                break
            if entrada.strip().lower() == 'q':
                break
            stutter_actiu = not stutter_actiu
    stutter_actiu = False
    print("Stream tancat.")


def comprova_stutter():
    """Prova sense hardware: blocs de 4 mostres, cinta de 8."""
    global N, stutter_buffer, stutter_actiu, posicio
    N_guardat = N
    N = 8
    stutter_buffer = np.zeros(N, dtype='float32')
    stutter_actiu = False
    posicio = 0

    def crida(valors):
        out = np.zeros((4, 1), dtype='float32')
        stutter_callback(np.array(valors, dtype='float32').reshape(-1, 1), out, 4, None, None)
        return out[:, 0]

    try:
        # mode normal: pass-through i gravació
        assert np.allclose(crida([1, 2, 3, 4]), [1, 2, 3, 4])
        assert np.allclose(crida([5, 6, 7, 8]), [5, 6, 7, 8])
        # enganxem: ha de sonar 1..8 en bucle, ignorant l'entrada
        stutter_actiu = True
        assert np.allclose(crida([0, 0, 0, 0]), [1, 2, 3, 4])
        assert np.allclose(crida([0, 0, 0, 0]), [5, 6, 7, 8])
        assert np.allclose(crida([9, 9, 9, 9]), [1, 2, 3, 4])   # torna a començar
        # deixem anar: torna el pass-through
        stutter_actiu = False
        assert np.allclose(crida([9, 9, 9, 9]), [9, 9, 9, 9])
    finally:
        N = N_guardat
        stutter_buffer = np.zeros(N, dtype='float32')
        stutter_actiu = False
        posicio = 0
    print("✅ Stutter: grava, congela, reprodueix en bucle i torna a pass-through")


print("Funcions definides:  comprova_stutter()   escolta_stutter()")
print("⚠️  Auriculars posats!")
