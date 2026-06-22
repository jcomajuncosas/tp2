# Slides — Bloc 2, Sessió 2
### El so com a fitxer: WAV, lectura/escriptura i combinació de sons

> **Instruccions de muntatge:** Crea una presentació de Google Slides, mateix estil que la Sessió 1. Temps total estimat: 15-20 min.

---

### Diapositiva 1 — Portada
**Bloc 2 — El so com a fitxer**
*De l'array a Disc i del Disc a l'array*

---

### Diapositiva 2 — Recapitulació Sessió 1
- Vam generar so: `wave = amplitude * np.sin(2*pi*freq*t)` → un array
- Vam aplicar gain (`* amplitude`) i una envolvent (fade in/out)
- Avui: què fem amb aquest array un cop el tenim? Com el desem? Com en llegim un altre?

---

### Diapositiva 3 — Un fitxer WAV és... un array (+ metadades)
- Un WAV = capçalera (sample rate, nombre de canals, format) + dades (les mostres, com `wave`)
- Diagrama: caixa "array NumPy" ↔ fletxes ↔ caixa "fitxer .wav al disc"
- `soundfile` fa aquesta conversió en totes dues direccions

---

### Diapositiva 4 — Escriure un WAV
```python
import soundfile as sf
sf.write("el_meu_so.wav", wave, sample_rate)
```
- `wave`: array (com els que ja sabeu fer)
- `sample_rate`: el mateix concepte de la Sessió 1
- Demo: escriure el `generate_tone()` de la setmana passada a un fitxer real

---

### Diapositiva 5 — Llegir un WAV
```python
data, sr = sf.read("el_meu_so.wav")
```
- Retorna l'array (`data`) i el sample rate (`sr`) del fitxer
- `data` és un array normal: el podem multiplicar, sumar, retallar... com `wave`
- Demo: llegir el fitxer que acabem d'escriure i comprovar que `data` és (gairebé) igual a `wave`

---

### Diapositiva 6 — Mono vs. Estèreo (breu)
- Mono: `data.shape` → `(n_mostres,)`
- Estèreo: `data.shape` → `(n_mostres, 2)` (columna esquerra/dreta)
- No hi entrarem avui a fons — només per no sorprendre's si un fitxer dona un array 2D

---

### Diapositiva 7 — Visualitzar amb librosa
```python
import librosa.display
librosa.display.waveshow(data, sr=sr)
```
- `librosa` és una llibreria gran per a anàlisi d'àudio (la veurem a fons al Bloc 6)
- Avui només: carregar i visualitzar la forma d'ona
- Demo: visualitzar el fitxer de percussió (`perc_loop.wav`)

---

### Diapositiva 8 — Transformacions: gain, fade (repàs ràpid)
- Gain: `data * factor` (ja ho vam fer a Sessió 1)
- Fade: multiplicar per una envolvent (ja ho vam fer a Sessió 1)
- Avui ho apliquem a un so **carregat d'un fitxer**, no només generat

---

### Diapositiva 9 — Mixing: sumar dos sons
```python
mix = so1 + so2
```
- **Atenció:** els dos arrays han de tenir la mateixa longitud (mateix `len()`)
- Si no, cal retallar (`[:n]`) o allargar amb zeros (`np.pad`)
- Risc de "clipping" si la suma supera 1 → normalitzar després

---

### Diapositiva 10 — Loop: repetir un fragment
```python
loop_x4 = np.tile(loop, 4)
```
- `np.tile` repeteix un array N vegades
- Connexió amb TP1: és l'equivalent de `for _ in range(4): ...` però per a arrays sencers

---

### Diapositiva 11 — Connexió amb TP1 i preview
- `np.tile` / concatenació d'arrays ↔ els bucles `for`/`while True` que repetien patrons de notes (TP1)
- Avui: "patrons" de so en lloc de patrons de notes
- Preview: al Bloc 3 farem tot això **en temps real**, mentre sona — avui encara treballem amb fitxers ja gravats
