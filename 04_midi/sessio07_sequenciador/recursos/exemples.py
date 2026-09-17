"""
Exemples — Bloc 4b, Sessió 7 (Thonny)
pretty_midi, MidiSynth en temps real, i timing precís

Requereix: midisynth.py a la mateixa carpeta (descarrega de recursos/)
Requereix: FluidSynth instal·lat al sistema (vegeu midisynth.py per instruccions)
"""

import time
import pretty_midi
from midisynth import MidiSynth


# ---------------------------------------------------------------
# 1. MidiSynth bàsic: tocar algunes notes
# ---------------------------------------------------------------
print("=== 1. MidiSynth bàsic ===")

synth = MidiSynth()

for note in [60, 64, 67, 72]:
    synth.note_on(note, velocity=90)
    time.sleep(0.4)
    synth.note_off(note)
    time.sleep(0.1)

synth.close()
print("Fet.\n")


# ---------------------------------------------------------------
# 2. Canviar instrument (General MIDI)
# ---------------------------------------------------------------
print("=== 2. Canviar instrument ===")

synth = MidiSynth()

instruments = {0: "Piano", 24: "Guitarra", 40: "Violí", 73: "Flauta"}

for program, nom in instruments.items():
    print(f"  {nom} (program={program})")
    synth.program(program)
    synth.note_on(60, velocity=90)
    time.sleep(0.5)
    synth.note_off(60)
    time.sleep(0.2)

synth.close()
print("Fet.\n")


# ---------------------------------------------------------------
# 3. Reproduir una seqüència pretty_midi amb MidiSynth
#    (convertim les notes pretty_midi a crides note_on/note_off)
# ---------------------------------------------------------------
print("=== 3. Reproduir un PrettyMIDI amb MidiSynth ===")

def reprodueix_blocking(pm_instrument, synth):
    """Reprodueix les notes en ordre, esperant amb time.sleep (Estrategia A)."""
    notes_ordenades = sorted(pm_instrument.notes, key=lambda n: n.start)
    t_anterior = 0.0
    for nota in notes_ordenades:
        time.sleep(nota.start - t_anterior)
        synth.note_on(nota.pitch, velocity=nota.velocity)
        time.sleep(nota.end - nota.start)
        synth.note_off(nota.pitch)
        t_anterior = nota.end

pm = pretty_midi.PrettyMIDI(initial_tempo=120)
instrument = pretty_midi.Instrument(program=0)
t = 0.0
for pitch in [60, 64, 67, 72, 67, 64, 60]:
    nota = pretty_midi.Note(velocity=85, pitch=pitch, start=t, end=t+0.2)
    instrument.notes.append(nota)
    t += 0.25
pm.instruments.append(instrument)

synth = MidiSynth()
reprodueix_blocking(instrument, synth)
synth.close()
print("Fet.\n")


# ---------------------------------------------------------------
# 4. ESTRATÈGIA A vs B — comparació audible
# ---------------------------------------------------------------
print("=== 4. Comparació de timing: Estrategia A vs B ===")
print("Mateix patró de bateria (140bpm, 24 corxeres), dues estratègies.\n")

n_notes = 24
tempo_bpm = 140
durada_corxera = 60 / tempo_bpm / 2  # ~0.214s
durada_nota = 0.03  # durada del so de cada cop (curt, tipus hi-hat)

synth = MidiSynth()
synth.program(118)  # Synth drum

print("--- Estrategia A: time.sleep() repetit (acumula error) ---")
for i in range(n_notes):
    synth.note_on(60, velocity=100)
    time.sleep(durada_nota)
    synth.note_off(60)
    time.sleep(durada_corxera - durada_nota)
    # Cada time.sleep() pot dormir una mica MÉS del demanat (mai menys).
    # Aquest excés es va acumulant nota rere nota -> el tempo s'alenteix
    # progressivament al llarg del patró.

time.sleep(0.5)

print("--- Estrategia B: temps objectiu absolut (perf_counter, sense acumular error) ---")
t_inici = time.perf_counter()
for i in range(n_notes):
    t_objectiu_inici = t_inici + i * durada_corxera  # objectiu calculat des de l'ORIGEN, no acumulat pas a pas
    while time.perf_counter() < t_objectiu_inici:
        pass  # busy-wait: espera activa, molt més precisa que sleep

    synth.note_on(60, velocity=100)

    t_objectiu_off = t_objectiu_inici + durada_nota
    while time.perf_counter() < t_objectiu_off:
        pass
    synth.note_off(60)

synth.close()
print("\nLa clau de l'Estrategia B: cada objectiu es calcula com 'inici + i*pas',")
print("MAI sumant temps anteriors -- així un petit retard puntual no es propaga")
print("a les notes següents (no hi ha acumulació d'error).")

