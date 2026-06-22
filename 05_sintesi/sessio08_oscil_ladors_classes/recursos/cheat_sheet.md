# Cheat sheet — Sessió 8
### Bloc 5a: Síntesi amb classes — Oscillator, Envelope, SamplePlayer

> **Instruccions de muntatge:** Crea un Google Doc i penja'l com a "book" al tema "Sessió 8".

---

## 1. Per què classes, ara?

Fins ara hem usat **funcions** que reben paràmetres i retornen un array (`generate_tone`, `echo`, `arpegiador`...). Funciona bé quan tota la informació necessària cap en una crida.

Però un oscil·lador té **estat propi** que cal recordar entre crides: la seva freqüència actual, si està sonant o no, en quin punt de l'envolvent es troba... Quan una funció necessita "recordar coses" entre crides, una classe és l'eina natural:

```python
# Amb funcions: cada crida és independent, no recorda res
wave = generate_tone(freq=440, duration=1.0)

# Amb classes: l'objecte recorda el seu estat
osc = Oscillator(freq=440)
wave1 = osc.generate(duration=0.5)
osc.set_freq(880)          # canviem l'estat
wave2 = osc.generate(duration=0.5)  # ara genera a la nova freqüència
```

**Recordeu la Sessió 5:** quan volíem dos ecos simultanis amb buffers globals, necessitàvem dues variables globals separades. Amb classes, cada `Oscillator()` porta el seu propi estat — en podem crear tants com calguin sense embolicar-nos amb noms de variables.

---

## 2. Repàs ràpid de classes (Python)

```python
class Oscillator:
    def __init__(self, freq, sample_rate=44100):
        self.freq = freq                # atribut: dades de la instància
        self.sample_rate = sample_rate

    def generate(self, duration):       # mètode: funció que pertany a la classe
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        return np.sin(2 * np.pi * self.freq * t)

osc = Oscillator(freq=440)   # crida __init__, crea una instància
wave = osc.generate(1.0)     # crida el mètode generate
```

`self` és la pròpia instància — permet que el mètode accedeixi als seus propis atributs (`self.freq`).

---

## 3. La classe `Oscillator` (model modular)

```python
class Oscillator:
    def __init__(self, freq=440.0, waveform='sine', sample_rate=44100):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate

    def set_freq(self, freq):
        self.freq = freq

    def generate(self, duration):
        n = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n, endpoint=False)

        if self.waveform == 'sine':
            return np.sin(2 * np.pi * self.freq * t)
        elif self.waveform == 'square':
            return signal.square(2 * np.pi * self.freq * t)
        elif self.waveform == 'sawtooth':
            return signal.sawtooth(2 * np.pi * self.freq * t)
        else:
            raise ValueError(f"Forma d'ona desconeguda: {self.waveform}")
```

**Important:** `Oscillator` per si sol **no té forma de "nota"** — només xiula contínuament a una freqüència. Si li demanes 2 segons, sonarà 2 segons sencers sense atac ni final suau. Li falta l'envolvent.

---

## 4. La classe `Envelope` (ADSR, separada)

ADSR = **A**ttack, **D**ecay, **S**ustain, **R**elease — quatre fases d'amplitud al llarg del temps:

```
amplitud
   |    /\
   |   /  \___________
   |  /                \
   | /                  \
   |/____________________\___ temps
     A   D    S          R
```

- **Attack:** temps per pujar de 0 al màxim
- **Decay:** temps per baixar del màxim al nivell de sustain
- **Sustain:** nivell (no temps!) que es manté mentre la nota està activa
- **Release:** temps per baixar de sustain a 0, després de deixar anar la nota

```python
class Envelope:
    def __init__(self, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release

    def generate(self, note_duration, sample_rate=44100):
        """
        note_duration: quant de temps la nota està 'premuda'
        (no inclou el release — el release s'afegeix DESPRÉS)
        """
        n_attack  = int(self.attack  * sample_rate)
        n_decay   = int(self.decay   * sample_rate)
        n_sustain = max(0, int(note_duration * sample_rate) - n_attack - n_decay)
        n_release = int(self.release * sample_rate)

        env_attack  = np.linspace(0, 1, n_attack)
        env_decay   = np.linspace(1, self.sustain, n_decay)
        env_sustain = np.full(n_sustain, self.sustain)
        env_release = np.linspace(self.sustain, 0, n_release)

        return np.concatenate([env_attack, env_decay, env_sustain, env_release])
```

---

## 5. Combinar-los: una "nota" completa

```python
osc = Oscillator(freq=440, waveform='sine')
env = Envelope(attack=0.02, decay=0.1, sustain=0.6, release=0.3)

note_duration = 0.5  # quant de temps es manté premuda la nota
total_duration = note_duration + env.release  # l'oscil·lador ha de sonar tota l'estona

wave = osc.generate(total_duration)
envelope_curve = env.generate(note_duration)

# Igualem longituds (per arrodoniments) i multipliquem
n = min(len(wave), len(envelope_curve))
nota_final = wave[:n] * envelope_curve[:n]
```

**La idea central de la sessió:** l'oscil·lador defineix el *timbre* (el color del so); l'envolvent defineix la *forma temporal* (com neix i mor la nota). Es combinen multiplicant, mai barrejant la lògica dins una sola classe.

---

## 6. MIDI controla l'embolcall, no l'oscil·lador

```python
# note_on: comença l'Attack de l'envolvent (l'oscil·lador NO "es dispara")
# note_off: comença el Release

def note_to_freq(note_number):
    """Converteix número MIDI a freqüència (Hz)."""
    return 440.0 * (2 ** ((note_number - 69) / 12))

# Exemple: nota 60 (Do central)
freq = note_to_freq(60)  # ~261.6 Hz

osc = Oscillator(freq=freq)
env = Envelope(attack=0.01, decay=0.05, sustain=0.7, release=0.2)
```

`note_on(60, velocity=80)` no "encén" l'oscil·lador — fixa la seva freqüència i dispara l'Attack de l'envolvent. `note_off(60)` dispara el Release. L'oscil·lador, conceptualment, "sona sempre" — és l'envolvent qui decideix quan el sentim.

---

## 7. La classe `SamplePlayer` (one-shot, un component diferent)

Fins ara: l'`Oscillator` **genera** so des de zero amb matemàtiques. El `SamplePlayer` és diferent — **reprodueix** un so ja gravat (un fitxer WAV curt, com un cop de bombo o una veu), des del principi, cada vegada que se li demana:

```python
class SamplePlayer:
    def __init__(self, filepath, sample_rate=44100):
        self.sample_rate = sample_rate
        data, sr = sf.read(filepath)
        if sr != sample_rate:
            # (simplificació: assumim mateix sample_rate; resampling és més complex)
            pass
        self.sample = data

    def play(self, gain=1.0):
        """Retorna l'array del sample, llest per sonar."""
        return self.sample * gain

# Ús:
kick = SamplePlayer('kick.wav')
wave = kick.play(gain=0.8)
```

**Contrast clau:** `Oscillator` = generem el so (síntesi). `SamplePlayer` = reproduïm un so ja existent (sampling). Els dos són components vàlids d'un sintetitzador/instrument, i sovint es combinen (per exemple, un kick sintetitzat + un sample de crash de platet).

---

## 8. Taula resum

| Classe | Funció | Genera o reprodueix? | Té "forma de nota"? |
|---|---|---|---|
| `Oscillator` | Defineix el timbre (forma d'ona, freqüència) | Genera | No — sona sempre igual |
| `Envelope` | Defineix la forma temporal (ADSR) | Genera una corba | És la que dona forma de nota |
| `SamplePlayer` | Reprodueix un so pregravat | Reprodueix | Depèn del sample (sovint ja en té) |

---

## 9. Connexió amb TP1 i preview

- Classes a TP1 (poc treballades) → ara és on cobren sentit real: encapsular estat (freqüència, fase, paràmetres ADSR) que cal recordar entre crides
- Connexió amb Sessió 5: el buffer global de l'eco "hauria estat millor com a classe" — avui veiem exactament per què
- **Sessió 9:** FM synthesis (un oscil·lador modula la freqüència d'un altre), integració amb MIDI en temps real, i un primer tast de `pyo` (la mateixa idea, en una llibreria professional)
