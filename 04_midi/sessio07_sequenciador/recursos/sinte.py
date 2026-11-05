"""
sinte.py — Sintetitzador mínim + metrònom + eines de timing (Sessió 7)
======================================================================

Aquest mòdul es proporciona fet: no cal modificar-lo, però sí LLEGIR-LO.
És el mateix model de callback del Bloc 3, amb un so molt simple:

    - Cada nota és un sinus (+ una mica del 2n harmònic) que s'apaga sol.
    - El fil principal NO toca l'àudio: només deixa "encàrrecs" (note_on,
      note_off) en una llista. El callback els recull al principi de cada bloc.
    - Opcionalment, el callback genera un METRÒNOM comptant mostres. Aquest
      click el marca el rellotge de la targeta de so, no Python: és la
      referència per escoltar si el nostre seqüenciador va a temps.

Només fa servir numpy i sounddevice (els mateixos del Bloc 3).

Ús:
    from sinte import SinteSimple, espera_fins
    synth = SinteSimple()               # o SinteSimple(bpm_click=120)
    synth.note_on(60, 90)
    time.sleep(0.5)
    synth.note_off(60)
    synth.close()                       # sempre al final
"""

import time
import math
import numpy as np
import sounddevice as sd

SR = 44100      # mostres per segon
BLOC = 64       # mostres per callback: 64 / 44100 = 1.45 ms de termini


def nota_a_freq(nota):
    """Número de nota MIDI → freqüència en Hz (69 = La 440)."""
    return 440.0 * 2 ** ((nota - 69) / 12)


class SinteSimple:

    def __init__(self, bpm_click=0, volum=0.25):
        self.volum = volum
        self.veus = []            # notes sonant: [freq, amplitud, fase, guany, decaiment, nota]
        self.encarrecs = []       # el fil principal hi afegeix, el callback llegeix
        self.llegits = 0          # quants encàrrecs ha recollit ja el callback
        self.n = 0                # mostres generades des de l'inici
        self.registre_on = []     # a quina mostra ha començat cada note_on

        # decaïment per mostra: la nota perd la meitat del volum en X segons
        self.decaiment_llarg = 0.5 ** (1 / (0.6 * SR))    # nota tocada: 0.6 s
        self.decaiment_curt = 0.5 ** (1 / (0.025 * SR))   # nota deixada anar: 25 ms

        # metrònom: un "bucle" de P mostres amb un click curt al principi
        self.P = 0
        if bpm_click > 0:
            self.P = int(round(60 / bpm_click * SR))      # mostres entre clicks
            t = np.arange(int(0.012 * SR)) / SR
            click = 0.5 * np.sin(2 * np.pi * 2000 * t) * np.exp(-t / 0.003)
            self.ona_click = np.zeros(self.P)
            self.ona_click[0:len(click)] = click

        # per mesurar si el callback arriba tard (veure perdut_ms)
        self.t_callback = None    # perf_counter de l'últim callback
        self.n_callback = 0       # mostra inicial de l'últim callback
        self.t_ref = None
        self.n_ref = 0

        self.stream = sd.OutputStream(samplerate=SR, blocksize=BLOC, channels=1,
                                      latency='low', callback=self.callback)
        self.stream.start()

    # ------------------------------------------------------------------
    # Fil principal: només deixa encàrrecs
    # ------------------------------------------------------------------
    def note_on(self, nota, velocity=90, curta=False):
        """Comença una nota. curta=True: s'apaga sola de seguida (percussió)."""
        self.encarrecs.append(['on', nota, velocity, curta])

    def note_off(self, nota):
        self.encarrecs.append(['off', nota, 0, False])

    def close(self):
        time.sleep(0.3)           # deixa acabar les cues de les notes
        self.stream.stop()
        self.stream.close()

    # ------------------------------------------------------------------
    # Fil d'àudio: el callback (com al Bloc 3)
    # ------------------------------------------------------------------
    def callback(self, outdata, frames, time_info, status):
        self.t_callback = time.perf_counter()
        self.n_callback = self.n
        if self.t_ref is None and self.n > 0.3 * SR:
            self.t_ref = self.t_callback
            self.n_ref = self.n

        # 1) Recull els encàrrecs nous
        while self.llegits < len(self.encarrecs):
            tipus, nota, velocity, curta = self.encarrecs[self.llegits]
            self.llegits += 1
            if tipus == 'on':
                decaiment = self.decaiment_llarg
                if curta:
                    decaiment = self.decaiment_curt
                amplitud = self.volum * velocity / 127
                self.veus.append([nota_a_freq(nota), amplitud, 0.0, 1.0, decaiment, nota])
                self.registre_on.append(self.n)
            else:
                for veu in self.veus:
                    if veu[5] == nota:
                        veu[4] = self.decaiment_curt

        # 2) Suma totes les veus
        k = np.arange(frames)
        sortida = np.zeros(frames)
        vives = []
        for veu in self.veus:
            freq, amplitud, fase, guany, decaiment, nota = veu
            w = 2 * np.pi * freq / SR
            fases = fase + w * k
            envolupant = guany * decaiment ** k
            sortida += amplitud * envolupant * (np.sin(fases) + 0.3 * np.sin(2 * fases))
            veu[2] = (fase + w * frames) % (2 * np.pi)     # la fase continua al bloc següent
            veu[3] = guany * decaiment ** frames
            if veu[3] > 0.0001:                            # encara se sent: la guardem
                vives.append(veu)
        self.veus = vives

        # 3) Metrònom: la posició dins el bucle del click és (mostra % P)
        if self.P > 0:
            sortida += self.ona_click[(self.n + k) % self.P]

        outdata[:, 0] = np.clip(sortida, -1, 1)
        self.n += frames

    # ------------------------------------------------------------------
    # Eines de mesura
    # ------------------------------------------------------------------
    def proper_click(self, marge=0.3):
        """Retorna (temps perf_counter, número de mostra) del primer click
        que sonarà d'aquí a 'marge' segons. Serveix per arrencar un patró
        alineat amb el metrònom."""
        while self.t_callback is None:
            time.sleep(0.01)
        ara = time.perf_counter()
        mostra_ara = self.n_callback + (ara - self.t_callback) * SR
        mostra_click = math.ceil((mostra_ara + marge * SR) / self.P) * self.P
        t_click = self.t_callback + (mostra_click - self.n_callback) / SR
        return t_click, mostra_click

    def perdut_ms(self):
        """Temps (ms) que ha passat sense que el callback generés àudio.
        Si creix, el callback ha arribat tard i la targeta ha sonat silenci.
        (macOS no sempre ho avisa: per això ho mesurem nosaltres.)"""
        while self.t_ref is None:
            time.sleep(0.01)
        rellotge = (self.t_callback - self.t_ref) * SR
        mostres = self.n_callback - self.n_ref
        return (rellotge - mostres) / SR * 1000


# ----------------------------------------------------------------------
# Eines de timing per al fil principal
# ----------------------------------------------------------------------

def espera_fins(t_objectiu):
    """ESTRATÈGIA B (espera híbrida): espera fins a l'instant t_objectiu
    (en temps de time.perf_counter()).
      1) dorm fins a 2 ms abans: no gasta CPU i deixa treballar el callback
      2) els darrers 2 ms, espera activa: precisió de microsegons"""
    falta = t_objectiu - time.perf_counter()
    if falta > 0.002:
        time.sleep(falta - 0.002)
    while time.perf_counter() < t_objectiu:
        pass


def feina_simulada(ms, tipus='espera'):
    """Simula la feina que fa un seqüenciador real entre nota i nota.
    tipus='espera': una tasca que tarda però deixa córrer els altres fils
                    (esperar un port, un fitxer, la pantalla...)
    tipus='cpu':    càlcul pur en Python; mentre dura, el callback d'àudio
                    no pot executar-se (el GIL: només un fil de Python
                    alhora executa codi)"""
    if tipus == 'espera':
        time.sleep(ms / 1000)
    else:
        t = time.perf_counter()
        while time.perf_counter() - t < ms / 1000:
            pass
