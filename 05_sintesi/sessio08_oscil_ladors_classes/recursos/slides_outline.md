# Slides — Bloc 5a, Sessió 8
### Síntesi amb classes: Oscillator, Envelope, SamplePlayer

> **Instruccions de muntatge:** Mateix estil. Temps estimat: ~20 min (bloc "Mini-teoria" de `guia.md`, 0:08–0:28). Les diapositives 3–7 (classes) són les importants: anar a poc a poc, amb codi escrit en directe a la pissarra o al projector. La 16 introdueix l'exercici en paper, que es fa després de la demo.

---

### Diapositiva 1 — Portada
**Bloc 5 — Síntesi sonora (I)**
*Classes: Oscillator, Envelope, SamplePlayer*

---

### Diapositiva 2 — On som
- Blocs 1-2: generar i processar so (funcions, arrays)
- Bloc 3: temps real (callbacks, globals per recordar coses)
- Bloc 4: MIDI (notes, velocity, seqüències)
- Avui: organitzem el so en **classes** — peces reutilitzables que porten les seves pròpies dades

---

### Diapositiva 3 — La pregunta que va quedar oberta a la S05
```python
fase_sinus = 0.0      # la memòria del sinus
fase_ringmod = 0.0    # una global NOVA per a cada oscil·lador...
delay_buffer_1 = ...
delay_buffer_2 = ...  # ...i una cinta nova per a cada eco
```
- "I si en volguéssim 5? I un trèmolo a sobre?"
- Una funció té amnèsia: quan acaba, oblida tot
- 🎤 *Pregunta: on guardaríeu la fase de 5 oscil·ladors sense fer 5 globals?*

---

### Diapositiva 4 — Classe i instància
```python
class Fader:                        # el MOTLLE
    def __init__(self, nivell=1.0): # s'executa en crear cada objecte
        self.nivell = nivell        # atribut: dada que guarda l'objecte

    def aplica(self, so):           # mètode: funció que pertany a la classe
        return so * self.nivell

f1 = Fader(1.0)                     # una INSTÀNCIA (un objecte concret)
f1.aplica(so)                       # cridem un mètode
```
- Escriure-ho en directe, línia a línia
- `self` = "aquest objecte en concret"
- Classe = motlle. Instància = cada peça que en surt

---

### Diapositiva 5 — Dues instàncies, dues memòries
```python
f1 = Fader(1.0)
f2 = Fader(0.2)
f1.nivell = 0.5      # només canvia f1
print(f2.nivell)     # 0.2
```
- Dibuixar a la pissarra dues caixes (`f1`, `f2`), cadascuna amb el seu `nivell`
- Seguir a mà què passa amb `f1.nivell = 0.5`: la caixa de `f2` no es toca
- 🎤 *Pregunta: i si en volem cinc? (resposta: cinc instàncies, zero globals)*

---

### Diapositiva 6 — Errors típics (els veureu avui)
- Oblidar `self` com a primer paràmetre: `def aplica(so):` → error en cridar-lo
- Oblidar `self.` en guardar: `nivell = nivell` → la dada es perd en acabar `__init__`
  → `AttributeError: 'Fader' object has no attribute 'nivell'`
- Cridar sense parèntesis: `f1.aplica` no executa res, només "assenyala" el mètode
- Confondre la classe amb la instància: `Fader.aplica(so)` vs `f1.aplica(so)`

---

### Diapositiva 7 — Configuració i estat intern
```python
self.freq = freq      # configuració: la tria qui fa servir l'objecte
self._phase = 0.0     # estat intern: l'objecte el fa canviar sol
```
- El guió baix és un **conveni**: "no ho toquis des de fora"
- Python no ho impedeix (confia en tu). C++ i Java tenen `private` i el compilador ho fa complir
- Res de `get_freq()` / `set_freq()`: a Python, `osc.freq = 880` i llestos

---

### Diapositiva 8 — Disseny modular: components separats
- **Oscillator**: genera el timbre (forma d'ona contínua)
- **Envelope**: dona forma temporal (ADSR)
- **SamplePlayer**: reprodueix un so ja gravat
- Es combinen, no es barregen — com mòduls d'un sintetitzador físic
- Diagrama: 3 caixes separades amb fletxes cap a una caixa "mix final"

---

### Diapositiva 9 — Oscillator amb memòria
```python
fases = self._phase + increment * np.arange(n)            # continuem on ho vam deixar
self._phase = (self._phase + increment * n) % (2 * np.pi) # recordem per a la propera
```
- Les mateixes dues línies de la S05, però la fase viu **dins** l'objecte
- Demo (patches, secció 1-2): 200 trossos de 512 mostres sense fase → brunzit; amb fase → continu
- 🎤 *Pregunta: per què el brunzit té to? (un salt cada 512 mostres = ~86 salts per segon)*

---

### Diapositiva 10 — Envelope: ADSR
- **A**ttack, **D**ecay, **S**ustain, **R**elease
- Gràfic ADSR clàssic (amplitud vs temps)
- Sustain és un **nivell**, no un temps — es manté mentre la nota està premuda
- Demo: visualitzar la corba ADSR per separat

---

### Diapositiva 11 — Combinar: oscil·lador × envolvent
```python
corba = env.generate(note_duration)
ona = osc.generate(len(corba) / sample_rate)   # tantes mostres com la corba
nota = ona * corba
```
- Multiplicar element a element — el mateix patró de gain que ja coneixeu
- L'oscil·lador defineix el *timbre*; l'envolvent, la *forma temporal*

---

### Diapositiva 12 — MIDI controla l'envolvent, no l'oscil·lador
- `note_on` → comença l'Attack; `note_off` → comença el Release
- L'oscil·lador, conceptualment, sona sempre: és l'envolvent qui decideix quan el sentim
- **Avui és una aproximació:** `env.generate(note_duration)` sap la durada per endavant. En temps real no la sabem — ho resoldrem a la S09
- Recordatori: `note_to_freq(n) = 440 · 2^((n−69)/12)` (Bloc 4)

---

### Diapositiva 13 — SamplePlayer: un component diferent
- `Oscillator` **genera** (síntesi, matemàtiques)
- `SamplePlayer` **reprodueix** (un WAV ja gravat, com un cop de bombo)
- `generate(duration)` retorna exactament `duration` segons: retalla, o afegeix silenci
- Connexió amb Bloc 2 (`sf.read`) — ara encapsulat en una classe

---

### Diapositiva 14 — Mateix nom per a la mateixa feina
```python
fonts = [Oscillator(55, 'sawtooth'), SamplePlayer('kick_sample.wav')]
for font in fonts:
    so = font.generate(0.5)      # cada objecte ho fa a la seva manera
```
- El bucle no sap (ni li cal saber) qui és qui: n'hi ha prou que el mètode es digui igual
- Anècdota: a STK (C++) tots els components tenien `tick()` — una idea molt bonica. A Python funciona sense cap mecanisme especial (*duck typing*)
- La S09 ho converteix en conveni per a tots els components

---

### Diapositiva 15 — Taula resum
| Classe | Genera o reprodueix | Estat intern | Té forma de nota? |
|---|---|---|---|
| Oscillator | Genera | `_phase` | No |
| Envelope | Genera una corba | — | Sí, és qui la dona |
| SamplePlayer | Reprodueix | — | Sovint ja en té |

---

### Diapositiva 16 — Exercici en paper (després de la demo)
- Per parelles, sense ordinador, ~15'
- Una groovebox descrita en prosa → quines classes hi ha?
- Caixes: nom / atributs / mètodes amb signatura
- Esquelet a mà de dues classes
- Posada en comú a la pissarra

---

### Diapositiva 17 — Tancament i preview
- Avui: classes = dades + mètodes; cada instància amb la seva memòria
- **Sessió 9 (Thonny, temps real):** `generate(duration)` → `process(n_samples)` (el callback parla en mostres), l'envolvent amb `note_on`/`note_off` de debò, FM, MIDI en directe, i un tast de `signalflow`
