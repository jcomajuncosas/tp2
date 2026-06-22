"""
Projecte final — Rol: DRUM-REPLACER (beatbox)
Trigger per energia (Bloc 3) + features/classificador (Bloc 6-7) per substituir
el timbre del beatbox per sons de percussió sintètics, mantenint el ritme exacte
que has tocat tu.

INSTRUMENT AUTÒNOM: no depèn de cap altre instrument de l'ensemble, ni n'envia
ni en rep res. El seu tempo surt només dels teus propis cops de veu.

Requereix: sounddevice, numpy, librosa, scikit-learn, mido, python-rtmidi

Com s'executa:
  python3 drum_replacer.py

CONTROLS MIDI (notes per defecte, configurables a CONFIG més avall):
  Nota 24 (C0)  -> REC_KICK:  comença a gravar referències del TEU so de "kick" vocal
  Nota 26 (D0)  -> REC_HIHAT: comença a gravar referències del TEU so de "hihat" vocal
  Nota 28 (E0)  -> STOP_REC:  atura la gravació de referències (es poden repetir REC_KICK/REC_HIHAT)
  Nota 30 (F0)  -> TRAIN:     entrena el classificador amb totes les referències gravades
  Nota 36 (C1)  -> REC:       comença a capturar el loop real (un cop ja hi ha TRAIN fet)
  Nota 38 (D1)  -> PLAY:      tanca el loop i el reprodueix amb substitució tímbrica
  Nota 40 (E1)  -> STOP:      atura tot

MÀQUINA D'ESTATS (ara en dues fases — ENSENYAR i TOCAR):
  Fase 1, ENSENYAR (classificació SUPERVISADA, igual que S11-S12):
    IDLE --[REC_KICK]--> GRAVANT_KICK --[STOP_REC]--> IDLE  (repeteix uns quants cops)
    IDLE --[REC_HIHAT]--> GRAVANT_HIHAT --[STOP_REC]--> IDLE (repeteix uns quants cops)
    IDLE --[TRAIN]--> LLEST  (entrena KNN amb les teves pròpies referències etiquetades)

  Fase 2, TOCAR:
    LLEST --[REC]--> ESCOLTANT --[PLAY]--> REPRODUINT --[STOP]--> LLEST

ESTRUCTURA D'AQUEST FITXER:
  - NUCLI MÍNIM (TODO 1-4): trigger per energia, captura de referències, classificació
    supervisada, reproducció amb substitució.
  - EXTENSIONS (TODO 5-6): opcionals — overdub, més classes de percussió.
"""

import time
import numpy as np
import sounddevice as sd

try:
    import mido
except ModuleNotFoundError:
    print("Aquest exemple necessita mido: pip3 install mido python-rtmidi")
    raise

import librosa
from sklearn.neighbors import KNeighborsClassifier

SAMPLE_RATE = 44100
BLOCK = 512

CONFIG = {
    'nota_rec_kick': 24,
    'nota_rec_hihat': 26,
    'nota_stop_rec': 28,
    'nota_train': 30,
    'nota_rec': 36,
    'nota_play': 38,
    'nota_stop': 40,
    'llindar_energia': 0.05,   # RMS per sobre d'aquest valor = "hi ha un cop"
    'refractari_s': 0.08,      # temps mínim entre dos triggers consecutius
    'min_referencies_per_classe': 3,  # cal almenys aquestes per poder fer TRAIN
}


# =================================================================
# UGens ja coneguts de S8-S10 — NO cal tocar-los
# =================================================================
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
                    self.stage = 'decay'
                    self.stage_samples = 0
                    continue
            elif self.stage == 'decay':
                nd = max(1, int(self.decay * self.sample_rate))
                t = min(1.0, self.stage_samples / nd)
                self.level = 1.0 + t * (self.sustain - 1.0)
                if self.stage_samples >= nd:
                    self.stage = 'idle'
                    self.level = 0.0
            else:
                self.level = 0.0
            out[k] = self.level
            self.stage_samples += 1
        return out


def fes_kick(n_samples=int(SAMPLE_RATE * 0.2)):
    """Genera un kick complet (S10): Oscillator amb pitch-drop + Envelope."""
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
    """Genera un hi-hat (S10): Noise + Envelope curta."""
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


# =================================================================
# TODO 1 (NUCLI MÍNIM): detector de trigger per energia
# =================================================================
def hi_ha_trigger(bloc_audio, llindar=CONFIG['llindar_energia']):
    """
    Donat un bloc d'àudio (array NumPy), retorna True si l'energia (RMS)
    supera el llindar — és a dir, si "hi ha un cop" en aquest bloc.

    Pista: RMS = np.sqrt(np.mean(bloc_audio ** 2))
    """
    # TODO 1: calcula el RMS del bloc i compara'l amb 'llindar'
    return False  # <-- substitueix


# =================================================================
# TODO 2 (NUCLI MÍNIM): extreure features d'un cop capturat
# =================================================================
def extreu_features_cop(audio_cop, sr=SAMPLE_RATE):
    """
    Donat un array d'àudio curt (un sol "cop" de beatbox ja retallat),
    retorna un array NumPy [centroid, zcr] — les mateixes 2 features
    senzilles que vau fer servir a la Sessió 11/12.

    Pista (igual que sempre): librosa.feature.spectral_centroid(...).mean(),
    librosa.feature.zero_crossing_rate(...).mean()
    """
    n_fft = min(2048, len(audio_cop))
    # TODO 2: calcula centroid i zcr, retorna np.array([centroid, zcr])
    return np.array([0.0, 0.0])  # <-- substitueix


# =================================================================
# TODO 3 (NUCLI MÍNIM): entrenar el classificador amb les TEVES referències
# =================================================================
def entrena_classificador(referencies_kick, referencies_hihat):
    """
    A diferència de S11-S12 (dataset extern ja preparat), aquí TU has
    gravat els teus propis exemples de referència abans de tocar el loop
    (fase ENSENYAR: REC_KICK / REC_HIHAT). Aquesta funció fa exactament
    el mateix pipeline supervisat que ja coneixeu:

      1. extreu features de cada referència (extreu_features_cop, ja fet)
      2. construeix X (totes les features) i y (0=kick per a cada
         referència de 'referencies_kick', 1=hihat per a cada referència
         de 'referencies_hihat') -- exactament com 'classe' al CSV de S11
      3. entrena un KNeighborsClassifier(n_neighbors=3) amb clf.fit(X, y)

    Retorna: el classificador ja entrenat (clf).
    """
    X_kick = [extreu_features_cop(c) for c in referencies_kick]
    X_hihat = [extreu_features_cop(c) for c in referencies_hihat]

    # TODO 3: construeix X (concatena X_kick + X_hihat) i y (0...0, 1...1),
    #         crea un KNeighborsClassifier(n_neighbors=3), entrena'l, i
    #         retorna'l. Pista: np.array(X_kick + X_hihat) per X.
    return None  # <-- substitueix


# =================================================================
# TODO 4 (NUCLI MÍNIM): generar el so de substitució per a un cop
# =================================================================
def so_substitut(etiqueta):
    """
    Donada una etiqueta (0=kick, 1=hihat), retorna l'àudio sintètic
    corresponent fent servir fes_kick() o fes_hihat() (ja donades).
    """
    # TODO 4: retorna fes_kick() si etiqueta==0, fes_hihat() si etiqueta==1
    return None  # <-- substitueix


# =================================================================
# EXTENSIONS OPCIONALS (TODO 5-6)
# =================================================================
#
# TODO 5 (EXTENSIÓ): overdub
#   Després d'arribar a REPRODUINT, permet capturar un SEGON loop
#   superposat (per exemple amb una quarta nota MIDI) sense esborrar
#   el primer — caldrà sumar els dos buffers de sortida.
#
# TODO 6 (EXTENSIÓ): més de 2 classes
#   En lloc de dividir només per la mediana del centroide (kick/hihat),
#   fes servir KMeans (sklearn.cluster.KMeans, n_clusters=3) per separar
#   en 3 grups, i afegeix una tercera funció de síntesi (per exemple,
#   un snare = Oscillator greu + Noise combinats, com al Challenge 2 de S10).


# =================================================================
# Màquina d'estats — NO cal tocar-la
# =================================================================
class DrumReplacer:
    """
    Dues fases:
      ENSENYAR: graves referències etiquetades del teu propi so vocal
                (igual que el dataset de S11, però fet per tu mateix).
      TOCAR:    un cop entrenat el classificador, captures un loop real
                i es reprodueix substituint cada cop pel so sintètic
                de la classe detectada.
    """

    def __init__(self):
        self.stage = 'IDLE'  # IDLE | GRAVANT_KICK | GRAVANT_HIHAT | ESCOLTANT | REPRODUINT
        self.entrenat = False

        self.referencies_kick = []
        self.referencies_hihat = []
        self.clf = None

        self.cops_capturats = []
        self.temps_cops = []
        self.t_inici_rec = None
        self.ultim_trigger_t = -999

        self.t_play_inici = None
        self.durada_loop = None
        self.etiquetes_loop = None
        self.cop_actual_idx = 0

    # ---- Fase ENSENYAR ----
    def rec_kick(self):
        if self.stage == 'IDLE':
            self.stage = 'GRAVANT_KICK'
            print(">> Gravant referències de KICK (fes el so unes quantes vegades)...")

    def rec_hihat(self):
        if self.stage == 'IDLE':
            self.stage = 'GRAVANT_HIHAT'
            print(">> Gravant referències de HIHAT (fes el so unes quantes vegades)...")

    def stop_rec(self):
        if self.stage in ('GRAVANT_KICK', 'GRAVANT_HIHAT'):
            self.stage = 'IDLE'
            n_kick, n_hihat = len(self.referencies_kick), len(self.referencies_hihat)
            print(f">> Stop. Referències acumulades: {n_kick} kick, {n_hihat} hihat")

    def train(self):
        if self.stage != 'IDLE':
            return
        minim = CONFIG['min_referencies_per_classe']
        if len(self.referencies_kick) < minim or len(self.referencies_hihat) < minim:
            print(f">> TRAIN cancel·lat: calen almenys {minim} referències de cada classe "
                  f"(tens {len(self.referencies_kick)} kick, {len(self.referencies_hihat)} hihat)")
            return
        self.clf = entrena_classificador(self.referencies_kick, self.referencies_hihat)
        if self.clf is not None:
            self.entrenat = True
            print(">> TRAIN fet. Classificador llest — ja pots fer REC del teu loop.")
        else:
            print(">> TRAIN ha retornat None — revisa entrena_classificador() (TODO 3)")

    # ---- Fase TOCAR ----
    def rec(self):
        if self.stage == 'IDLE' and self.entrenat:
            self.stage = 'ESCOLTANT'
            self.cops_capturats = []
            self.temps_cops = []
            self.t_inici_rec = time.perf_counter()
            print(">> REC: toca el teu loop...")
        elif not self.entrenat:
            print(">> Cal fer TRAIN abans de REC")

    def play(self):
        if self.stage == 'ESCOLTANT' and len(self.cops_capturats) >= 1:
            self.durada_loop = time.perf_counter() - self.t_inici_rec
            features = np.array([extreu_features_cop(c) for c in self.cops_capturats])
            self.etiquetes_loop = self.clf.predict(features)
            self.stage = 'REPRODUINT'
            self.t_play_inici = time.perf_counter()
            self.cop_actual_idx = 0
            print(f">> PLAY: loop de {self.durada_loop:.2f}s, "
                  f"{len(self.cops_capturats)} cops classificats: {self.etiquetes_loop}")

    def stop(self):
        self.stage = 'IDLE'
        print(">> STOP")

    # ---- Processament d'àudio (cridat des del callback) ----
    def processa_bloc_entrada(self, bloc_in):
        if self.stage == 'GRAVANT_KICK' and hi_ha_trigger(bloc_in):
            self.referencies_kick.append(bloc_in.copy())
            print(f"   referència kick #{len(self.referencies_kick)} capturada")
            time.sleep(CONFIG['refractari_s'])  # evita capturar el mateix so dos cops

        elif self.stage == 'GRAVANT_HIHAT' and hi_ha_trigger(bloc_in):
            self.referencies_hihat.append(bloc_in.copy())
            print(f"   referència hihat #{len(self.referencies_hihat)} capturada")
            time.sleep(CONFIG['refractari_s'])

        elif self.stage == 'ESCOLTANT':
            t_actual = time.perf_counter() - self.t_inici_rec
            if hi_ha_trigger(bloc_in) and (t_actual - self.ultim_trigger_t) > CONFIG['refractari_s']:
                self.ultim_trigger_t = t_actual
                self.cops_capturats.append(bloc_in.copy())
                self.temps_cops.append(t_actual)
                print(f"   cop detectat a t={t_actual:.2f}s (total: {len(self.cops_capturats)})")

    def genera_bloc_sortida(self, n_samples):
        out = np.zeros(n_samples, dtype='float32')
        if self.stage != 'REPRODUINT':
            return out

        t_loop = (time.perf_counter() - self.t_play_inici) % self.durada_loop

        if self.cop_actual_idx < len(self.temps_cops):
            t_objectiu = self.temps_cops[self.cop_actual_idx]
            if t_loop >= t_objectiu:
                so = so_substitut(self.etiquetes_loop[self.cop_actual_idx])
                if so is not None:
                    n = min(len(so), n_samples)
                    out[:n] += so[:n]
                self.cop_actual_idx += 1

        if self.cop_actual_idx >= len(self.temps_cops) and t_loop < 0.05:
            self.cop_actual_idx = 0

        return out


def main():
    dr = DrumReplacer()

    print("Dispositius MIDI disponibles:", mido.get_input_names())
    inport = mido.open_input()

    def callback(indata, outdata, frames, time_info, status):
        dr.processa_bloc_entrada(indata[:, 0])
        outdata[:, 0] = dr.genera_bloc_sortida(frames)

    with sd.Stream(samplerate=SAMPLE_RATE, blocksize=BLOCK, channels=1, callback=callback):
        print("Drum-replacer actiu. Comença gravant referències (REC_KICK / REC_HIHAT).")
        print("Ctrl+C per aturar.")
        try:
            for msg in inport:
                if msg.type != 'note_on' or msg.velocity == 0:
                    continue
                if msg.note == CONFIG['nota_rec_kick']:
                    dr.rec_kick()
                elif msg.note == CONFIG['nota_rec_hihat']:
                    dr.rec_hihat()
                elif msg.note == CONFIG['nota_stop_rec']:
                    dr.stop_rec()
                elif msg.note == CONFIG['nota_train']:
                    dr.train()
                elif msg.note == CONFIG['nota_rec']:
                    dr.rec()
                elif msg.note == CONFIG['nota_play']:
                    dr.play()
                elif msg.note == CONFIG['nota_stop']:
                    dr.stop()
        except KeyboardInterrupt:
            print("\nAturant...")


if __name__ == "__main__":
    main()
