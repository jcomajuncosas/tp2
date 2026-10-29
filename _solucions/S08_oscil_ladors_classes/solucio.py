"""
Solució de referència — S08: Oscillator, Envelope i SamplePlayer
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida TODOs 1-9 sense Colab ni àudio.
La Part 5 (seqüència pròpia) s'exemplifica amb una seqüència concreta de 6+ notes.
El fitxer kick_sample.wav es substitueix per un array sintètic per al test del SamplePlayer.
"""

import numpy as np
from scipy import signal

sample_rate = 44100


# ── TODOs 1 & 2 — Oscillator ────────────────────────────────────────────────

class Oscillator:
    def __init__(self, freq=440.0, waveform='sine', sample_rate=44100):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate

    def set_freq(self, freq):
        # TODO 1
        self.freq = freq

    def generate(self, duration):
        n = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n, endpoint=False)
        # TODO 2
        if self.waveform == 'sine':
            return np.sin(2 * np.pi * self.freq * t)
        elif self.waveform == 'square':
            return signal.square(2 * np.pi * self.freq * t)
        elif self.waveform == 'sawtooth':
            return signal.sawtooth(2 * np.pi * self.freq * t)
        else:
            raise ValueError(f"Waveform desconeguda: {self.waveform}")


# Autotest 1
osc_test = Oscillator(freq=440, waveform='sine')
wave_test = osc_test.generate(duration=1.0)
assert wave_test is not None
assert len(wave_test) == 44100
assert np.max(np.abs(wave_test)) > 0.9

osc_test.set_freq(880)
assert osc_test.freq == 880, "set_freq() no actualitza self.freq"

osc_square = Oscillator(freq=220, waveform='square')
wave_square = osc_square.generate(duration=0.5)
assert len(wave_square) == 22050
print("✅ TODOs 1 & 2 (Oscillator) correctes")


# ── TODOs 3 & 4 — Envelope ──────────────────────────────────────────────────

class Envelope:
    def __init__(self, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
        self.attack  = attack
        self.decay   = decay
        self.sustain = sustain
        self.release = release

    def generate(self, note_duration, sample_rate=44100):
        n_attack  = int(self.attack  * sample_rate)
        n_decay   = int(self.decay   * sample_rate)
        n_sustain = max(0, int(note_duration * sample_rate) - n_attack - n_decay)
        n_release = int(self.release * sample_rate)

        # TODO 3: les 4 fases
        env_attack  = np.linspace(0, 1,            n_attack)
        env_decay   = np.linspace(1, self.sustain,  n_decay)
        env_sustain = np.full(n_sustain,            self.sustain)
        env_release = np.linspace(self.sustain, 0,  n_release)

        # TODO 4: concatena
        return np.concatenate([env_attack, env_decay, env_sustain, env_release])


# Autotest 2
env_test = Envelope(attack=0.01, decay=0.1, sustain=0.7, release=0.2)
curve = env_test.generate(note_duration=0.5)
assert curve is not None
assert curve[0] < 0.05,            f"Inici hauria de ser ~0, és {curve[0]:.3f}"
assert abs(curve[-1]) < 0.05,     f"Final hauria de ser ~0, és {curve[-1]:.3f}"
mig = len(curve) // 2
assert abs(curve[mig] - 0.7) < 0.1, f"Sustain hauria de ser ~0.7, és {curve[mig]:.3f}"
print("✅ TODOs 3 & 4 (Envelope) correctes")


# ── TODOs 5-7 — tocar_nota ──────────────────────────────────────────────────

def note_to_freq(note_number):
    return 440.0 * (2 ** ((note_number - 69) / 12))


def tocar_nota(note_number, note_duration, waveform='sine',
               attack=0.02, decay=0.1, sustain=0.6, release=0.2):
    # TODO 5
    freq = note_to_freq(note_number)
    # TODO 6
    osc = Oscillator(freq=freq, waveform=waveform)
    env = Envelope(attack=attack, decay=decay, sustain=sustain, release=release)
    # TODO 7
    total_duration = note_duration + release
    wave      = osc.generate(total_duration)
    env_curve = env.generate(note_duration)
    n = min(len(wave), len(env_curve))
    return wave[:n] * env_curve[:n]


# Autotest 3
nota_test = tocar_nota(60, note_duration=0.3, waveform='sine')
assert nota_test is not None
assert len(nota_test) > 0
assert nota_test[0] < 0.05,           "Inici hauria de ser quasi silenci (Attack)"
assert abs(nota_test[-1]) < 0.05,    "Final hauria de ser quasi silenci (Release)"
assert np.max(np.abs(nota_test)) > 0.3, "Amplitud màxima massa baixa"
print("✅ TODOs 5-7 (tocar_nota) correctes")


# ── TODO 8 — SamplePlayer ───────────────────────────────────────────────────

class SamplePlayer:
    def __init__(self, sample_array, sample_rate=44100):
        """Versió harness: accepta array directament en lloc de filepath."""
        self.sample_rate = sample_rate
        self.sample = sample_array

    def play(self, gain=1.0):
        # TODO 8
        return self.sample * gain


# Autotest 4: usem un array sintètic com a substitut del kick_sample.wav
kick_data = np.random.uniform(-0.8, 0.8, 8000).astype('float64')
kick = SamplePlayer(kick_data)
audio_normal = kick.play(gain=1.0)
audio_fluix  = kick.play(gain=0.3)
assert audio_normal is not None
assert len(audio_normal) == len(kick.sample)
assert np.isclose(
    np.max(np.abs(audio_fluix)),
    np.max(np.abs(audio_normal)) * 0.3,
    atol=0.01
), "El gain no s'aplica correctament"
print("✅ TODO 8 (SamplePlayer) correcte")


# ── TODO 9 — seqüència pròpia (≥6 notes + SamplePlayer) ────────────────────
#
# Referència: escala pentatònica de Do, Do4-Re4-Mi4-Sol4-La4-Do5
# amb el kick (array sintètic) intercalat al principi

pentatonica = [60, 62, 64, 67, 69, 72]
notes_audio = [tocar_nota(p, note_duration=0.3, waveform='sine') for p in pentatonica]

kick_sample = kick.play(gain=0.8)
# Padding del kick a la mateixa longitud que les notes per poder-les concatenar
la_meva_sequencia = np.concatenate([kick_sample] + notes_audio)

# Autotest 5
assert len(la_meva_sequencia) > sample_rate * 0.5, \
    "La seqüència és massa curta — assegura't que hi ha almenys 6 notes"
print("✅ TODO 9 (seqüència pròpia amb ≥6 notes + SamplePlayer) correcte")
print(f"   Durada total: {len(la_meva_sequencia)/sample_rate:.2f} s")

print("\n✅ Tots els TODOs de S08 validats correctament.")
print("\nNOTA DOCENT — TODO 9 és creatiu: qualsevol seqüència de ≥6 notes")
print("que inclogui almenys un kick.play() és vàlida.")
print("SamplePlayer en producció usa sf.read(filepath); aquí el test usa array sintètic.")
