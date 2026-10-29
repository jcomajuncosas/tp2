"""
Solució de referència — Projecte final: LOOPER/BASSLINE
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida TODOs 1-4 sense sounddevice ni MIDI.
La màquina d'estats i el main() no s'executen (requereixen hardware).
"""

import numpy as np
import time

SAMPLE_RATE = 44100
BLOCK = 512
N_PASSOS = 8


# ── UGens donats (còpia del template) ────────────────────────────────────────

class Oscillator:
    def __init__(self, freq=110.0, waveform='saw', sample_rate=SAMPLE_RATE):
        self.freq = freq; self.waveform = waveform
        self.sample_rate = sample_rate; self.phase = 0.0

    def process(self, n):
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self.phase + phase_inc * np.arange(n)
        out = 2 * ((phases / (2 * np.pi)) % 1.0) - 1 if self.waveform == 'saw' else np.sin(phases)
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out


class Envelope:
    def __init__(self, attack=0.005, decay=0.15, sustain=0.0, sample_rate=SAMPLE_RATE):
        self.attack=attack; self.decay=decay; self.sustain=sustain
        self.sample_rate=sample_rate; self.stage='idle'; self.level=0.0; self.stage_samples=0

    def note_on(self): self.stage='attack'; self.stage_samples=0

    def process(self, n):
        out = np.zeros(n)
        for k in range(n):
            if self.stage == 'attack':
                na = max(1, int(self.attack * self.sample_rate))
                self.level = min(1.0, self.stage_samples / na)
                if self.stage_samples >= na: self.stage='decay'; self.stage_samples=0; continue
            elif self.stage == 'decay':
                nd = max(1, int(self.decay * self.sample_rate))
                t = min(1.0, self.stage_samples / nd)
                self.level = 1.0 + t * (self.sustain - 1.0)
                if self.stage_samples >= nd: self.stage='idle'; self.level=0.0
            else:
                self.level = 0.0
            out[k] = self.level; self.stage_samples += 1
        return out


def midi_a_freq(nota_midi):
    return 440.0 * (2 ** ((nota_midi - 69) / 12))


def fes_nota_baix(nota_midi, n_samples=int(SAMPLE_RATE * 0.25)):
    osc = Oscillator(freq=midi_a_freq(nota_midi), waveform='saw')
    env = Envelope(attack=0.005, decay=0.18, sustain=0.0)
    env.note_on()
    out = np.zeros(n_samples, dtype='float32'); i = 0
    while i < n_samples:
        n = min(BLOCK, n_samples - i)
        out[i:i + n] = osc.process(n) * env.process(n); i += n
    return out


# ── TODO 1 — seguent_pas ─────────────────────────────────────────────────────

def seguent_pas(pas_actual, n_passos=N_PASSOS):
    """Avança al pas següent, tornant a 0 després de l'últim (mòdul)."""
    return (pas_actual + 1) % n_passos


# Autotests TODO 1
assert seguent_pas(0) == 1
assert seguent_pas(7) == 0, "Hauria de tornar a 0 després del pas 7 (N_PASSOS=8)"
assert seguent_pas(3) == 4
for p in range(N_PASSOS):
    assert seguent_pas(p) == (p + 1) % N_PASSOS
print("✅ TODO 1 (seguent_pas) correcte")


# ── TODO 2 — calcula_durada_pas ──────────────────────────────────────────────

def calcula_durada_pas(t_tap_anterior, t_tap_actual, durada_actual):
    """Retorna l'interval entre els dos taps, o durada_actual si és el primer tap."""
    if t_tap_anterior is None:
        return durada_actual
    return t_tap_actual - t_tap_anterior


# Autotests TODO 2
assert calcula_durada_pas(None, 1.0, 0.3) == 0.3,   "Primer tap: retorna durada_actual"
assert abs(calcula_durada_pas(1.0, 1.5, 0.3) - 0.5) < 1e-9, "Ha de retornar la diferència"
assert abs(calcula_durada_pas(2.0, 2.25, 0.5) - 0.25) < 1e-9
print("✅ TODO 2 (calcula_durada_pas) correcte")


# ── TODO 3 — toca_avancar_pas ────────────────────────────────────────────────

def toca_avancar_pas(t_ultim_canvi, t_ara, durada_pas):
    """Retorna True si ha passat prou temps per avançar al pas següent."""
    return (t_ara - t_ultim_canvi) >= durada_pas


# Autotests TODO 3
assert toca_avancar_pas(0.0, 0.3, 0.3) is True  or toca_avancar_pas(0.0, 0.3, 0.3)   # >= 
assert not toca_avancar_pas(0.0, 0.2, 0.3),  "Encara no ha passat prou temps"
assert toca_avancar_pas(1.0, 1.5, 0.4),      "Hauria d'avançar"
assert not toca_avancar_pas(1.0, 1.3, 0.4),  "Encara no"
print("✅ TODO 3 (toca_avancar_pas) correcte")


# ── TODO 4 — so_del_pas ──────────────────────────────────────────────────────

def so_del_pas(passos, idx_pas):
    """Retorna l'àudio del pas, o zeros si el pas és None (silenci)."""
    nota = passos[idx_pas]
    if nota is None:
        return np.zeros(BLOCK, dtype='float32')
    return fes_nota_baix(nota)


# Autotests TODO 4
passos_test = [None, 60, None, 64, None, 67, None, 72]

so_buit = so_del_pas(passos_test, 0)
assert isinstance(so_buit, np.ndarray), "Ha de retornar un array"
assert np.all(so_buit == 0), "Pas buit (None) hauria de retornar zeros"

so_nota = so_del_pas(passos_test, 1)
assert isinstance(so_nota, np.ndarray)
assert len(so_nota) > 0
assert np.max(np.abs(so_nota)) > 0, "Nota assignada hauria de sonar (no tot zeros)"

# Comprova que notes MIDI 60 i 64 donen freqüències (i per tant sons) diferents
so_do  = so_del_pas([60], 0)
so_mi  = so_del_pas([64], 0)
assert not np.array_equal(so_do[:BLOCK], so_mi[:BLOCK]), \
    "Dues notes MIDI diferents han de generar sons diferents"
print("✅ TODO 4 (so_del_pas) correcte")


# ── Test d'integració: simula un cicle complet del transport ─────────────────

passos = [60, None, 64, None, 67, None, 60, 55]  # línia de baix senzilla
durada_pas = 0.25  # 240ms per pas (≈ 100BPM si 4 passos/temps)

sortida_total = []
pas_actual = 0
t = 0.0
t_ultim_canvi = 0.0

for _ in range(N_PASSOS * 2):  # 2 cicles complets
    if toca_avancar_pas(t_ultim_canvi, t, durada_pas):
        bloc = so_del_pas(passos, pas_actual)
        sortida_total.append(bloc)
        pas_actual = seguent_pas(pas_actual)
        t_ultim_canvi = t
    t += durada_pas

assert len(sortida_total) > 0, "El transport no ha generat cap bloc"
print(f"✅ Integració transport: {len(sortida_total)} passos generats en 2 cicles")

print("\n✅ Tots els TODOs del Looper/Bassline validats correctament.")
print("\nNOTA DOCENT — Extensions TODO 5 (swing) i TODO 6 (accent per pas) opcionals.")
print("La màquina d'estats i el main() no es validen aquí (requereixen hardware).")
