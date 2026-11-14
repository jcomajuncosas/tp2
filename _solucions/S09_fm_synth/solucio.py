"""
SOLUCIÓ — Assignment — Bloc 5b, Sessió 9 (Thonny)
La teva VeuFM, en temps real

IMPORTANT: executa amb Thonny (entorn local). NO funciona a Colab.
Un cop completat, puja aquest fitxer al Classroom (a més del notebook).

COM TREBALLAR-HI A THONNY:
  1. Completa una part.
  2. Prem F5 (Run). Això només DEFINEIX les classes i funcions; no sona res.
  3. A la consola (Shell), crida la funció d'aquella part:
         >>> comprova_classes()
         >>> escolta_demo()
  4. Passa a la part següent.

Parts:  A  enganxa les teves classes del notebook
        B  la velocity també controla la brillantor
        C  escolta-la en temps real (ja fet: llegeix-lo!)
        D  el teu preset i la teva seqüència
        E  reflexió  ·  CHALLENGE polifonia
"""

import numpy as np
import sounddevice as sd
from scipy import signal

sample_rate = 44100
blocksize = 512


def note_to_freq(note_number):
    return 440.0 * (2 ** ((note_number - 69) / 12))


# ===============================================================
# PART A — Les teves classes
#
#   Copia aquí, del teu notebook, les tres classes tal com les tens:
#     - Oscillator (amb _ona, process i process_freqs)
#     - Envelope (la de la Part 4, la que té self.stage)
#     - VeuFM (la teva, Part 5)
#   Després F5 i, a la Shell:  >>> comprova_classes()
# ===============================================================

class Oscillator:
    def __init__(self, freq=440.0, waveform='sine', sample_rate=44100):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate
        self._phase = 0.0

    def _ona(self, fases):
        if self.waveform == 'sine':
            return np.sin(fases)
        elif self.waveform == 'square':
            return signal.square(fases)
        elif self.waveform == 'sawtooth':
            return signal.sawtooth(fases)
        else:
            print("Forma d'ona desconeguda:", self.waveform, "→ retorno silenci")
            return np.zeros(len(fases))

    def generate(self, duration):
        return self.process(int(round(self.sample_rate * duration)))

    def process(self, n_samples):
        increment = 2 * np.pi * self.freq / self.sample_rate
        fases = self._phase + increment * np.arange(n_samples)
        self._phase = (self._phase + increment * n_samples) % (2 * np.pi)
        return self._ona(fases)

    def process_freqs(self, freqs):
        fases = np.zeros(len(freqs))
        for k in range(len(freqs)):
            fases[k] = self._phase
            self._phase = (self._phase + 2 * np.pi * freqs[k] / self.sample_rate) % (2 * np.pi)
        return self._ona(fases)


class Envelope:
    def __init__(self, attack=0.01, decay=0.1, sustain=0.7, release=0.2, sample_rate=44100):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.sample_rate = sample_rate
        self.stage = 'idle'
        self.level = 0.0
        self._pas = 0.0

    def note_on(self):
        self.stage = 'attack'
        n_attack = max(1, int(self.attack * self.sample_rate))
        self._pas = 1.0 / n_attack

    def note_off(self):
        if self.stage == 'idle':
            return
        self.stage = 'release'
        n_release = max(1, int(self.release * self.sample_rate))
        self._pas = self.level / n_release

    def process(self, n_samples):
        out = np.zeros(n_samples)
        for k in range(n_samples):
            if self.stage == 'attack':
                self.level = self.level + self._pas
                if self.level >= 1.0:
                    self.level = 1.0
                    self.stage = 'decay'
                    n_decay = max(1, int(self.decay * self.sample_rate))
                    self._pas = (1.0 - self.sustain) / n_decay
            elif self.stage == 'decay':
                self.level = self.level - self._pas
                if self.level <= self.sustain:
                    self.level = self.sustain
                    self.stage = 'sustain'
            elif self.stage == 'sustain':
                self.level = self.sustain
            elif self.stage == 'release':
                self.level = self.level - self._pas
                if self.level <= 0.0:
                    self.level = 0.0
                    self.stage = 'idle'
            out[k] = self.level
        return out


class VeuFM:
    def __init__(self, ratio=1.0, I_max=3.0, attack=0.01, decay=0.2, sustain=0.6, release=0.3):
        self.ratio = ratio
        self.I_max = I_max
        self.carrier = Oscillator()
        self.modulator = Oscillator()
        self.env = Envelope(attack, decay, sustain, release)
        self.gain = 0.0
        self.I_nota = I_max                       # PART B

    def note_on(self, note_number, velocity=100):
        self.carrier.freq = note_to_freq(note_number)
        self.modulator.freq = self.carrier.freq * self.ratio
        self.gain = velocity / 127
        # PART B: brillantor segons la velocity. Una corba suau: a velocity
        # 127 l'índex és I_max; a velocity baixa, cap a un 20% d'I_max.
        self.I_nota = self.I_max * (0.2 + 0.8 * (velocity / 127) ** 2)
        self.env.note_on()

    def note_off(self):
        self.env.note_off()

    def process(self, n_samples):
        corba = self.env.process(n_samples)
        index = self.I_nota * corba               # PART B: I_nota en lloc d'I_max
        mod = self.modulator.process(n_samples)
        freqs = self.carrier.freq + index * self.modulator.freq * mod
        return self.carrier.process_freqs(freqs) * corba * self.gain


def comprova_classes():
    """Comprova que les classes enganxades funcionen fora del notebook."""
    if 'VeuFM' not in globals() or 'Envelope' not in globals() or 'Oscillator' not in globals():
        print("❌ Falten classes: enganxa Oscillator, Envelope i VeuFM a la Part A i prem F5")
        return
    veu = VeuFM(ratio=2.0, I_max=4.0)
    veu.note_on(57, 127)
    bloc = veu.process(blocksize)
    assert len(bloc) == blocksize, "process(512) no retorna 512 mostres"
    assert abs(veu.modulator.freq - 440.0) < 0.01, "El modulador hauria de ser portador × ratio"
    veu.note_off()
    for i in range(60):
        bloc = veu.process(blocksize)
    assert np.max(np.abs(bloc)) < 1e-6, "Després del release hauria d'haver-hi silenci"
    print("✅ Part A: les teves classes funcionen a Thonny")


# ===============================================================
# PART B — La velocity també controla la brillantor
#
#   En un instrument acústic, tocar més fort no només fa més volum:
#   també fa el so més brillant (més harmònics). Amb FM això és
#   molt fàcil: la brillantor és l'índex.
#
#   Modifica la TEVA VeuFM (a la Part A) perquè l'índex màxim de
#   cada nota depengui de la velocity:
#     - a velocity 127, l'índex de la nota és I_max
#     - com més fluix, més petit (però mai 0: una nota fluixa
#       també ha de tenir una mica de timbre)
#   La corba la tries tu (lineal? quadràtica? amb un mínim?).
#   Pensa on cal calcular-ho (quan arriba la nota) i on cal
#   fer-ho servir (a cada bloc).
#
#   >>> comprova_velocity()
#   >>> escolta_velocity()     (la mateixa nota, de pp a ff)
# ===============================================================

def fora_de_la_fonamental(x, f0):
    """Fracció de l'energia que NO és a la fonamental f0: 0 = sinus pur; com més alta, més timbre."""
    s = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    f = np.fft.rfftfreq(len(x), 1 / sample_rate)
    a_la_fonamental = np.sum(s[np.abs(f - f0) < 15])
    return 1 - a_la_fonamental / np.sum(s)


def nota_aillada(veu, nota, velocity, blocs=40):
    veu.note_on(nota, velocity)
    trossos = []
    for i in range(blocs):
        trossos.append(veu.process(blocksize))
    return np.concatenate(trossos)


def comprova_velocity():
    valors = []
    for vel in [20, 60, 100, 127]:
        so = nota_aillada(VeuFM(ratio=1.0, I_max=2.5, sustain=0.8), 57, vel)
        valors.append(fora_de_la_fonamental(so[2048:], 220.0))
    print("   energia fora de la fonamental a velocity 20, 60, 100, 127:", np.round(valors, 3))
    assert valors[0] > 0.02, \
        "A velocity baixa el so s'ha quedat sense timbre (gairebé un sinus pur): l'índex no hauria d'arribar a 0"
    for i in range(3):
        assert valors[i] < valors[i + 1] - 0.01, \
            "Com més forta la velocity, més timbre hauria de tenir el so (l'índex ha de créixer amb la velocity)"
    print("✅ Part B: la velocity controla la brillantor")


def escolta_velocity():
    veu = VeuFM(ratio=1.0, I_max=6.0, attack=0.01, decay=0.4, sustain=0.5, release=0.3)
    notes = []
    t = 0.0
    for vel in [20, 45, 70, 95, 127]:
        notes.append((52, vel, t, t + 0.5))
        t = t + 0.7
    print("La mateixa nota, de pp a ff. Escolta el volum I el timbre.")
    toca_en_directe(veu, notes)


# ===============================================================
# PART C — En temps real (ja fet: llegeix-lo amb calma)
#
#   El Reproductor és, ell mateix, un UGen: té process(n). A cada
#   bloc mira si algun note_on / note_off cau dins el bloc, els
#   envia a la veu, i després li demana les mostres.
#   Precisió: la de bloc (512 mostres ≈ 11,6 ms). Per a precisió de
#   mostra caldria el lookahead de la Sessió 7.
#
#   Fixa't: el callback només fa UNA cosa, demanar un bloc.
#   Tota la memòria (fases, estat de l'envolvent, on som de la
#   seqüència) viu dins els objectes, no en globals.
# ===============================================================

class Reproductor:
    def __init__(self, veu, notes):
        """notes: llista de (nota, velocity, segon_on, segon_off), en ordre de temps."""
        self.veu = veu
        self.notes = notes
        self._mostra = 0                          # estat: on som de la seqüència

    def process(self, n_samples):
        inici = self._mostra
        fi = inici + n_samples
        for nota, vel, t_on, t_off in self.notes:
            if inici <= int(t_off * sample_rate) < fi:
                self.veu.note_off()
            if inici <= int(t_on * sample_rate) < fi:
                self.veu.note_on(nota, vel)
        self._mostra = fi
        return self.veu.process(n_samples)


reproductor = None                                # l'única global: el que sona ara


def callback(outdata, frames, time_info, status):
    if status:
        print(status)
    outdata[:, 0] = 0.5 * reproductor.process(frames)


def toca_en_directe(veu, notes):
    global reproductor
    reproductor = Reproductor(veu, notes)
    final = 0.0
    for nota, vel, t_on, t_off in notes:
        final = max(final, t_off)
    durada = final + veu.env.release + 0.3
    with sd.OutputStream(samplerate=sample_rate, blocksize=blocksize,
                         channels=1, dtype='float32', callback=callback):
        sd.sleep(int(durada * 1000))


def escolta_demo():
    veu = VeuFM(ratio=1.0, I_max=5.0, attack=0.05, decay=0.3, sustain=0.6, release=0.2)
    notes = [(55, 100, 0.0, 0.35), (59, 90, 0.4, 0.75), (62, 110, 0.8, 1.15),
             (67, 127, 1.2, 2.0), (66, 80, 2.1, 2.3), (64, 70, 2.4, 2.6), (62, 100, 2.7, 3.6)]
    toca_en_directe(veu, notes)


# ===============================================================
# PART D — El teu instrument
#
#   1. Tria el teu preset: ratio, I_max i l'envolvent (pots partir
#      de la taula de timbres del notebook).
#   2. Escriu una seqüència d'almenys 8 notes amb velocities
#      diferents (que se senti el canvi de brillantor!).
#   Format de cada nota: (nota_midi, velocity, segon_on, segon_off)
#
#   >>> escolta_meva()
# ===============================================================

el_meu_preset = VeuFM(ratio=3.5, I_max=4.0, attack=0.005, decay=0.25, sustain=0.2, release=0.15)

la_meva_sequencia = [
    (48, 120, 0.00, 0.20), (48, 50, 0.25, 0.45), (55, 90, 0.50, 0.70), (48, 40, 0.75, 0.95),
    (51, 127, 1.00, 1.20), (51, 45, 1.25, 1.45), (58, 100, 1.50, 1.70), (53, 70, 1.75, 2.30),
]


def escolta_meva():
    assert el_meu_preset is not None, "Crea el_meu_preset (una VeuFM)"
    assert len(la_meva_sequencia) >= 8, "La seqüència ha de tenir almenys 8 notes"
    velocities = []
    for nota, vel, t_on, t_off in la_meva_sequencia:
        assert t_off > t_on, "Cada nota ha d'acabar després de començar"
        if vel not in velocities:
            velocities.append(vel)
    assert len(velocities) >= 3, "Fes servir almenys 3 velocities diferents"
    toca_en_directe(el_meu_preset, la_meva_sequencia)


# ===============================================================
# PART E — Reflexió (respon dins les cometes)
# ===============================================================

reflexio_callback = """
El callback només demana un bloc al reproductor. Tota la memòria viu als
objectes: la fase de cada oscil·lador, l'stage i el level de l'envolvent,
i la posició de la seqüència al Reproductor. Amb globals en caldrien moltes.
"""

reflexio_cost = """
process_freqs fa un bucle de Python mostra a mostra, i l'envolvent també.
Segueix sonant bé perquè 512 mostres es calculen molt per sota dels 11,6 ms
que dura el bloc. Amb moltes veus alhora podria no arribar-hi.
"""


# ===============================================================
# 🚀 CHALLENGE (opcional) — Polifonia
#
#   Ara només sona una nota alhora: si en toques una de nova, la
#   veu salta. Fes una classe Polifonic amb una LLISTA de 4 VeuFM
#   i els mètodes note_on / note_off / process:
#     - cada note_on va a la veu següent (l'operador % és el teu amic)
#     - note_off(nota) ha d'apagar la veu que toca AQUELLA nota
#       (què haurà de recordar cada veu?)
#     - process(n) suma les 4 veus
#   Caldrà adaptar el Reproductor perquè cridi note_off(nota).
#   Toca un acord!
# ===============================================================

# El teu codi del challenge aquí


print("Funcions definides. Crida-les des de la consola:")
print("  comprova_classes()   escolta_demo()")
print("  comprova_velocity()  escolta_velocity()   escolta_meva()")
