"""
Assignment — Bloc 4b, Sessió 7
Seqüenciador / arpegiador en temps real
=======================================

ON I PER QUÈ
  Tot aquest assignment és a Thonny: el que construeixes ha de sonar a
  temps, al teu ordinador, pel teu altaveu. (Els fitxers .mid sense temps
  real, com a la Sessió 6, es poden fer a Colab; el temps real, no.)
  Necessites sinte.py a la mateixa carpeta que aquest fitxer.

QUÈ CONSTRUEIXES
  Part 1  arpegiador(...)     d'un acord a una seqüència, ara a diverses octaves
  Part 2  notes_a_midi(...)   la seqüència com a notes pretty_midi, amb tempo,
                              gate (staccato/legato) i accents
  Part 3  reprodueix(...)     la toca en directe amb l'estratègia B
  Part 4  el_meu_sequenciador()   ho muntes tot i ho escoltes
  Part 5  reflexió

COM ES TREBALLA
  F5 només DEFINEIX les funcions. Després, des del Shell, per a cada part:
      escolta_part1()      🔊 escolta el que fa la teva funció
      comprova_part1()     ✅ autotest
  i igual amb les parts 2 i 3. Al final:
      el_meu_sequenciador()
      comprova_part4()
      comprova_part5()
  Les funcions escolta_ i comprova_ ja estan fetes: no les modifiquis.
"""

import os
import time
import pretty_midi
from sinte import SinteSimple, espera_fins, SR


def toca_amb_sleep(instrument, synth):
    """(Ja feta.) Toca les notes d'un instrument esperant amb time.sleep.
    És l'estratègia A: serveix per escoltar les parts 1 i 2 de seguida.
    A la Part 3 en faràs la versió precisa."""
    notes = instrument.notes
    for i in range(len(notes)):
        synth.note_on(notes[i].pitch, notes[i].velocity)
        time.sleep(notes[i].end - notes[i].start)
        synth.note_off(notes[i].pitch)
        if i + 1 < len(notes):
            time.sleep(notes[i + 1].start - notes[i].end)


def toca_pitches(pitches, durada=0.15):
    """(Ja feta.) Toca una llista de números de nota, una rere l'altra."""
    instrument = pretty_midi.Instrument(program=0)
    t = 0.0
    for p in pitches:
        instrument.notes.append(pretty_midi.Note(velocity=85, pitch=p, start=t, end=t + durada * 0.9))
        t += durada
    synth = SinteSimple()
    toca_amb_sleep(instrument, synth)
    synth.close()


# ======================================================================
# PART 1 — Arpegiador amb octaves
# ======================================================================
#
# A classe l'arpegiador només feia servir les notes de l'acord. Ara, amb
# octaves=2, l'acord es repeteix una octava amunt (+12) ABANS d'aplicar el mode:
#
#   arpegiador([60, 64, 67], 1, 'up', octaves=2)
#       → [60, 64, 67, 72, 76, 79]
#   arpegiador([60, 64, 67], 1, 'updown', octaves=2)
#       → [60, 64, 67, 72, 76, 79, 76, 72, 67, 64]
#
# Recorda: llista[::-1] és la llista al revés; llista[1:-1] la llista sense
# el primer ni l'últim element; llista * n és la llista repetida n vegades.

def arpegiador(acord, n_repeticions, mode='up', octaves=1):

    # TODO 1a: construeix 'notes': l'acord sencer a cada octava.
    #   Octava 0: les notes tal qual. Octava 1: cada nota + 12. Octava 2: + 24...
    #   (un for per a les octaves, i dins un altre for per a les notes de l'acord)
    notes = []

    # TODO 1b: aplica el mode a 'notes' (com a classe: 'up', 'down', 'updown')
    seq = None   # <-- substitueix

    # TODO 1c: retorna 'seq' repetida 'n_repeticions' vegades
    return None  # <-- substitueix


def escolta_part1(acord=[57, 60, 64], mode='updown', octaves=2):
    """🔊 Prova també octaves=1 i octaves=3, i els altres modes."""
    seq = arpegiador(acord, 2, mode, octaves)
    print(f"{mode}, {octaves} octava/es → {seq}")
    toca_pitches(seq)


def comprova_part1():
    c = [60, 64, 67]
    r = arpegiador(c, 2, 'up')
    assert r is not None, "arpegiador retorna None: completa els TODO 1b i 1c"
    assert r == [60, 64, 67, 60, 64, 67], f"'up' amb 2 repeticions incorrecte: {r}"
    r = arpegiador(c, 1, 'down')
    assert r == [67, 64, 60], f"'down' incorrecte: {r}"
    r = arpegiador(c, 1, 'updown')
    assert r == [60, 64, 67, 64], f"'updown' incorrecte (no repeteixis els extrems): {r}"
    r = arpegiador(c, 1, 'up', octaves=2)
    assert r == [60, 64, 67, 72, 76, 79], \
        f"octaves=2 incorrecte: {r}. Has construït 'notes' i aplicat el mode sobre 'notes'?"
    r = arpegiador(c, 1, 'updown', octaves=2)
    assert r == [60, 64, 67, 72, 76, 79, 76, 72, 67, 64], f"'updown' amb octaves=2 incorrecte: {r}"
    r = arpegiador(c, 1, 'down', octaves=3)
    assert r == [91, 88, 84, 79, 76, 72, 67, 64, 60], f"'down' amb octaves=3 incorrecte: {r}"
    print("✅ Part 1 correcta")


# ======================================================================
# PART 2 — De la seqüència a notes pretty_midi: tempo, gate i accents
# ======================================================================
#
# A classe cada nota durava un nombre fix de segons. Ara:
#   - la durada surt del TEMPO: una negra dura 60/tempo segons, i
#     'subdivisio' diu quantes notes caben en una negra (4 = semicorxeres)
#   - el GATE diu quina part de la durada sona: 1.0 = legato, 0.3 = staccato
#   - la primera nota de cada grup de 'cada' notes porta ACCENT
#     (pista: i % cada == 0, el mòdul de TP1)
#
#   notes_a_midi([60, 64, 67, 72], tempo=120, subdivisio=4, gate=0.8)
#   durada = 60/120/4 = 0.125 s
#   nota 0: start 0.000, end 0.100, velocity 110 (accent)
#   nota 1: start 0.125, end 0.225, velocity 70
#   ...

def notes_a_midi(pitches, tempo=120, subdivisio=4, gate=0.8, velocity=70, accent=110, cada=4):
    pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    instrument = pretty_midi.Instrument(program=0)

    # TODO 2a: calcula la durada de cada nota (en segons) a partir de tempo i subdivisio
    durada = 0   # <-- substitueix

    for i in range(len(pitches)):
        # TODO 2b: start i end de la nota i (end depèn del gate)
        start = 0  # <-- substitueix
        end = 0    # <-- substitueix

        # TODO 2c: velocity normal, o 'accent' si és la primera del grup
        vel = velocity

        instrument.notes.append(pretty_midi.Note(velocity=vel, pitch=pitches[i], start=start, end=end))

    pm.instruments.append(instrument)
    return pm


def escolta_part2(gate=0.8, cada=4):
    """🔊 Escolta gate=0.3 (staccato) contra gate=1.0 (legato).
    Prova cada=3 sobre aquest arpegi de 4 notes: l'accent es desplaça (3 contra 4)."""
    seq = arpegiador([57, 60, 64, 67], 4, 'up')
    pm = notes_a_midi(seq, tempo=110, subdivisio=4, gate=gate, cada=cada)
    print(f"gate={gate}, accent cada {cada} notes")
    synth = SinteSimple()
    toca_amb_sleep(pm.instruments[0], synth)
    synth.close()


def comprova_part2():
    pm = notes_a_midi([60, 64, 67, 72], tempo=120, subdivisio=4, gate=0.8)
    assert len(pm.instruments) == 1, "Hi ha d'haver 1 instrument"
    n = pm.instruments[0].notes
    assert len(n) == 4, f"Hi ha d'haver 4 notes, n'hi ha {len(n)}"
    assert abs(n[1].start - 0.125) < 0.0001, \
        f"A 120 bpm en semicorxeres, la 2a nota comença a 0.125 s, no a {n[1].start}. Revisa 'durada' (TODO 2a)"
    assert abs(n[3].start - 0.375) < 0.0001, f"La 4a nota hauria de començar a 0.375 s: {n[3].start}"
    assert abs(n[0].end - 0.1) < 0.0001, \
        f"Amb gate=0.8, la 1a nota acaba a 0.1 s, no a {n[0].end}. Revisa 'end' (TODO 2b)"
    vels = []
    for nota in n:
        vels.append(nota.velocity)
    assert vels == [110, 70, 70, 70], f"Velocities {vels}: només la 1a de cada 4 porta accent (TODO 2c)"
    pm = notes_a_midi([60, 64, 67, 72], tempo=60, subdivisio=2, gate=1.0, cada=2)
    n = pm.instruments[0].notes
    assert abs(n[1].start - 0.5) < 0.0001, f"A 60 bpm en corxeres la 2a nota comença a 0.5 s: {n[1].start}"
    assert abs(n[0].end - 0.5) < 0.0001, f"Amb gate=1.0 la nota dura tota la corxera: end={n[0].end}"
    vels = []
    for nota in n:
        vels.append(nota.velocity)
    assert vels == [110, 70, 110, 70], f"Amb cada=2, velocities {vels}"
    print("✅ Part 2 correcta")


# ======================================================================
# PART 3 — Reproduir en directe amb l'estratègia B
# ======================================================================
#
# pretty_midi ja et dona el TEMPS ABSOLUT de cada nota (start, end des de
# l'inici). Això és exactament el que necessita l'estratègia B:
#     instant objectiu = t_inici + nota.start
# Per a cada nota:  espera fins al seu start → note_on
#                   espera fins al seu end   → note_off
# Fes servir espera_fins() de sinte.py (obre'l i mira com funciona).

def reprodueix(pm, synth, t_inici=None):
    if t_inici is None:
        t_inici = time.perf_counter() + 0.2    # comencem d'aquí a 0.2 s

    # TODO 3: recorre pm.instruments[0].notes i toca cada nota a temps
    pass  # <-- substitueix


def escolta_part3(tempo=140):
    """🔊 El teu arpegi amb el metrònom de la targeta (click a les negres).
    Si la Part 3 és correcta, les notes es queden enganxades al click."""
    seq = arpegiador([57, 60, 64], 4, 'updown', octaves=2)
    pm = notes_a_midi(seq, tempo=tempo, subdivisio=4, gate=0.6)
    synth = SinteSimple(bpm_click=tempo)
    t_inici, mostra_inici = synth.proper_click()
    reprodueix(pm, synth, t_inici)
    synth.close()

    pitjor = 0.0
    notes = pm.instruments[0].notes
    for i in range(len(synth.registre_on)):
        ideal = mostra_inici + notes[i].start * SR
        error = abs(synth.registre_on[i] - ideal) / SR * 1000
        pitjor = max(pitjor, error)
    print(f"{len(synth.registre_on)} notes. Pitjor error respecte al metrònom: {pitjor:.1f} ms")


class SynthFals:
    """Per a l'autotest: no fa so, apunta QUAN li arriba cada missatge.
    A la 6a nota s'encalla 25 ms (com si l'ordinador fes una altra feina)."""
    def __init__(self):
        self.on = []
        self.off = []

    def note_on(self, nota, velocity=90):
        self.on.append(time.perf_counter())
        if len(self.on) == 6:
            time.sleep(0.025)

    def note_off(self, nota):
        self.off.append(time.perf_counter())


def comprova_part3():
    seq = arpegiador([60, 64, 67, 72], 4, 'up')
    assert seq is not None, "Abans de la Part 3 cal que la Part 1 funcioni (comprova_part1)"
    pm = notes_a_midi(seq, tempo=140, subdivisio=4, gate=0.5)
    notes = pm.instruments[0].notes
    synth = SynthFals()
    t_inici = time.perf_counter() + 0.1
    reprodueix(pm, synth, t_inici)
    assert len(synth.on) == 16, f"S'esperaven 16 note_on, n'han arribat {len(synth.on)}"
    assert len(synth.off) == 16, f"S'esperaven 16 note_off, n'han arribat {len(synth.off)}"
    for i in range(16):
        error_on = (synth.on[i] - (t_inici + notes[i].start)) * 1000
        assert error_on > -1, f"La nota {i + 1} ha començat {-error_on:.1f} ms ABANS d'hora"
        if i != 5:
            assert error_on < 5, (f"La nota {i + 1} ha començat {error_on:.1f} ms tard. "
                                  "Si totes les notes després de la 6a van tard, el retard "
                                  "s'arrossega: espera fins a t_inici + nota.start, no 'una durada'.")
        assert synth.off[i] > synth.on[i], f"El note_off de la nota {i + 1} arriba abans del note_on"
    print("✅ Part 3 correcta: la 6a nota s'ha encallat 25 ms i les següents han tornat a lloc")


# ======================================================================
# PART 4 — Munta-ho i escolta-ho
# ======================================================================
#
# Escriu tu aquesta funció de principi a fi:
#   1. tria un acord (mínim 3 notes), mode, octaves i repeticions
#      (la seqüència ha de tenir com a mínim 16 notes)
#   2. tria tempo, subdivisio, gate, accent i cada
#   3. crea la seqüència (Part 1) i les notes (Part 2)
#   4. toca-la amb reprodueix (Part 3). Amb metrònom o sense: tu tries
#   5. desa-la amb pm.write('el_meu_sequenciador.mid')
#      (pots obrir el fitxer en un DAW o a Colab, com a la Sessió 6)

def el_meu_sequenciador():
    pass  # <-- el teu codi


def comprova_part4():
    assert os.path.exists('el_meu_sequenciador.mid'), \
        "No trobo 'el_meu_sequenciador.mid': executa abans el_meu_sequenciador()"
    pm = pretty_midi.PrettyMIDI('el_meu_sequenciador.mid')
    n = pm.instruments[0].notes
    assert len(n) >= 16, f"La seqüència ha de tenir com a mínim 16 notes, en té {len(n)}"
    diferents = []
    for nota in n:
        if nota.pitch not in diferents:
            diferents.append(nota.pitch)
    assert len(diferents) >= 3, "L'acord ha de tenir com a mínim 3 notes diferents"
    print(f"✅ Part 4: {len(n)} notes, {len(diferents)} alçades diferents")


# ======================================================================
# PART 5 — Reflexió (escriu dins les cometes)
# ======================================================================

# 1. A la Sessió 6, mido donava el temps de cada missatge en DELTA (des del
#    missatge anterior). pretty_midi el dona en ABSOLUT (des de l'inici).
#    Quina de les dues formes encaixa amb l'estratègia A, i quina amb la B? Per què?
resposta_1 = """

"""

# 2. A demo_5_la_trampa(), segons Python l'estratègia B no tenia cap retard,
#    però l'altaveu feia espetecs i les notes i el click es desquadraven.
#    Què passava? Què canviaries d'un seqüenciador que ha de fer molt de càlcul
#    entre nota i nota?
resposta_2 = """

"""

# 3. Executa demo_3_mesura() (a exemples.py) al teu ordinador.
#    Quants ms es passa cada time.sleep, de mitjana? (retard final d'A / 31)
#    A quina nota perd A una semicorxera sencera? Coincideix amb l'exercici en paper?
resposta_3 = """

"""


def comprova_part5():
    respostes = [resposta_1, resposta_2, resposta_3]
    for i in range(3):
        assert len(respostes[i].strip()) > 30, f"La resposta {i + 1} és buida o massa curta"
    print("✅ Part 5: reflexió escrita")


# ======================================================================
# 🚀 CHALLENGES (opcionals)
# ======================================================================
#
# 1. Baix: afegeix un segon instrument que toqui la fonamental de l'acord una
#    octava avall, a les negres, alhora que l'arpegi. Ara les notes dels dos
#    instruments s'encreuen: cal tocar els esdeveniments (on i off de tots dos)
#    en ordre de temps.
#
# 2. Clock extern: fes que el teu arpegiador avanci una nota cada 6 missatges
#    de clock MIDI (byte 248; 24 per negra) rebuts amb rtmidi2, com a la Sessió 6.
#    El tempo el marca qui envia el clock: un DAW pel bus IAC, o una placa Arduino.
#
# 3. Precís a la mostra: amb l'estratègia B, cada nota encara pot caure fins a
#    1.45 ms tard (el bloc del callback). Fes una versió de SinteSimple que
#    rebi les notes amb el NÚMERO DE MOSTRA on han de començar i les engegui
#    dins el callback a la mostra exacta. És com treballa un seqüenciador
#    professional, i és el que necessitareu per a la plantilla Looper/bassline
#    del projecte final.
