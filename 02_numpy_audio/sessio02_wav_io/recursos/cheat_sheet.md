# Cheat sheet — Sessió 2
### El so com a fitxer: WAV, mixing i loops

> **Instruccions de muntatge:** Crea un Google Doc amb aquest contingut i penja'l com a "book" al tema "Sessió 2" del Classroom.

---

A la Sessió 1 vam generar so com a array (`wave`). Avui aprenem a **desar-lo a disc** i **llegir-ne d'altres**, i a **combinar** diversos sons. La connexió amb TP1 aquí és més subtil que a la Sessió 1, però hi és:

## 1. `soundfile`: el pont entre array i fitxer

```python
import soundfile as sf

# Escriure (array -> fitxer)
sf.write("el_meu_so.wav", wave, sample_rate)

# Llegir (fitxer -> array)
data, sr = sf.read("el_meu_so.wav")
```

Pensa-ho com `open()`/`write()`/`read()` de TP1 (Files & I/O), però en lloc de text, l'array sencer de mostres es desa/llegeix d'un cop.

## 2. `data` és un array com qualsevol altre

Un cop llegit, `data` es comporta exactament igual que el `wave` de la Sessió 1: el pots multiplicar (`data * 0.5`), sumar amb un altre array, retallar (`data[:1000]`), etc.

## 3. Mixing: sumar dos sons

```python
mix = so1 + so2
```

**Requisit:** `len(so1) == len(so2)`. Si no coincideixen:

```python
n = min(len(so1), len(so2))
mix = so1[:n] + so2[:n]
```

Després de sumar, normalitza per evitar clipping:
```python
mix = mix / np.max(np.abs(mix))
```

## 4. Loop: repetir un array

```python
loop_x4 = np.tile(loop, 4)
```

`np.tile(array, N)` és l'equivalent, per a arrays sencers, del que feien a TP1 amb `for _ in range(N): tocar_patró()` — però aquí no hi ha bucle explícit: es genera tot l'array repetit d'un cop.

## 5. Visualitzar (preview de librosa)

```python
import librosa
import librosa.display
import matplotlib.pyplot as plt

data, sr = librosa.load("perc_loop.wav", sr=None)  # sr=None: respecta el sample rate original
librosa.display.waveshow(data, sr=sr)
plt.show()
```

`librosa` té moltíssimes més funcions (les veurem al Bloc 6). Avui només "carregar i mirar".

## 6. Taula de referència ràpida

| Vols fer... | Com es fa |
|---|---|
| Desar un array com WAV | `sf.write("nom.wav", wave, sample_rate)` |
| Llegir un WAV | `data, sr = sf.read("nom.wav")` |
| Comprovar la durada (segons) | `len(data) / sr` |
| Sumar dos sons (mixing) | `so1[:n] + so2[:n]` (mateixa longitud `n`) |
| Repetir un fragment N vegades | `np.tile(array, N)` |
| Visualitzar la forma d'ona | `librosa.display.waveshow(data, sr=sr)` |

## 7. Preview — el que ve després

- Avui treballem amb fitxers ja gravats/generats. Al **Bloc 3** farem el mateix però **en directe**, mentre el so s'està capturant/reproduint.
- `np.tile` (loop) reapareixerà conceptualment al **Bloc 4**, quan els "loops" siguin seqüències MIDI en lloc d'arrays d'àudio.
