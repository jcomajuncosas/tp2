# Challenges opcionals — Sessió 10
### Per a qui vulgui aprofundir fora de classe (NO avaluat, NO contingut de classe)

---

## Challenge 1 — FM mostra a mostra (la versió "correcta")

A S9 vam veure que `fm_synth()` actualitza `carrier.freq` només un cop per bloc, cosa que introdueix sota-mostreig real (Sessió 9, Secció 4). Implementa una versió que actualitzi la freqüència del portador **mostra a mostra**:

```python
def fm_synth_mostra_a_mostra(carrier_freq, mod_freq, I, duration, sample_rate=44100):
    n_total = int(sample_rate * duration)
    sortida = np.zeros(n_total)

    mod_phase = 0.0
    car_phase = 0.0
    mod_phase_inc = 2 * np.pi * mod_freq / sample_rate

    for i in range(n_total):
        mod_val = np.sin(mod_phase)
        car_freq_instant = carrier_freq + I * mod_val
        car_phase_inc = 2 * np.pi * car_freq_instant / sample_rate

        sortida[i] = np.sin(car_phase)

        mod_phase = (mod_phase + mod_phase_inc) % (2 * np.pi)
        car_phase = (car_phase + car_phase_inc) % (2 * np.pi)

    return sortida
```

**Compara-ho** amb `fm_synth()` de la Sessió 9 (la versió per blocs): cronometra totes dues (esperaràs que aquesta sigui molt més lenta — relaciona-ho amb el profiling d'avui) i escolta la diferència sonora amb `I` gran. Hi ha menys "soroll" o artefactes en la versió mostra a mostra?

---

## Challenge 2 — Ampliar el kit de percussió

El repte d'avui té només Kick i Hi-hat. Amplia'l amb un tercer so:

- **Snare:** combina `Oscillator` (un to greu curt, com el kick però més agut, ~180Hz) AMB `Noise` (per donar-li la part "sorollosa" característica d'una caixa) — multiplica'ls per la mateixa envolvent o suma'ls
- Nota MIDI suggerida: 38 (Acoustic Snare, GM)

**Pregunta per reflexionar:** per què creus que una caixa (snare) combina un component tonal i un component de soroll, mentre que el kick (Challenge previ) és només tonal i el hi-hat només soroll?

---

## Challenge 3 — Explorar els exemples oficials de `signalflow`

Instal·la `signalflow` (`python3 -m venv signalflow-env && source signalflow-env/bin/activate && pip3 install signalflow`) i explora els exemples oficials del repositori:
`https://github.com/ideoforms/signalflow/tree/master/examples`

> **Si tens problemes d'instal·lació** (especialment amb Conda/Miniforge/Anaconda instal·lat, o errors de `ModuleNotFoundError`/`NameError` estranys després d'instal·lar-ho), consulta la guia de troubleshooting completa, validada en un cas real, a `05_sintesi/sessio09_fm_synth/recursos/challenges.md` (Challenge 2).

Tria almenys 2 exemples de categories diferents (per exemple: control bàsic, FM, granulació, MIDI) i:
1. Executa'ls i escolta el resultat
2. Identifica quins nodes de `signalflow` fan servir que NO hem vist a classe
3. Per a un d'ells, intenta relacionar-lo amb algun concepte del nostre curs (UGen, control rate, envolvents...) — encara que `signalflow` ho resolgui d'una manera molt més sofisticada

---

## Challenge 4 — Implementar el "cor" de string ensemble amb signalflow

Reprodueix i amplia l'exemple de la Secció 5 d'`exemples.py`:

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
graph.wait()
```

**Experimenta:**
- Canvia el nombre de veus (4, 8, 16...) — com afecta el "gruix" del so?
- Canvia la freqüència del `SineLFO` (més ràpida, més lenta) i el rang `min`/`max` del `delay_time` — quan deixa de sonar "chorus" i comença a sonar com un altre efecte (flanger, vibrato de pitch)?
- Prova substituir `OneTapDelay` per `CombDelay` (que té `feedback`) — quina diferència sents?
- Consulta la pàgina de "Multichannel nodes" (`https://signalflow.dev/node/multichannel/`) — com modificaries el codi perquè cada veu del cor surti per un canal diferent en lloc de sumar-les totes a mono?

---

## Per què aquests challenges queden fora de classe

El docent ha decidit explícitament no incloure'ls a la Sessió 10: el Challenge 1 reforça el profiling d'avui però amb una implementació més llarga; el 2 amplia el repte amb un so addicional que no aporta cap concepte nou; el 3 i el 4 conviden a explorar `signalflow` lliurement, cosa que requereix temps d'instal·lació i exploració personal que no encaixa en una sessió de consolidació ja densa. Són aquí per a qui vulgui aprofundir-hi pel seu compte, especialment de cara al projecte final.
