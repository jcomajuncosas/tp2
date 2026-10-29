"""
Solució de referència — S11 Challenges opcionals
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Challenge 1: espectrograma (exploratòric — codi de referència comentat)
Challenge 2: més features (bandwidth, rolloff, rms) — executat i validat
Challenge 3: tercera classe — procediment de referència
Challenge 4: signalflow FFT (exploratòric — procediment de referència)
"""

import numpy as np
import librosa
import glob
import warnings
import os

warnings.filterwarnings('ignore')

# ── Ruta al dataset ───────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT   = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DATASET_DIR = os.path.join(REPO_ROOT, '06_analisi_ml', 'sessio11_fft_features', 'dataset')

if not os.path.exists(DATASET_DIR):
    DATASET_DIR = "/ruta/al/teu/repo/06_analisi_ml/sessio11_fft_features/dataset"

assert os.path.exists(DATASET_DIR), \
    f"No s'ha trobat el dataset a:\n  {DATASET_DIR}\nAjusta DATASET_DIR."

kick_files  = sorted(glob.glob(f"{DATASET_DIR}/kick/*.wav"))
hihat_files = sorted(glob.glob(f"{DATASET_DIR}/hihat/*.wav"))


# ── Challenge 1 — Espectrograma (codi de referència, no executa plt.show) ────

print("Challenge 1 — Espectrograma (codi per executar a Colab):")
print("""
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

y, sr = librosa.load("el_teu_so.wav", sr=None)
D     = librosa.stft(y)                              # Short-Time Fourier Transform
S_db  = librosa.amplitude_to_db(np.abs(D), ref=np.max)

plt.figure(figsize=(10, 4))
librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz')
plt.colorbar(format='%+2.0f dB')
plt.title('Espectrograma')
plt.show()
""")
print("   Concepte clau: un espectrograma és una FFT repetida sobre finestres")
print("   curtes consecutives (STFT). Mostra COM canvia l'espectre al llarg del")
print("   temps — una FFT única ('instant') vs. una 'pel·lícula' de FFTs.")
print("   Sons estables (vocal sostinguda): bandes horitzontals constants.")
print("   Transitoris (consonant, cop): energia dispersa en moltes freqüències.")


# ── Challenge 2 — Més features: bandwidth, rolloff, rms ──────────────────────

def extreu_features_ampliada(filepath):
    """Versió ampliada: afegeix bandwidth, rolloff i rms a les features base."""
    audio, sr = librosa.load(filepath, sr=None)
    n_fft = min(2048, len(audio))
    return {
        'centroid':  float(librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=n_fft).mean()),
        'zcr':       float(librosa.feature.zero_crossing_rate(audio).mean()),
        'bandwidth': float(librosa.feature.spectral_bandwidth(y=audio, sr=sr, n_fft=n_fft).mean()),
        'rolloff':   float(librosa.feature.spectral_rolloff(y=audio, sr=sr, n_fft=n_fft).mean()),
        'rms':       float(librosa.feature.rms(y=audio).mean()),
        **{f'mfcc_{i}': v for i, v in enumerate(
            librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, n_fft=n_fft).mean(axis=1)
        )},
    }


feat_kick  = extreu_features_ampliada(kick_files[0])
feat_hihat = extreu_features_ampliada(hihat_files[0])

# Comprova que les noves features discriminen kick/hihat
assert 'bandwidth' in feat_kick and 'rolloff' in feat_kick and 'rms' in feat_kick
# El hihat concentra energia en freqüències altes → bandwidth i rolloff majors
assert feat_kick['bandwidth'] < feat_hihat['bandwidth'], \
    "Bandwidth del kick hauria de ser < hihat"
assert feat_kick['rolloff'] < feat_hihat['rolloff'], \
    "Rolloff del kick hauria de ser < hihat"

print(f"\n✅ Challenge 2 (més features):")
print(f"   {'Feature':<12} {'Kick':>10} {'Hihat':>10}  {'Discrimina?':>12}")
print(f"   {'-'*46}")
for feat in ['centroid', 'bandwidth', 'rolloff', 'rms', 'zcr']:
    vk = feat_kick[feat]; vh = feat_hihat[feat]
    disc = "✓" if abs(vk - vh) / (max(abs(vk), abs(vh)) + 1e-9) > 0.2 else "~"
    unit = "Hz" if feat in ('centroid', 'bandwidth', 'rolloff') else ""
    print(f"   {feat:<12} {vk:>9.0f}{unit} {vh:>9.0f}{unit}  {disc:>12}")
print()
print("   bandwidth i rolloff separen kick/hihat tant com el centroide.")
print("   rms (energia mitjana) pot variar molt entre fitxers — menys fiable")
print("   com a feature única, però útil combinada amb les altres.")


# ── Challenge 3 — Tercera classe (procediment de referència) ─────────────────

print(f"\nChallenge 3 — Tercera classe (procediment de referència):")
print(f"   1. Descarrega una altra categoria del Freesound One-Shot Percussive")
print(f"      Sounds Dataset (Zenodo DOI 10.5281/zenodo.3665275), p.ex. 'clap' o 'tom'.")
print(f"   2. Afegeix els fitxers a dataset/clap/ (o la categoria triada).")
print(f"   3. Al bucle de construcció del CSV, afegeix:")
print(f"      for fp in sorted(glob.glob(f'{{DATASET_DIR}}/clap/*.wav')):")
print(f"          f = extreu_features(fp); f['classe'] = 'clap'; rows.append(f)")
print(f"   4. A S12, ajusta la codificació y:")
print(f"      from sklearn.preprocessing import LabelEncoder")
print(f"      le = LabelEncoder(); y = le.fit_transform(df['classe'])")
print(f"      # o manualment: {{'kick':0, 'hihat':1, 'clap':2}}")
print(f"   Amb 3 classes l'accuracy global sol baixar: el classificador té")
print(f"   més opcions per equivocar-se. La confusion matrix (3×3) mostra")
print(f"   quins parells de sons es confonen entre si — molt més informativa")
print(f"   que l'accuracy escalar.")


# ── Challenge 4 — signalflow FFT (procediment de referència) ─────────────────

print(f"\nChallenge 4 — signalflow per a anàlisi FFT en temps real:")
print(f"   Documentació de nodes FFT: https://signalflow.dev/library/")
print(f"   Nodes rellevants: FFT, IFFT, FFTContrast, FFTPhaseVocoder...")
print()
print(f"   Diferència conceptual clau:")
print(f"   - FFT 'offline' (avui): calculem np.fft.rfft() sobre un fitxer complet")
print(f"     → un sol vector de magnituds per a tot el so.")
print(f"   - FFT en temps real (signalflow): el node FFT calcula l'espectre")
print(f"     a cada bloc de l'àudio en viu → el resultat és un senyal que")
print(f"     canvia contínuament mostra a mostra, dins el graf de nodes.")
print(f"   La FFT offline és adequada per a ML (extracció de features de fitxers);")
print(f"   la FFT en temps real és per a efectes espectrals en viu (phase vocoder,")
print(f"   convolució espectral, filtratge espectral adaptatiu).")
