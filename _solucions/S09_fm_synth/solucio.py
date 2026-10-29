"""
Solució de referència — S09: FM Synthesis (vibrato i fm_synth)
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida TODOs 1 & 2 (vibrato + fm_synth) i el Challenge 1 (benchmark).
"""

import numpy as np
import time

sample_rate = 44100


# ── Classe donada ────────────────────────────────────────────────────────────

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
        elif self.waveform == 'square':
            out = np.sign(np.sin(phases))
        elif self.waveform == 'sawtooth':
            out = 2 * ((phases / (2 * np.pi)) % 1.0) - 1.0
        else:
            raise ValueError(f"Forma d'ona desconeguda: {self.waveform}")
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out

    # Challenge 1: versió sample-by-sample (afegida a la classe per comoditat)
    def process_sample_by_sample(self, n_samples):
        out = np.zeros(n_samples)
        for i in range(n_samples):
            out[i] = np.sin(self.phase)
            self.phase += 2 * np.pi * self.freq / self.sample_rate
            self.phase %= 2 * np.pi
        return out


# ── TODO 1 — vibrato ─────────────────────────────────────────────────────────

def vibrato(base_freq, lfo_freq, depth, duration, sample_rate=44100, block=512):
    n_total = int(sample_rate * duration)
    sortida = np.zeros(n_total, dtype='float32')

    lfo = Oscillator(freq=lfo_freq, waveform='sine', sample_rate=sample_rate)
    osc = Oscillator(freq=base_freq, waveform='sine', sample_rate=sample_rate)

    i = 0
    while i < n_total:
        n = min(block, n_total - i)
        lfo_bloc = lfo.process(n)
        osc.freq = base_freq + depth * lfo_bloc[-1]
        sortida[i:i + n] = osc.process(n)
        i += n

    return sortida


# Autotests 1, 2, 3 (de l'assignment)
out = vibrato(base_freq=440, lfo_freq=5, depth=6, duration=0.5)
assert out is not None
assert isinstance(out, np.ndarray)
assert len(out) == int(44100 * 0.5)
assert np.max(np.abs(out)) <= 1.0 + 1e-6
assert not np.any(np.isnan(out))
assert np.max(np.abs(out)) > 0.5

out_sense = vibrato(base_freq=440, lfo_freq=5, depth=0, duration=0.5)
diff = np.max(np.abs(out - out_sense))
assert diff > 0.01, "Amb depth=6 i depth=0 el resultat hauria de diferir"
print("✅ TODO 1 (vibrato) correcte")


# ── TODO 2 — fm_synth ────────────────────────────────────────────────────────

def fm_synth(carrier_freq, mod_freq, I, duration, sample_rate=44100, block=512):
    n_total = int(sample_rate * duration)
    sortida = np.zeros(n_total, dtype='float32')

    modulator = Oscillator(freq=mod_freq,     waveform='sine', sample_rate=sample_rate)
    carrier   = Oscillator(freq=carrier_freq, waveform='sine', sample_rate=sample_rate)

    i = 0
    while i < n_total:
        n = min(block, n_total - i)
        mod_bloc = modulator.process(n)
        carrier.freq = carrier_freq + I * mod_bloc[-1]
        sortida[i:i + n] = carrier.process(n)
        i += n

    return sortida


out_fm = fm_synth(carrier_freq=440, mod_freq=80, I=200, duration=0.5)
assert out_fm is not None
assert len(out_fm) == int(44100 * 0.5)
assert np.max(np.abs(out_fm)) <= 1.0 + 1e-6
assert not np.any(np.isnan(out_fm))
assert np.max(np.abs(out_fm)) > 0.5

out_fm_sense = fm_synth(carrier_freq=440, mod_freq=80, I=0, duration=0.5)
diff_fm = np.max(np.abs(out_fm - out_fm_sense))
assert diff_fm > 0.01, "Amb I=200 i I=0 el resultat hauria de diferir molt"
print("✅ TODO 2 (fm_synth) correcte")


# Test 3: vibrato vs FM amplada de banda
def amplada_de_banda(signal, sample_rate=44100, threshold_db=-20):
    spec = np.abs(np.fft.rfft(signal))
    spec_db = 20 * np.log10(spec / np.max(spec) + 1e-12)
    freqs = np.fft.rfftfreq(len(signal), 1 / sample_rate)
    mask = spec_db > threshold_db
    return freqs[mask].max() - freqs[mask].min() if np.any(mask) else 0

v  = vibrato(base_freq=440, lfo_freq=5, depth=6, duration=1.0)
fm = fm_synth(carrier_freq=440, mod_freq=80, I=200, duration=1.0)
bw_v, bw_fm = amplada_de_banda(v), amplada_de_banda(fm)
assert bw_fm > bw_v * 3, f"FM hauria d'ocupar més banda ({bw_fm:.0f}Hz vs {bw_v:.0f}Hz vibrato)"
print(f"✅ Test amplada de banda: vibrato={bw_v:.0f}Hz | FM={bw_fm:.0f}Hz")


print("
✅ Tots els TODOs de S09 validats correctament.")
print("
NOTA DOCENT — Challenges: veure S09_challenges_solucio.py")
