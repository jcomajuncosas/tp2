"""
S07 — Solucions dels challenges (no es distribueix)
====================================================
Necessita solucio.py i sinte.py a la mateixa carpeta.

  challenge_1_baix()                 arpegi + baix: esdeveniments de 2 instruments en ordre
  challenge_2_clock_extern(port)     l'arpegi avança amb el clock MIDI que arriba pel port
  envia_clock(port, bpm, negres)     font de clock per provar el 2 sense Arduino (bus IAC)
  challenge_3_a_la_mostra()          notes programades a la mostra exacta, dins el callback

El 1 i el 3 són concrets i s'han validat amb un stream simulat.
El 2 és exploratori: depèn de la font de clock (DAW, Arduino) i s'ha validat
només la lògica, cridant el callback amb missatges simulats.
"""

import time
import numpy as np
import pretty_midi
from sinte import SinteSimple, espera_fins, SR
from solucio import arpegiador, notes_a_midi


# ======================================================================
# Challenge 1 — Baix: dos instruments, un sol fil, esdeveniments en ordre
# ======================================================================

def esdeveniments_en_ordre(pm):
    """Tots els note_on i note_off de tots els instruments, ordenats per temps.
    Sense sorted(): a cada pas es busca el més aviat dels que queden.
    A igual temps, el note_off va primer (tipus 0 abans que tipus 1)."""
    pendents = []
    for instrument in pm.instruments:
        for nota in instrument.notes:
            pendents.append([nota.start, 1, nota.pitch, nota.velocity])
            pendents.append([nota.end, 0, nota.pitch, 0])

    ordenats = []
    while len(pendents) > 0:
        millor = 0
        for i in range(1, len(pendents)):
            if pendents[i][0] < pendents[millor][0]:
                millor = i
            elif pendents[i][0] == pendents[millor][0] and pendents[i][1] < pendents[millor][1]:
                millor = i
        ordenats.append(pendents[millor])
        del pendents[millor]
    return ordenats


def reprodueix_multi(pm, synth, t_inici=None):
    if t_inici is None:
        t_inici = time.perf_counter() + 0.2
    for temps, tipus, pitch, velocity in esdeveniments_en_ordre(pm):
        espera_fins(t_inici + temps)
        if tipus == 1:
            synth.note_on(pitch, velocity)
        else:
            synth.note_off(pitch)


def challenge_1_baix(tempo=100):
    acord = [57, 60, 64]
    seq = arpegiador(acord, 4, 'updown', octaves=2)            # 10 notes x 4
    pm = notes_a_midi(seq, tempo=tempo, subdivisio=4, gate=0.6)

    baix = pretty_midi.Instrument(program=32)
    negra = 60 / tempo
    n_negres = int(pm.get_end_time() / negra + 0.5)
    for i in range(n_negres):
        baix.notes.append(pretty_midi.Note(velocity=100, pitch=acord[0] - 12,
                                           start=i * negra, end=i * negra + negra * 0.9))
    pm.instruments.append(baix)

    synth = SinteSimple(bpm_click=tempo)
    t_inici, mostra_inici = synth.proper_click()
    reprodueix_multi(pm, synth, t_inici)
    synth.close()
    pm.write('arpegi_i_baix.mid')
    print(f"{len(pm.instruments[0].notes)} notes d'arpegi + {len(baix.notes)} de baix")


# ======================================================================
# Challenge 2 — Clock extern (exploratori)
# ======================================================================
# El clock MIDI són missatges d'un sol byte: 248 = clock (24 per negra),
# 250 = start, 252 = stop. Qui l'envia marca el tempo; nosaltres només
# comptem. 6 clocks = una semicorxera.

CLOCK = 248
START = 250
STOP = 252


class ArpegiadorEsclau:
    """L'estat que comparteix el callback MIDI (fil de RtMidi) amb el programa."""
    def __init__(self, synth, seq, clocks_per_nota=6):
        self.synth = synth
        self.seq = seq
        self.clocks_per_nota = clocks_per_nota
        self.comptador = 0
        self.posicio = 0
        self.sonant = None
        self.en_marxa = False

    def quan_arriba(self, dades, timestamp):
        byte = dades[0]
        if byte == START:
            self.comptador = 0
            self.posicio = 0
            self.en_marxa = True
        elif byte == STOP:
            self.en_marxa = False
            if self.sonant is not None:
                self.synth.note_off(self.sonant)
                self.sonant = None
        elif byte == CLOCK and self.en_marxa:
            if self.comptador % self.clocks_per_nota == 0:
                if self.sonant is not None:
                    self.synth.note_off(self.sonant)
                nota = self.seq[self.posicio % len(self.seq)]
                self.synth.note_on(nota, 90)
                self.sonant = nota
                self.posicio += 1
            self.comptador += 1


def challenge_2_clock_extern(port=0, segons=10):
    import rtmidi2
    synth = SinteSimple()
    esclau = ArpegiadorEsclau(synth, arpegiador([57, 60, 64], 1, 'updown', octaves=2))
    entrada = rtmidi2.MidiIn()
    print(entrada.ports)
    entrada.open_port(port)
    entrada.callback = esclau.quan_arriba
    print(f"Escoltant clock durant {segons} s (cal que la font enviï START)...")
    time.sleep(segons)
    entrada.close_port()
    synth.close()


def envia_clock(port=0, bpm=120, negres=16):
    """Font de clock amb l'estratègia B: 24 missatges per negra, a temps absolut."""
    import rtmidi2
    sortida = rtmidi2.MidiOut()
    sortida.open_port(port)
    pas = 60 / bpm / 24
    sortida.send_message([START])
    t_inici = time.perf_counter() + 0.05
    for i in range(negres * 24):
        espera_fins(t_inici + i * pas)
        sortida.send_message([CLOCK])
    sortida.send_message([STOP])
    sortida.close_port()


# ======================================================================
# Challenge 3 — Precís a la mostra: les notes s'engeguen DINS el callback
# ======================================================================

class SinteMostra(SinteSimple):
    """Com SinteSimple, però les notes es poden programar per número de mostra.
    El fil principal ho programa tot ABANS de començar; el callback, que és qui
    compta les mostres, engega cada nota a la mostra exacta dins el bloc.
    (El note_off es fa al bloc on cau: fins a 1.45 ms de diferència, inaudible
    en una cua de 25 ms.)
    Les notes s'han de programar en ordre de temps."""

    def __init__(self, bpm_click=0, volum=0.25):
        self.programades = []       # [mostra, tipus, nota, velocity], en ordre
        self.seguent = 0
        SinteSimple.__init__(self, bpm_click, volum)

    def programa(self, mostra, tipus, nota, velocity=90):
        self.programades.append([mostra, tipus, nota, velocity])

    def callback(self, outdata, frames, time_info, status):
        self.t_callback = time.perf_counter()
        self.n_callback = self.n
        if self.t_ref is None and self.n > 0.3 * SR:
            self.t_ref = self.t_callback
            self.n_ref = self.n

        # 1) Notes programades que cauen dins aquest bloc
        while self.seguent < len(self.programades) and self.programades[self.seguent][0] < self.n + frames:
            mostra, tipus, nota, velocity = self.programades[self.seguent]
            self.seguent += 1
            if tipus == 'on':
                retard = max(0, mostra - self.n)          # on comença dins el bloc
                amplitud = self.volum * velocity / 127
                self.veus.append([nota_a_freq(nota), amplitud, 0.0, 1.0, self.decaiment_llarg, nota, retard])
                self.registre_on.append(self.n + retard)
            else:
                for veu in self.veus:
                    if veu[5] == nota:
                        veu[4] = self.decaiment_curt

        # 2) Veus: abans de 'retard' la veu encara no sona
        k = np.arange(frames)
        sortida = np.zeros(frames)
        vives = []
        for veu in self.veus:
            freq, amplitud, fase, guany, decaiment, nota, retard = veu
            w = 2 * np.pi * freq / SR
            kk = k - retard
            sona = kk >= 0
            fases = fase + w * kk
            envolupant = guany * decaiment ** (kk * sona) * sona
            sortida += amplitud * envolupant * (np.sin(fases) + 0.3 * np.sin(2 * fases))
            veu[2] = (fase + w * (frames - retard)) % (2 * np.pi)
            veu[3] = guany * decaiment ** (frames - retard)
            veu[6] = 0
            if veu[3] > 0.0001:
                vives.append(veu)
        self.veus = vives

        if self.P > 0:
            sortida += self.ona_click[(self.n + k) % self.P]
        outdata[:, 0] = np.clip(sortida, -1, 1)
        self.n += frames


def nota_a_freq(nota):
    return 440.0 * 2 ** ((nota - 69) / 12)


def challenge_3_a_la_mostra(tempo=140):
    seq = arpegiador([57, 60, 64], 4, 'updown', octaves=2)
    pm = notes_a_midi(seq, tempo=tempo, subdivisio=4, gate=0.6)
    synth = SinteMostra(bpm_click=tempo)
    t_click, mostra_inici = synth.proper_click(0.5)
    for nota in pm.instruments[0].notes:
        synth.programa(mostra_inici + int(round(nota.start * SR)), 'on', nota.pitch, nota.velocity)
        synth.programa(mostra_inici + int(round(nota.end * SR)), 'off', nota.pitch)
    espera_fins(t_click + pm.get_end_time() + 0.3)       # el fil principal només espera
    synth.close()

    pitjor = 0
    notes = pm.instruments[0].notes
    for i in range(len(synth.registre_on)):
        ideal = mostra_inici + int(round(notes[i].start * SR))
        pitjor = max(pitjor, abs(synth.registre_on[i] - ideal))
    print(f"{len(synth.registre_on)} notes. Pitjor error respecte al metrònom: {pitjor} mostres")
