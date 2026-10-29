"""
Solució de referència — Projecte final: VOCODER
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida TODO 1 (banc de filtres del vocoder) amb el backend null de signalflow.
AudioIn(1) no funciona amb el backend null, es substitueix per WhiteNoise()
(equivalent sintètic per a la validació de l'arquitectura).
"""

from signalflow import *
import numpy as np

SAMPLE_RATE = 44100

BANDES_HZ = [100, 144, 208, 300, 387, 500, 646, 835, 1078,
             1392, 1798, 2323, 3000, 4160, 5769, 8000]

RESONANCIA_BANDES  = 0.8
SUAVITZAT_ENVOLUPANT = 0.99


# ── Solució de referència de VocoderPatch (TODO 1) ───────────────────────────

class VocoderPatch(Patch):
    def __init__(self):
        super().__init__()

        note = self.add_input("note", 60)
        gate = self.add_input("gate", 1.0)

        # AudioIn(1) no funciona amb el backend null →
        # substituïm per WhiteNoise() per validar l'arquitectura
        modulator = WhiteNoise()

        carrier = SquareOscillator(MidiNoteToFrequency(note))
        carrier = carrier * ADSREnvelope(0.01, 0.05, 0.8, 0.3, gate=gate)

        # TODO 1: banc de filtres del vocoder
        bandes_modulades = []
        for freq in BANDES_HZ:
            # a) Filtra el modulador en aquesta banda
            banda_mod = BiquadFilter(modulator,
                                     SIGNALFLOW_FILTER_TYPE_BAND_PASS,
                                     cutoff=freq,
                                     resonance=RESONANCIA_BANDES)
            # b) Extreu l'envolupant: Abs + Smooth
            envolupant = Smooth(Abs(banda_mod), SUAVITZAT_ENVOLUPANT)
            # c) Filtra el carrier en la mateixa banda
            banda_car  = BiquadFilter(carrier,
                                      SIGNALFLOW_FILTER_TYPE_BAND_PASS,
                                      cutoff=freq,
                                      resonance=RESONANCIA_BANDES)
            # d) Multiplica carrier filtrat × envolupant del modulador
            bandes_modulades.append(banda_car * envolupant)

        self.out_node = Sum(bandes_modulades)
        self.set_output(self.out_node * 0.15)


# ── Validació amb backend null ────────────────────────────────────────────────

config = AudioGraphConfig()
config.backend_name = "null"
config.sample_rate  = SAMPLE_RATE
graph = AudioGraph(config=config)

patch = VocoderPatch()
patch.set_input("note", 60)
patch.set_input("gate", 1.0)
patch.play()

bufsize  = graph.output_buffer_size
N_BLOCKS = 30   # ~0.3s per arribar al sustain de l'ADSR del carrier

for _ in range(N_BLOCKS):
    graph.render(bufsize)

out = patch.out_node.output_buffer[0]

assert out is not None,            "output_buffer[0] és None"
assert len(out) == bufsize,        f"Longitud inesperada: {len(out)}"
assert not np.all(out == 0),       "Sortida tot zeros — revisa el bucle de TODO 1 (bandes_modulades)"
assert not np.any(np.isnan(out)),  "La sortida conté NaN"

# El gain *0.15 amb 16 bandes hauria de mantenir la sortida en rang raonable
max_out = float(np.max(np.abs(out)))
assert max_out <= 2.0, f"Sortida fora de rang: max={max_out:.3f}"

print(f"✅ TODO 1 (banc de filtres: {len(BANDES_HZ)} bandes, BiquadFilter + Abs + Smooth + Sum)")
print(f"   Sortida: {bufsize} mostres/bloc, max={max_out:.4f}")

# Verifica que la suma de les 16 bandes dona senyal (no s'han cancel·lat totes)
assert max_out > 1e-4, "Max massa baix — comprova que Sum(bandes_modulades) és correcte"
print(f"✅ Sum de {len(BANDES_HZ)} bandes té contingut (no cancel·lació total)")

graph.destroy()

print("\nTODOs 2-3 (extensió) — exemples de referència:")
print()
print("TODO 2 (barreja carrier/veu):")
print("  mix = self.add_input('mix', 0.0)")
print("  output = self.out_node * (1 - mix) + modulator * mix")
print("  self.set_output(output * 0.15)")
print()
print("TODO 3 (carrier alternatiu amb FM):")
print("  I = 50")
print("  mod_fm = SineOscillator(MidiNoteToFrequency(note) * 2) * I")
print("  carrier = SineOscillator(MidiNoteToFrequency(note) + mod_fm)")
print("  carrier = carrier * ADSREnvelope(0.01, 0.05, 0.8, 0.3, gate=gate)")

print("\n✅ Projecte Vocoder validat correctament.")
print("\nNOTA DOCENT — AudioIn(1) s'ha substituït per WhiteNoise() per al test.")
print("En producció real el modulador és AudioIn(1) (micròfon connectat).")
print("Criteris d'avaluació: que les 16 bandes estiguin totes connectades,")
print("que Abs+Smooth segueixi l'envolupant i que Sum combini correctament.")
