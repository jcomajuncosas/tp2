# Slides — Bloc 5a, Sessió 8
### Síntesi amb classes: Oscillator, Envelope, SamplePlayer

> **Instruccions de muntatge:** Mateix estil. Temps estimat: 20-25 min (introdueix OOP aplicat, mereix una mica més de temps).

---

### Diapositiva 1 — Portada
**Bloc 5 — Síntesi sonora (I)**
*Classes: Oscillator, Envelope, SamplePlayer*

---

### Diapositiva 2 — On som
- Blocs 1-2: generar i processar so (funcions, arrays)
- Bloc 3: temps real (callbacks, buffers globals)
- Bloc 4: MIDI (notes, velocity, seqüències)
- Avui: organitzem tot això en **classes** — components reutilitzables amb estat propi

---

### Diapositiva 3 — El problema que resolen les classes
- Recordeu la Sessió 5: dos ecos simultanis → dos buffers globals separats
- Si en volguéssim 5, necessitaríem 5 parells de variables globals
- Una funció "oblida" tot en acabar — no pot recordar el seu propi estat
- Una **classe** pot: cada instància porta les seves pròpies dades

---

### Diapositiva 4 — Repàs ràpid: classes en Python
```python
class Oscillator:
    def __init__(self, freq):
        self.freq = freq      # atribut

    def generate(self, duration):
        ...                    # mètode

osc = Oscillator(440)          # instància
wave = osc.generate(1.0)       # crida un mètode
```
- `self` = la pròpia instància
- `__init__` s'executa en crear l'objecte

---

### Diapositiva 5 — Disseny modular: 3 components separats
- **Oscillator**: genera el timbre (forma d'ona contínua)
- **Envelope**: dona forma temporal (ADSR)
- **SamplePlayer**: reprodueix un so ja gravat
- Es combinen, no es barregen — com mòduls d'un sintetitzador físic
- Diagrama: 3 caixes separades amb fletxes cap a una caixa "mix final"

---

### Diapositiva 6 — Oscillator: només timbre
```python
osc = Oscillator(freq=440, waveform='sine')
wave = osc.generate(duration=2.0)
```
- Demo en directe: escoltar 2 segons d'`Oscillator` sol
- 🎤 *Pregunta: com sona? Té atac? Té final suau?*
- Resposta esperada: sona "tot pla", entra i surt sobtadament

---

### Diapositiva 7 — Envelope: ADSR
- **A**ttack, **D**ecay, **S**ustain, **R**elease
- Gràfic ADSR clàssic (amplitud vs temps)
- Sustain és un **nivell**, no un temps — es manté mentre la nota està premuda
- Demo: visualitzar la corba ADSR per separat (sense so, només el gràfic)

---

### Diapositiva 8 — Combinar Oscillator + Envelope
```python
wave = osc.generate(total_duration)
env_curve = env.generate(note_duration)
nota_final = wave * env_curve
```
- Multiplicar element a element — el mateix patró de gain que ja coneixeu
- Demo en directe: el mateix `Oscillator` d'abans, ara amb envolvent — escoltar la diferència

---

### Diapositiva 9 — MIDI controla l'embolcall, no l'oscil·lador
- `note_on` → comença l'Attack de l'**envolvent**
- `note_off` → comença el Release de l'**envolvent**
- L'**oscil·lador** no "s'encén" ni "s'apaga" — conceptualment sona sempre
- És l'envolvent qui decideix quan el sentim
- Aquesta distinció és la idea central de tota la sessió

---

### Diapositiva 10 — Number MIDI → freqüència
```python
def note_to_freq(note_number):
    return 440.0 * (2 ** ((note_number - 69) / 12))
```
- 440 Hz = La4 = nota MIDI 69 (referència)
- Cada semitò = multiplicar/dividir per 2^(1/12)
- Demo: provar amb diverses notes i escoltar

---

### Diapositiva 11 — SamplePlayer: un component diferent
- `Oscillator` **genera** (síntesi, matemàtiques)
- `SamplePlayer` **reprodueix** (un WAV ja gravat, com un cop de bombo)
- Contrast clar: timbre sintetitzat vs. timbre gravat
- Connexió amb Bloc 2 (lectura WAV, ja conegut) — ara encapsulat en una classe que "es dispara"

---

### Diapositiva 12 — Taula resum
| Classe | Genera o reprodueix | Té forma de nota? |
|---|---|---|
| Oscillator | Genera | No |
| Envelope | Genera corba | Sí, és qui la dona |
| SamplePlayer | Reprodueix | Sovint ja en té |

---

### Diapositiva 13 — Connexió amb TP1 i preview
- Classes a TP1: poc treballades — avui cobren sentit real
- Connexió amb Sessió 5: "el buffer global de l'eco hauria estat millor com a classe" — avui veiem per què
- **Sessió 9:** FM synthesis (un oscil·lador modula un altre), integració amb MIDI en temps real, i primer tast de `pyo`
