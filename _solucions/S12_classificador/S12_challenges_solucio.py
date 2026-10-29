"""
Solució de referència — S12 Challenges opcionals
ÚS EXCLUSIU DEL DOCENT — no distribuir als alumnes.

Challenge 1: cross-validation (cv=5 sobre els 3 classificadors) — executat i validat
Challenge 2: 3 classes — procediment de referència (depèn del Ch.3 de S11)
Challenge 3: Random Forest — executat i validat
Challenge 4: dataset propi (exploratòric) — procediment de referència
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

# ── Genera el dataset (mateix pipeline que S12) ───────────────────────────────

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT   = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DATASET_DIR = os.path.join(REPO_ROOT, '06_analisi_ml', 'sessio11_fft_features', 'dataset')

if not os.path.exists(DATASET_DIR):
    DATASET_DIR = "/ruta/al/teu/repo/06_analisi_ml/sessio11_fft_features/dataset"

assert os.path.exists(DATASET_DIR), \
    f"No s'ha trobat el dataset a:\n  {DATASET_DIR}\nAjusta DATASET_DIR."

rows = []
for categoria in ['kick', 'hihat']:
    for f in sorted(glob.glob(f"{DATASET_DIR}/{categoria}/*.wav")):
        audio, sr = librosa.load(f, sr=None)
        n_fft = min(2048, len(audio))
        centroid = librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=n_fft).mean()
        zcr      = librosa.feature.zero_crossing_rate(audio).mean()
        mfcc     = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, n_fft=n_fft).mean(axis=1)
        row = {'fitxer': os.path.basename(f), 'classe': categoria,
               'centroid': centroid, 'zcr': zcr}
        for i, val in enumerate(mfcc): row[f'mfcc_{i}'] = val
        rows.append(row)
df = pd.DataFrame(rows)

X_all = df[['centroid', 'zcr']].values
y_all = (df['classe'] == 'hihat').astype(int).values
X_train, X_test, y_train, y_test = train_test_split(
    X_all, y_all, test_size=0.3, random_state=42, stratify=y_all)

classificadors = {
    'KNN (k=3)':     KNeighborsClassifier(n_neighbors=3),
    'Decision Tree': DecisionTreeClassifier(max_depth=3, random_state=42),
    'SVM (rbf)':     SVC(kernel='rbf', random_state=42),
}


# ── Challenge 1 — Cross-validation ───────────────────────────────────────────

print("✅ Challenge 1 (cross-validation cv=5):")
print(f"   {'Classificador':<18} {'Acc. split':>10} {'CV mean':>8} {'CV std':>8}")
print(f"   {'-'*46}")

for nom, clf in classificadors.items():
    clf.fit(X_train, y_train)
    acc_split = accuracy_score(y_test, clf.predict(X_test))
    # Reinicialitza per al CV (no contamina l'split anterior)
    clf2 = clf.__class__(**clf.get_params())
    scores = cross_val_score(clf2, X_all, y_all, cv=5)
    print(f"   {nom:<18} {acc_split:>9.0%} {scores.mean():>7.0%} {scores.std():>7.0%}")

print()
print("   Interpretació: amb 29 mostres i cv=5, cada fold té ~6 mostres de test.")
print("   La desviació estàndard mostra la variabilitat de la mesura — en un")
print("   dataset petit, el resultat depèn molt de 'quina sort' tenim amb la")
print("   partició. cv=5 promitja 5 estimacions independents → menys biaix.")
print("   Quan acc. split ≈ cv mean, la partició única era representativa.")
print("   Quan difereixen, cv és l'estimació més fiable del rendiment real.")


# ── Challenge 2 — 3 classes (procediment de referència) ──────────────────────

print(f"\nChallenge 2 — 3 classes (procediment de referència):")
print(f"   Prerequisit: completar el Challenge 3 de S11 (afegir fitxers d'una")
print(f"   tercera classe al dataset, p.ex. 'clap').")
print(f"   Canvis a fer a S12:")
print(f"""
   from sklearn.preprocessing import LabelEncoder
   le = LabelEncoder()
   y  = le.fit_transform(df['classe'])   # 0=hihat, 1=kick, 2=clap (ordre alfabètic)

   # La confusion matrix (3×3) mostra quins parells es confonen:
   from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
   cm  = confusion_matrix(y_test, clf.predict(X_test))
   disp = ConfusionMatrixDisplay(cm, display_labels=le.classes_)
   disp.plot()
""")
print("   Amb 3 classes l'accuracy global baixa però la confusion matrix és")
print("   molt més informativa: pots veure si el classificador confon kick/clap")
print("   (ambdós tenen component tonal) però no kick/hihat (espectres oposats).")


# ── Challenge 3 — Random Forest ──────────────────────────────────────────────

print(f"\n✅ Challenge 3 (Random Forest):")
print(f"   {'Model':<25} {'Acc. split':>10} {'CV mean':>8} {'CV std':>8}")
print(f"   {'-'*55}")

dt = DecisionTreeClassifier(max_depth=3, random_state=42)
rf = RandomForestClassifier(n_estimators=50, random_state=42)

for nom, clf in [('Decision Tree (1 arbre)', dt), ('Random Forest (50 arbres)', rf)]:
    clf.fit(X_train, y_train)
    acc = accuracy_score(y_test, clf.predict(X_test))
    clf2 = clf.__class__(**clf.get_params())
    scores = cross_val_score(clf2, X_all, y_all, cv=5)
    print(f"   {nom:<25} {acc:>9.0%} {scores.mean():>7.0%} {scores.std():>7.0%}")

print()
print("   Per què el Random Forest sol ser millor:")
print("   - Entrena N arbres, cadascun amb una submostra aleatòria de dades")
print("     (bagging) i subconjunt aleatori de features en cada divisió.")
print("   - El vot majoritari dels N arbres cancel·la errors individuals →")
print("     menys overfitting que un sol arbre.")
print("   - La frontera de decisió del RF és menys 'rectilínia' (menys")
print("     esglaonada) que la del DT → generalitza millor a dades noves.")
print("   - Amb 29 mostres la diferència és mínima; amb datasets grans")
print("     (> 1000 exemples) la diferència és consistent i robusta.")


# ── Challenge 4 — Dataset propi (procediment de referència) ──────────────────

print(f"\nChallenge 4 — Dataset de sons sintètics (procediment de referència):")
print(f"   Genera els sons amb les classes de S8-S10:")
print(f"""
   import numpy as np, soundfile as sf
   from S10_consolidacio_solucio import fes_kick, fes_hihat
   # + fes_snare del Challenge 2 de S10

   sr = 44100
   for i in range(10):
       sf.write(f'dataset_sintetic/kick/kick_{{i:02d}}.wav', fes_kick(), sr)
       sf.write(f'dataset_sintetic/hihat/hihat_{{i:02d}}.wav', fes_hihat(), sr)
       sf.write(f'dataset_sintetic/snare/snare_{{i:02d}}.wav', fes_snare(), sr)
""")
print("   Sons sintètics vs. reals: la classificació hauria de ser MÉS FÀCIL")
print("   perquè els sons sintètics d'una mateixa classe són molt semblants")
print("   entre ells (el kick sempre té el mateix pitch-drop, el hihat sempre")
print("   el mateix soroll blanc). Els sons reals varien molt més entre si →")
print("   les fronteres de decisió han de ser més flexibles.")
