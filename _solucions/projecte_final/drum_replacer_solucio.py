"""
Solució de referència — Projecte final: DRUM-REPLACER
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida TODOs 1-4 sense micròfon, sounddevice ni MIDI.
La màquina d'estats i el main() no s'executen (requereixen hardware).
"""

import numpy as np

SAMPLE_RATE = 44100
BLOCK = 512


# ── UGens donats (còpia del template) ────────────────────────────────────────

class Oscillator:
    def __init__(self, freq=440.0, waveform='sine', sample_rate=SAMPLE_RATE):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.phase = 0.0

    def process(self, n):
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self.phase + phase_inc * np.arange(n)
        out = np.sin(phases) if self.waveform == 'sine' else np.sign(np.sin(phases))
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out


class Noise:
    def process(self, n):
        return np.random.uniform(-1.0, 1.0, n)


class Envelope:
    def __init__(self, attack=0.002, decay=0.12, sustain=0.0, release=0.01, sample_rate=SAMPLE_RATE):
        self.attack, self.decay, self.sustain, self.release = attack, decay, sustain, release
        self.sample_rate = sample_rate
        self.stage = 'idle'
        self.level = 0.0
        self.stage_samples = 0

    def note_on(self):
        self.stage = 'attack'
        self.stage_samples = 0

    def process(self, n):
        out = np.zeros(n)
        for k in range(n):
            if self.stage == 'attack':
                na = max(1, int(self.attack * self.sample_rate))
                self.level = min(1.0, self.stage_samples / na)
                if self.stage_samples >= na:
                    self.stage = 'decay'; self.stage_samples = 0; continue
            elif self.stage == 'decay':
                nd = max(1, int(self.decay * self.sample_rate))
                t = min(1.0, self.stage_samples / nd)
                self.level = 1.0 + t * (self.sustain - 1.0)
                if self.stage_samples >= nd:
                    self.stage = 'idle'; self.level = 0.0
            else:
                self.level = 0.0
            out[k] = self.level
            self.stage_samples += 1
        return out


def fes_kick(n_samples=int(SAMPLE_RATE * 0.2)):
    osc = Oscillator(freq=150, waveform='sine')
    env = Envelope(attack=0.002, decay=0.15, sustain=0.0)
    env.note_on()
    out = np.zeros(n_samples, dtype='float32')
    i = 0
    while i < n_samples:
        n = min(BLOCK, n_samples - i)
        progress = min(1.0, i / (0.05 * SAMPLE_RATE))
        osc.freq = 40 + (150 - 40) * np.exp(-5 * progress)
        out[i:i + n] = osc.process(n) * env.process(n)
        i += n
    return out


def fes_hihat(n_samples=int(SAMPLE_RATE * 0.1)):
    noise = Noise()
    env = Envelope(attack=0.001, decay=0.05, sustain=0.0)
    env.note_on()
    out = np.zeros(n_samples, dtype='float32')
    i = 0
    while i < n_samples:
        n = min(BLOCK, n_samples - i)
        out[i:i + n] = noise.process(n) * env.process(n)
        i += n
    return out


# ── TODO 1 — hi_ha_trigger ───────────────────────────────────────────────────

def hi_ha_trigger(bloc_audio, llindar=0.05):
    """Retorna True si el RMS del bloc supera el llindar."""
    rms = np.sqrt(np.mean(bloc_audio ** 2))
    return rms > llindar


# Autotests TODO 1
silenci = np.zeros(BLOCK, dtype='float32')
soroll_fort = np.ones(BLOCK, dtype='float32') * 0.5
soroll_fluix = np.ones(BLOCK, dtype='float32') * 0.01

assert not hi_ha_trigger(silenci),      "Silenci no hauria de fer trigger"
assert hi_ha_trigger(soroll_fort),   "Soroll fort hauria de fer trigger"
assert not hi_ha_trigger(soroll_fluix), "Soroll fluix (per sota del llindar) no hauria de fer trigger"
print("✅ TODO 1 (hi_ha_trigger) correcte")


# ── TODO 2 — extreu_features_cop ─────────────────────────────────────────────

import librosa

def extreu_features_cop(audio_cop, sr=SAMPLE_RATE):
    """Retorna np.array([centroid, zcr]) del cop."""
    n_fft = min(2048, len(audio_cop))
    centroid = float(librosa.feature.spectral_centroid(y=audio_cop.astype('float32'),
                                                        sr=sr, n_fft=n_fft).mean())
    zcr = float(librosa.feature.zero_crossing_rate(audio_cop).mean())
    return np.array([centroid, zcr])


# Autotests TODO 2
kick_audio  = fes_kick()
hihat_audio = fes_hihat()

feat_kick  = extreu_features_cop(kick_audio)
feat_hihat = extreu_features_cop(hihat_audio)

assert feat_kick.shape == (2,),  f"Ha de retornar 2 features, en retorna {feat_kick.shape}"
assert feat_hihat.shape == (2,)
assert feat_kick[0] < feat_hihat[0], \
    f"Centroid kick ({feat_kick[0]:.0f}Hz) hauria de ser menor que hihat ({feat_hihat[0]:.0f}Hz)"
print(f"✅ TODO 2 (extreu_features_cop) correcte — "
      f"centroid kick: {feat_kick[0]:.0f}Hz, hihat: {feat_hihat[0]:.0f}Hz")


# ── TODO 3 — entrena_classificador ───────────────────────────────────────────

from sklearn.neighbors import KNeighborsClassifier

def entrena_classificador(referencies_kick, referencies_hihat):
    """Construeix X/y amb les referències etiquetades i entrena un KNN(k=3)."""
    X_kick  = [extreu_features_cop(c) for c in referencies_kick]
    X_hihat = [extreu_features_cop(c) for c in referencies_hihat]
    X = np.array(X_kick + X_hihat)
    y = np.array([0] * len(X_kick) + [1] * len(X_hihat))
    clf = KNeighborsClassifier(n_neighbors=3)
    clf.fit(X, y)
    return clf


# Autotests TODO 3 — usem 5 repeticions sintètiques de cada so
np.random.seed(42)
refs_kick  = [fes_kick()  for _ in range(5)]
refs_hihat = [fes_hihat() for _ in range(5)]


clf = entrena_classificador(refs_kick, refs_hihat)
assert clf is not None

# Comprova que classifica correctament els seus propis exemples d'entrenament
pred_kick  = clf.predict([extreu_features_cop(fes_kick())])
pred_hihat = clf.predict([extreu_features_cop(fes_hihat())])
assert pred_kick[0]  == 0, f"Kick hauria de classificar-se com 0, ha donat {pred_kick[0]}"
assert pred_hihat[0] == 1, f"Hihat hauria de classificar-se com 1, ha donat {pred_hihat[0]}"
print("✅ TODO 3 (entrena_classificador) correcte")


# ── TODO 4 — so_substitut ────────────────────────────────────────────────────

def so_substitut(etiqueta):
    """Retorna fes_kick() si etiqueta==0, fes_hihat() si etiqueta==1."""
    if etiqueta == 0:
        return fes_kick()
    elif etiqueta == 1:
        return fes_hihat()
    return None


# Autotests TODO 4
so_k = so_substitut(0)
so_h = so_substitut(1)
assert so_k is not None, "so_substitut(0) ha retornat None"
assert so_h is not None, "so_substitut(1) ha retornat None"
assert isinstance(so_k, np.ndarray) and isinstance(so_h, np.ndarray)
assert len(so_k) > 0 and len(so_h) > 0
print("✅ TODO 4 (so_substitut) correcte")

print("\n✅ Tots els TODOs del Drum-Replacer validats correctament.")
print("\nNOTA DOCENT — Extensions TODO 5 (overdub) i TODO 6 (>2 classes) opcionals.")
print("La màquina d'estats i el main() no es validen aquí (requereixen hardware).")
