# Setup / Reconnexió — De TP1 a TP2
### Python per al so: el mateix llenguatge, nou context

> **Instruccions de muntatge:** Crea un Google Doc amb aquest contingut (pots copiar/enganxar i formatar amb els estils de títol de Google Docs). Penja'l com a "book" al tema "Sessió 1" del Classroom, abans de la sessió. No cal que els alumnes el "treballin"; és material de consulta per durant tot el bloc 1-3.

---

Fa un any vau aprendre Python amb exemples musicals (notes MIDI, escales, seqüències). A TP2 farem servir **el mateix Python**, però ara els "números" no representen notes sinó **mostres de so**. La sintaxi que ja coneixeu reapareixerà constantment — només canvia el que hi posem a dins.

---

## 1. Variables i expressions

**TP1** (notes i durades):
```python
pitch = 60
duration = 0.25
velocity = 0.7
```

**TP2** (paràmetres de so):
```python
freq = 440          # Hz (freqüència, "to" del so)
duration = 2.0       # segons
amplitude = 0.5       # volum (0 a 1)
sample_rate = 44100   # mostres per segon (estàndard d'àudio)
```

Mateixa idea: variables amb noms descriptius que representen paràmetres. Ara els paràmetres descriuen una *ona*, no una *nota*.

---

## 2. `range()` i bucles `for`

**TP1**:
```python
for p in range(55, 80, 3):
    piano(p, 0.7, 0.25)
```

**TP2 — diferència important:** en comptes de recórrer notes una a una amb `for`, treballarem amb **arrays de NumPy**, que apliquen una operació a *tots els valors alhora*, sense bucle explícit.

```python
import numpy as np
t = np.linspace(0, duration, int(sample_rate * duration))
wave = np.sin(2 * np.pi * freq * t)   # calcula el sinus per a TOTS els valors de t a la vegada
```

👉 La lògica de `range()` (generar una seqüència de valors) **no desapareix** — reapareixerà al Bloc 4 (seqüenciació MIDI), on tornarem a recórrer llistes nota a nota com a TP1.

---

## 3. Llistes vs. Arrays — el canvi més important

**TP1** (llista normal de Python):
```python
pattern = [60, 64, 67]
# pattern * 2  -->  [60, 64, 67, 60, 64, 67]   (duplica la llista!)
```

**TP2** (array de NumPy):
```python
pattern = np.array([60, 64, 67])
# pattern * 2  -->  [120, 128, 134]   (multiplica CADA element!)
```

Aquest comportament ("broadcasting") és la base de tot el que farem amb senyals: sumar, multiplicar o transformar un so sencer amb una sola línia, sense bucles.

---

## 4. Funcions

**TP1** (funció genèrica que retorna un valor):
```python
def transpose(note, semitones):
    return note + semitones
```

**TP2** (funció que retorna un array — un so sencer):
```python
def generate_tone(freq, duration, amplitude=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * freq * t)
    return wave
```

Mateixa estructura (`def`, paràmetres, `return`) — ara la funció no retorna un número sinó un **array sencer** (el so).

---

## 5. Taula de referència ràpida (NumPy)

| Vols fer... | Com es fa |
|---|---|
| Crear un eix de temps de 0 a `duration` amb N punts | `np.linspace(0, duration, N, endpoint=False)` |
| Generar una ona sinusoidal | `np.sin(2 * np.pi * freq * t)` |
| Saber quantes mostres té un array | `len(wave)` o `wave.shape` |
| Agafar les primeres 10 mostres | `wave[:10]` |
| Multiplicar tot un array per un número (canviar volum) | `wave * 0.5` |
| Sumar dos arrays (barrejar dos sons) | `wave1 + wave2` |
| Crear un array de zeros (silenci) | `np.zeros(N)` |

---

## 6. El que ve després (preview)

Aquests conceptes reapareixeran transformats:

- El patró `for offset in range(...)` que feieu per transposar seqüències → és la mateixa lògica que la **síntesi additiva** (Bloc 5): un bucle que suma components a un so.
- El `block=False` per fer sonar veus simultànies → és conceptualment el mateix que **sumar arrays** per barrejar senyals (Bloc 3 i 5).
- `enumerate()` i `% N` per seleccionar posicions → tornaran al Bloc 4 per a seqüenciació MIDI.

No cal que ho entengueu ara — només és per reconèixer-ho quan ho trobeu.
