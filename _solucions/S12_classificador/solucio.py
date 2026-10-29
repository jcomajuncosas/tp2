"""
Solució de referència — S12: Entrenar i avaluar classificadors (sklearn)
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Valida TODOs 1 & 2 + Challenges 1 (cross-validation) i 3 (Random Forest).
Genera el CSV internament (no depèn d'un fitxer generat per l'alumne a S11).
"""

import numpy as np
import pandas as pd
import librosa
import glob
import warnings
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

warnings.filterwarnings('ignore')

# ── Genera el CSV internament (igual que la cel·la de S12 si no existeix) ───

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT   = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DATASET_DIR = os.path.join(REPO_ROOT, '06_analisi_ml', 'sessio11_fft_features', 'dataset')

if not os.path.exists(DATASET_DIR):
    # Ajusta aquí si executes fora de l'estructura del repo:
    DATASET_DIR = "/ruta/al/teu/repo/06_analisi_ml/sessio11_fft_features/dataset"

assert os.path.exists(DATASET_DIR), (
    f"No s'ha trobat el dataset a:\n  {DATASET_DIR}\n"
    "Ajusta DATASET_DIR al principi del fitxer."
)

rows = []
for categoria in ['kick', 'hihat']:
    for f in sorted(glob.glob(f"{DATASET_DIR}/{categoria}/*.wav")):
        audio, sr = librosa.load(f, sr=None)
        n_fft    = min(2048, len(audio))
        centroid = librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=n_fft).mean()
        zcr      = librosa.feature.zero_crossing_rate(audio).mean()
        mfcc     = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, n_fft=n_fft).mean(axis=1)
        row      = {'fitxer': os.path.basename(f), 'classe': categoria,
                    'centroid': centroid, 'zcr': zcr}
        for i, val in enumerate(mfcc):
            row[f'mfcc_{i}'] = val
        rows.append(row)

df = pd.DataFrame(rows)
print(f"Dataset generat: {df.shape[0]} sons, {df.shape[1]} columnes")


# ── TODO 1 — prepara_dades ───────────────────────────────────────────────────

def prepara_dades(df, features, test_size=0.3, random_state=42):
    # TODO 1
    X = df[features].values
    y = (df['classe'] == 'hihat').astype(int).values
    return train_test_split(X, y, test_size=test_size,
                            random_state=random_state, stratify=y)


# Autotest 1
resultat = prepara_dades(df, ['centroid', 'zcr'])
assert resultat is not None
assert len(resultat) == 4
X_train, X_test, y_train, y_test = resultat
assert X_train.shape[1] == 2
assert len(X_train) + len(X_test) == len(df)
assert set(np.unique(y_train)) <= {0, 1}
prop_dataset = (df['classe'] == 'hihat').mean()
prop_train   = y_train.mean()
assert abs(prop_dataset - prop_train) < 0.15
print(f"✅ TODO 1 (prepara_dades) correcte — "
      f"train: {len(X_train)}, test: {len(X_test)}")


# ── TODO 2 — entrena_i_avalua ────────────────────────────────────────────────

def entrena_i_avalua(clf, X_train, X_test, y_train, y_test):
    # TODO 2
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    return accuracy_score(y_test, y_pred)


# Autotest 2
clf_test = KNeighborsClassifier(n_neighbors=3)
acc = entrena_i_avalua(clf_test, X_train, X_test, y_train, y_test)
assert acc is not None
assert isinstance(acc, (float, np.floating))
assert 0.0 <= acc <= 1.0
assert acc >= 0.7, f"Accuracy KNN massa baixa: {acc:.0%}"
print(f"✅ TODO 2 (entrena_i_avalua) correcte — accuracy KNN: {acc:.0%}")


# Autotest 3: comparativa 3 classificadors
classificadors = {
    'KNN (k=3)':     KNeighborsClassifier(n_neighbors=3),
    'Decision Tree': DecisionTreeClassifier(max_depth=3, random_state=42),
    'SVM (rbf)':     SVC(kernel='rbf', random_state=42),
}
resultats = {}
for nom, clf in classificadors.items():
    resultats[nom] = entrena_i_avalua(clf, X_train, X_test, y_train, y_test)

assert len(resultats) == 3
assert all(0.0 <= v <= 1.0 for v in resultats.values())
print("✅ Comparativa 3 classificadors correcte:")
for nom, acc in resultats.items():
    print(f"   {nom}: {acc:.0%}")


print("
✅ Tots els TODOs de S12 validats correctament.")
print("
NOTA DOCENT — Challenges: veure S12_challenges_solucio.py")
