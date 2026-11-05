"""
exemples.py — Sessió 7 (Thonny): pretty_midi, arpegiador i timing precís
=========================================================================

PER QUÈ TOT A THONNY AQUESTA SESSIÓ?
  A la Sessió 6 treballàvem amb FITXERS .mid: llegir-los, escriure'ls,
  dibuixar-los. Això no depèn del temps real i es fa bé a Colab.
  Avui el tema és el TEMPS REAL: que les notes sonin a l'instant just,
  al teu ordinador i pel teu altaveu. Colab s'executa en un servidor de
  Google, sense altaveu ni rellotge "teu". Per això avui tot és a Thonny,
  encara que també desem algun fitxer .mid.

COM FUNCIONA AQUEST FITXER
  F5 només DEFINEIX les funcions. Després, des del Shell, crida-les:

    demo_1_notes()                    pretty_midi: notes amb inici i final en segons
    demo_2_arpegiador('updown')       'up', 'down' o 'updown'
    demo_3_mesura()                   mesura la deriva d'A i B (gràfic, sense so)
    demo_3_mesura(feina_ms=4)         ... amb feina entre nota i nota
    demo_4_escolta('A')               A amb el metrònom de la targeta: se'n va
    demo_4_escolta('B')               B amb el metrònom: es queda enganxat
    demo_5_la_trampa()                B amb feina de CPU: Python diu 0 ms... escolta-ho

Necessites sinte.py a la mateixa carpeta.
"""

import time
import pretty_midi
import matplotlib.pyplot as plt
from sinte import SinteSimple, espera_fins, feina_simulada, SR


# ----------------------------------------------------------------------
# 1. pretty_midi: cada nota porta el seu inici i final, en segons
# ----------------------------------------------------------------------

def toca_amb_sleep(instrument, synth):
    """Toca les notes una rere l'altra esperant amb time.sleep.
    (Funciona... però guarda-te-la: és l'ESTRATÈGIA A de la demo 3.)"""
    for nota in instrument.notes:
        synth.note_on(nota.pitch, nota.velocity)
        time.sleep(nota.end - nota.start)
        synth.note_off(nota.pitch)


def demo_1_notes():
    pm = pretty_midi.PrettyMIDI(initial_tempo=120)
    piano = pretty_midi.Instrument(program=0)

    t = 0.0
    for pitch in [60, 64, 67, 72]:
        nota = pretty_midi.Note(velocity=90, pitch=pitch, start=t, end=t + 0.4)
        piano.notes.append(nota)
        t += 0.4

    pm.instruments.append(piano)
    pm.write('demo1.mid')             # el mateix objecte es pot desar com a fitxer

    print("   pitch   start    end")
    for nota in piano.notes:
        print(f"   {nota.pitch:5}  {nota.start:5.2f}  {nota.end:5.2f}")
    print("Cap delta, cap tick: 'start' és el temps DES DE L'INICI (temps absolut).")

    synth = SinteSimple()
    toca_amb_sleep(piano, synth)
    synth.close()


# ----------------------------------------------------------------------
# 2. Arpegiador: d'un acord a una seqüència de notes
# ----------------------------------------------------------------------

def arpegiador(acord, n_repeticions, mode='up'):
    if mode == 'up':
        seq = acord
    elif mode == 'down':
        seq = acord[::-1]                       # [::-1]: la llista al revés
    elif mode == 'updown':
        seq = acord + acord[::-1][1:-1]         # [1:-1]: sense el primer ni l'últim
    else:
        print("Mode desconegut:", mode)
        seq = []
    return seq * n_repeticions                  # llista * n: la llista repetida n cops


def notes_a_midi(pitches, durada):
    pm = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0)
    t = 0.0
    for pitch in pitches:
        instrument.notes.append(pretty_midi.Note(velocity=85, pitch=pitch, start=t, end=t + durada))
        t += durada
    pm.instruments.append(instrument)
    return pm


def demo_2_arpegiador(mode='updown'):
    seq = arpegiador([60, 64, 67], 3, mode)
    print(mode, "→", seq)
    pm = notes_a_midi(seq, 0.15)
    synth = SinteSimple()
    toca_amb_sleep(pm.instruments[0], synth)
    synth.close()


# ----------------------------------------------------------------------
# 3. Mesurem: estratègia A (sleep) contra estratègia B (temps objectiu)
#    Sense so: només el rellotge. Corxeres a 140 bpm.
# ----------------------------------------------------------------------

def mesura_A(n_notes, pas, feina_ms):
    """A: 'fes la nota, espera un pas'. Cada espera comença quan acaba l'anterior."""
    t_inici = time.perf_counter()
    retards = []
    for i in range(n_notes):
        ara = time.perf_counter() - t_inici
        retards.append((ara - i * pas) * 1000)      # ms de retard d'aquesta nota
        feina_simulada(feina_ms)
        time.sleep(pas)
    return retards


def mesura_B(n_notes, pas, feina_ms):
    """B: 'la nota i toca a l'instant inici + i*pas'. L'objectiu no depèn de quan
    ha acabat l'espera anterior: un retard puntual no s'arrossega."""
    t_inici = time.perf_counter()
    retards = []
    for i in range(n_notes):
        espera_fins(t_inici + i * pas)
        ara = time.perf_counter() - t_inici
        retards.append((ara - i * pas) * 1000)
        feina_simulada(feina_ms)
    return retards


def demo_3_mesura(n_notes=32, bpm=140, feina_ms=0):
    pas = 60 / bpm / 2
    print(f"Mesurant {n_notes} corxeres a {bpm} bpm (una corxera = {pas*1000:.0f} ms)...")
    retards_A = mesura_A(n_notes, pas, feina_ms)
    retards_B = mesura_B(n_notes, pas, feina_ms)

    print(f"Retard de l'última nota:  A = {retards_A[-1]:6.1f} ms   B = {retards_B[-1]:5.1f} ms")
    print(f"Una semicorxera dura {pas*1000/2:.0f} ms. Quantes notes triga A a perdre-la?")

    plt.figure(figsize=(9, 4))
    plt.plot(retards_A, 'o-', color='crimson', label='A: time.sleep(pas)')
    plt.plot(retards_B, 'o-', color='seagreen', label='B: espera_fins(inici + i·pas)')
    plt.axhline(pas * 1000 / 2, color='gray', linestyle='--', label='una semicorxera')
    plt.xlabel('número de nota')
    plt.ylabel('retard respecte a l\'instant ideal (ms)')
    plt.title(f'La teva màquina — feina entre notes: {feina_ms} ms')
    plt.legend()
    plt.tight_layout()
    plt.show()


# ----------------------------------------------------------------------
# 4. Escoltem-ho contra un metrònom que NO depèn de Python
#    El click el genera el callback comptant mostres (rellotge de la targeta).
#    Les notes (hi-hat agut) les envia el fil principal amb l'estratègia triada.
# ----------------------------------------------------------------------

def toca_patro(estrategia, feina_ms, tipus_feina, n_notes=32, bpm=140):
    pas = 60 / bpm / 2
    synth = SinteSimple(bpm_click=bpm)            # click a cada negra
    t_inici, mostra_inici = synth.proper_click()   # arrenquem amb un click
    espera_fins(t_inici)
    perdut_inici = synth.perdut_ms()
    retard_python = 0.0                            # retard de l'última nota, segons perf_counter

    if estrategia == 'A':
        for i in range(n_notes):
            retard_python = (time.perf_counter() - t_inici - i * pas) * 1000
            synth.note_on(84, 100, curta=True)
            feina_simulada(feina_ms, tipus_feina)
            time.sleep(pas)
    else:
        for i in range(n_notes):
            espera_fins(t_inici + i * pas)
            retard_python = (time.perf_counter() - t_inici - i * pas) * 1000
            synth.note_on(84, 100, curta=True)
            feina_simulada(feina_ms, tipus_feina)

    time.sleep(0.5)
    perdut = synth.perdut_ms() - perdut_inici
    synth.close()

    # On ha sonat cada nota segons la TARGETA (mostres), respecte al click?
    print(f"Estratègia {estrategia}, feina {feina_ms} ms ({tipus_feina}). "
          f"Error respecte al metrònom:")
    for i in [0, 7, 15, 23, n_notes - 1]:
        mostra_ideal = mostra_inici + i * pas * SR
        error = (synth.registre_on[i] - mostra_ideal) / SR * 1000
        print(f"   nota {i + 1:2}: {error:7.1f} ms")
    print(f"Retard de l'última nota segons Python (perf_counter): {retard_python:.1f} ms")
    print(f"Àudio perdut (callback que no ha arribat a temps): {perdut:.0f} ms")


def demo_4_escolta(estrategia='A', feina_ms=4):
    toca_patro(estrategia, feina_ms, 'espera')


# ----------------------------------------------------------------------
# 5. La trampa: B perfecta segons Python... però escolta l'altaveu
# ----------------------------------------------------------------------

def demo_5_la_trampa(feina_ms=4):
    """Mateixa estratègia B, però ara la feina és càlcul pur en Python.
    Mentre el fil principal calcula, el callback no pot entrar (GIL):
    arriba tard al seu termini de 1.45 ms i la targeta sona silenci."""
    toca_patro('B', feina_ms, 'cpu')
    print("Segons Python, B continua perfecta. L'altaveu diu una altra cosa:")
    print("el termini del callback depèn de TOT el que fa el programa.")
