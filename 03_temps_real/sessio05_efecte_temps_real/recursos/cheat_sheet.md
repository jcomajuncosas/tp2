# Cheat sheet — Sessió 5
### Bloc 3c: Efectes en temps real — eco, distorsió i control amb sliders

> **Instruccions de muntatge:** Crea un Google Doc i penja'l com a "book" al tema "Sessió 5".

---

## 1. El repte dels efectes amb memòria

A la Sessió 3 vam aplicar efectes *offline*: l'eco sumava una còpia retardada de l'array complet. En temps real, **el callback rep un bloc de ~23ms cada vegada** — no té accés a les mostres passades, que ja han marxat.

Per fer eco en temps real necessitem **recordar mostres passades** entre crides al callback. La solució: un **buffer de retard** que viu *fora* del callback (variable global) i que el callback llegeix i actualitza cada crida.

---

## 2. Buffer de retard — la idea

```
Crida 1:  [bloc 1] → llegim del buffer (buit) → escrivim bloc 1 al buffer
Crida 2:  [bloc 2] → llegim bloc 1 del buffer → sumem a bloc 2 → escrivim bloc 2
Crida 3:  [bloc 3] → llegim bloc 2 del buffer → sumem a bloc 3 → ...
```

En codi:

```python
import numpy as np
import sounddevice as sd

sample_rate = 44100
delay_seconds = 0.3
delay_samples = int(delay_seconds * sample_rate)  # 13230 mostres

# Buffer global — viu entre crides al callback
delay_buffer = np.zeros(delay_samples, dtype='float32')

def eco_callback(indata, outdata, frames, time, status):
    global delay_buffer
    mono = indata[:, 0]  # agafem el canal mono

    # Llegim les mostres que van entrar fa 'delay_seconds' segons
    eco = delay_buffer[:frames]   # les PRIMERES 'frames' mostres (les mes antigues)

    # Sortida = entrada + eco atenuat
    out = mono + eco * decay

    # Actualitzem el buffer: desplacem i afegim les mostres noves
    delay_buffer = np.roll(delay_buffer, -frames)
    delay_buffer[-frames:] = mono

    outdata[:, 0] = out
```

**Per qué `np.roll`?** Desplaça el buffer circular: les mostres més antigues surten per un extrem i les noves entren per l'altre. És la implementació més clara (no la més eficient, però suficient per a blocs curts).

---

## 3. Paràmetres de l'eco en temps real

```python
delay_seconds = 0.3   # temps de retard (segons)
decay = 0.5           # atenuació de l'eco (0=silenci, 1=igual de fort)
```

Ambdós es poden canviar en temps real (des del programa principal o des d'un slider) — el callback els llegeix a cada crida.

---

## 4. Control amb ipywidgets (Colab)

A Colab, podem usar sliders per controlar paràmetres **sense** que el codi de temps real s'executi al servidor. El slider modifica una variable Python que el codi local (Thonny) llegeix via un fitxer o socket — o simplement l'usem per a demos conceptuals a Colab (el slider canvia una variable i veiem el resultat en un gràfic, sense so real).

Per a **Thonny**, el control interactiu és via `input()` (com a la Sessió 4) o via teclat (amb `keyboard` o `pynput`).

Per a **demos visuals a Colab** (sense so real):

```python
import ipywidgets as widgets
from IPython.display import display
import numpy as np
import matplotlib.pyplot as plt

@widgets.interact(delay_ms=(50, 500, 10), decay=(0.0, 1.0, 0.05))
def visualitza_eco(delay_ms=300, decay=0.5):
    sr = 44100
    t = np.linspace(0, 1, sr, endpoint=False)
    signal = np.zeros(sr)
    signal[sr//4] = 1.0  # impuls al 25%
    delay_samples = int(delay_ms / 1000 * sr)
    eco = np.zeros(sr)
    eco[sr//4 + delay_samples] = decay
    plt.figure(figsize=(10, 3))
    plt.plot(t, signal + eco)
    plt.title(f"Eco: delay={delay_ms}ms, decay={decay}")
    plt.show()
```

---

## 5. Distorsió en temps real

La distorsió és un dels efectes més simples en temps real perquè **no té memòria** — cada bloc és independent:

```python
drive = 4.0
threshold = 0.7

def distorsio_callback(indata, outdata, frames, time, status):
    mono = indata[:, 0]
    clipped = np.clip(mono * drive, -threshold, threshold)
    outdata[:, 0] = clipped / threshold  # normalitzem
```

Cap buffer, cap estat extern — és el cas ideal per a un callback.

---

## 6. Combinar efectes en temps real

Es poden combinar efectes dins d'un sol callback:

```python
def combo_callback(indata, outdata, frames, time, status):
    global delay_buffer
    mono = indata[:, 0]

    # 1. Distorsió
    dist = np.clip(mono * drive, -threshold, threshold) / threshold

    # 2. Eco (sobre la distorsió)
    eco = delay_buffer[:frames]
    out = dist + eco * decay
    delay_buffer = np.roll(delay_buffer, -frames)
    delay_buffer[-frames:] = dist  # guardem la distorsió al buffer, no el raw

    outdata[:, 0] = np.clip(out, -1.0, 1.0)  # clip final de seguretat
```

---

## 7. Per qué les classes seran millors (preview Bloc 5)

El buffer global funciona, però té un problema clar: si volem **dos ecos** simultanis (delays diferents), necessitem dos buffers globals amb noms diferents. Si volem encapsular tot l'estat d'un efecte (buffer + paràmetres), una **classe** és la solució natural:

```python
class EcoEffect:
    def __init__(self, delay_seconds, decay, sample_rate=44100):
        self.delay_samples = int(delay_seconds * sample_rate)
        self.decay = decay
        self.buffer = np.zeros(self.delay_samples, dtype='float32')

    def process(self, mono_block):
        frames = len(mono_block)
        eco = self.buffer[-frames:]
        out = mono_block + eco * self.decay
        self.buffer = np.roll(self.buffer, -frames)
        self.buffer[-frames:] = mono_block
        return out
```

Al **Bloc 5** construirem oscil·ladors i sintetitzadors com a classes seguint exactament aquest patró. L'eco de Sessió 5 és la motivació per entendre per qué les classes existeixen.

---

## 8. Regles d'or del callback (resum)

1. **Cap I/O** dins el callback (ni `sf.read`, ni `input`, ni `print` habitual)
2. **Cap càlcul pesat** — el mínim per processar el bloc
3. **Variables compartides simples** (float, int): variable global (funciona, és lleig)
4. **Arrays compartits** (buffer de retard): variable global + `np.roll` o índex circular
5. **En producció**: `queue.Queue` per a paràmetres, classes per a l'estat
