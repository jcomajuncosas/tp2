# Cheat sheet — Sessió 3
### Bloc 3a: Captura, playback i efectes offline (blocking)

> **Instruccions de muntatge:** Crea un Google Doc amb aquest contingut i penja'l com a "book" al tema "Sessió 3" del Classroom.

---

## 1. El model blocking

En el model **blocking**, el programa fa les coses **una darrere l'altra** i espera que cada operació acabi abans de continuar. El programa té tot el control — però **no pot fer res més mentre espera**.

```python
import sounddevice as sd
import numpy as np

sample_rate = 44100
duration = 3.0

# 1. Grava (el programa s'atura aquí fins que acaben els 3 segons)
print("Gravant...")
recording = sd.rec(int(duration * sample_rate),
                   samplerate=sample_rate,
                   channels=1,
                   dtype='float32')
sd.wait()  # espera que acabi
print("Fet!")

# 2. Processa (aquí tens l'array complet per manipular)
resultat = recording.flatten() * 0.5  # gain al 50%

# 3. Reprodueix
sd.play(resultat, sample_rate)
sd.wait()
```

**Característica clau:** mentre grava o reprodueix, el programa **no respon** a res més (MIDI in, controladors, interfície...). Acceptable per a processament offline, no per a temps real.

---

## 2. Resum de funcions blocking de sounddevice

| Funció | Descripció |
|---|---|
| `sd.rec(n_mostres, samplerate, channels, dtype)` | Grava `n_mostres` del micròfon |
| `sd.play(data, samplerate)` | Reprodueix l'array `data` |
| `sd.wait()` | Espera que acabi la gravació/reproducció en curs |
| `sd.stop()` | Atura la reproducció/gravació immediatament |

**Nota:** `sd.rec()` retorna un array 2D (mostres × canals). Per treballar amb mono, aplana'l: `data.flatten()` o `data[:, 0]`.

---

## 3. Catàleg d'efectes offline

Tots els efectes d'aquesta sessió treballen sobre un array `data` ja gravat o carregat. Reben un array, retornen un array.

### Amplitud i temps

```python
# Reverse — inverteix el so (per que creus que es impossible en temps real?)
def reverse(data):
    return data[::-1]

# Fade in
def fade_in(data, duration, sample_rate=44100):
    n = int(duration * sample_rate)
    n = min(n, len(data))
    envelope = np.ones(len(data))
    envelope[:n] = np.linspace(0, 1, n)
    return data * envelope

# Fade out
def fade_out(data, duration, sample_rate=44100):
    n = int(duration * sample_rate)
    n = min(n, len(data))
    envelope = np.ones(len(data))
    envelope[-n:] = np.linspace(1, 0, n)
    return data * envelope
```

### Retard (delay / echo)

```python
# Echo simple: una sola repeticio retardada i atenuada
def echo(data, delay_seconds, decay=0.5, sample_rate=44100):
    delay_samples = int(delay_seconds * sample_rate)
    result = np.copy(data)
    result[delay_samples:] += data[:-delay_samples] * decay
    return result

# Delay amb multiples repeticions
def delay_multi(data, delay_seconds, decay=0.5, n_repeats=4, sample_rate=44100):
    result = np.copy(data)
    delay_samples = int(delay_seconds * sample_rate)
    for i in range(1, n_repeats + 1):
        start = i * delay_samples
        if start >= len(data):
            break
        result[start:] += data[:len(data)-start] * (decay ** i)
    return result
```

### Distorsió

```python
# Distorsio per clipping: amplifica i retalla
# drive: quant amplifiques abans de retallar (mes alt = mes distorsio)
def distortion(data, drive=5.0, threshold=0.7):
    clipped = np.clip(data * drive, -threshold, threshold)
    return clipped / np.max(np.abs(clipped))  # normalitza
```

### Modulació (preview del Bloc 5)

```python
# Tremolo: modula l'amplitud amb un LFO lent (efecte de "vibrat de volum")
def tremolo(data, rate=5.0, depth=0.5, sample_rate=44100):
    t = np.linspace(0, len(data)/sample_rate, len(data), endpoint=False)
    lfo = 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t))
    return data * lfo

# Ring modulation: multiplica per una portadora (crea freqüències noves)
def ring_modulation(data, carrier_freq=200.0, sample_rate=44100):
    t = np.linspace(0, len(data)/sample_rate, len(data), endpoint=False)
    carrier = np.sin(2 * np.pi * carrier_freq * t)
    return data * carrier
```

### Velocitat de reproducció

```python
# Canvia la velocitat de reproducció (i amb ella el to i la durada)
# NO es un pitch shift real: si acceleres, el so es fa mes curt I mes agut
# Per que? (Pensa en que representa sample_rate de la Sessio 1)
def playback_speed(data, factor, sample_rate=44100):
    new_sr = int(sample_rate * factor)
    return data, new_sr  # reprodueix amb: sd.play(data, new_sr)
```

---

## 4. Combinar efectes: encadenar funcions

Com que cada efecte rep i retorna un array, es poden encadenar:

```python
resultat = echo(distortion(recording, drive=3.0), delay_seconds=0.3)
```

O més llegible:
```python
resultat = recording
resultat = distortion(resultat, drive=3.0)
resultat = echo(resultat, delay_seconds=0.3, decay=0.4)
resultat = fade_out(resultat, duration=0.5)
```

---

## 5. Preview — el que ve després

Avui: grava → processa → reprodueix (tres passos separats, blocking).
Sessió 4: processa **mentre** el so entra i surt, en temps real → model de **callback**.

La pregunta que deixem oberta: *si volguessis aplicar `echo` en temps real (mentre sones), per on hauries de començar a pensar diferent?*
