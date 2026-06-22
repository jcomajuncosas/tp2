"""
Projecte final — Rol: SINTE
Template basat en signalflow, seguint el patró del Bloc 5 (Oscillator/Envelope/process())
que vau construir a mà a les Sessions 8-9, ara amb una llibreria professional.

Requereix: signalflow, mido, python-rtmidi
  pip3 install signalflow mido python-rtmidi
(Si tens problemes d'instal·lació, consulta la guia de troubleshooting a
05_sintesi/sessio09_fm_synth/recursos/challenges.md, Challenge 2.)

Com s'executa:
  python3 sinte.py                  # llista dispositius MIDI disponibles
  python3 sinte.py -i "Nom del dispositiu"

ESTRUCTURA D'AQUEST FITXER:
  - NUCLI MÍNIM (TODO 1-3): imprescindible per tenir un sinte que soni i respongui a MIDI.
  - EXTENSIONS (TODO 4-6): opcionals, per qui vagi més ràpid o treballi en parella.
"""

import sys
import argparse

try:
    import mido
except ModuleNotFoundError:
    print("Aquest exemple necessita mido: pip3 install mido python-rtmidi")
    sys.exit(1)

from signalflow import *


# =================================================================
# NotePatch: una veu del sinte (es crea una instància per cada nota tocada)
# =================================================================
class NotePatch(Patch):
    """
    Recordatori de S8-S9: un Oscillator "sona sempre"; és l'Envelope qui
    dona forma de nota (Attack a note_on, Release a note_off). Aquí és
    exactament el mateix concepte, amb ADSREnvelope(..., gate=gate) en
    lloc dels mètodes note_on()/note_off() que vau programar a mà.
    """

    def __init__(self):
        super().__init__()

        # 'note', 'amplitude' i 'gate' són els inputs que el callback
        # MIDI (més avall) ompliran per a cada veu individual.
        note = self.add_input("note", 60)
        amplitude = self.add_input("amplitude", 0.5)
        gate = self.add_input("gate", 1.0)

        freq = MidiNoteToFrequency(note)

        # ===========================================================
        # TODO 1 (NUCLI MÍNIM): crea l'oscil·lador portador
        # ===========================================================
        # Tria UNA forma d'ona inicial (pots canviar-la més endavant):
        #   SineOscillator(freq)      -> so pur, suau
        #   SawOscillator(freq)       -> so brillant, ric en harmònics
        #   SquareOscillator(freq)    -> so "buit", típic de videojocs antics
        # Substitueix la línia següent:
        signal = None  # <-- TODO 1: substitueix per un oscil·lador real

        # ===========================================================
        # TODO 2 (NUCLI MÍNIM): defineix l'envolvent ADSR
        # ===========================================================
        # ADSREnvelope(attack, decay, sustain, release, gate=gate)
        # Recordatori de S8: sustain és un NIVELL (0-1), no un temps.
        # Substitueix la línia següent amb valors propis (segons quin
        # caràcter vulguis donar a la teva veu: percussiu? sostingut?):
        env = None  # <-- TODO 2: substitueix per un ADSREnvelope real

        # ===========================================================
        # TODO 3 (NUCLI MÍNIM): combina senyal + envolvent + sortida
        # ===========================================================
        # Multiplica el senyal per l'envolvent i per 'amplitude' (la
        # velocity de la nota MIDI, ja normalitzada a 0-1), igual que
        # fèieu a S8 amb wave * env_curve:
        output = None  # <-- TODO 3: substitueix (signal * env * amplitude)

        self.set_output(output)


# =================================================================
# EXTENSIONS OPCIONALS (TODO 4-6) — completa-les si vas sobrat de temps
# =================================================================
#
# TODO 4 (EXTENSIÓ): afegeix vibrato (Secció 3 de S9)
#   Crea un LFO i fa'l modular lleugerament la freqüència del portador,
#   ABANS de crear 'signal' al TODO 1:
#     vibrato_lfo = SineLFO(5, -3, 3)   # 5Hz, excursió +-3Hz
#     freq_amb_vibrato = freq + vibrato_lfo
#   i fes servir 'freq_amb_vibrato' en lloc de 'freq' al teu oscil·lador.
#
# TODO 5 (EXTENSIÓ): converteix-lo en una FM senzilla (Secció 4 de S9)
#   Crea un segon oscil·lador com a modulador i fes-lo sumar a la freq
#   del portador, amb un índex I (Hz d'excursió):
#     modulator = SineOscillator(freq * 2) * I
#     signal = SineOscillator(freq + modulator)
#
# TODO 6 (EXTENSIÓ): filtre amb cutoff modulat per una envolvent pròpia
#   (similar al filter_env de l'exemple oficial de signalflow)
#     filter_env = ADSREnvelope(0.01, 0.3, 0.3, 0.3, gate=gate)
#     filter_env = ScaleLinExp(filter_env, 0, 1, 400, 4000)
#     signal = SVFilter(signal, SIGNALFLOW_FILTER_TYPE_LOW_PASS, filter_env, 0.7)
#   (fes-ho ABANS de combinar amb env a TODO 3)


def main(args):
    if args.list_devices:
        print("Dispositius MIDI d'entrada disponibles:")
        for device in mido.get_input_names():
            print(f"  - {device}")
        sys.exit(0)

    graph = AudioGraph()

    inport = mido.open_input(args.device_name)
    print(f"Connectat a: {inport}")
    print("Toca el teu controlador MIDI. Ctrl+C per aturar.\n")

    spec = NotePatch().to_spec()
    veus_actives = [None] * 128  # una veu per cada nota MIDI possible (0-127)

    try:
        for msg in inport:
            if msg.type == 'note_on' and msg.velocity > 0:
                veu = Patch(spec)
                veu.set_input("note", msg.note)
                veu.set_input("amplitude", msg.velocity / 127)
                veu.auto_free = True
                veu.play()
                veus_actives[msg.note] = veu

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if veus_actives[msg.note] is not None:
                    veus_actives[msg.note].set_input("gate", 0)
                    veus_actives[msg.note] = None

    except KeyboardInterrupt:
        print("\nAturant...")
    finally:
        inport.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sinte del projecte final (signalflow + MIDI)")
    parser.add_argument("-i", "--device-name", help="Nom del dispositiu MIDI d'entrada")
    parser.add_argument("-l", "--list-devices", action="store_true", help="Llista dispositius i surt")
    args = parser.parse_args()
    main(args)
