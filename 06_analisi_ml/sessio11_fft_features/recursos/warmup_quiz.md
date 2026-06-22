# Warm-up — Sessió 11
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 5-8 minuts.

---

### Pregunta 1 — Repàs Bloc 1 (so com a array)

**Recordeu el Bloc 1: un so és, per a Python,...**

- A) Un fitxer especial que Python no pot llegir directament
- ✅ B) Un array de números (amplitud al llarg del temps)
- C) Una funció matemàtica contínua, sense valors discrets
- D) Un objecte propi de la llibreria librosa, sense relació amb NumPy

---

### Pregunta 2 — Repàs Sessió 10 (kick vs. hihat)

**A la Sessió 10 vau construir un Kick (Oscillator amb pitch-drop) i un Hi-hat (Noise). Quina diferència de "contingut freqüencial" esperaríeu entre tots dos?**

- A) Cap diferència — sonen diferent només per l'envolvent, no pel timbre
- ✅ B) El kick concentra l'energia en freqüències baixes; el hi-hat l'escampa per freqüències altes
- C) El hi-hat només té una freqüència fixa, com una sinusoide pura
- D) El kick té més freqüències agudes que el hi-hat

---

### Pregunta 3 — Intuïció: què fa una FFT

**Si un so és "amplitud al llarg del temps", i la FFT el transforma en un altre array... què creieu que representa aquest nou array?**

- A) El mateix so, però més curt en durada
- ✅ B) Quanta energia hi ha a cada freqüència del so
- C) El volum mitjà del so en cada instant
- D) Una llista de totes les notes MIDI presents al so

---

### Pregunta 4 — Intuïció: per què no cal "reinventar" les features

**Un cop saps calcular una FFT (l'espectre d'un so), calcular el "centroide espectral" és bàsicament fer una mitjana ponderada d'aquell espectre. Té sentit que cada projecte reimplementi aquest càlcul des de zero?**

- A) Sí, sempre és millor programar-ho tot des de zero
- ✅ B) No: un cop el concepte és clar, usar una llibreria testejada estalvia temps sense perdre comprensió
- C) No es pot calcular cap centroide a partir d'una FFT
- D) Sí, perquè librosa no permet calcular centroides

---

### Pregunta 5 — Predicció (lectura de codi)

```python
audio, sr = librosa.load("hihat.wav", sr=None)
centroid = librosa.feature.spectral_centroid(y=audio, sr=sr).mean()
```

**Si comparéssiu aquest `centroid` amb el d'un fitxer "kick.wav" processat igual, què esperaríeu?**

- A) Que els dos centroides siguin pràcticament idèntics
- ✅ B) Que el centroide del hihat sigui clarament més alt que el del kick
- C) Que el centroide del kick sigui clarament més alt que el del hihat
- D) Que `centroid` no es pugui comparar entre fitxers diferents

---

### Pregunta 6 — Concepte clau: per a què serveix construir un dataset de features

**Per què avui, en lloc de quedar-nos només amb "escoltar i mirar gràfics", construïm una taula (CSV) amb números per cada so?**

- A) Perquè els gràfics ocupen massa espai al disc
- ✅ B) Perquè un classificador, que veurem la propera sessió, necessita dades numèriques organitzades
- C) Perquè els fitxers WAV no es poden llegir més d'un cop
- D) Per fer una còpia de seguretat dels sons originals

---

### Pregunta 7 — Llicències i dades (connexió amb el procés real del curs)

**El mini-dataset d'avui prové d'un repositori acadèmic (Zenodo) que documenta la llicència de cada so individualment. Per què creieu que això és important quan es construeix material educatiu?**

- A) No és important, qualsevol so trobat per internet es pot fer servir lliurement
- ✅ B) Perquè cal saber si es pot usar, compartir i redistribuir un so legalment, i no totes les fonts ho deixen igual de clar
- C) Només importa la llicència si el so es ven comercialment
- D) Les llicències només afecten el codi, mai els fitxers d'àudio
