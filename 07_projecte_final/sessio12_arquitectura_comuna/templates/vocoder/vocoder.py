"""
Projecte final — Rol: VOCODER
"Cantant solista": cantes/parles per micro (modulador) mentre toques una
nota amb el controlador MIDI (carrier). El resultat és la teva veu amb
l'alçada exacta de la nota tocada — l'efecte vocoder clàssic dels anys 70-80
(Kraftwerk, Bode/Moog Vocoder, EMS Vocoder 5000...).

INSTRUMENT AUTÒNOM: només processa la teva pròpia veu i les teves pròpies
notes — no depèn de cap altre instrument de l'ensemble.

Requereix: signalflow, mido, python-rtmidi

Com s'executa:
  python3 vocoder.py                  # llista dispositius MIDI disponibles
  python3 vocoder.py -i "Nom del dispositiu"

COM FUNCIONA UN VOCODER DE BANC DE FILTRES (l'arquitectura "vintage"):
  1. El MODULADOR (la teva veu) i el CARRIER (un oscil·lador, tocat per
     MIDI) es divideixen CADASCUN en les MATEIXES N bandes de freqüència
     (com dividir l'espectre en "trossos").
  2. De cada banda del MODULADOR se n'extreu l'envolupant (quanta energia
     hi ha en aquell tros AHORA MATEIX — "com d'oberta tens la boca" en
     aquella zona de freqüències).
  3. Cada banda del CARRIER es multiplica per l'envolupant corresponent
     del modulador.
  4. Se sumen totes les bandes ja modulades -> sortida.

  El resultat: el carrier (que té l'alçada que tu decideixis per MIDI)
  pren la "forma" tímbrica de la teva veu — sona com si cantessis
  exactament la nota que toques.

CONTROLS MIDI:
  Qualsevol nota -> defineix l'alçada del carrier mentre la mantens
                     polsada (note_on/note_off, com el Sinte — monofònic:
                     només sona la darrera nota, no és polifònic).

ESTRUCTURA D'AQUEST FITXER:
  - NUCLI MÍNIM (TODO 1): la cadena completa del vocoder — construir el
    banc de filtres del modulador, seguir-ne l'envolupant per banda,
    aplicar-la al carrier filtrat per les mateixes bandes. És UN sol
    procés en diversos passos relacionats, no peces soltes.
  - EXTENSIONS (TODO 2-3): opcionals.
"""

import sys
import argparse

try:
    import mido
except ModuleNotFoundError:
    print("Aquest exemple necessita mido: pip3 install mido python-rtmidi")
    sys.exit(1)

from signalflow import *

# 16 bandes, repartiment logarítmic amb més densitat a la zona de
# formants vocals (300-3000Hz, on viu la intel·ligibilitat de la parla) —
# inspirat en el repartiment típic de vocoders clàssics (Bode/Moog ~10
# bandes, EMS Vocoder 5000, Roland VP-330).
BANDES_HZ = [100, 144, 208, 300, 387, 500, 646, 835, 1078,
             1392, 1798, 2323, 3000, 4160, 5769, 8000]

RESONANCIA_BANDES = 0.8   # més alt = bandes més estretes/definides
SUAVITZAT_ENVOLUPANT = 0.99  # 0=sense memòria, 0.999=molt suau (com 'Smooth' de signalflow)


class VocoderPatch(Patch):
    """
    Una sola instància (NO una per nota — el vocoder és monofònic: només
    hi ha un carrier, que canvia de nota amb 'note', i només sona quan
    'gate' és 1).
    """

    def __init__(self):
        super().__init__()

        note = self.add_input("note", 60)
        gate = self.add_input("gate", 1.0)

        # ===========================================================
        # Modulador i carrier — ja donats (NO cal tocar-los)
        # ===========================================================
        # En producció real: AudioIn(1) captura el micro connectat.
        modulator = AudioIn(1)

        # Carrier ric en harmònics (cal contingut a moltes freqüències
        # perquè el filtratge per bandes tingui res a "esculpir" —
        # una sinusoide pura no funcionaria gairebé en cap banda).
        carrier = SquareOscillator(MidiNoteToFrequency(note))
        carrier = carrier * ADSREnvelope(0.01, 0.05, 0.8, 0.3, gate=gate)

        # ===========================================================
        # TODO 1 (NUCLI MÍNIM): la cadena completa del vocoder
        # ===========================================================
        # Per CADA freqüència de BANDES_HZ, has de:
        #   a) Filtrar el 'modulator' amb un BiquadFilter band-pass
        #      centrat en aquesta freqüència:
        #        BiquadFilter(modulator, SIGNALFLOW_FILTER_TYPE_BAND_PASS,
        #                     cutoff=freq, resonance=RESONANCIA_BANDES)
        #   b) Seguir-ne l'envolupant (quanta energia hi ha ARA en
        #      aquesta banda): rectificar amb Abs() i suavitzar amb
        #      Smooth(..., SUAVITZAT_ENVOLUPANT):
        #        Smooth(Abs(banda_modulador), SUAVITZAT_ENVOLUPANT)
        #   c) Filtrar el 'carrier' EXACTAMENT a la mateixa freqüència
        #      (mateix BiquadFilter band-pass, sobre 'carrier' en lloc
        #      de 'modulator'):
        #        BiquadFilter(carrier, SIGNALFLOW_FILTER_TYPE_BAND_PASS,
        #                     cutoff=freq, resonance=RESONANCIA_BANDES)
        #   d) Multiplicar la banda del carrier per l'envolupant del
        #      modulador (b * c) i guardar-ho en una llista.
        #
        # Quan tinguis les 16 bandes ja modulades a la llista, suma-les
        # amb Sum(la_teva_llista) i guarda-ho a self.output_node.
        #
        # Pots fer-ho amb un bucle 'for freq in BANDES_HZ: ...' (igual
        # que ja heu fet servir per construir coses repetitives a tot
        # el curs) o escrivint-ho explícitament — el que us sigui més
        # còmode de llegir i depurar.

        self.output_node = None  # <-- TODO 1: substitueix pel Sum() de les 16 bandes modulades
        self.set_output(self.output_node * 0.15)  # *0.15: marge per evitar saturació amb 16 bandes sumades


# =================================================================
# EXTENSIONS OPCIONALS (TODO 2-3) — completa-les si vas sobrat de temps
# =================================================================
#
# TODO 2 (EXTENSIÓ): barreja de carrier (robot pur <-> veu reconeixible)
#   Crea una segona via que NO passi pel banc de filtres (el modulator
#   "net", directe), i barreja-la amb la sortida del vocoder amb un
#   input nou (p.ex. "mix", 0=100% vocoder/robot, 1=100% veu original):
#     mix = self.add_input("mix", 0.0)
#     output = vocoder_output * (1 - mix) + modulator * mix
#
# TODO 3 (EXTENSIÓ): carrier alternatiu
#   Substitueix SquareOscillator per una FM senzilla (com a S9) o per
#   SawOscillator — cada carrier dona un caràcter de veu robòtica
#   diferent. Pots també afegir un LFO de vibrato sobre la freqüència
#   del carrier (igual que al Sinte, TODO 4) per a un vocoder "cantant".


def main(args):
    if args.list_devices:
        print("Dispositius MIDI d'entrada disponibles:")
        for device in mido.get_input_names():
            print(f"  - {device}")
        sys.exit(0)

    graph = AudioGraph()

    inport = mido.open_input(args.device_name)
    print(f"Connectat a: {inport}")
    print("Canta/parla pel micro mentre toques notes. Ctrl+C per aturar.\n")

    veu = VocoderPatch()
    veu.play()

    try:
        for msg in inport:
            if msg.type == 'note_on' and msg.velocity > 0:
                veu.set_input("note", msg.note)
                veu.set_input("gate", 1.0)

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                veu.set_input("gate", 0.0)

    except KeyboardInterrupt:
        print("\nAturant...")
    finally:
        inport.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vocoder del projecte final (signalflow + MIDI)")
    parser.add_argument("-i", "--device-name", help="Nom del dispositiu MIDI d'entrada")
    parser.add_argument("-l", "--list-devices", action="store_true", help="Llista dispositius i surt")
    args = parser.parse_args()
    main(args)
