# Slides — Bloc 5c, Sessió 10
### Consolidació de síntesi: profiling, kit de percussió, tast ampliat de signalflow

> **Instruccions de muntatge:** Mateix estil. Temps estimat: 12-15 min (sessió de consolidació; el pes principal és el repte, no la teoria).

---

### Diapositiva 1 — Portada
**Bloc 5 — Síntesi sonora (III): Consolidació**
*Profiling, kit de percussió, un altre tipus de síntesi*

---

### Diapositiva 2 — On érem
- Bloc 5: `Oscillator`, `Envelope`, arquetip UGen (`process()`), vibrato, FM, integració MIDI temps real
- Dues coses van quedar pendents de quantificar a S9: per què processar en blocs, i quan llegir un modulador a baixa resolució és segur
- Avui: mesurem-ho de debò, i ho posem tot junt en un projecte

---

### Diapositiva 3 — Profiling: vectoritzat vs. sample-by-sample
```python
t0 = time.perf_counter()
out_vec = osc.process(n_samples)          # NumPy, tot el bloc de cop
t_vec = time.perf_counter() - t0

t0 = time.perf_counter()
out_sbs = osc.process_sample_by_sample(n_samples)  # bucle Python
t_sbs = time.perf_counter() - t0
```
- Demo en directe: mesurar 5 segons d'àudio amb tots dos mètodes
- 🎤 *Pregunta: quants cops més lent esperes que sigui el bucle Python?*

---

### Diapositiva 4 — Resultat del profiling
- Típicament 10-20x més lent el sample-by-sample
- Resultats numèrics pràcticament idèntics (error ~1e-11, soroll de punt flotant)
- Gràfic de barres comparatiu
- Per què: cada crida individual a una funció té un cost fix que es multiplica per cada mostra

---

### Diapositiva 5 — Quan llegir un modulador a baixa resolució és segur
- Recordatori S9: `vibrato()`/`fm_synth()` llegeixen el modulador a "1 valor/bloc"
- Mesurem l'error real (RMS) comparant amb llegir-lo a resolució completa
- 🎤 *Pregunta: a quina freqüència del modulador creus que l'error comença a créixer molt?*

---

### Diapositiva 6 — Resultat: error segons la freqüència del modulador
| Freq. modulador | Error RMS |
|---|---|
| 5 Hz | ~0.15 (petit) |
| 20 Hz | ~0.56 |
| 80 Hz | ~1.0 (saturat) |
| 200 Hz | ~1.0 (saturat) |
- Gràfic de barres amb la transició
- Confirma objectivament la distinció vibrato/FM de S9

---

### Diapositiva 7 — El repte d'avui: kit de percussió sintètica
- Combina TOT el Bloc 5 en un sol projecte
- Dos sons nous: **Kick** (Oscillator amb pitch-drop) i **Hi-hat** (Noise)
- Disparats per esdeveniments tipus MIDI, amb el mapa General MIDI real (36=Kick, 42=Hi-Hat)

---

### Diapositiva 8 — `Noise`: l'UGen més senzill possible
```python
class Noise:
    def process(self, n_samples):
        return np.random.uniform(-1.0, 1.0, n_samples)
```
- Cap estat — a diferència d'`Oscillator` (`self.phase`) i `Envelope` (`self.stage`)
- 🎤 *Pregunta: segueix sent un UGen vàlid, encara que no recordi res?*
- Resposta esperada: sí — només cal que implementi `process()`

---

### Diapositiva 9 — `Kick`: pitch-drop amb un sol oscil·lador
```python
freqs = freq_end + (freq_start - freq_end) * np.exp(-5 * progress)
self.osc.freq = float(freqs[-1])
```
- La freqüència baixa ràpidament (p.ex. 150Hz → 40Hz en 50ms)
- Demo en directe: escoltar el kick sol
- Truc clàssic dels sintetitzadors de bateria electrònics

---

### Diapositiva 10 — Demo: kick + hi-hat sonant
- Escoltar els dos sons del kit
- 🎤 *Pregunta: amb quins dos components de S8/S9 es construeix cadascun?*
- Resposta esperada: Oscillator+Envelope (kick), Noise+Envelope (hi-hat)

---

### Diapositiva 11 — Workshop: completeu `assignment.py`
- `Noise.process()`, `Kick.process()`, `percussion_kit()`
- Mateix patró de sempre: esquelet + TODO + autotests
- ~70 minuts — és el cos de la sessió

---

### Diapositiva 12 — Tast ampliat de `signalflow`: un altre tipus de síntesi
```python
freqs = [220 * (1 + random.uniform(-0.01, 0.01)) for _ in range(8)]
veus = [SineOscillator(f) for f in freqs]
cor = veus[0]
for v in veus[1:]: cor = cor + v
lfo = SineLFO(0.25, min=0.005, max=0.02)
chorus = cor + OneTapDelay(cor, delay_time=lfo, max_delay_time=0.03) * 0.6
```
- NO és una classe calculada a mà — és apilar moltes veus simples + un chorus CONSTRUÏT amb el mateix patró d'avui (LFO → delay_time)
- Referència: Solina/ARP String Ensemble (1974-81), string ensemble analògic clàssic
- NO és exercici avui — exemples oficials per explorar pel vostre compte (i `signalflow` funciona bé en Mac Apple Silicon, a diferència de `pyo`)

---

### Diapositiva 13 — Taula resum: tot el Bloc 5
| Concepte | Sessió | Idea central |
|---|---|---|
| Oscillator, Envelope, SamplePlayer | S8 | Components separats d'un sintetitzador |
| `process(n_samples)`, UGen | S9 | Estat persistent, blocs continus |
| Vibrato, FM, MIDI temps real | S9 | Control rate vs. audio rate, integració callback |
| Noise, Kick, profiling | S10 | Consolidació + mesures reals |

---

### Diapositiva 14 — Preview Bloc 6
- Bloc 6: FFT i extracció de features (centroid, MFCC, ZCR)
- Passem de GENERAR so a ANALITZAR-LO
- Connexió: el mateix so que hem après a sintetitzar, ara el descomponem en les seves freqüències
