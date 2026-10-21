# Cheat sheet — Sessió 5
### Bloc 3c: Efectes amb memòria — la fase d'un oscil·lador i la cinta d'un eco

---

## 1. La callback té amnèsia

Cada vegada que l'stream crida la callback, aquesta només veu **el bloc actual** (1024 mostres ≈ 23 ms). No sap res del bloc anterior. Tot el que s'hagi de recordar d'una crida a la següent ha de viure **fora**, en una variable global.

| Efecte | Què ha de recordar entre crides |
|---|---|
| Distorsió, gain (S04) | Res: cada mostra només depèn d'ella mateixa |
| Oscil·lador (sinus, ring mod, trèmolo) | **Un número**: la fase |
| Eco | **Moltes mostres**: una cinta de retard |

Regla pràctica: **inicialitza l'estat abans d'obrir l'stream**, i fes que només la callback l'escrigui.

---

## 2. Memòria d'un número: la fase

Si generes un sinus amb `t = np.arange(frames) / sample_rate`, `t` torna a 0 a **cada bloc**: el sinus es talla i torna a començar 43 vegades per segon → **brunzit de ~43 Hz** (`sample_rate / blocksize`).

La solució: guardar **on s'ha quedat** l'oscil·lador (la fase, 0 … 2π) i continuar des d'allà.

```python
freq = 440.0
fase = 0.0                      # ← la memòria, FORA de la callback

def sinus_callback(indata, outdata, frames, time_info, status):
    global fase                 # l'escrivim → cal `global`
    increment = 2 * np.pi * freq / sample_rate          # avanç per mostra
    fases = fase + increment * np.arange(frames)        # fases d'aquest bloc
    outdata[:, 0] = 0.2 * np.sin(fases)
    fase = (fase + increment * frames) % (2 * np.pi)    # on comença el següent
```

El `% (2 * np.pi)` només manté el número petit: sumar voltes senceres no canvia el sinus.

---

## 3. Ring modulator

Multiplica l'entrada per un sinus (la **portadora**):

```python
portadora = np.sin(fase + increment * np.arange(frames))
outdata[:, 0] = indata[:, 0] * portadora
```

- Portadora de 100–1000 Hz → so metàl·lic, robòtic: apareixen freqüències noves (suma i diferència de l'entrada i la portadora).
- Portadora molt lenta (< 20 Hz) → el volum puja i baixa (i canvia de signe): s'assembla a un trèmolo.

**Trèmolo** (el faràs a l'assignment): el mateix oscil·lador, lent, però com a guany que no canvia de signe:

```python
lfo   = 0.5 + 0.5 * np.sin(fases)      # 0 … 1
guany = 1 - profunditat * lfo          # 1 … (1 - profunditat)
```

---

## 4. Memòria de moltes mostres: la cinta del retard

Per fer un eco hem de recordar el so de fa `delay_s` segons. El guardem en una **cinta** de `delay_samples` mostres. A cada crida, tres passos:

```
              ┌──────────── cinta (delay_samples mostres) ────────────┐
  surt ◄──  [ més antic  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  més nou ]  ◄── entra
  (eco)
```

```python
delay_s = 0.3
volum_eco = 0.6
delay_samples = int(delay_s * sample_rate)                # 13230 mostres
delay_buffer = np.zeros(delay_samples, dtype='float32')   # cinta en blanc

def eco_callback(indata, outdata, frames, time_info, status):
    global delay_buffer
    mono = indata[:, 0]

    eco = delay_buffer[:frames]                      # 1. LLEGIR l'extrem més antic
    sortida = mono + volum_eco * eco                 # 2. MESCLAR

    delay_buffer = np.roll(delay_buffer, -frames)    # 3. AVANÇAR la cinta...
    delay_buffer[-frames:] = mono                    #    ...i ESCRIURE el bloc nou

    outdata[:, 0] = np.clip(sortida, -1.0, 1.0)
```

- **Retard = mida de la cinta**, en mostres. Exacte, sigui quin sigui el blocksize.
- ⚠️ Llegeix `[:frames]` (el més antic). Si llegeixes `[-frames:]` obtens el bloc anterior: retard d'un sol bloc (23 ms), no de 0.3 s.
- **Retard mínim = un bloc** (1024 / 44100 ≈ 23 ms): la cinta ha de tenir com a mínim `frames` mostres per poder-ne llegir `frames`.
- Si a la cinta hi escrius `mono`, l'eco fa **una sola repetició**. Què passaria si hi escrivissis `sortida`? → assignment.

**Nota d'honestedat:** això no és un *buffer circular* de veritat. `np.roll` mou **totes** les mostres a cada crida. Un buffer circular deixa les dades quietes i mou un **índex**. La cinta és més clara i prou ràpida per a nosaltres.

---

## 5. Canviar paràmetres en directe

```python
with sd.Stream(..., callback=eco_control_callback):
    while True:
        entrada = input("> ").strip().lower().replace('=', ' ')
        if entrada == 'q':
            break
        parts = entrada.split()
        if len(parts) != 2 or parts[0] not in ('r', 'v'):
            print("No t'entenc: 'r 0.5', 'v 0.7' o 'q'")    # mai ignorar en silenci
            continue
        ...
```

**Repartiment de feines:** el bucle només canvia **números** (`delay_samples`, `volum_eco`). La callback és **l'única** que toca la cinta (si el retard ha canviat, en fa una de nova).

---

## 6. Encadenar efectes: l'ordre importa

```python
# distorsió → eco: l'eco repeteix el so JA distorsionat
dist = np.tanh(mono * drive)
eco = delay_buffer[:frames]
sortida = dist + volum_eco * eco
...
delay_buffer[-frames:] = dist          # a la cinta hi va el que vols repetir
```

L'ordre invers (eco → distorsió) no sona igual. Per què? → assignment.

---

## 7. Comptem globals (pregunta per al Bloc 5)

Avui: `fase_sinus`, `fase_ringmod`, `delay_buffer`, `delay_buffer_1`, `delay_buffer_2`... més tots els paràmetres de cada efecte.

**I si volguéssim 5 ecos i un trèmolo, cadascun amb els seus paràmetres?** Ho resoldrem al Bloc 5.

---

## 8. Regles d'or de la callback (actualitzades)

1. **Cap I/O** dins la callback (ni `input`, ni fitxers). Només el `print` de `status`.
2. **Cap càlcul pesat**: el mínim per processar el bloc.
3. **L'estat viu fora** (global) i s'**inicialitza abans** d'obrir l'stream.
4. **Només la callback escriu el seu estat** (fase, cinta). El bucle principal només canvia paràmetres.
5. Signatura: `callback(indata, outdata, frames, time_info, status)`.
