"""
Exemples — Bloc 5a, Sessió 8 (Thonny)
Síntesi amb classes: Oscillator, Envelope, SamplePlayer

Requereix: kick_sample.wav a la mateixa carpeta
(descarrega'l de recursos/audio/kick_sample.wav)
"""

import numpy as np
from scipy import signal
import soundfile as sf
import sounddevice as sd
import matplotlib.pyplot as plt

sample_rate = 44100


# ---------------------------------------------------------------
# 1. La classe Oscillator
# ---------------------------------------------------------------
class Oscillator:
    def __init__(self, freq=440.0, waveform='sine', sample_rate=44100):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate

    def set_freq(self, freq):
        self.freq = freq

    def generate(self, duration):
        n = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n, endpoint=False)

        if self.waveform == 'sine':
            return np.sin(2 * np.pi * self.freq * t)
        elif self.waveform == 'square':
            return signal.square(2 * np.pi * self.freq * t)
        elif self.waveform == 'sawtooth':
            return signal.sawtooth(2 * np.pi * self.freq * t)
        else:
            raise ValueError(f"Forma d'ona desconeguda: {self.waveform}")


print("=== 1. Oscillator sol ===")
osc = Oscillator(freq=440, waveform='sine')
wave = osc.generate(duration=2.0)
sd.play(wave, sample_rate)
sd.wait()
print("Nota: comença i acaba sobtadament, sense atac ni final suaus.\n")


# ---------------------------------------------------------------
# 2. La classe Envelope (ADSR)
# ---------------------------------------------------------------
class Envelope:
    def __init__(self, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release

    def generate(self, note_duration, sample_rate=44100):
        n_attack  = int(self.attack  * sample_rate)
        n_decay   = int(self.decay   * sample_rate)
        n_sustain = max(0, int(note_duration * sample_rate) - n_attack - n_decay)
        n_release = int(self.release * sample_rate)

        env_attack  = np.linspace(0, 1, n_attack)
        env_decay   = np.linspace(1, self.sustain, n_decay)
        env_sustain = np.full(n_sustain, self.sustain)
        env_release = np.linspace(self.sustain, 0, n_release)

        return np.concatenate([env_attack, env_decay, env_sustain, env_release])


print("=== 2. Envelope visualitzada ===")
env = Envelope(attack=0.05, decay=0.15, sustain=0.6, release=0.3)
env_curve = env.generate(note_duration=0.5)
plt.plot(env_curve)
plt.title("Envolvent ADSR")
plt.show()


# ---------------------------------------------------------------
# 3. Combinar Oscillator + Envelope
# ---------------------------------------------------------------
print("=== 3. Oscillator x Envelope ===")
osc = Oscillator(freq=440, waveform='sine')
env = Envelope(attack=0.02, decay=0.1, sustain=0.6, release=0.3)

note_duration = 0.5
total_duration = note_duration + env.release

wave = osc.generate(total_duration)
env_curve = env.generate(note_duration)
n = min(len(wave), len(env_curve))
nota_final = wave[:n] * env_curve[:n]

print("Sense envolvent:")
sd.play(wave[:n], sample_rate)
sd.wait()

print("Amb envolvent:")
sd.play(nota_final, sample_rate)
sd.wait()


# ---------------------------------------------------------------
# 4. MIDI -> freqüència
# ---------------------------------------------------------------
def note_to_freq(note_number):
    return 440.0 * (2 ** ((note_number - 69) / 12))


print("\n=== 4. Number MIDI -> freqüència ===")
for note in [60, 64, 67, 72]:
    print(f"  Nota MIDI {note} -> {note_to_freq(note):.2f} Hz")


# ---------------------------------------------------------------
# 5. tocar_nota: combina tot
# ---------------------------------------------------------------
def tocar_nota(note_number, note_duration, waveform='sine',
               attack=0.02, decay=0.1, sustain=0.6, release=0.2):
    freq = note_to_freq(note_number)
    osc = Oscillator(freq=freq, waveform=waveform)
    env = Envelope(attack=attack, decay=decay, sustain=sustain, release=release)

    total_duration = note_duration + release
    wave = osc.generate(total_duration)
    env_curve = env.generate(note_duration)

    n = min(len(wave), len(env_curve))
    return wave[:n] * env_curve[:n]


print("\n=== 5. Petit arpegi ===")
acord = [60, 64, 67, 72]
trossos = [tocar_nota(n, note_duration=0.2) for n in acord]
sequencia = np.concatenate(trossos)
sd.play(sequencia, sample_rate)
sd.wait()


# ---------------------------------------------------------------
# 6. SamplePlayer
# ---------------------------------------------------------------
class SamplePlayer:
    def __init__(self, filepath, sample_rate=44100):
        self.sample_rate = sample_rate
        data, sr = sf.read(filepath)
        self.sample = data

    def play(self, gain=1.0):
        return self.sample * gain


print("\n=== 6. Oscillator vs SamplePlayer ===")
kick = SamplePlayer('kick_sample.wav')

print("Oscillator (genera matemàticament):")
sd.play(tocar_nota(36, note_duration=0.2), sample_rate)
sd.wait()

print("SamplePlayer (reprodueix un so ja gravat):")
sd.play(kick.play(), sample_rate)
sd.wait()


# ---------------------------------------------------------------
# 7. Combinar síntesi + sample
# ---------------------------------------------------------------
print("\n=== 7. Combo: nota greu sintetitzada + kick ===")
bass_note = tocar_nota(36, note_duration=0.25, waveform='sawtooth',
                       attack=0.005, decay=0.05, sustain=0.5, release=0.1)
kick_hit = kick.play(gain=0.8)

n = min(len(bass_note), len(kick_hit))
combo = bass_note[:n] + kick_hit[:n]
combo = combo / np.max(np.abs(combo))

sd.play(combo, sample_rate)
sd.wait()
