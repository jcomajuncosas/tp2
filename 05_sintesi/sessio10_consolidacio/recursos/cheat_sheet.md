# Cheat sheet — Sessió 10
### Bloc 5c: Consolidació — resum complet del Bloc 5 (S8+S9+S10)

> **Instruccions de muntatge:** Crea un Google Doc i penja'l com a "book" al tema "Sessió 10".

---

## 1. Profiling: per què processem en blocs vectoritzats

```python
# Vectoritzat (NumPy fa tota l'operació en codi C compilat)
def process(self, n_samples):
    phases = self.phase + phase_inc * np.arange(n_samples)
    return np.sin(phases)

# Sample-by-sample (Python crida np.sin() un cop per mostra)
def process_sample_by_sample(self, n_samples):
    out = np.zeros(n_samples)
    for i in range(n_samples):
        out[i] = np.sin(self.phase)
        self.phase += phase_inc
    return out
```

Mesurat amb `time.perf_counter()`: el sample-by-sample sol ser **10-20x més lent** generant la mateixa quantitat de so, amb resultats numèrics pràcticament idèntics. El motiu: cada crida individual a una funció Python/NumPy té un overhead fix que es multiplica per cada mostra; processar tot el bloc d'un cop ho evita.

---

## 2. Quan llegir un modulador a baixa resolució introdueix aliasing

Recordatori de S9: `vibrato()` i `fm_synth()` llegeixen el modulador a "1 valor/bloc" (`lfo_out[-1]`). Mesurant l'error real (RMS) entre llegir-lo així vs. a resolució completa:

| Freqüència del modulador | Error RMS (aprox.) | Cas |
|---|---|---|
| 5 Hz | ~0.15 (petit) | Vibrato — no perd informació rellevant |
| 20 Hz | ~0.56 | Zona de transició |
| 80 Hz | ~1.0 (saturat) | FM — aliasing real |
| 200 Hz | ~1.0 (saturat) | FM — aliasing real |

L'error creix bruscament a partir d'uns 15-20Hz. Per sota d'aquest llindar, llegir el modulador a baixa resolució és segur; per sobre, no.

---

## 3. `Noise`: l'UGen més senzill possible

```python
class Noise:
    """Sense estat — cada process() és independent del que ha vingut abans."""
    def process(self, n_samples):
        return np.random.uniform(-1.0, 1.0, n_samples)
```

Contrast amb `Oscillator` (necessita `self.phase` persistent) i `Envelope` (necessita `self.stage`): `Noise` no necessita recordar res entre crides — segueix sent un UGen vàlid (implementa `process()`), només que el cas més simple possible.

---

## 4. `Kick`: pitch-drop amb un sol oscil·lador

```python
class Kick:
    def __init__(self, freq_start=150.0, freq_end=40.0, drop_time=0.05, sample_rate=44100):
        self.osc = Oscillator(freq=freq_start, waveform='sine', sample_rate=sample_rate)
        self.elapsed = 0.0
        ...

    def process(self, n_samples):
        progress = ...  # 0 a 1, segons quant ha avançat dins drop_time
        freqs = self.freq_end + (self.freq_start - self.freq_end) * np.exp(-5 * progress)
        self.osc.freq = float(freqs[-1])
        out = self.osc.process(n_samples)
        self.elapsed += n_samples / self.sample_rate
        return out
```

**Idea:** un bombo/kick electrònic clàssic és, sovint, només una sinusoide la freqüència de la qual cau molt ràpidament (de ~150Hz a ~40Hz en uns 50ms) combinada amb una envolvent curta sense sustain. No cal soroll ni res més complex.

---

## 5. Kit de percussió complet (Oscillator + Noise + Envelope + MIDI)

```python
def percussion_kit(events, total_duration, sample_rate=44100, block=512):
    kick = Kick()
    kick_env = Envelope(attack=0.002, decay=0.15, sustain=0.0, release=0.01)
    noise = Noise()
    hh_env = Envelope(attack=0.001, decay=0.05, sustain=0.0, release=0.005)

    # events: (nota_midi, t_on). Mapa General MIDI:
    #   36 (C1, Kick)            -> kick
    #   42 (F#1, Closed Hi-Hat)  -> hi-hat
    for note, t_on in events:
        if t_actual >= t_on:
            if note == 36:
                kick.reset(); kick_env.note_on()
            elif note == 42:
                hh_env.note_on()

    sortida = kick.process(n) * kick_env.process(n) + noise.process(n) * hh_env.process(n)
```

**Envolvents sense sustain** (`sustain=0.0`): a diferència de les notes melòdiques de S8/S9, un cop de percussió no es manté — `attack` molt curt, `decay` defineix tota la durada del so, i passa directament a `idle` (no cal `note_off()` explícit).

---

## 6. Taula resum: tot el Bloc 5

| Concepte | On es va introduir | Idea central |
|---|---|---|
| `Oscillator.generate(duration)` | S8 | Calcula tot l'array d'un cop; no serveix per a temps real |
| `Envelope` (ADSR) | S8 | Forma temporal d'una nota, separada del timbre |
| `SamplePlayer` | S8 | Reprodueix un so gravat, en lloc de generar-lo |
| `process(n_samples)` (arquetip UGen) | S9 | Estat persistent (`self.phase`) — permet blocs continus sense click |
| `LFO` / vibrato | S9 | Control rate "fingit": 1 valor/bloc és segur si el modulador va lent |
| FM synthesis (`I`, índex de modulació) | S9 | UGens encadenats a audio rate — sota-mostreig real si es llegeix a 1 valor/bloc |
| Integració temps real + MIDI | S9 | `Envelope` amb `stage` + `note_on()`/`note_off()` dins un callback |
| `Noise` | S10 | UGen sense estat — el cas més simple |
| `Kick` (pitch-drop) | S10 | Combinar `Oscillator` + corba de freqüència pròpia |
| Profiling (blocs vs. mostra a mostra) | S10 | ~10-20x de diferència real, mesurat |
| Profiling (aliasing per sota-mostreig) | S10 | Error creix bruscament per sobre d'uns 15-20Hz de modulador |

---

## 7. `signalflow`: un altre tipus de síntesi (additiva massiva + chorus construït)

```python
from signalflow import *
import random

graph = AudioGraph()

freqs = [220 * (1 + random.uniform(-0.01, 0.01)) for _ in range(8)]
veus = [SineOscillator(f) for f in freqs]
cor = veus[0]
for v in veus[1:]:
    cor = cor + v
cor = cor * (0.1 / len(veus))

lfo = SineLFO(0.25, min=0.005, max=0.02)
cor_amb_chorus = cor + OneTapDelay(cor, delay_time=lfo, max_delay_time=0.03) * 0.6

so_final = StereoPanner(cor_amb_chorus) * 0.5
so_final.play()
```

**Idea diferent de tot el que hem fet:** en lloc d'una classe que calculem a mà, s'apilen moltes veus simples (8 sinusoides lleugerament desafinades) i es construeix un chorus amb el MATEIX patró d'avui (`SineLFO` alimentant el `delay_time` d'un `OneTapDelay`) — un "efecte professional" també és UGens encadenats. Tècnica clàssica dels "string ensemble" analògics dels 70 (Solina/ARP String Ensemble: dotze generadors de to, sense filtre, definits pel seu chorus integrat).

**Per què `signalflow` i no `pyo`:** `pyo` (considerat inicialment) no s'ha actualitzat des de fa anys i no funciona amb versions recents de Python ni s'instal·la fàcilment en Mac Apple Silicon. `signalflow` és una alternativa activa (última versió: 2025), verificada en Mac M-series.

Exemples oficials per explorar pel vostre compte: `https://github.com/ideoforms/signalflow/tree/master/examples`
