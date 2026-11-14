"""
Assignment — Bloc 5b, Sessió 9 (Thonny)
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

# Enganxa aquí les teves classes Oscillator, Envelope i VeuFM




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

el_meu_preset = None        # <-- una VeuFM amb els teus paràmetres

la_meva_sequencia = []      # <-- almenys 8 notes


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
Compara aquest callback amb els de la Sessió 5 (trèmolo, eco).
On és ara la memòria (fases, estat de l'envolvent, posició de la
seqüència)? Quantes globals hauries necessitat sense classes?
"""

reflexio_cost = """
process_freqs i Envelope.process tenen un bucle de Python mostra a
mostra, dins el callback. Per què creus que no se sent cap tall?
Què passaria si toquessis 20 notes alhora?
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
