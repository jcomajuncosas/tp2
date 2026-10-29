"""
Solució de referència — S09 Challenges opcionals
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Challenge 1: benchmark vectoritzat vs. sample-by-sample
Challenges 2 i 3 (signalflow FM i MIDI): exploratòrics — procediment de referència.
"""

import numpy as np
import time

sample_rate = 44100


# ── Classe base necessària ────────────────────────────────────────────────────

class Oscillator:
    def __init__(self, freq=440.0, waveform='sine', sample_rate=44100):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.phase = 0.0

    def process(self, n_samples):
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self.phase + phase_inc * np.arange(n_samples)
        out = np.sin(phases)
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out

    # Challenge 1 — versió sample-by-sample (codi donat al challenge)
    def process_sample_by_sample(self, n_samples):
        out = np.zeros(n_samples)
        for i in range(n_samples):
            out[i] = np.sin(self.phase)
            self.phase += 2 * np.pi * self.freq / self.sample_rate
            self.phase %= 2 * np.pi
        return out


# ── Challenge 1 — Benchmark ──────────────────────────────────────────────────
# Repte: implementa process_sample_by_sample (codi donat al challenge) i
# cronometra les dues versions generant 10 segons de so (441000 mostres).

N = 441000  # 10s a 44100 Hz

osc_v = Oscillator(freq=440)
t0 = time.perf_counter()
_ = osc_v.process(N)
t1 = time.perf_counter()
temps_vectoritzat = t1 - t0

osc_s = Oscillator(freq=440)
t0 = time.perf_counter()
_ = osc_s.process_sample_by_sample(N)
t1 = time.perf_counter()
temps_sample = t1 - t0

ratio = temps_sample / temps_vectoritzat

assert temps_vectoritzat < temps_sample, \
    "La versió vectoritzada hauria de ser més ràpida"
print(f"✅ Challenge 1 (benchmark):")
print(f"   Vectoritzada:      {temps_vectoritzat * 1000:.1f} ms")
print(f"   Sample-by-sample:  {temps_sample * 1000:.1f} ms")
print(f"   Ràtio: {ratio:.0f}× més lenta (sample-by-sample)")
print()
print("   Resposta a les preguntes del challenge:")
print(f"   - La versió sample-by-sample és ~{ratio:.0f}× més lenta perquè")
print("     cada iteració del bucle for té overhead d'intèrpret Python.")
print("     NumPy executa el bucle en C compilat sobre tot l'array de cop.")
print("   - El blocksize de ~512 és compromís: prou gran per beneficiar-se")
print("     de la vectorització, prou petit per mantenir latència baixa (~12ms).")


# ── Challenges 2 i 3 — signalflow (procediment de referència) ────────────────

print()
print("Challenge 2 — FM amb signalflow (codi de referència):")
print("""
from signalflow import *
graph = AudioGraph()

I = 200
modulator = SineOscillator(80) * I
carrier = SineOscillator(440 + modulator)
carrier.play()
graph.wait()
""")
print("   Diferència vs. fm_synth() de l'assignment: signalflow actualitza")
print("   carrier.freq MOSTRA A MOSTRA (no un cop per bloc) → menys aliasing,")
print("   to FM matemàticament correcte (Chowning). El nostre fm_synth() sota-")
print("   mostra el modulador → artefactes audibles amb I gran.")
print()
print("Challenge 2 — ADSR amb signalflow:")
print("""
graph = AudioGraph()
gate = 1
env = ADSREnvelope(attack=0.01, decay=0.1, sustain=0.6, release=0.3, gate=gate)
osc = SineOscillator(440) * env
osc.play()
graph.wait(1.0)
env.set_input("gate", 0)   # equivalent al nostre note_off()
graph.wait(1.0)
""")
print("   API: en lloc de note_on()/note_off() (els nostres mètodes Python),")
print("   signalflow usa un paràmetre 'gate' (1=on, 0=off) canviable amb")
print("   set_input() en qualsevol moment. Avantatge: el canvi és processat")
print("   al proper buffer → latència mínima garantida pel motor d'àudio.")
print()
print("Challenge 3 — MIDI amb signalflow: veure l'exemple oficial a")
print("  https://github.com/ideoforms/signalflow/blob/master/examples/midi-keyboard-example.py")
print("  Combina MidiNoteToFrequency(note) + ADSREnvelope(..., gate=gate) + mido.")
print("  Instal·lació: pip install mido python-rtmidi (a més de signalflow).")
