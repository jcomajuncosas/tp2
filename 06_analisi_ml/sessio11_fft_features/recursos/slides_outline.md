# Slides — Bloc 6, Sessió 11
### FFT pràctic i extracció de features espectrals

> **Instruccions de muntatge:** Mateix estil. Temps estimat: 15-17 min.

---

### Diapositiva 1 — Portada
**Bloc 6 — Anàlisi de so: FFT i features**
*De generar so a entendre'l*

---

### Diapositiva 2 — On érem
- Blocs 1-5: hem GENERAT so (NumPy, WAV, temps real, MIDI, síntesi)
- Avui canviem de direcció: ANALITZAR so ja existent
- Tornem a Colab (com S1-S8) — FFT i features no necessiten temps real

---

### Diapositiva 3 — Recordatori: un so és un array
```python
audio, sr = librosa.load("so.wav", sr=None)
print(audio.shape)   # un array de números
print(sr)             # quantes mostres per segon
```
- Res de nou conceptualment des del Bloc 1
- Avui: una NOVA transformació matemàtica sobre aquest array

---

### Diapositiva 4 — Què és una FFT
- FFT = *Fast Fourier Transform*
- Transforma "amplitud al llarg del temps" → "energia a cada freqüència"
- 🎤 *Pregunta: si un kick sona greu i un hihat agut, on esperaríeu trobar l'energia de cadascun?*

---

### Diapositiva 5 — FFT manual amb NumPy
```python
fft_result = np.fft.rfft(audio)
freqs = np.fft.rfftfreq(len(audio), 1/sr)
magnitude = np.abs(fft_result)
```
- `rfft`/`rfftfreq`: la versió "real" (un senyal real té espectre simètric, només calculem la meitat útil)
- Demo en directe: espectre d'un kick vs. un hihat — comparar gràfics

---

### Diapositiva 6 — Demo: kick vs. hihat
- Gràfic costat a costat dels dos espectres
- Kick: energia concentrada per sota de ~200Hz
- Hihat: energia repartida fins a freqüències molt més altes
- "Un pic" descriu bé el kick, però no tant el hihat — calen mesures millors

---

### Diapositiva 7 — Per què NO implementem features a mà
- Centroide espectral = mitjana ponderada de l'espectre — cap concepte nou un cop entesa la FFT
- Decisió conscient: FFT manual breu pel concepte, `librosa` per a la resta
- Reinventar-ho aquí no ensenyaria res de nou, i ens robaria temps per al que importa avui

---

### Diapositiva 8 — Features amb librosa
```python
centroid = librosa.feature.spectral_centroid(y=audio, sr=sr).mean()
zcr = librosa.feature.zero_crossing_rate(audio).mean()
mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13).mean(axis=1)
```
- Centroide: "brillantor" del so
- ZCR: quant "sorollós" és (creuaments per zero)
- MFCC: forma global del timbre, en 13 números

---

### Diapositiva 9 — Demo: comparativa numèrica
- Centroide kick vs. hihat (números reals, no només gràfics)
- ZCR kick vs. hihat
- 🎤 *Pregunta: si haguéssiu de triar UNA sola feature per distingir-los, quina triaríeu?*

---

### Diapositiva 10 — El mini-dataset d'avui
- 29 sons de percussió: 14 kicks + 15 hihats
- Font: Freesound One-Shot Percussive Sounds Dataset (MTG-UPF, Zenodo)
- Llicència verificada fitxer per fitxer (CC0 / CC-BY 3.0) — veure `dataset/CREDITS.md`
- **Per què un dataset extern i no el vostre kit de S10:** paràmetres lliures per alumne fan que no sigui comparable entre tothom

---

### Diapositiva 11 — Construint la taula de features
```python
rows = []
for filepath, label in fitxers_i_etiquetes:
    feats = extreu_features(filepath)
    feats['classe'] = label
    rows.append(feats)
df = pd.DataFrame(rows)
df.to_csv('features.csv')
```
- Una fila per so, una columna per feature
- Aquest és exactament el format que necessita un classificador

---

### Diapositiva 12 — Workshop: completeu `notebook.ipynb`
- `freq_pic()`: FFT manual sobre un array
- `extreu_features()`: centroide, ZCR, MFCC amb librosa
- Construïu `features_percussio.csv` — el necessitareu la propera sessió

---

### Diapositiva 13 — Preview Sessió 12
- Amb el CSV ja preparat: entrenem un classificador (KNN / arbre de decisió)
- Primer contacte amb ML real, sobre dades d'àudio que heu processat vosaltres
- El dataset d'avui és clarament separable (100% accuracy en proves) — bon punt de partida per veure ML "funcionant" de seguida
