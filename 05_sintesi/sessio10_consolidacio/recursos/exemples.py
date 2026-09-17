"""
Exemples — Bloc 5c, Sessió 10 (Thonny)
Consolidació del Bloc 5: profiling, kit de percussió sintètica, tast ampliat de signalflow

Requereix: sounddevice, numpy, matplotlib
"""

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import time

sample_rate = 44100


# =================================================================
# 1. Recordatori: les classes UGen de S8+S9 (Oscillator, Envelope)
# =================================================================
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

    def process_sample_by_sample(self, n_samples):
        """Versió NO vectoritzada, només per al profiling de la Secció 2."""
        out = np.zeros(n_samples)
        for i in range(n_samples):
            out[i] = np.sin(self.phase)
            self.phase += 2 * np.pi * self.freq / self.sample_rate
            self.phase %= 2 * np.pi
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
                    # percussió: sense sustain, passem directament a idle
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


print("=== Sessió 10: consolidació del Bloc 5 ===\n")


# =================================================================
# 2. Profiling: vectoritzat vs. sample-by-sample (pendent de S9)
# =================================================================
print("=== 2. Profiling: per què processem en blocs vectoritzats ===")

n_test = sample_rate * 5  # 5 segons

osc_vec = Oscillator(freq=440)
t0 = time.perf_counter()
out_vec = osc_vec.process(n_test)
t1 = time.perf_counter()
temps_vec = t1 - t0

osc_sbs = Oscillator(freq=440)
t0 = time.perf_counter()
out_sbs = osc_sbs.process_sample_by_sample(n_test)
t1 = time.perf_counter()
temps_sbs = t1 - t0

print(f"Generar 5s d'àudio (220500 mostres):")
print(f"  Vectoritzat (NumPy):      {temps_vec:.4f}s")
print(f"  Sample-by-sample (bucle): {temps_sbs:.4f}s")
print(f"  Ratio: {temps_sbs / temps_vec:.1f}x més lent el bucle Python")
print(f"  (els resultats numèrics són pràcticament idèntics: error màxim {np.max(np.abs(out_vec - out_sbs)):.2e})")
print()
print("Per què: NumPy executa l'operació matemàtica sobre TOT el bloc")
print("en codi C compilat d'un sol cop. El bucle Python crida la funció")
print("np.sin() i actualitza self.phase 220500 cops per separat — cada")
print("crida individual té un overhead que es multiplica.")
print()

# Visualització
plt.figure(figsize=(6, 4))
plt.bar(['Vectoritzat\n(NumPy)', 'Sample-by-sample\n(bucle Python)'],
        [temps_vec, temps_sbs], color=['#2a9d8f', '#e76f51'])
plt.ylabel('Temps (segons)')
plt.title(f'Generar 5s d\'àudio: {temps_sbs/temps_vec:.0f}x més lent sample-by-sample')
plt.tight_layout()
plt.savefig('profiling_vectoritzat.png', dpi=100)
plt.show()
print("Gràfic desat a profiling_vectoritzat.png\n")


# =================================================================
# 3. Profiling: quan llegir un modulador a baixa resolució és segur
# =================================================================
print("=== 3. Quan 1 valor/bloc perd informació (pendent de S9) ===")


def error_lectura_baixa_resolucio(mod_freq, block=512, duration=0.5, sample_rate=44100):
    """
    Compara llegir un Oscillator a resolució completa (referència) vs.
    llegir-ne només 1 valor/bloc (com fem amb vibrato()/fm_synth()).
    Retorna l'error RMS entre les dues versions.
    """
    mod_full = Oscillator(freq=mod_freq, sample_rate=sample_rate)
    mod_block = Oscillator(freq=mod_freq, sample_rate=sample_rate)

    n_total = int(sample_rate * duration)
    full_res = mod_full.process(n_total)  # resolució completa, referència

    low_res = np.zeros(n_total)
    i = 0
    while i < n_total:
        n = min(block, n_total - i)
        bloc = mod_block.process(n)
        low_res[i:i + n] = bloc[-1]  # com si l'haguéssim "llegit" a 1 valor/bloc
        i += n

    return np.sqrt(np.mean((full_res - low_res) ** 2))


freqs_test = [5, 20, 80, 200]
errors = [error_lectura_baixa_resolucio(f) for f in freqs_test]

print("Freqüència del modulador -> error RMS de llegir-lo a 1 valor/bloc:")
for f, e in zip(freqs_test, errors):
    barra = '█' * int(e * 30)
    print(f"  {f:>4}Hz: error={e:.3f}  {barra}")
print()
print("Per sota d'uns 10-15Hz l'error és petit (vibrato, Secció 3 de S9).")
print("A partir d'uns 20-30Hz l'error creix molt ràpid i s'acosta a la")
print("magnitud del propi senyal (FM, Secció 4 de S9) — és aliasing real,")
print("no una simplificació inofensiva.\n")

plt.figure(figsize=(6, 4))
plt.bar([f"{f}Hz" for f in freqs_test], errors, color='#264653')
plt.ylabel('Error RMS')
plt.title('Error de llegir el modulador a 1 valor/bloc, segons la seva freqüència')
plt.axhline(y=0.3, color='gray', linestyle='--', label='zona de transició aprox.')
plt.legend()
plt.tight_layout()
plt.savefig('profiling_aliasing.png', dpi=100)
plt.show()
print("Gràfic desat a profiling_aliasing.png\n")


# =================================================================
# 4. Kit de percussió sintètica (RECORDATORI — el repte és a assignment.py)
# =================================================================
print("=== 4. Demo del kit de percussió que construireu ===")
print("(Aquest bloc és només una DEMO del resultat final;")
print(" el repte guiat amb TODO és a assignment.py)\n")


class Noise:
    """UGen trivial: no té estat (no necessita fase ni res persistent)."""

    def process(self, n_samples):
        return np.random.uniform(-1.0, 1.0, n_samples)


class Kick:
    """
    Oscillator amb 'pitch-drop': la freqüència baixa ràpidament de
    freq_start a freq_end durant els primers drop_time segons — és
    el truc clàssic per sintetitzar un bombo/kick amb un sol oscil·lador.
    """

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
        freqs = self.freq_end + (self.freq_start - self.freq_end) * np.exp(-5 * progress)
        self.osc.freq = float(freqs[-1])  # simplificació: freq del final del bloc
        out = self.osc.process(n_samples)
        self.elapsed += n_samples / self.sample_rate
        return out


# Demo: un kick i un hi-hat sonant
kick = Kick()
kick_env = Envelope(attack=0.002, decay=0.15, sustain=0.0, release=0.01)
kick_env.note_on()

n_dur = int(sample_rate * 0.3)
block = 512
kick_audio = np.zeros(n_dur, dtype='float32')
i = 0
while i < n_dur:
    n = min(block, n_dur - i)
    wave = kick.process(n)
    env_curve = kick_env.process(n)
    kick_audio[i:i + n] = wave * env_curve
    i += n

print("Kick (sine amb pitch-drop + envelope curta):")
sd.play(kick_audio, sample_rate)
sd.wait()

noise = Noise()
hh_env = Envelope(attack=0.001, decay=0.05, sustain=0.0, release=0.005)
hh_env.note_on()

n_dur_hh = int(sample_rate * 0.15)
hh_audio = np.zeros(n_dur_hh, dtype='float32')
i = 0
while i < n_dur_hh:
    n = min(block, n_dur_hh - i)
    wave = noise.process(n)
    env_curve = hh_env.process(n)
    hh_audio[i:i + n] = wave * env_curve
    i += n

print("Hi-hat (soroll + envelope molt curta):")
sd.play(hh_audio, sample_rate)
sd.wait()
print()
print("El repte (assignment.py) connecta això amb MIDI: nota 36 (C1, Kick")
print("GM) dispara el kick, nota 42 (F#1, Closed Hi-Hat GM) dispara el hi-hat.\n")


# =================================================================
# 5. Tast ampliat de signalflow: un altre tipus de síntesi (cor + chorus)
# =================================================================
print("=== 5. Tast de signalflow: síntesi additiva massiva + efectes (estil Solina) ===")
print("""
Tot el que hem construït (Oscillator, Envelope, Noise, Kick) és síntesi
"artesanal": una classe, un procés clar. Però hi ha tota una altra manera
d'arribar a sons rics: APILAR moltes veus lleugerament desafinades i
passar-les per efectes de modulació. És la tècnica clàssica dels
"string ensemble" analògics dels anys 70 (per exemple el Solina/ARP
String Ensemble, 1974-81): dotze generadors de to per octave-divide-down,
sense cap filtre, i un chorus integrat que els dona el seu caràcter.

NO cal instal·lar signalflow ni executar-ho avui — només mira el codi
(API real, documentació a https://signalflow.dev/):

    from signalflow import *
    import random

    graph = AudioGraph()

    # Un "cor" de 8 oscil·ladors, cadascun lleugerament desafinat
    freqs = [220 * (1 + random.uniform(-0.01, 0.01)) for _ in range(8)]
    veus = [SineOscillator(f) for f in freqs]
    cor = veus[0]
    for v in veus[1:]:
        cor = cor + v
    cor = cor * (0.1 / len(veus))

    # Un xorus de debò: un LFO lent modulant el delay_time d'un OneTapDelay
    # — exactament el mateix patró "un node alimenta el paràmetre d'un
    # altre" que hem fet servir tota la sessió, ara construint un EFECTE.
    # (la doc oficial confirma que els paràmetres accepten "audio-rate
    # inputs" en general; verifica-ho en executar-ho la primera vegada)
    lfo = SineLFO(0.25, min=0.005, max=0.02)
    cor_amb_chorus = cor + OneTapDelay(cor, delay_time=lfo, max_delay_time=0.03) * 0.6

    so_final = StereoPanner(cor_amb_chorus) * 0.5
    so_final.play()
    graph.wait()

Compara-ho amb la nostra FM o el nostre kit de percussió: aquí la idea
NO és una classe que calculem a mà — és combinar MOLTES veus simples
(8 sinusoides desafinades) i un efecte de chorus CONSTRUÏT amb el mateix
patró d'avui (un LFO alimenta el paràmetre delay_time d'un OneTapDelay).
Un "efecte professional" també és, al capdavall, UGens encadenats.

Si vols instal·lar-la i explorar més exemples bonics (granular synthesis,
FFT, MIDI real...): mira els exemples oficials del repositori
https://github.com/ideoforms/signalflow/tree/master/examples — Challenge
opcional. Funciona correctament en Mac Apple Silicon.
""")

print("=== Fi de la demo. Resum del Bloc 5 a recursos/cheat_sheet.md ===")
