"""
Solució de referència — S10 Challenges opcionals
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Challenge 1: FM mostra a mostra (codi donat al challenge, aquí executat i benchmarkat)
Challenge 2: Snare (nova classe de percussió, nota MIDI 38)
Challenges 3 i 4 (signalflow exploratòrics): procediment de referència
"""

import numpy as np
import time

SAMPLE_RATE = 44100
BLOCK = 512


# ── Classes base necessàries ──────────────────────────────────────────────────

class Oscillator:
    def __init__(self, freq=440.0, waveform='sine', sample_rate=SAMPLE_RATE):
        self.freq = freq; self.waveform = waveform
        self.sample_rate = sample_rate; self.phase = 0.0

    def process(self, n_samples):
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self.phase + phase_inc * np.arange(n_samples)
        out = np.sin(phases)
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out


class Noise:
    def process(self, n_samples):
        return np.random.uniform(-1.0, 1.0, n_samples)


class Envelope:
    def __init__(self, attack=0.002, decay=0.12, sustain=0.0,
                 release=0.01, sample_rate=SAMPLE_RATE):
        self.attack=attack; self.decay=decay; self.sustain=sustain
        self.release=release; self.sample_rate=sample_rate
        self.stage='idle'; self.level=0.0; self.stage_samples=0

    def note_on(self): self.stage='attack'; self.stage_samples=0

    def process(self, n):
        out = np.zeros(n)
        for k in range(n):
            if self.stage == 'attack':
                na = max(1, int(self.attack * self.sample_rate))
                self.level = min(1.0, self.stage_samples / na)
                if self.stage_samples >= na:
                    self.stage='decay'; self.stage_samples=0; continue
            elif self.stage == 'decay':
                nd = max(1, int(self.decay * self.sample_rate))
                t = min(1.0, self.stage_samples / nd)
                self.level = 1.0 + t * (self.sustain - 1.0)
                if self.stage_samples >= nd:
                    self.stage='idle'; self.level=0.0
            else:
                self.level = 0.0
            out[k] = self.level; self.stage_samples += 1
        return out


# ── Challenge 1 — FM mostra a mostra ─────────────────────────────────────────
# Codi proporcionat íntegrament al challenge; aquí l'executem i el benchmarkem.

def fm_synth_mostra_a_mostra(carrier_freq, mod_freq, I, duration, sample_rate=44100):
    n_total = int(sample_rate * duration)
    sortida = np.zeros(n_total)
    mod_phase = 0.0
    car_phase = 0.0
    mod_phase_inc = 2 * np.pi * mod_freq / sample_rate
    for i in range(n_total):
        mod_val = np.sin(mod_phase)
        car_freq_instant = carrier_freq + I * mod_val
        car_phase_inc = 2 * np.pi * car_freq_instant / sample_rate
        sortida[i] = np.sin(car_phase)
        mod_phase = (mod_phase + mod_phase_inc) % (2 * np.pi)
        car_phase = (car_phase + car_phase_inc) % (2 * np.pi)
    return sortida


def fm_synth_blocs(carrier_freq, mod_freq, I, duration,
                   sample_rate=44100, block=512):
    n_total = int(sample_rate * duration)
    sortida = np.zeros(n_total, dtype='float32')
    mod = Oscillator(freq=mod_freq, sample_rate=sample_rate)
    car = Oscillator(freq=carrier_freq, sample_rate=sample_rate)
    i = 0
    while i < n_total:
        n = min(block, n_total - i)
        mb = mod.process(n)
        car.freq = carrier_freq + I * mb[-1]
        sortida[i:i + n] = car.process(n)
        i += n
    return sortida


# Benchmark (0.5s per no trigar massa)
t0 = time.perf_counter(); _ = fm_synth_blocs(440, 80, 200, 0.5); t1 = time.perf_counter()
temps_blocs = t1 - t0

t0 = time.perf_counter(); _ = fm_synth_mostra_a_mostra(440, 80, 200, 0.5); t1 = time.perf_counter()
temps_sbs = t1 - t0

print(f"✅ Challenge 1 (FM mostra-a-mostra):")
print(f"   Per blocs:          {temps_blocs * 1000:.1f} ms (0.5s de so)")
print(f"   Mostra a mostra:    {temps_sbs * 1000:.1f} ms (0.5s de so)")
print(f"   Ràtio: {temps_sbs / temps_blocs:.0f}× més lenta la versió mostra-a-mostra")
print()
print("   Diferència sonora: la versió mostra-a-mostra actualitza la freq del")
print("   portador a cada mostra → menys aliasing, més fidel a la FM de Chowning.")
print("   La versió per blocs actualitza un cop cada 512 mostres → sota-mostreig")
print("   del modulador → artefactes audibles amb I gran (> ~100).")


# ── Challenge 2 — Snare (nota MIDI 38, Acoustic Snare GM) ────────────────────

class Snare:
    """
    Combina un oscil·lador tonal curt (~180Hz, el 'cos' de la caixa)
    amb soroll blanc (el ressort característic del snare).
    Nota MIDI GM: 38 (Acoustic Snare).

    Per què kick=tonal, hihat=soroll, snare=tonal+soroll?
      - El kick té una cavitat tancada que ressona → to pur descendent.
      - El hihat és metall obert, so breu i sense to definit → soroll.
      - El snare té un cos (aporta el to) i un ressort de corda (snare wire)
        que vibra contra el parxe inferior → barreja de to i soroll.
    """
    def __init__(self, tone_freq=180.0, sample_rate=SAMPLE_RATE):
        self.osc   = Oscillator(freq=tone_freq, waveform='sine', sample_rate=sample_rate)
        self.noise = Noise()
        self.sample_rate = sample_rate

    def reset(self):
        self.osc.phase = 0.0

    def process(self, n_samples):
        tonal  = self.osc.process(n_samples)
        soroll = self.noise.process(n_samples)
        return 0.5 * tonal + 0.5 * soroll   # barreja 50/50


def fes_snare(n_samples=int(SAMPLE_RATE * 0.15)):
    snare = Snare()
    env = Envelope(attack=0.002, decay=0.08, sustain=0.0)
    env.note_on()
    out = np.zeros(n_samples, dtype='float32')
    i = 0
    while i < n_samples:
        n = min(BLOCK, n_samples - i)
        out[i:i + n] = snare.process(n) * env.process(n)
        i += n
    return out


# Versió ampliada de percussion_kit amb suport per a nota 38 (Snare)
def percussion_kit_3_classes(events, total_duration,
                              sample_rate=SAMPLE_RATE, block=BLOCK):
    class Kick:
        def __init__(self):
            self.osc = Oscillator(freq=150); self.elapsed = 0.0
        def reset(self): self.elapsed = 0.0; self.osc.phase = 0.0
        def process(self, n):
            progress = min(1.0, self.elapsed * SAMPLE_RATE / max(1, int(0.05 * SAMPLE_RATE)))
            self.osc.freq = 40 + (150 - 40) * np.exp(-5 * progress)
            out = self.osc.process(n); self.elapsed += n / SAMPLE_RATE
            return out

    n_total = int(sample_rate * total_duration)
    sortida = np.zeros(n_total, dtype='float32')

    kick = Kick()
    kick_env = Envelope(attack=0.002, decay=0.15, sustain=0.0)
    noise = Noise()
    hh_env = Envelope(attack=0.001, decay=0.05, sustain=0.0)
    snare = Snare()
    snare_env = Envelope(attack=0.002, decay=0.08, sustain=0.0)

    events_fets = set()
    i = 0
    while i < n_total:
        n = min(block, n_total - i)
        t_actual = i / sample_rate
        for idx, (note, t_on) in enumerate(events):
            if idx not in events_fets and t_actual >= t_on:
                if note == 36: kick.reset(); kick_env.note_on()
                elif note == 42: hh_env.note_on()
                elif note == 38: snare.reset(); snare_env.note_on()
                events_fets.add(idx)
        kick_w  = kick.process(n)  * kick_env.process(n)
        hh_w    = noise.process(n) * hh_env.process(n)
        snare_w = snare.process(n) * snare_env.process(n)
        sortida[i:i + n] = kick_w + hh_w + snare_w
        i += n
    return np.clip(sortida, -1.0, 1.0)


# Test Snare independent (sense importació de S10)
so_snare = fes_snare()
assert len(so_snare) > 0
assert np.max(np.abs(so_snare)) > 0.01
assert np.max(np.abs(so_snare)) <= 1.0 + 1e-6

print(f"\n✅ Challenge 2 (Snare):")
print(f"   Snare = 0.5 × sine(180Hz) + 0.5 × noise, nota MIDI 38 (Acoustic Snare GM)")
print(f"   So generat: {len(so_snare)} mostres, max={np.max(np.abs(so_snare)):.3f}")
print()
print("   Reflexió — per què kick=tonal, hihat=soroll, snare=tonal+soroll:")
print("   Kick: cavitat tancada → ressona com un to descendent.")
print("   Hihat: disc metàl·lic obert → decau ràpid sense to definit.")
print("   Snare: té cos (to) + ressort de corda (snare wire, soroll).")


# ── Challenges 3 i 4 — signalflow (procediment de referència) ────────────────

print()
print("Challenge 3 — Exemples oficials de signalflow:")
print("  https://github.com/ideoforms/signalflow/tree/master/examples")
print("  Instal·lació: python3 -m venv venv --copies && pip install signalflow")
print("  Veure guia troubleshooting completa a:")
print("  05_sintesi/sessio10_consolidacio/recursos/challenges.md (Annex signalflow)")
print()
print("Challenge 4 — Cor de string ensemble amb signalflow (codi de referència):")
print("""
from signalflow import *
import random

graph = AudioGraph()
freqs = [220 * (1 + random.uniform(-0.01, 0.01)) for _ in range(8)]
veus  = [SineOscillator(f) for f in freqs]
cor   = veus[0]
for v in veus[1:]:
    cor = cor + v
cor = cor * (0.1 / len(veus))

lfo = SineLFO(0.25, min=0.005, max=0.02)
cor_chorus = cor + OneTapDelay(cor, delay_time=lfo, max_delay_time=0.03) * 0.6
StereoPanner(cor_chorus * 0.5).play()
graph.wait()
""")
print("  Quan el delay_time del LFO és molt curt (< ~5ms) → flanger.")
print("  Quan oscil·la a > ~10Hz → vibrato de pitch en lloc de chorus.")
print("  CombDelay (amb feedback) afegeix ressò i color tonal addicional.")
