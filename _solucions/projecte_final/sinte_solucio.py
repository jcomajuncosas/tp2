"""
Solució de referència — Projecte final: SINTE
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida TODOs 1-3 (NotePatch) amb el backend null de signalflow.
Metodologia validada: AudioGraphConfig(backend_name="null") +
graph.render(bufsize) + node_guardat.output_buffer[0].
Els TODOs 4-6 (extensions opcionals) s'exemplifiquen però no es validen
amb asserts específics (depenen del gust musical del grup).
"""

from signalflow import *
import numpy as np

SAMPLE_RATE = 44100


# ── Solució de referència de NotePatch (TODOs 1-3) ───────────────────────────

class NotePatch(Patch):
    def __init__(self):
        super().__init__()

        note      = self.add_input("note",      60)
        amplitude = self.add_input("amplitude", 0.5)
        gate      = self.add_input("gate",      1.0)

        freq = MidiNoteToFrequency(note)

        # TODO 1: oscil·lador portador — SawOscillator (ric en harmònics)
        signal = SawOscillator(freq)

        # TODO 2: envolvent ADSR — caràcter sostingut
        env = ADSREnvelope(attack=0.05, decay=0.1, sustain=0.7, release=0.3, gate=gate)

        # TODO 3: combina senyal + envolvent + amplitud (velocity)
        self.out_node = signal * env * amplitude   # guardat per poder llegir output_buffer
        self.set_output(self.out_node)


# ── Validació amb backend null ────────────────────────────────────────────────

config = AudioGraphConfig()
config.backend_name = "null"
config.sample_rate  = SAMPLE_RATE
graph = AudioGraph(config=config)

patch = NotePatch()
patch.set_input("note",      69)    # La4 = 440Hz
patch.set_input("amplitude", 0.7)
patch.set_input("gate",      1.0)
patch.play()

bufsize = graph.output_buffer_size  # 441 per defecte amb el null backend
N_BLOCKS = 20                       # renderitzem ~0.2s per arribar al sustain

for _ in range(N_BLOCKS):
    graph.render(bufsize)

out = patch.out_node.output_buffer[0]

assert out is not None,            "output_buffer[0] és None"
assert len(out) == bufsize,        f"Longitud inesperada: {len(out)}"
assert not np.all(out == 0),       "Sortida tot zeros — revisa TODO 1 i TODO 3"
assert not np.any(np.isnan(out)),  "La sortida conté NaN"
assert np.max(np.abs(out)) <= 1.0 + 1e-3, \
    f"Sortida fora de rang: max={np.max(np.abs(out)):.3f}"
assert np.max(np.abs(out)) > 0.05, \
    "Zona de Sustain massa silenciosa — revisa TODO 2 (ADSREnvelope)"

print(f"✅ TODOs 1-3 (NotePatch: SawOscillator + ADSR + output) correctes")
print(f"   Sortida: {bufsize} mostres/bloc, max={float(np.max(np.abs(out))):.3f}")

# Comprova que note_off (gate=0) redueix la sortida (Release en marxa)
max_on = float(np.max(np.abs(out)))
patch.set_input("gate", 0.0)
for _ in range(5):   # uns pocs blocs — la reducció comença immediatament
    graph.render(bufsize)
out_off = patch.out_node.output_buffer[0]
max_off = float(np.max(np.abs(out_off)))
assert max_off < max_on, f"gate=0: {max_off:.3f} hauria de ser < {max_on:.3f}"
print(f"✅ gate=0 (note_off) redueix la sortida: {max_off:.3f} < {max_on:.3f}")

graph.destroy()

print("\nTODOs 4-6 (vibrato, FM, filtre) — exemples de referència:")
print()
print("TODO 4 (vibrato):")
print("  vibrato_lfo = SineLFO(5, -3, 3)")
print("  freq_amb_vibrato = freq + vibrato_lfo")
print("  signal = SawOscillator(freq_amb_vibrato)  # en lloc de SawOscillator(freq)")
print()
print("TODO 5 (FM):")
print("  I = 200")
print("  modulator = SineOscillator(freq * 2) * I")
print("  signal = SineOscillator(freq + modulator)")
print()
print("TODO 6 (filtre):")
print("  filter_env = ADSREnvelope(0.01, 0.3, 0.3, 0.3, gate=gate)")
print("  filter_env = ScaleLinExp(filter_env, 0, 1, 400, 4000)")
print("  signal = SVFilter(signal, SIGNALFLOW_FILTER_TYPE_LOW_PASS, filter_env, 0.7)")

print("\n✅ Projecte Sinte validat correctament.")
print("\nNOTA DOCENT — Criteris d'avaluació del Nucli Mínim:")
print("  - Nota MIDI controla l'alçada (MidiNoteToFrequency → oscil·lador)")
print("  - Note_on (gate=1) dispara l'envolvent, note_off (gate=0) la tanca")
print("  - Polifonia: cada note_on crea un Patch independent (ja donat al main())")
