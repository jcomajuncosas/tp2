# Cheat sheet — Sessió 4
### Bloc 3b: El model callback — àudio en temps real

> **Instruccions de muntatge:** Crea un Google Doc amb aquest contingut i penja'l com a "book" al tema "Sessió 4" del Classroom.

---

## 1. Per què el model blocking no és suficient per a temps real

En el model blocking (Sessió 3):

```
grava (3s) → espera → processa → reprodueix → espera
```

Problemes per a temps real:
- Latència altíssima: has d'esperar que acabi la gravació abans de processar
- El programa **no respon a res** mentre grava o reprodueix (MIDI in, controladors, UI...)
- No pots modificar l'efecte mentre sona

Necessitem un model diferent.

---

## 2. El model callback — inversió de control

En el model callback, **el sistema crida la teva funció** cada vegada que necessita un bloc d'àudio nou (~cada 10ms). Tu no controles quan passa — defineixes *què fer* quan passi.

```
┌─────────────────────────────────────────────────────┐
│  BLOCKING                  CALLBACK (streaming)     │
├─────────────────────────────────────────────────────┤
│  Tu crides sd.rec()        Tu defineixes process()  │
│  Tu esperes (sd.wait())    El sistema crida process()│
│  Tu processes              process() ha de ser RÀPID│
│  Tu crides sd.play()       El sistema gestiona I/O  │
│  Tu esperes (sd.wait())                             │
├─────────────────────────────────────────────────────┤
│  Control: tu               Control: el sistema      │
│  Latència: alta (>1s)      Latència: baixa (~10ms)  │
│  Resposta a altres         Pot respondre entre      │
│  inputs: ❌ NO             callbacks: ✅ SÍ          │
│  Risc: cap                 Risc: callback massa lenta│
│                            → glitch (o pitjor que   │
│                            blocking)                │
├─────────────────────────────────────────────────────┤
│  Quan usar-lo              Quan usar-lo             │
│  - Efectes offline         - Efectes en temps real  │
│  - Processar fitxers       - Sintetitzadors         │
│  - Exportar WAV            - Loopers, sequenciadors │
└─────────────────────────────────────────────────────┘
```

**Analogia:** Blocking és anar a buscar el correu quan vols. Callback és tenir timbre — no fas res fins que sona, però quan sona **has de respondre ràpid**. Si trigues massa, el visitant (el sistema d'àudio) no espera.

**"És com gestionar dues coses alhora":** el teu programa principal continua executant-se (pot llegir MIDI, moure sliders, respondre al teclat...) mentre el sistema crida periòdicament la teva funció de processament d'àudio, ~cada 10ms. No gestiones tu aquesta periodicitat — simplement defineixes *què fer* cada cop que toca.

---

## 3. Estructura d'un callback

```python
def process(indata, outdata, frames, time, status):
    # indata:  array (frames, channels) — el so que entra (micròfon)
    # outdata: array (frames, channels) — el so que ha de sortir (altaveu)
    # frames:  nombre de mostres en aquest bloc (= mida del buffer)
    # time:    timestamps (rarament necessari)
    # status:  flags d'error (overrun, underrun...)

    if status:
        print(status)  # atenció: print() dins callback es lent!

    outdata[:] = indata  # pass-through: copia l'entrada a la sortida
```

**Regla d'or:** dins del callback, **fes el mínim possible**. Cap `input()`, cap `sf.read()`, cap operació lenta. Si el callback triga més que la durada del buffer → glitch.

---

## 4. Obrir un Stream

```python
import sounddevice as sd

with sd.Stream(samplerate=44100,
               blocksize=1024,
               channels=1,
               dtype='float32',
               callback=process):
    print("Streaming actiu. Ctrl+C per aturar.")
    sd.sleep(10000)  # manté el stream actiu 10 segons
```

- `blocksize`: nombre de mostres per bloc (buffer). Valors típics: 256, 512, 1024
  - Petit → menys latència, més risc de glitch
  - Gran → més latència, més marge de temps per processar
- `sd.sleep(ms)`: manera no-blocking d'esperar (a diferència de `time.sleep`)

---

## 5. Pass-through + gain amb variable compartida

```python
import sounddevice as sd
import numpy as np

gain = 0.5  # variable global — accessible des del callback I des del programa principal

def process(indata, outdata, frames, time, status):
    outdata[:] = indata * gain  # usa la variable global

with sd.Stream(samplerate=44100, blocksize=1024,
               channels=1, dtype='float32', callback=process):
    while True:
        try:
            nou_gain = float(input("Gain (0.0-1.0, Enter per sortir): "))
            gain = nou_gain
        except (ValueError, EOFError):
            break
```

⚠️ **Nota sobre la variable global:** és la solució més simple, però en sistemes de producció reals es fan servir cues de missatges (`queue.Queue`) o variables atòmiques per evitar problemes de concurrència. Per a Python amb el GIL i valors simples (un float), funciona en pràctica, però és "lleig" i ho hem de saber.

---

## 6. Per què Colab no funciona per a temps real

El codi de Colab s'executa en un **servidor remot de Google**, no al teu ordinador. El so hauria de viatjar: micròfon → xarxa → servidor → processa → xarxa → altaveu. La latència de xarxa (~50-200ms) fa impossible el temps real (~10ms).

**Contrast amb WebAudio API:** els navegadors moderns (Chrome, Firefox) sí que poden fer àudio en temps real perquè WebAudio s'executa directament al teu ordinador (client), amb accés directe al hardware local. Moltes eines professionals d'àudio web es basen en WebAudio. Colab és un servidor; WebAudio és local — problema diferent, solució diferent.

**Per això el codi d'aquesta sessió és exclusivament Thonny** (entorn local, accés directe al hardware).

---

## 7. Taula de referència ràpida

| Concepte | Valor/Notes |
|---|---|
| `blocksize` típic | 256–1024 mostres |
| Latència aproximada (blocksize=512, sr=44100) | ~11ms |
| Regla d'or del callback | Cap I/O, cap càlcul pesat, cap `input()` |
| Variable compartida simple | Variable global (funciona, però és lleig) |
| Variable compartida correcta (producció) | `queue.Queue` o variable atòmica |
| Quan hi ha glitch | El callback ha trigat més que la durada del buffer |

---

## 8. Preview — el que ve després

- Sessió 5: efectes reals en temps real (eco, distorsió), control amb sliders (`ipywidgets` a Colab com a excepció controlada), i el repte del `stutter`
- Blocs 4-5: el sintetitzador i el seqüenciador que fareu al projecte final usaran exactament aquest model de callback com a motor d'àudio
