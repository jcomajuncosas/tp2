# Challenges opcionals — Sessió 11
### Per a qui vulgui aprofundir fora de classe (NO avaluat, NO contingut de classe)

---

## Challenge 1 — Visualitzar l'espectrograma (FFT al llarg del temps)

A classe hem vist la FFT d'un so sencer (un sol "instant"). Un **espectrograma** mostra com l'espectre canvia al llarg del temps — és una FFT calculada repetidament sobre finestres curtes consecutives.

```python
import librosa.display

y, sr = librosa.load("el_teu_so.wav", sr=None)
D = librosa.stft(y)  # Short-Time Fourier Transform
S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

plt.figure(figsize=(10, 4))
librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz')
plt.colorbar(format='%+2.0f dB')
plt.title('Espectrograma')
plt.show()
```

**Experimenta:** prova-ho amb un so més llarg i complex (per exemple, una gravació de veu de la Sessió 2). Compara visualment com canvia l'espectre entre un so estable (vocal sostinguda) i un de transitori (consonant explosiva, cop sec).

---

## Challenge 2 — Afegir més features al dataset

El repte d'avui calcula centroide, ZCR i MFCC. `librosa` n'ofereix moltes més:

```python
bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr).mean()
rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr).mean()
rms = librosa.feature.rms(y=audio).mean()
```

Amplia `extreu_features()` per incloure-les, regenera `features_percussio.csv`, i visualitza (com a `patches_bloc6.ipynb`) si alguna d'aquestes noves features separa les classes encara millor que el centroide.

---

## Challenge 3 — Ampliar el dataset amb una tercera classe

El "Freesound One-Shot Percussive Sounds Dataset" complet té moltes més categories que kick/hihat (toms, claps, percussió diversa...). Consulta `licenses.json` del dataset original (Zenodo, DOI [10.5281/zenodo.3665275](https://doi.org/10.5281/zenodo.3665275)) per trobar-ne, filtrant per llicència CC0/CC-BY igual que es va fer per al mini-dataset d'avui, i amplia el classificador de la Sessió 12 a 3 classes en lloc de 2.

**Pregunta per reflexionar:** com creus que canviaria la dificultat del problema (i la precisió esperada) en passar de 2 a 3 o més classes?

---

## Challenge 4 — Explorar `signalflow` per a anàlisi (no només síntesi)

`signalflow` (vist a S9-S10) també té nodes d'anàlisi FFT natius (`FFT`, `FFTLFO`, `FFTContrast`...). Si ja el tens instal·lat (veure `05_sintesi/sessio09_fm_synth/recursos/challenges.md` per la guia d'instal·lació), explora la documentació de nodes FFT a `https://signalflow.dev/library/` i compara com es plantejaria una FFT en temps real (mostra a mostra, dins un graf de nodes) respecte a la FFT "offline" que hem fet avui sobre un fitxer sencer.

---

## Per què aquests challenges queden fora de classe

El docent ha decidit explícitament no incloure'ls a la Sessió 11: l'espectrograma (Challenge 1) és visualment ric però no aporta cap concepte nou més enllà de "FFT repetida en finestres"; ampliar features (Challenge 2) i el dataset (Challenge 3) són extensions naturals però no imprescindibles per arribar al classificador de S12; i l'anàlisi FFT en temps real amb `signalflow` (Challenge 4) connecta amb una eina ja introduïda però amb un nivell de complexitat (graf de nodes en temps real) que s'allunya del nucli "FFT + features per a ML" d'avui. Són aquí per a qui vulgui aprofundir-hi pel seu compte.
