"""
Solució de referència — S10: Kit de percussió sintètica (Noise + Kick + percussion_kit)
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida TODOs 1-3 + Challenge 1 (FM mostra-a-mostra) + Challenge 2 (Snare).
"""

import numpy as np
import time

sample_rate = 44100


# ── Classes donades (còpia de l'assignment) ──────────────────────────────────

class Oscillator:
    def __init__(self, freq=440.0, waveform='sine', sample_rate=44100):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.phase = 0.0

    def process(self, n_samples):
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self.phase + phase_inc * np.arange(n_samples)
        if self.waveform == 'sine':
            out = np.sin(phases)
        else:
            raise ValueError(f"Forma d'ona desconeguda: {self.waveform}")
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out


class Envelope:
    def __init__(self, attack=0.01, decay=0.1, sustain=0.7, release=0.2, sample_rate=44100):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.sample_rate = sample_rate
        self.stage = 'idle'
        self.level = 0.0
        self.stage_samples = 0

    def note_on(self):
        self.stage = 'attack'
        self.stage_samples = 0

    def note_off(self):
        self.stage = 'release'
        self.stage_samples = 0
        self._release_start_level = self.level

    def process(self, n_samples):
        out = np.zeros(n_samples)
        for k in range(n_samples):
            if self.stage == 'attack':
                n_a = max(1, int(self.attack * self.sample_rate))
                self.level = min(1.0, self.stage_samples / n_a)
                if self.stage_samples >= n_a:
                    self.stage = 'decay'
                    self.stage_samples = 0
                    continue
            elif self.stage == 'decay':
                n_d = max(1, int(self.decay * self.sample_rate))
                t = min(1.0, self.stage_samples / n_d)
                self.level = 1.0 + t * (self.sustain - 1.0)
                if self.stage_samples >= n_d:
                    self.stage = 'sustain'
                    self.stage_samples = 0
                    continue
            elif self.stage == 'sustain':
                self.level = self.sustain
                if self.sustain == 0.0:
                    self.stage = 'idle'
            elif self.stage == 'release':
                n_r = max(1, int(self.release * self.sample_rate))
                t = min(1.0, self.stage_samples / n_r)
                self.level = self._release_start_level * (1.0 - t)
                if self.stage_samples >= n_r:
                    self.stage = 'idle'
                    self.level = 0.0
            else:
                self.level = 0.0
            out[k] = self.level
            self.stage_samples += 1
        return out


# ── TODO 1 — Noise ───────────────────────────────────────────────────────────

class Noise:
    def process(self, n_samples):
        # TODO 1
        return np.random.uniform(-1.0, 1.0, n_samples)


# Autotest 1
noise = Noise()
out_n = noise.process(1000)
assert out_n is not None
assert isinstance(out_n, np.ndarray)
assert out_n.shape == (1000,)
assert np.max(np.abs(out_n)) <= 1.0 + 1e-6
out_n2 = noise.process(1000)
assert not np.array_equal(out_n, out_n2), "Dues crides haurien de donar soroll diferent"
assert abs(out_n.mean()) < 0.15
print("✅ TODO 1 (Noise) correcte")


# ── TODO 2 — Kick ────────────────────────────────────────────────────────────

class Kick:
    def __init__(self, freq_start=150.0, freq_end=40.0, drop_time=0.05, sample_rate=44100):
        self.freq_start = freq_start
        self.freq_end = freq_end
        self.drop_time = drop_time
        self.sample_rate = sample_rate
        self.osc = Oscillator(freq=freq_start, waveform='sine', sample_rate=sample_rate)
        self.elapsed = 0.0

    def reset(self):
        self.elapsed = 0.0
        self.osc.freq = self.freq_start
        self.osc.phase = 0.0

    def process(self, n_samples):
        n_drop = max(1, int(self.drop_time * self.sample_rate))
        block_t = np.arange(n_samples) + (self.elapsed * self.sample_rate)
        progress = np.clip(block_t / n_drop, 0, 1)
        # TODO 2: corba exponencial de freq_start a freq_end
        freqs = self.freq_end + (self.freq_start - self.freq_end) * np.exp(-5 * progress)
        self.osc.freq = float(freqs[-1])
        out = self.osc.process(n_samples)
        self.elapsed += n_samples / self.sample_rate
        return out


# Autotest 2
kick = Kick(freq_start=150, freq_end=40, drop_time=0.05)
block = 512
n_total = int(44100 * 0.3)
sortida_k = np.zeros(n_total)
freqs_log = []
i = 0
while i < n_total:
    n = min(block, n_total - i)
    sortida_k[i:i + n] = kick.process(n)
    freqs_log.append(kick.osc.freq)
    i += n

assert not np.any(np.isnan(sortida_k))
assert np.max(np.abs(sortida_k)) <= 1.0 + 1e-6
assert freqs_log[0] > freqs_log[-1], "La freqüència hauria de BAIXAR"
assert abs(freqs_log[-1] - 40) < 10, "La freq final hauria d'acostar-se a 40Hz"
print(f"✅ TODO 2 (Kick) correcte — freq {freqs_log[0]:.1f}Hz → {freqs_log[-1]:.1f}Hz")


# ── TODO 3 — percussion_kit ──────────────────────────────────────────────────

def percussion_kit(events, total_duration, sample_rate=44100, block=512):
    n_total = int(sample_rate * total_duration)
    sortida = np.zeros(n_total, dtype='float32')

    kick = Kick()
    kick_env = Envelope(attack=0.002, decay=0.15, sustain=0.0, release=0.01, sample_rate=sample_rate)

    noise = Noise()
    hh_env = Envelope(attack=0.001, decay=0.05, sustain=0.0, release=0.005, sample_rate=sample_rate)

    events_fets = set()

    i = 0
    while i < n_total:
        n = min(block, n_total - i)
        t_actual = i / sample_rate

        # TODO 3
        for idx, (note, t_on) in enumerate(events):
            if idx not in events_fets and t_actual >= t_on:
                if note == 36:
                    kick.reset()
                    kick_env.note_on()
                elif note == 42:
                    hh_env.note_on()
                events_fets.add(idx)

        kick_wave = kick.process(n) * kick_env.process(n)
        hh_wave   = noise.process(n) * hh_env.process(n)
        sortida[i:i + n] = kick_wave + hh_wave
        i += n

    return np.clip(sortida, -1.0, 1.0)


# Autotest 3
events_test = [(36, 0.0), (42, 0.2), (36, 0.4)]
out_pk = percussion_kit(events_test, total_duration=0.8)
assert out_pk is not None
assert len(out_pk) == int(44100 * 0.8)
assert np.max(np.abs(out_pk)) <= 1.0 + 1e-6
assert not np.any(np.isnan(out_pk))
sr = 44100
for note, t_on in events_test:
    idx_s = int(t_on * sr)
    idx_e = min(len(out_pk), idx_s + int(0.05 * sr))
    assert np.max(np.abs(out_pk[idx_s:idx_e])) > 0.05, \
        f"No hi ha senyal prop de l'event (nota={note}, t={t_on}s)"
print("✅ TODO 3 (percussion_kit) correcte")

# Autotest 4 (timing)
events_late = [(36, 0.5)]
out_late = percussion_kit(events_late, total_duration=0.8)
avant  = out_late[:int(0.48 * sr)]
despres = out_late[int(0.5 * sr):int(0.5 * sr) + int(0.05 * sr)]
assert np.max(np.abs(avant)) < 0.05,   "Hi ha so ABANS de l'event — revisa t_actual >= t_on"
assert np.max(np.abs(despres)) > 0.05, "No hi ha so just DESPRÉS de l'event"
print("✅ Timing correcte: el so només comença quan toca")


print("
✅ Tots els TODOs de S10 validats correctament.")
print("
NOTA DOCENT — Challenges: veure S10_challenges_solucio.py")
