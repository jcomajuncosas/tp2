# Slides — Bloc 5b, Sessió 9
### Arquitectura UGen, control rate (vibrato), FM synthesis (timbre), integració temps real + MIDI

> **Instruccions de muntatge:** Mateix estil. Temps estimat: ~20 min (coincidint amb el bloc "Mini-teoria" de `guia.md`, 0:08–0:28). Sessió DENSA: aquestes diapositives cobreixen la teoria i una primera passada de cada demo; l'aprofundiment pràctic de cada demo es fa després amb `exemples.py` (Thonny), no cal allargar-se aquí en cada execució.

---

### Diapositiva 1 — Portada
**Bloc 5 — Síntesi sonora (II)**
*Arquitectura UGen, vibrato, FM, MIDI en temps real*

---

### Diapositiva 2 — On érem (Sessió 8)
```python
osc.generate(duration)        # tot l'array d'un sol cop
env.generate(note_duration)   # calcula tota la corba ADSR, sabent la durada per endavant
```
- Calen saber la durada per endavant
- Avui: què passa quan NO la sabem (temps real)?

---

### Diapositiva 3 — El problema
```python
osc = Oscillator(freq=440)
bloc1 = osc.generate(0.1)
bloc2 = osc.generate(0.1)
junts = np.concatenate([bloc1, bloc2])
```
- Demo en directe: escoltar `junts` — hi ha un click audible
- 🎤 *Pregunta: per què? Cada crida de `generate()` torna a començar a `t=0`*

---

### Diapositiva 4 — La pregunta clau
- I si, en lloc de demanar "genera'm X segons", li demanéssim "dona'm el SEGÜENT tros, i recorda on et quedaves"?
- Calen dues coses: (1) un mètode pensat per blocs, (2) estat que persisteixi entre crides

---

### Diapositiva 5 — L'arquetip UGen
```python
def process(self, n_samples):
    ...
    self.phase = ...   # es guarda per a la PROPERA crida
    return out
```
- `process(n_samples) -> array`, amb `self.phase` persistent
- "UGen" (*unit generator*): interfície comuna per a qualsevol component d'un sintetitzador modular

---

### Diapositiva 6 — Connexió amb Max/Pd
- Un patch és exactament això: objectes que reben/envien blocs de senyal contínuament, cadascun amb el seu propi estat
- `process()` és el "cable" entre objectes, en codi
- **Nota de disseny:** `Oscillator`, `LFO`, `Envelope` comparteixen `process()` per CONVENI, sense herència formal — el grup només té TP1 com a base d'OOP

---

### Diapositiva 7 — Demo en directe: sense click
```python
osc = Oscillator(freq=440)
bloc1 = osc.process(4410)
bloc2 = osc.process(4410)
junts = np.concatenate([bloc1, bloc2])
```
- Mateixos dos blocs d'abans, ara amb `process()` — escoltar la diferència
- 🎤 *Hauria de sonar com una ona contínua, sense salt de fase*

---

### Diapositiva 8 — Control rate: la idea real (en un motor DSP)
- Un generador de control (LFO, envolupant) calcula els seus propis valors a una freqüència molt inferior a la d'àudio
- Exemple: 100-200 valors/segon, en lloc dels 44100/s que calen per al so directe
- El paràmetre que controla (vibrato, tremolo...) no necessita més resolució que aquesta

---

### Diapositiva 9 — ⚠️ El nostre LFO és un híbrid pedagògic
```python
class LFO:
    # MATEIXA lògica que Oscillator — calcula a 44100Hz
    # NO genera realment menys valors
    ...
```
- Per simplicitat, `LFO` reutilitza exactament el codi d'`Oscillator`
- "Fingim" control rate llegint només l'última mostra de cada bloc (`lfo_out[-1]`)
- Important dir-ho explícitament: el codi NO fa el que fa un generador de control real

---

### Diapositiva 10 — Vibrato: per què l'híbrid funciona igualment
```python
lfo_out = lfo.process(n)
osc.freq = base_freq + depth * lfo_out[-1]
sortida[i:i+n] = osc.process(n)
```
- El LFO es mou lent (5Hz) — el seu valor amb prou feines canvia dins un bloc
- Llegir-ne només 1 valor/bloc NO perd informació rellevant (NO és estalvi de CPU — calculem el bloc sencer igualment)
- Referència real: el Yamaha DX7 té un LFO global enrutable a vibrato (pitch) i/o tremolo (amplitud)

---

### Diapositiva 11 — Demo en directe: vibrato
- Escoltar la mateixa nota, amb i sense vibrato (`depth=0` vs. `depth=6`)
- 🎤 *Pregunta: què sents? És "la mateixa nota" ondulant, o un timbre nou?*
- Resposta esperada: la mateixa nota, ondulant suaument

---

### Diapositiva 12 — FM synthesis: i si el modulador es mou ràpid?
- Mateix patró de codi que el vibrato — un `process()` alimenta el paràmetre d'un altre
- Però ara: modulador a freqüència d'àudio (80Hz), no de control
- Llegir-lo només 1 cop/bloc ja NO és segur — introdueix sota-mostreig/aliasing real

---

### Diapositiva 13 — FM: el mateix patró, motor diferent
```python
mod_out = modulator.process(n)
carrier.freq = carrier_freq + I * mod_out[-1]
sortida[i:i+n] = carrier.process(n)
```
- `I` = índex de modulació (notació estàndard: Chowning, DX7) — no `beta`
- Literalment el mateix codi que el vibrato — només canvia `mod_freq` (ara audio rate) i la magnitud d'`I`
- ⚠️ Simplificació: `carrier.freq` s'actualitza 1 cop/bloc, no mostra a mostra — artefactes coneguts (Challenge: versió correcta)

---

### Diapositiva 14 — Demo en directe: FM
- Escoltar amb `I` petit vs. `I` gran
- 🎤 *Pregunta: encara reconeixes "la mateixa nota"?*
- Resposta esperada: no — és un timbre nou, no vibrato

---

### Diapositiva 15 — Vibrato vs. FM: la mateixa eina, dos resultats
| | Modulador | Amplada de banda | Es percep com |
|---|---|---|---|
| Vibrato | 5Hz (lent) | ~20 Hz | la mateixa nota, ondulant |
| FM | 80Hz (audio) | ~480 Hz | un timbre nou |
- El que distingeix "control" de "timbre" no és si el senyal "és" d'un tipus o l'altre — és si la freqüència del modulador permet llegir-lo a baixa resolució sense perdre informació

---

### Diapositiva 16 — Envelope, també redissenyada
- `generate(note_duration)` (S8) necessitava saber la durada per endavant
- En temps real no ho sabem — calen `note_on()` / `note_off()` + un `stage` intern (`'idle'|'attack'|'decay'|'sustain'|'release'`)
- `note_on()` dispara l'Attack; `note_off()` dispara el Release, sigui quin sigui el moment

---

### Diapositiva 17 — Tot junt: el callback
```python
def synth_callback(outdata, frames, time, status):
    wave = synth_osc.process(frames)
    env_curve = synth_env.process(frames)
    outdata[:, 0] = (wave * env_curve).astype('float32')
```
- Mateix patró de callback que la Sessió 5 (`sd.OutputStream`)
- Ara alimentat per les nostres classes UGen, disparades per MIDI (`note_on`/`note_off`)

---

### Diapositiva 18 — Demo: teclat MIDI en directe (o simulació)
- Tocar el sintetitzador propi en temps real amb un controlador MIDI connectat
- Sense teclat a l'aula: seqüència de notes programada (mateix patró, sense port MIDI físic)

---

### Diapositiva 19 — Tast de signalflow
```python
I = 200
modulator = SineOscillator(80) * I
carrier = SineOscillator(440 + modulator)
carrier.play()
```
- Mateixa FM, en 3 línies — i sense els artefactes de la nostra simplificació per blocs
- "Vosaltres ja sabeu què hi ha a dins"
- Distingeix `Oscillator` de `LFO` com a classes separades — la distinció que hem treballat avui, ja integrada a la llibreria
- NO és exercici avui — Challenge opcional si es vol instal·lar i provar de debò (funciona bé en Mac Apple Silicon, a diferència d'altres opcions més antigues)

---

### Diapositiva 20 — Connexió amb TP1 i preview
- Recuperem el fil de classes (poc treballades a TP1) amb un cas d'ús real: estat persistent entre crides
- Connexió amb Sessió 5: "el buffer global de l'eco hauria estat millor com a classe" — avui ho fem amb tot un sintetitzador
- **Sessió 10:** consolidació de tot el Bloc 5 (Oscillator + Envelope + UGen + vibrato + FM + MIDI temps real), amb un mini-repte més ampli
