# Cheat sheet — Sessió 9
### Bloc 5b: Arquitectura UGen, control rate, FM, integració temps real + MIDI

> **Instruccions de muntatge:** Crea un Google Doc i penja'l com a "book" al tema "Sessió 9".

---

## 1. El problema: `generate(duration)` no recorda la fase

A la Sessió 8, `Oscillator.generate(duration)` sempre començava `t=0`:

```python
osc = Oscillator(freq=440)
bloc1 = osc.generate(0.1)
bloc2 = osc.generate(0.1)   # torna a començar a t=0!
junts = np.concatenate([bloc1, bloc2])  # hi ha un "salt" de fase -> click
```

Si volem so continu generat **bloc a bloc** (com exigeix el temps real), necessitem que l'oscil·lador recordi on s'havia quedat.

---

## 2. L'arquetip UGen: `process(n_samples)`

```python
class Oscillator:
    def __init__(self, freq=440.0, waveform='sine', sample_rate=44100):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.phase = 0.0          # ESTAT persistent

    def process(self, n_samples):
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self.phase + phase_inc * np.arange(n_samples)
        out = np.sin(phases)      # (o square/sawtooth)
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)   # actualitzem per la propera crida
        return out
```

**Idea central:** `process(n)` és una interfície comuna — qualsevol peça d'un sintetitzador modular ("UGen" = *unit generator*) la pot implementar: oscil·ladors, LFOs, envolvents... Cridar-la repetidament, bloc a bloc, produeix so continu sense salts.

**Connexió amb Max/Pd:** és exactament el model mental d'un patch — cada objecte rep i envia blocs de senyal contínuament, mantenint el seu propi estat intern. No hi ha "herència Python" formal aquí (cada classe implementa `process()` pel seu compte) — és un **conveni de disseny**, no un mecanisme de llenguatge nou.

---

## 3. Control rate vs. audio rate: vibrato

**Control rate de debò (en un motor DSP real):** un generador de control (LFO, envolupant) calcula els seus propis valors a una freqüència molt inferior a la d'àudio — p.ex. 100-200 valors/segon en lloc de 44100/s — perquè el paràmetre que controla no necessita més resolució.

| | Audio rate | Control rate (real) |
|---|---|---|
| Què és | El so que sentim directament | Un valor que modula un paràmetre |
| Freqüència típica | Centenars/milers de Hz | < 20 Hz normalment (LFOs) |
| Es calcula a | 44100 valors/s | Molts menys valors/s (ex: 100-200/s) |

**⚠️ El nostre `LFO` d'aquí sota és un HÍBRID PEDAGÒGIC, no control rate real:** per simplicitat, reutilitza exactament la mateixa lògica que `Oscillator` — calcula a 44100Hz igual que el portador, NO genera realment menys valors. El que fem és "fingir" que està a control rate llegint-ne només l'última mostra de cada bloc (`lfo_out[-1]`):

```python
class LFO:
    """HÍBRID: mateixa lògica que Oscillator (calcula a 44100Hz). NO és un
    generador de control rate real — només en llegim l'última mostra del
    bloc, com si ho fos."""
    def __init__(self, freq=5.0, sample_rate=44100):
        self.freq = freq
        self.sample_rate = sample_rate
        self.phase = 0.0

    def process(self, n_samples):
        phase_inc = 2 * np.pi * self.freq / self.sample_rate
        phases = self.phase + phase_inc * np.arange(n_samples)
        out = np.sin(phases)
        self.phase = (phases[-1] + phase_inc) % (2 * np.pi)
        return out


def vibrato(base_freq, lfo_freq, depth, duration, sample_rate=44100, block=512):
    lfo = LFO(freq=lfo_freq)
    osc = Oscillator(freq=base_freq, waveform='sine')

    i = 0
    while i < n_total:
        n = min(block, n_total - i)
        lfo_out = lfo.process(n)
        osc.freq = base_freq + depth * lfo_out[-1]   # llegim el LFO a "control rate": 1 valor/bloc
        sortida[i:i+n] = osc.process(n)
        i += n
```

**Per què funciona igualment (tot i ser un híbrid):** com que el LFO es mou lent (5Hz), el seu valor amb prou feines canvia dins d'un bloc — llegir-ne només l'última mostra no perd informació rellevant. **No és un estalvi de CPU**: el `process(n)` calcula igualment el bloc sencer; només en llencem la majoria de mostres.

**Referència real:** el Yamaha DX7 té un únic LFO global que es pot enrutar com a vibrato (modula pitch) i/o tremolo (modula amplitud) de qualsevol operador — exactament aquesta idea.

---

## 4. FM synthesis: UGens encadenats, però a AUDIO RATE

**Diferència de fons amb el vibrato:** la FM és, per definició, modulació a audio rate — el modulador es mou dins el rang audible, no a freqüència de control. Si el llegim només 1 cop/bloc (com fem aquí per simplicitat), estem **sota-mostrejant-lo**: introduïm artefactes/aliasing perquè es mou massa ràpid per a aquesta resolució.

```python
carrier_freq = 440.0
mod_freq = 80.0
I = 200.0    # índex de modulació (notació estàndard: Chowning, DX7)

modulator = Oscillator(freq=mod_freq, waveform='sine')
carrier = Oscillator(freq=carrier_freq, waveform='sine')

block = 512
i = 0
while i < n_total:
    n = min(block, n_total - i)
    mod_out = modulator.process(n)
    carrier.freq = carrier_freq + I * mod_out[-1]   # actualitzem freq del portador
    sortida[i:i+n] = carrier.process(n)
    i += n
```

**Comparativa objectiva (amplada de banda espectral) amb els valors per defecte — conseqüència del mecanisme, no la causa:**

| | Modulador | Resolució de lectura | Amplada de banda | Es percep com |
|---|---|---|---|---|
| Vibrato (Secció 3) | 5Hz (lent) | 1 valor/bloc, sense artefactes | ~20 Hz | la mateixa nota, ondulant |
| FM (aquí) | 80Hz (audio) | 1 valor/bloc, JA introdueix aliasing | ~480 Hz | un timbre nou |

⚠️ **Simplificació important:** aquí `carrier.freq` s'actualitza un cop per bloc (cada 512 mostres), no mostra a mostra. És prou per sentir l'efecte i entendre el patró, però introdueix artefactes coneguts — NO és l'FM "real" mostra-a-mostra dels sintetitzadors clàssics. Veure Challenge per a la versió correcta.

**Nota:** `signalflow` i altres motors de síntesi professionals (o entorns "tot audio rate" com VCV Rack) eviten aquest problema processant sempre a la resolució completa — per això `signalflow` pot fer `SineOscillator(440 + SineOscillator(80) * 200)` en una línia sense els artefactes de la nostra simplificació per blocs.

**Per no confondre-ho:** l'estalvi de CPU real de processar en blocs (com fem des de la Secció 2, tant pel modulador com pel portador) és un tema diferent d'aquest — ve de reduir l'overhead de cridar `process()` moltes vegades amb poques mostres cada cop, no de llegir el modulador a baixa resolució. Es quantifica amb profiling a la Sessió 10.

---

## 5. `Envelope` redissenyada com a UGen

A S8, `Envelope.generate(note_duration)` necessitava saber la durada per endavant. En temps real no ho sabem (el `note_off` arriba quan arriba) — calen `note_on()`/`note_off()` + `process()` amb un estat de `stage`:

```python
class Envelope:
    def __init__(self, attack=0.01, decay=0.1, sustain=0.7, release=0.2, sample_rate=44100):
        self.attack = attack; self.decay = decay
        self.sustain = sustain; self.release = release
        self.sample_rate = sample_rate
        self.stage = 'idle'       # 'idle'|'attack'|'decay'|'sustain'|'release'
        self.level = 0.0
        self.stage_samples = 0

    def note_on(self):
        self.stage = 'attack'
        self.stage_samples = 0

    def note_off(self):
        self.stage = 'release'
        self.stage_samples = 0
        self._release_start_level = self.level

    def process(self, n_samples):
        # ... avança el 'stage' mostra a mostra, retorna la corba del bloc
        ...
```

`note_on()` dispara l'Attack; `note_off()` dispara el Release **sigui quin sigui el moment** — això és exactament el que calia per integrar-ho amb MIDI real.

---

## 6. Integració: callback temps real + MIDI

```python
import mido
import sounddevice as sd

synth_osc = Oscillator(freq=440, waveform='sawtooth')
synth_env = Envelope(attack=0.01, decay=0.08, sustain=0.6, release=0.3)

def synth_callback(outdata, frames, time, status):
    wave = synth_osc.process(frames)
    env_curve = synth_env.process(frames)
    outdata[:, 0] = (wave * env_curve).astype('float32')

with mido.open_input(port_name) as inport:
    with sd.OutputStream(samplerate=44100, blocksize=512,
                          channels=1, dtype='float32', callback=synth_callback):
        for msg in inport:
            if msg.type == 'note_on' and msg.velocity > 0:
                synth_osc.freq = note_to_freq(msg.note)
                synth_env.note_on()
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                synth_env.note_off()
```

**El callback no canvia respecte a la Sessió 5** (`outdata[:, 0] = ...` dins un `with sd.OutputStream(...)`) — el que ha canviat és **qui genera el senyal**: ara són les nostres classes UGen, alimentades per esdeveniments MIDI en lloc d'efectes sobre l'entrada de micròfon.

**Sense teclat MIDI?** Mateix patró exacte, substituint el port `mido` per una llista de `(nota, t_on, t_off)` consultada amb `perf_counter()` — vegeu `exemples.py` Secció 6b.

---

## 7. `signalflow`: la mateixa idea, professionalitzada (i sense els artefactes)

```python
from signalflow import *
graph = AudioGraph()

I = 200                                       # índex de modulació (Hz)
modulator = SineOscillator(80) * I
carrier = SineOscillator(440 + modulator)     # FM en una línia!
carrier.play()
graph.wait()
```

`signalflow` ja implementa l'arquetip UGen de manera optimitzada — a audio rate de veritat, mostra a mostra, en C++ per sota — sense l'aliasing de la nostra simplificació per blocs. Passar la sortida d'un node com a paràmetre d'un altre (com fem aquí amb `modulator` dins `SineOscillator(440 + modulator)`) es diu **input audio-rate** en la seva documentació — exactament el concepte de "UGen alimenta el paràmetre d'un altre" que hem vist avui. No és exercici avui — només contrast: la mateixa idea (mateix `I`) que acabem de construir a mà, ja resolta professionalment.

**Avantatge addicional respecte a `pyo`:** `signalflow` és una llibreria activament mantinguda (última versió: 2025) amb suport real per a Python recent i Apple Silicon, mentre que `pyo` (l'opció considerada inicialment) no s'ha actualitzat per a versions de Python posteriors a la 3.11 i té problemes coneguts d'instal·lació en Mac M-series.

---

## 8. Taula resum

| Concepte | Sessió 8 | Sessió 9 |
|---|---|---|
| Mètode principal | `generate(duration)` | `process(n_samples)` |
| Estat de fase | No (sempre `t=0`) | Sí (`self.phase` persistent) |
| Envolvent | Calcula tota la corba d'un cop | Avança per `stage`, reacciona a `note_on`/`note_off` |
| Ús típic | So offline (Colab) | So en temps real (Thonny) |
| Nou aquí | — | LFO, FM, integració MIDI temps real, tast `signalflow` |
