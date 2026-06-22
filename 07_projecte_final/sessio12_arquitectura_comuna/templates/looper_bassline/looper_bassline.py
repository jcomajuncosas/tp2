"""
Projecte final — Rol: LOOPER/BASSLINE
Step-sequencer per a una línia de baix sintetitzada (Oscillator + Envelope,
S8-S9), amb tempo marcat per TU mateix en directe (tap-to-tempo manual).

INSTRUMENT AUTÒNOM: no depèn de cap altre instrument de l'ensemble — el teu
tempo surt només dels teus propis taps, no es sincronitza per codi amb ningú.

Requereix: numpy, sounddevice, mido, python-rtmidi

Com s'executa:
  python3 looper_bassline.py

CONTROLS MIDI (notes per defecte, configurables a CONFIG més avall):
  Nota 24 (C0)  -> TAP:         marca el tempo (prem-la diverses vegades seguides al pols)
  Nota 26 (D0)  -> NEXT_STEP:   mou el cursor d'edició al pas següent (cicle 0..N_PASSOS-1)
  Nota 28 (E0)  -> CLEAR_STEP:  buida el pas on és el cursor (queda en silenci)
  Nota 30 (F0)  -> PLAY:        engega el transport (recorre els passos al tempo marcat)
  Nota 31 (F#0) -> STOP:        atura el transport
  Qualsevol altra nota (p.ex. 36-72, tot el teclat) -> assigna AQUESTA alçada
                                al pas on és el cursor ara mateix (lliure, no
                                lligada a l'índex del pas: pots posar la nota
                                que vulguis a cada pas).

MÀQUINA D'ESTATS (un sol mode, navegació i edició conviuen sempre):
  EDITANT --[TAP x2]--> (tempo actualitzat, segueix EDITANT)
  EDITANT --[NEXT_STEP]--> (cursor avança un pas)
  EDITANT --[nota lliure]--> (pas del cursor assignat amb aquesta alçada)
  EDITANT --[PLAY]--> REPRODUINT --[STOP]--> EDITANT
  (es pot seguir editant passos mentre REPRODUINT — els canvis es senten al pròxim cicle)

ESTRUCTURA D'AQUEST FITXER:
  - NUCLI MÍNIM (TODO 1-4): avançar pas, tap-tempo, trigger de pas dins del
    bloc de sortida, generar la nota sintetitzada del pas.
  - EXTENSIONS (TODO 5-6): opcionals — swing, accent per pas.
"""

import time
import numpy as np
import sounddevice as sd

try:
    import mido
except ModuleNotFoundError:
    print("Aquest exemple necessita mido: pip3 install mido python-rtmidi")
    raise

SAMPLE_RATE = 44100
BLOCK = 512
N_PASSOS = 8

CONFIG = {
    'nota_tap': 24,
    'nota_next_step': 26,
    'nota_clear_step': 28,
    'nota_play': 30,
    'nota_stop': 31,
    'tempo_per_defecte_s': 0.3,  # durada de pas si encara no s'ha fet cap TAP
}


# =================================================================
# UGens ja coneguts de S8 — NO cal tocar-los
# =================================================================
class Oscillator:
    def __init__(self, freq=110.0, waveform='saw', sample_rate=SAMPLE_RATE):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.phase = 0.0

    def process(self, n):
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self.phase + phase_inc * np.arange(n)
        if self.waveform == 'saw':
            out = 2 * ((phases / (2 * np.pi)) % 1.0) - 1
        else:
            out = np.sin(phases)
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out


class Envelope:
    """Pluck curt: attack ràpid, decay cap a 0 (sense sustain) — típic de baix."""

    def __init__(self, attack=0.005, decay=0.15, sustain=0.0, sample_rate=SAMPLE_RATE):
        self.attack, self.decay, self.sustain = attack, decay, sustain
        self.sample_rate = sample_rate
        self.stage = 'idle'
        self.level = 0.0
        self.stage_samples = 0

    def note_on(self):
        self.stage = 'attack'
        self.stage_samples = 0

    def process(self, n):
        out = np.zeros(n)
        for k in range(n):
            if self.stage == 'attack':
                na = max(1, int(self.attack * self.sample_rate))
                self.level = min(1.0, self.stage_samples / na)
                if self.stage_samples >= na:
                    self.stage = 'decay'
                    self.stage_samples = 0
                    continue
            elif self.stage == 'decay':
                nd = max(1, int(self.decay * self.sample_rate))
                t = min(1.0, self.stage_samples / nd)
                self.level = 1.0 + t * (self.sustain - 1.0)
                if self.stage_samples >= nd:
                    self.stage = 'idle'
                    self.level = 0.0
            else:
                self.level = 0.0
            out[k] = self.level
            self.stage_samples += 1
        return out


def midi_a_freq(nota_midi):
    """Conversió estàndard nota MIDI -> Hz (la mateixa fórmula de TP1/Bloc 4)."""
    return 440.0 * (2 ** ((nota_midi - 69) / 12))


def fes_nota_baix(nota_midi, n_samples=int(SAMPLE_RATE * 0.25)):
    """Genera UNA nota de baix completa: Oscillator greu + Envelope tipus pluck."""
    osc = Oscillator(freq=midi_a_freq(nota_midi), waveform='saw')
    env = Envelope(attack=0.005, decay=0.18, sustain=0.0)
    env.note_on()
    out = np.zeros(n_samples, dtype='float32')
    i = 0
    while i < n_samples:
        n = min(BLOCK, n_samples - i)
        out[i:i + n] = osc.process(n) * env.process(n)
        i += n
    return out


# =================================================================
# TODO 1 (NUCLI MÍNIM): avançar el cursor de pas
# =================================================================
def seguent_pas(pas_actual, n_passos=N_PASSOS):
    """
    Donat el pas actual (0..n_passos-1), retorna el següent, tornant a 0
    després de l'últim — el mateix mòdul de TP1 (for/range, % n).
    """
    # TODO 1: substitueix per l'expressió correcta
    return 0  # <-- substitueix


# =================================================================
# TODO 2 (NUCLI MÍNIM): tap-to-tempo
# =================================================================
def calcula_durada_pas(t_tap_anterior, t_tap_actual, durada_actual):
    """
    Donat el moment del tap anterior i el d'ara (en segons, perfcounter),
    retorna la nova durada de pas (l'interval entre els dos taps).

    Si 't_tap_anterior' és None (és el primer tap de tots, encara no hi ha
    interval calculable), retorna 'durada_actual' sense canviar-la.
    """
    # TODO 2: si no hi ha tap anterior, retorna durada_actual sense tocar-la;
    #         si n'hi ha, retorna la diferència t_tap_actual - t_tap_anterior
    return durada_actual  # <-- substitueix


# =================================================================
# TODO 3 (NUCLI MÍNIM): decidir si toca disparar el pas dins d'aquest bloc
# =================================================================
def toca_avancar_pas(t_ultim_canvi, t_ara, durada_pas):
    """
    Donat el moment en què va començar el pas actual, el moment d'ara, i
    la durada que ha de tenir cada pas, retorna True si ja ha passat prou
    temps per avançar al pas següent.
    """
    # TODO 3: compara (t_ara - t_ultim_canvi) amb durada_pas
    return False  # <-- substitueix


# =================================================================
# TODO 4 (NUCLI MÍNIM): generar el so del pas actual
# =================================================================
def so_del_pas(passos, idx_pas):
    """
    Donada la llista de passos (cada element és None o una nota MIDI) i
    l'índex del pas actual, retorna l'àudio a sonar:
      - si el pas és None (buit), retorna un array de zeros (silenci)
      - si el pas té una nota assignada, retorna fes_nota_baix(nota)
    """
    # TODO 4: mira passos[idx_pas] i actua en conseqüència
    return np.zeros(BLOCK, dtype='float32')  # <-- substitueix


# =================================================================
# EXTENSIONS OPCIONALS (TODO 5-6)
# =================================================================
#
# TODO 5 (EXTENSIÓ): swing
#   Fes que els passos senars (1, 3, 5, 7) sonin lleugerament endarrerits
#   respecte als parells (per exemple, un 15% addicional de la durada de
#   pas) — el "groove" típic de moltes línies de baix. Caldrà guardar
#   aquest retard a 'toca_avancar_pas()' segons si l'índex és parell/senar.
#
# TODO 6 (EXTENSIÓ): accent per pas
#   En lloc que cada pas guardi només una nota MIDI, guarda una tupla
#   (nota, velocity) i fes que 'fes_nota_baix()' rebi un 'gain' proporcional
#   a la velocity (igual que 'amplitude' al Sinte) — així pots remarcar
#   alguns passos més fort que d'altres, com fa un baixista real.


# =================================================================
# Màquina d'estats i transport — NO cal tocar-la
# =================================================================
class LooperBassline:
    def __init__(self):
        self.passos = [None] * N_PASSOS   # cada element: None o nota MIDI (int)
        self.cursor_edicio = 0
        self.reproduint = False

        self.durada_pas = CONFIG['tempo_per_defecte_s']
        self.t_ultim_tap = None

        self.pas_actual = 0
        self.t_ultim_canvi_pas = None
        self.so_pas_actual = np.zeros(0, dtype='float32')
        self.pos_dins_so = 0

    # ---- Edició ----
    def next_step(self):
        self.cursor_edicio = seguent_pas(self.cursor_edicio)
        print(f">> Cursor al pas {self.cursor_edicio} "
              f"(actualment: {self.passos[self.cursor_edicio]})")

    def assigna_nota_al_cursor(self, nota_midi):
        self.passos[self.cursor_edicio] = nota_midi
        print(f">> Pas {self.cursor_edicio}: nota MIDI {nota_midi} assignada")

    def clear_step(self):
        self.passos[self.cursor_edicio] = None
        print(f">> Pas {self.cursor_edicio}: buidat")

    def tap(self):
        t_ara = time.perf_counter()
        self.durada_pas = calcula_durada_pas(self.t_ultim_tap, t_ara, self.durada_pas)
        self.t_ultim_tap = t_ara
        print(f">> TAP — durada de pas: {self.durada_pas:.3f}s "
              f"({60.0 / (self.durada_pas * 4):.0f} BPM aprox., 4 passos/temps)")

    # ---- Transport ----
    def play(self):
        if not self.reproduint:
            self.reproduint = True
            self.pas_actual = 0
            self.t_ultim_canvi_pas = time.perf_counter()
            self._dispara_pas_actual()
            print(">> PLAY")

    def stop(self):
        self.reproduint = False
        print(">> STOP")

    def _dispara_pas_actual(self):
        self.so_pas_actual = so_del_pas(self.passos, self.pas_actual)
        self.pos_dins_so = 0

    # ---- Processament d'àudio (cridat des del callback, per blocs) ----
    def genera_bloc_sortida(self, n_samples):
        out = np.zeros(n_samples, dtype='float32')
        if not self.reproduint:
            return out

        t_ara = time.perf_counter()
        if toca_avancar_pas(self.t_ultim_canvi_pas, t_ara, self.durada_pas):
            self.pas_actual = seguent_pas(self.pas_actual)
            self.t_ultim_canvi_pas = t_ara
            self._dispara_pas_actual()

        restant = len(self.so_pas_actual) - self.pos_dins_so
        if restant > 0:
            n = min(n_samples, restant)
            out[:n] = self.so_pas_actual[self.pos_dins_so:self.pos_dins_so + n]
            self.pos_dins_so += n

        return out


def main():
    lb = LooperBassline()

    print("Dispositius MIDI disponibles:", mido.get_input_names())
    inport = mido.open_input()

    def callback(indata, outdata, frames, time_info, status):
        outdata[:, 0] = lb.genera_bloc_sortida(frames)

    with sd.Stream(samplerate=SAMPLE_RATE, blocksize=BLOCK, channels=1, callback=callback):
        print("Looper/bassline actiu.")
        print("Mou el cursor amb NEXT_STEP, assigna alçades tocant notes lliures, després PLAY.")
        print("Ctrl+C per aturar.")
        try:
            for msg in inport:
                if msg.type != 'note_on' or msg.velocity == 0:
                    continue
                nota = msg.note
                if nota == CONFIG['nota_tap']:
                    lb.tap()
                elif nota == CONFIG['nota_next_step']:
                    lb.next_step()
                elif nota == CONFIG['nota_clear_step']:
                    lb.clear_step()
                elif nota == CONFIG['nota_play']:
                    lb.play()
                elif nota == CONFIG['nota_stop']:
                    lb.stop()
                elif nota >= 32:
                    # Qualsevol nota fora del rang de controls (24-31) assigna
                    # la seva alçada al pas on és el cursor ara mateix.
                    lb.assigna_nota_al_cursor(nota)
        except KeyboardInterrupt:
            print("\nAturant...")


if __name__ == "__main__":
    main()
