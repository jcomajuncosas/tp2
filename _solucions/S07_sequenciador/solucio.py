"""
Solució de referència — S07: Seqüenciador / Arpegiador amb pretty_midi
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida TODOs 1-4 sense Colab ni FluidSynth.
La Part 4 (reflexió) inclou respostes de referència.
"""

import pretty_midi
import numpy as np

# ── TODOs 1 & 2 — arpegiador ────────────────────────────────────────────────

def arpegiador(acord, n_repeticions, mode='up'):
    # TODO 1: implementa els 3 modes
    if mode == 'up':
        seq = list(acord)
    elif mode == 'down':
        seq = list(reversed(acord))
    elif mode == 'updown':
        # amunt i avall sense repetir extrems: acord + acord invertit sense 1r i últim
        seq = list(acord) + list(reversed(acord))[1:-1]
    else:
        raise ValueError(f"Mode desconegut: {mode}")

    # TODO 2: repeteix n_repeticions vegades
    return seq * n_repeticions


# Autotest 1
acord_test = [60, 64, 67]

result_up = arpegiador(acord_test, n_repeticions=2, mode='up')
assert result_up == [60, 64, 67, 60, 64, 67], f"Mode 'up' incorrecte: {result_up}"

result_down = arpegiador(acord_test, n_repeticions=1, mode='down')
assert result_down == [67, 64, 60], f"Mode 'down' incorrecte: {result_down}"

result_updown = arpegiador(acord_test, n_repeticions=1, mode='updown')
assert result_updown == [60, 64, 67, 64], f"Mode 'updown' incorrecte: {result_updown}"
print("✅ TODOs 1 & 2 (arpegiador) correctes")


# ── TODO 3 — notes_a_midi ───────────────────────────────────────────────────

def notes_a_midi(pitches, note_duration, velocity=85, tempo=120, program=0):
    pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    instrument = pretty_midi.Instrument(program=program)

    # TODO 3: notes consecutives
    t = 0.0
    for pitch in pitches:
        note = pretty_midi.Note(
            velocity=velocity,
            pitch=pitch,
            start=t,
            end=t + note_duration
        )
        instrument.notes.append(note)
        t += note_duration

    pm.instruments.append(instrument)
    return pm


# Autotest 2
pm_test = notes_a_midi([60, 64, 67], note_duration=0.25, tempo=120)
assert len(pm_test.instruments) == 1
notes_test = pm_test.instruments[0].notes
assert len(notes_test) == 3
assert notes_test[0].pitch == 60 and notes_test[0].start == 0.0
assert abs(notes_test[1].start - 0.25) < 0.001
assert abs(notes_test[2].start - 0.50) < 0.001
print("✅ TODO 3 (notes_a_midi) correcte")


# ── TODO 4 — seqüenciador complet ───────────────────────────────────────────
#
# Solució de referència: acord de La menor (Am), mode updown, 4 repeticions → 16 notes

el_meu_acord  = [57, 60, 64]   # La3, Do4, Mi4 (Am)
el_meu_mode   = 'updown'
n_repeticions = 4               # updown sobre 3 notes = 4 elements x 4 = 16
note_duration = 0.15

sequencia = arpegiador(el_meu_acord, n_repeticions, mode=el_meu_mode)
pm_final  = notes_a_midi(sequencia, note_duration=note_duration, tempo=120, program=0)

# Autotest 3
assert len(el_meu_acord) >= 3
assert len(sequencia) >= 16, f"Seqüència massa curta: {len(sequencia)}"
assert len(pm_final.instruments[0].notes) >= 16
print("✅ TODO 4 (seqüenciador complet) correcte")
print(f"   Seqüència: {sequencia}")
print(f"   Total notes: {len(sequencia)}")


# ── Reflexió (referència per al docent) ─────────────────────────────────────

reflexio_referencia = {
    'pretty_midi_vs_mido':
        "pretty_midi.Note(start, end) treballa en temps absolut en segons, "
        "que és natural per a músics. mido usa delta time en ticks relatius "
        "al beat, que requereix calcular manualment la posició de cada missatge "
        "i convertir amb ticks_per_beat i tempo.",

    'timing_en_directe':
        "L'estratègia B (time.perf_counter) és la correcta: mesurar el temps "
        "real transcorregut i enviar la nota MIDI quan el rellotge supera el "
        "temps previst. sleep() no és fiable perquè el SO pot retardar-lo "
        "de forma impredictible; perf_counter permet compensar el drift acumulat.",

    'connexio_tp1':
        "A TP1 la seqüenciació es feia amb un bucle for + sleep (bloqueig síncron). "
        "L'arpegiador d'avui fa exactament el mateix a nivell musical, però genera "
        "un fitxer MIDI persistent en lloc de disparar sons en temps real. "
        "La connexió és directa: pattern → iteració → trigger.",
}

for k in reflexio_referencia:
    print(f"✅ reflexio['{k}']: ✓")

print("\n✅ Tots els TODOs de S07 validats correctament.")
print("\nNOTA DOCENT — TODO 4 és creatiu: acord, mode i tempo lliures.")
print("Criteri mínim: ≥3 notes a l'acord, ≥16 notes a la seqüència final.")
