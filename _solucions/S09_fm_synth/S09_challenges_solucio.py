"""
SOLUCIÓ — Challenges opcionals de la Sessió 9 (notebook + assignment.py)

  1. FM amb feedback (un oscil·lador que es modula a si mateix, com el DX7)
  2. Tres operadors en pila
  3. La campana: l'índex amb la seva pròpia envolvent (més curta)
  4. Mesura't: process vs process_freqs
  5. (Thonny) Polifonia: 4 VeuFM en round-robin amb l'operador %

S'executa sencer offline (sense àudio) i imprimeix comprovacions.
Per escoltar els resultats a Colab, copia les funcions al notebook.
"""

import time
import numpy as np
from scipy import signal

sample_rate = 44100


def note_to_freq(note_number):
    return 440.0 * (2 ** ((note_number - 69) / 12))


# --- Classes de la sessió (solució de les Parts 1, 3, 4 i 5) -----------------

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
        self._pas = 1.0 / max(1, int(self.attack * self.sample_rate))

    def note_off(self):
        if self.stage == 'idle':
            return
        self.stage = 'release'
        self._pas = self.level / max(1, int(self.release * self.sample_rate))

    def process(self, n_samples):
        out = np.zeros(n_samples)
        for k in range(n_samples):
            if self.stage == 'attack':
                self.level = self.level + self._pas
                if self.level >= 1.0:
                    self.level = 1.0
                    self.stage = 'decay'
                    self._pas = (1.0 - self.sustain) / max(1, int(self.decay * self.sample_rate))
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

    def note_on(self, note_number, velocity=100):
        self.carrier.freq = note_to_freq(note_number)
        self.modulator.freq = self.carrier.freq * self.ratio
        self.gain = velocity / 127
        self.env.note_on()

    def note_off(self):
        self.env.note_off()

    def process(self, n_samples):
        corba = self.env.process(n_samples)
        index = self.I_max * corba
        mod = self.modulator.process(n_samples)
        freqs = self.carrier.freq + index * self.modulator.freq * mod
        return self.carrier.process_freqs(freqs) * corba * self.gain


def brillantor(x):
    s = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1 / sample_rate)
    return np.sum(f * s) / np.sum(s)


# =============================================================================
# Challenge 1 — Feedback
#   Com el DX7 (Tomisawa): la FASE de cada mostra es desplaça segons
#   l'ÚLTIMA mostra generada. Atenció: això és PM (modulació de fase), no la
#   FM de la sessió. Amb feedback, la versió en freqüència es comporta de
#   manera irregular (la freqüència mitjana es desplaça); per això el DX7 fa PM.
#     sortida[k] = sin(fase[k] + feedback × sortida[k-1])
#   No es pot vectoritzar: cada mostra necessita l'anterior. Per això el
#   bucle mostra a mostra és l'única manera.
#   feedback 0 → sinus; cap a 1 → cada cop més semblant a una dent de
#   serra (més brillant); a partir de ~1,5 → soroll (el sistema és caòtic).
# =============================================================================

class OscFeedback:
    def __init__(self, freq=220.0, feedback=0.5, sample_rate=44100):
        self.freq = freq
        self.feedback = feedback
        self.sample_rate = sample_rate
        self._phase = 0.0
        self._ultima = 0.0                        # estat nou: l'última mostra

    def process(self, n_samples):
        increment = 2 * np.pi * self.freq / self.sample_rate
        out = np.zeros(n_samples)
        for k in range(n_samples):
            out[k] = np.sin(self._phase + self.feedback * self._ultima)
            self._ultima = out[k]
            self._phase = (self._phase + increment) % (2 * np.pi)
        return out


print("=== Challenge 1: feedback ===")
for fb in [0.0, 0.5, 1.0, 1.5, 3.0, 6.0]:
    so = OscFeedback(220, fb).process(44100)
    print("  feedback", fb, "→ brillantor %.0f Hz" % brillantor(so))


# =============================================================================
# Challenge 2 — Tres operadors en pila (op3 → op2 → op1)
#   Paràmetres nous: una ratio i un índex per a cada modulador.
#   Peça reutilitzable: un Operador que rep (opcionalment) la modulació
#   de l'operador de sobre. És exactament el que el DX7 anomena "algorisme".
# =============================================================================

class Operador:
    def __init__(self, ratio=1.0, index=1.0):
        self.ratio = ratio
        self.index = index
        self.osc = Oscillator()

    def process(self, freq_base, n_samples, modulacio=None):
        """modulacio: sortida de l'operador de sobre (o None)."""
        self.osc.freq = freq_base * self.ratio
        if modulacio is None:
            return self.osc.process(n_samples)
        freqs = self.osc.freq + modulacio
        return self.osc.process_freqs(freqs)

    def excursio(self, sortida):
        """Què aporta aquest operador com a modulador: I × freq × sortida."""
        return self.index * self.osc.freq * sortida


def pila(freq, op1, op2, op3, n_blocs, block=512):
    trossos = []
    for b in range(n_blocs):
        s3 = op3.process(freq, block)
        s2 = op2.process(freq, block, op3.excursio(s3))
        s1 = op1.process(freq, block, op2.excursio(s2))
        trossos.append(s1)
    return np.concatenate(trossos)


print("\n=== Challenge 2: tres operadors ===")
dos = pila(220, Operador(1), Operador(2, 1.5), Operador(1, 0.0), 86)
tres = pila(220, Operador(1), Operador(2, 1.5), Operador(1, 2.0), 86)
def parcials(x, llindar_db=-40):
    """Quantes freqüències (de 10 en 10 Hz) superen el llindar: una mesura de "riquesa"."""
    s = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    d = 20 * np.log10(s / np.max(s) + 1e-12)
    return int(np.sum(d > llindar_db))


print("  2 operadors (op3 apagat): %d bins per sobre de -40 dB" % parcials(dos))
print("  3 operadors:              %d bins per sobre de -40 dB" % parcials(tres))
assert parcials(tres) > parcials(dos)


# =============================================================================
# Challenge 3 — Campana: l'índex té la seva pròpia envolvent, més curta
# =============================================================================

class Campana:
    def __init__(self, ratio=1.41, I_max=6.0):
        self.ratio = ratio
        self.I_max = I_max
        self.carrier = Oscillator()
        self.modulator = Oscillator()
        self.env_volum = Envelope(attack=0.001, decay=3.0, sustain=0.0, release=1.0)
        self.env_index = Envelope(attack=0.001, decay=0.6, sustain=0.0, release=0.3)
        self.gain = 0.0

    def note_on(self, note_number, velocity=100):
        self.carrier.freq = note_to_freq(note_number)
        self.modulator.freq = self.carrier.freq * self.ratio
        self.gain = velocity / 127
        self.env_volum.note_on()
        self.env_index.note_on()

    def note_off(self):
        self.env_volum.note_off()
        self.env_index.note_off()

    def process(self, n_samples):
        volum = self.env_volum.process(n_samples)
        index = self.I_max * self.env_index.process(n_samples)
        mod = self.modulator.process(n_samples)
        freqs = self.carrier.freq + index * self.modulator.freq * mod
        return self.carrier.process_freqs(freqs) * volum * self.gain


print("\n=== Challenge 3: campana ===")
c = Campana()
c.note_on(72, 110)
trossos = []
for b in range(200):
    trossos.append(c.process(512))
so = np.concatenate(trossos)
inici = brillantor(so[512:512 + 8192])
final = brillantor(so[80000:80000 + 8192])
print("  brillantor a l'inici %.0f Hz → al cap d'1,8 s %.0f Hz (només queda el to)" % (inici, final))
assert inici > 1.5 * final


# =============================================================================
# Challenge 4 — Mesura't
# =============================================================================

print("\n=== Challenge 4: process vs process_freqs (10 s de so) ===")
n = 10 * sample_rate
o = Oscillator(440)
t0 = time.perf_counter()
for b in range(n // 512):
    o.process(512)
t1 = time.perf_counter()
o = Oscillator(440)
freqs = np.full(512, 440.0)
for b in range(n // 512):
    o.process_freqs(freqs)
t2 = time.perf_counter()
print("  process:       %.3f s" % (t1 - t0))
print("  process_freqs: %.3f s  → %.0f vegades més lent" % (t2 - t1, (t2 - t1) / (t1 - t0)))
print("  (Tots dos molt per sota dels 10 s de so: per això sona en temps real.")
print("   La versió vectoritzada de process_freqs, amb np.cumsum, es veu a la S10.)")


# =============================================================================
# Challenge 5 (Thonny) — Polifonia
#   Cada veu recorda quina nota toca (self.nota_actual) perquè note_off(nota)
#   apagui la correcta. Round-robin amb %: la veu següent, i torna a començar.
#   El Reproductor de assignment.py ha de cridar note_off(nota) en lloc de note_off().
# =============================================================================

class Polifonic:
    def __init__(self, n_veus=4, ratio=1.0, I_max=3.0):
        self.veus = []
        self.notes = []                           # quina nota toca cada veu (None = cap)
        for i in range(n_veus):
            self.veus.append(VeuFM(ratio=ratio, I_max=I_max))
            self.notes.append(None)
        self._seguent = 0

    def note_on(self, nota, velocity=100):
        i = self._seguent
        self.veus[i].note_on(nota, velocity)
        self.notes[i] = nota
        self._seguent = (self._seguent + 1) % len(self.veus)

    def note_off(self, nota):
        for i in range(len(self.veus)):
            if self.notes[i] == nota:
                self.veus[i].note_off()
                self.notes[i] = None

    def process(self, n_samples):
        suma = np.zeros(n_samples)
        for veu in self.veus:
            suma = suma + veu.process(n_samples)
        return suma / len(self.veus)


print("\n=== Challenge 5: polifonia ===")
p = Polifonic()
for nota in [60, 64, 67]:
    p.note_on(nota, 100)
acord = np.concatenate([p.process(512), p.process(512), p.process(512)])
for nota in [60, 64, 67]:
    p.note_off(nota)
for b in range(40):
    cua = p.process(512)
print("  3 veus actives, i silenci després del release:", np.max(np.abs(cua)) < 1e-6)
t0 = time.perf_counter()
for b in range(100):
    p.process(512)
print("  4 veus: %.2f ms per bloc (límit 11,6 ms)" % ((time.perf_counter() - t0) / 100 * 1000))
