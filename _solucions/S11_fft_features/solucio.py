"""
Solució de referència — S11: Extracció de features espectrals
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida TODOs 1 & 2 + Challenges 2 (més features) i 3 (tercera classe).
Usa el dataset real del repositori (06_analisi_ml/sessio11_fft_features/dataset/).
Ajusta DATASET_DIR si executes des d'un lloc diferent.
"""

import numpy as np
import librosa
import glob
import warnings
import os

warnings.filterwarnings('ignore')

# ── Ruta al dataset — ajusta si cal ─────────────────────────────────────────
# El dataset es troba a: <repo>/06_analisi_ml/sessio11_fft_features/dataset/
# Intentem trobar-lo automàticament a partir de la ubicació d'aquest fitxer
# (_solucions/S11_fft_features/solucio.py → pujar 3 nivells → arrel del repo).

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT  = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DATASET_DIR = os.path.join(REPO_ROOT, '06_analisi_ml', 'sessio11_fft_features', 'dataset')

if not os.path.exists(DATASET_DIR):
    # Si executes el fitxer fora de l'estructura del repo, ajusta aquí:
    DATASET_DIR = "/ruta/al/teu/repo/06_analisi_ml/sessio11_fft_features/dataset"

assert os.path.exists(DATASET_DIR), (
    f"No s'ha trobat el dataset a:\n  {DATASET_DIR}\n"
    "Ajusta DATASET_DIR al principi del fitxer."
)
print(f"Dataset trobat: {DATASET_DIR}")


# ── TODO 1 — freq_pic ────────────────────────────────────────────────────────

def freq_pic(audio, sr):
    """Retorna la freqüència (Hz) on l'espectre d'amplitud té el pic màxim."""
    # TODO 1
    fft_result = np.fft.rfft(audio)
    freqs      = np.fft.rfftfreq(len(audio), 1 / sr)
    magnitude  = np.abs(fft_result)
    return freqs[np.argmax(magnitude)]


# Autotest 1
sr_t = 16000
t = np.linspace(0, 0.5, int(sr_t * 0.5), endpoint=False)

resultat = freq_pic(np.sin(2 * np.pi * 440 * t), sr_t)
assert resultat is not None
assert abs(resultat - 440) < 5, f"Esperava ~440Hz, ha donat {resultat:.1f}Hz"

resultat2 = freq_pic(np.sin(2 * np.pi * 2000 * t), sr_t)
assert abs(resultat2 - 2000) < 5, f"Esperava ~2000Hz, ha donat {resultat2:.1f}Hz"
print("✅ TODO 1 (freq_pic) correcte")


# ── TODO 2 — extreu_features ─────────────────────────────────────────────────

def extreu_features(filepath):
    """Retorna dict amb centroid, zcr i mfcc_0..mfcc_12."""
    audio, sr = librosa.load(filepath, sr=None)
    n_fft = min(2048, len(audio))

    # TODO 2
    centroid = librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=n_fft).mean()
    zcr      = librosa.feature.zero_crossing_rate(audio).mean()
    mfcc     = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, n_fft=n_fft).mean(axis=1)

    result = {'centroid': centroid, 'zcr': zcr}
    for i, val in enumerate(mfcc):
        result[f'mfcc_{i}'] = val
    return result


# Autotest 2
kick_files  = sorted(glob.glob(f"{DATASET_DIR}/kick/*.wav"))
hihat_files = sorted(glob.glob(f"{DATASET_DIR}/hihat/*.wav"))

assert len(kick_files)  > 0, "No s'han trobat fitxers de kick"
assert len(hihat_files) > 0, "No s'han trobat fitxers de hihat"

feat_kick  = extreu_features(kick_files[0])
feat_hihat = extreu_features(hihat_files[0])

assert feat_kick is not None
assert 'centroid' in feat_kick and feat_kick['centroid'] is not None
assert 'zcr'      in feat_kick and feat_kick['zcr']      is not None
assert all(f'mfcc_{i}' in feat_kick for i in range(13))
assert feat_kick['centroid'] < feat_hihat['centroid'], (
    f"El centroide del kick ({feat_kick['centroid']:.0f}Hz) hauria de ser "
    f"menor que el del hihat ({feat_hihat['centroid']:.0f}Hz)"
)
print(f"✅ TODO 2 (extreu_features) correcte — "
      f"centroid kick: {feat_kick['centroid']:.0f}Hz, hihat: {feat_hihat['centroid']:.0f}Hz")


# Autotest 3: dataset complet
import pandas as pd
rows = []
for fp in kick_files:
    f = extreu_features(fp); f['fitxer'] = os.path.basename(fp); f['classe'] = 'kick'; rows.append(f)
for fp in hihat_files:
    f = extreu_features(fp); f['fitxer'] = os.path.basename(fp); f['classe'] = 'hihat'; rows.append(f)
df = pd.DataFrame(rows)

assert len(df) >= 25, f"Esperava ≥25 sons, n'hi ha {len(df)}"
assert set(df['classe'].unique()) == {'kick', 'hihat'}
assert not df.isnull().values.any(), "Hi ha valors buits al dataset"
print(f"✅ Dataset complet: {len(df)} sons "
      f"({(df['classe']=='kick').sum()} kicks, {(df['classe']=='hihat').sum()} hihats)")


print("
✅ Tots els TODOs de S11 validats correctament.")
print("
NOTA DOCENT — Challenges: veure S11_challenges_solucio.py")
