# Cheat sheet — Sessió 4
### Bloc 3b: El model callback — àudio en temps real

⚠️ **Auriculars obligatoris** quan facis servir el micròfon: micròfon + altaveus = realimentació (Larsen).

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

En el model callback, **el sistema crida la teva funció** cada vegada que necessita un bloc d'àudio nou (cada `blocksize / sample_rate` segons: ~23 ms amb blocksize=1024). Tu no controles quan passa — defineixes *què fer* quan passi.

```
┌──────────────────────────────────────────────────────┐
│  BLOCKING                  CALLBACK (streaming)      │
├──────────────────────────────────────────────────────┤
│  Tu crides sd.rec()        Tu defineixes process()   │
│  Tu esperes (sd.wait())    El sistema crida process()│
│  Tu processes              process() ha de ser RÀPID │
│  Tu crides sd.play()       El sistema gestiona I/O   │
│  Tu esperes (sd.wait())                              │
├──────────────────────────────────────────────────────┤
│  Control: tu               Control: el sistema       │
│  Latència: segons          Latència: desenes de ms   │
│  Resposta a altres         Pot respondre mentre      │
│  inputs: ❌ NO             sona: ✅ SÍ               │
│  Risc: cap                 Risc: callback massa lenta│
│                            → glitch                  │
├──────────────────────────────────────────────────────┤
│  Quan usar-lo              Quan usar-lo              │
│  - Efectes offline         - Efectes en temps real   │
│  - Processar fitxers       - Sintetitzadors          │
│  - Exportar WAV            - Loopers, sequenciadors  │
└──────────────────────────────────────────────────────┘
```

**Analogia:** Blocking és anar a buscar el correu quan vols. Callback és tenir timbre — no fas res fins que sona, però quan sona **has de respondre ràpid**. Si trigues massa, el visitant (el sistema d'àudio) no espera.

---

## 3. Què és un stream?

Un `sd.Stream` és una **connexió oberta amb la targeta de so**. Mentre està oberta, la targeta va demanant blocs de mostres i, cada vegada, l'stream crida la teva callback: li passa el bloc que acaba d'entrar pel micròfon (`indata`) i un bloc buit que has d'omplir (`outdata`).

Tu no crides mai la callback: només la defineixes i la lliures a l'stream (`callback=...`). Tot passa "per darrere", **en paral·lel** al teu programa (en un altre *fil d'execució*, un thread). Per això el programa principal pot quedar-se adormit (`sleep`) o esperant que escriguis (`input`) i el so no s'atura.

---

## 4. Estructura d'un callback

```python
def process(indata, outdata, frames, time_info, status):
    # indata:    array (frames, channels) — el so que entra (micròfon)
    # outdata:   array (frames, channels) — el so que ha de sortir (altaveu)
    # frames:    nombre de mostres en aquest bloc (= blocksize)
    # time_info: timestamps (rarament necessari)
    # status:    avisos de l'stream (p. ex. si hi ha hagut glitch)

    if status:
        print(status)  # atenció: print() dins la callback és lent, només per avisos

    outdata[:] = indata  # pass-through: copia l'entrada a la sortida
```

**Regla d'or:** dins la callback, **fes el mínim possible**. Cap `input()`, cap `sf.read()`, cap operació lenta. Si la callback triga més que la durada d'un bloc → glitch.

---

## 5. Obrir un stream

```python
import sounddevice as sd

try:
    with sd.Stream(samplerate=44100,
                   blocksize=1024,
                   channels=1,
                   dtype='float32',
                   latency='low',
                   callback=process):
        sd.sleep(10000)          # el programa dorm 10 s; el so continua
except KeyboardInterrupt:        # Ctrl+C
    pass                         # sortim net, sense error vermell
```

- **`with`**: obre l'stream en entrar al bloc i el tanca en sortir-ne, passi el que passi. **El so dura el que dura el bloc indentat** — per això hi posem un `sleep` o un bucle.
- **`try / except`**: Python executa el `try`; si una línia llença una excepció, la resta del `try` se salta i s'executa l'`except` que hi coincideix. Si cap no hi coincideix, el programa s'atura amb error.
- **`KeyboardInterrupt`**: l'excepció que provoca **Ctrl+C** (no les altres tecles).
- **`pass`**: "no facis res".
- **`sd.sleep(ms)`**: atura el programa principal, igual que `time.sleep`. L'stream no s'atura perquè treballa en un altre fil.
- **`blocksize`**: mostres per bloc. Petit → menys latència, més risc de glitch. Gran → més latència, més marge per processar.
- **`latency='low'`**: demana al sistema els buffers més petits possibles. Sense això, el sistema n'afegeix de més grans i la latència real puja molt.

---

## 6. Pass-through + gain amb variable compartida

```python
gain = 0.5   # global: la veuen la callback i el programa principal

def process(indata, outdata, frames, time_info, status):
    outdata[:] = indata * gain       # només LLEGIR una global: no cal res

with sd.Stream(samplerate=44100, blocksize=1024, channels=1,
               dtype='float32', latency='low', callback=process):
    while True:                      # manté viu el `with` i llegeix el teclat
        try:
            entrada = input("Gain (0.0-2.0, 'q' per sortir): ")
            if entrada == 'q':
                break                # surt del while → surt del with
            gain = float(entrada)    # "hola" → ValueError
        except ValueError:
            print("Escriu un número")   # ...i el bucle continua
        except KeyboardInterrupt:    # Ctrl+C mentre input() espera
            break
```

- Mentre `input()` espera que premis Enter, el so continua (l'stream va pel seu fil).
- Si prems **Ctrl+C** mentre `input()` espera, `input()` no retorna cap text: llença `KeyboardInterrupt` i saltem a l'`except`.

**Llegir vs. assignar una global:**
- **Llegir-la** des d'una funció: no cal res.
- **Assignar-la** des de dins d'una funció: cal `global nom` a dins la funció.

⚠️ **La variable global** és la solució més simple, però en sistemes professionals es fan servir cues de missatges (`queue.Queue`) o variables atòmiques. Per a un valor simple (un float) funciona a la pràctica, però és "lletja" i ho hem de saber.

---

## 7. Latència: durada del bloc ≠ latència real

`blocksize / sample_rate` és només la **durada d'un bloc**. La latència real (el retard entre que parles i et sents) és **més gran**: hi ha buffers d'entrada, de sortida i del sistema operatiu.

```python
with sd.Stream(..., latency='low', callback=process) as stream:
    print(stream.latency)   # (entrada, sortida) en segons
```

El `as stream` guarda l'stream en una variable per poder-li preguntar coses.

---

## 8. Treballar amb Thonny (no hi ha cel·les)

1. Escriu cada demo o part com una **funció**.
2. **F5** (Run): només defineix les funcions; no sona res.
3. A la **consola (Shell)**, crida la que vulguis: `escolta_part1()`.
4. **Ctrl+C** atura l'stream actiu. El botó **Stop** reinicia Python (ho talla tot).

---

## 9. Per què Colab no funciona per a temps real

El codi de Colab s'executa en un **servidor remot de Google**, no al teu ordinador. El so hauria de viatjar: micròfon → xarxa → servidor → processa → xarxa → altaveu. La latència de xarxa (~50-200 ms) fa impossible el temps real.

**Contrast amb WebAudio API:** els navegadors sí que poden fer àudio en temps real perquè WebAudio s'executa directament al teu ordinador (client), amb accés directe al hardware local. Colab és un servidor; WebAudio és local — problema diferent, solució diferent.

**Per això el codi d'aquesta sessió és exclusivament Thonny** (entorn local, accés directe al hardware).

---

## 10. Taula de referència ràpida

| Concepte | Valor/Notes |
|---|---|
| `blocksize` típic | 256–1024 mostres |
| Durada d'un bloc (blocksize=512, sr=44100) | ~11.6 ms |
| Durada d'un bloc (blocksize=1024, sr=44100) | ~23.2 ms |
| Latència real | Sempre més gran que un bloc → `stream.latency` |
| Regla d'or de la callback | Cap I/O, cap càlcul pesat, cap `input()` |
| Quan hi ha glitch | La callback ha trigat més que la durada d'un bloc |
| Aturar un stream | Ctrl+C (amb `try/except KeyboardInterrupt`) |
| Variable compartida simple | Variable global (funciona, però és lletja) |
| Assignar una global dins una funció | `global nom` |
| Variable compartida correcta (producció) | `queue.Queue` o variable atòmica |

---

## 11. Preview — el que ve després

- Sessió 5: efectes reals en temps real (eco, distorsió), control amb sliders (`ipywidgets` a Colab com a excepció controlada), i el repte del `stutter`
- Blocs 4-5: el sintetitzador i el seqüenciador que fareu al projecte final usaran exactament aquest model de callback com a motor d'àudio
