# Cheat sheet — Sessió 11
### Bloc 6: FFT pràctic i extracció de features

> **Instruccions de muntatge:** Crea un Google Doc i penja'l com a "book" al tema "Sessió 11".

---

## 1. FFT manual amb NumPy

```python
fft_result = np.fft.rfft(audio)              # transformada (números complexos)
freqs = np.fft.rfftfreq(len(audio), 1/sr)     # freqüència corresponent a cada valor
magnitude = np.abs(fft_result)                # quanta energia hi ha a cada freqüència

peak_freq = freqs[np.argmax(magnitude)]       # freqüència amb més energia
```

**Idea central:** un so és un array de números (amplitud al llarg del temps). La FFT el transforma en un altre array: quanta energia hi ha a cada freqüència. `rfft`/`rfftfreq` (en lloc de `fft`/`fftfreq`) s'usen perquè un senyal real (no complex) té un espectre simètric — `rfft` només calcula la meitat útil.

---

## 2. Per què NO implementem features a mà a partir d'aquí

Un cop entesa la FFT, calcular el centroide espectral seria només una mitjana ponderada — no afegeix cap concepte nou. **Decisió conscient:** FFT manual breu per al concepte, `librosa` per a la resta, per centrar el temps de la sessió en construir un dataset real.

---

## 3. Features amb `librosa`

```python
import librosa

audio, sr = librosa.load(filepath, sr=None)   # sr=None manté el sample rate original

# Centroide espectral: "freqüència mitjana" ponderada per energia
centroid = librosa.feature.spectral_centroid(y=audio, sr=sr).mean()

# Zero Crossing Rate: quants cops el senyal travessa zero per segon
zcr = librosa.feature.zero_crossing_rate(audio).mean()

# MFCC: representació compacta del timbre (13 coeficients típics)
mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13).mean(axis=1)
```

| Feature | Què mesura | Sol ser ALT en... | Sol ser BAIX en... |
|---|---|---|---|
| Centroide espectral | "Brillantor" del so | hihats, sons aguts/sorollosos | kicks, sons greus |
| ZCR | Quant "sorollós"/no-tonal és | percussió no afinada, soroll | tons purs, sons greus |
| MFCC | Forma global del timbre | (no té un sol "sentit" intuïtiu — és multidimensional) | — |

⚠️ **Nota tècnica:** per sons molt curts, cal limitar `n_fft` a la longitud del so (`n_fft = min(2048, len(audio))`) per evitar avisos.

---

## 4. Construint un dataset de features

```python
import pandas as pd

rows = []
for filepath, label in llista_de_fitxers_i_etiquetes:
    audio, sr = librosa.load(filepath, sr=None)
    n_fft = min(2048, len(audio))
    
    centroid = librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=n_fft).mean()
    zcr = librosa.feature.zero_crossing_rate(audio).mean()
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, n_fft=n_fft).mean(axis=1)
    
    row = {'classe': label, 'centroid': centroid, 'zcr': zcr}
    for i, val in enumerate(mfcc):
        row[f'mfcc_{i}'] = val
    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv('features.csv', index=False)
```

**Resultat:** una taula amb una fila per so i una columna per feature — exactament el format que necessita qualsevol classificador (Sessió 12).

---

## 5. El mini-dataset d'avui

29 sons de percussió (14 kicks + 15 hihats), del **Freesound One-Shot Percussive Sounds Dataset** (Ramires et al., MTG-UPF, DOI: [10.5281/zenodo.3665275](https://doi.org/10.5281/zenodo.3665275)), filtrats per llicència CC0/CC-BY 3.0. Atribució completa a `dataset/CREDITS.md`.

Validat: separació total per centroide espectral (kicks 106-1340Hz vs. hihats 2848-5415Hz) — 100% d'accuracy amb un classificador KNN simple de prova.

---

## 6. Taula resum del flux complet

| Pas | Eina | Output |
|---|---|---|
| Carregar àudio | `librosa.load()` | array NumPy + sample rate |
| Veure l'espectre | `np.fft.rfft()` | quina energia hi ha a cada freqüència |
| Resumir el timbre | `librosa.feature.*` | uns pocs números per so (centroid, ZCR, MFCC...) |
| Organitzar dades | `pandas.DataFrame` | taula llesta per a ML |

**Sessió 12:** amb aquesta taula (`features_percussio.csv`), entrenarem un classificador (KNN / arbre de decisió) que aprengui a distingir kick de hihat automàticament.
