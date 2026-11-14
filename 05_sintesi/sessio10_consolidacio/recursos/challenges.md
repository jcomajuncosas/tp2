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

## Annex — Instal·lar i provar `signalflow` (abans era el Challenge 2 de la Sessió 9)

Instruccions completes per instal·lar `signalflow` (incloent-hi els problemes reals trobats en un Mac M-series) i tres reptes per començar. Els Challenges 3 i 4 d'aquesta sessió en depenen.

### Instal·lació bàsica

```bash
python3 -m venv signalflow-env
source signalflow-env/bin/activate
pip3 install signalflow
signalflow test   # hauria de sonar un to de prova
```
Documentació completa: https://signalflow.dev/. Funciona correctament en Mac Apple Silicon (M1/M2/M3), Linux i Windows amb Python 3.8-3.13.

### ⚠️ Si tens Conda/Miniforge/Anaconda instal·lat (problema real, confirmat)

Si el teu prompt mostra `(base)` abans del nom d'usuari (per exemple `(base) usuari@ordinador %`), tens Conda actiu de fons, i el procediment bàsic d'amunt **probablement et fallarà** de maneres confuses. Aquest és exactament el cas que es va trobar i resoldre durant la preparació d'aquest curs en un Mac M-series real — la solució completa, pas a pas:

**Problema 1 — `pip3 install signalflow` diu "No matching distribution found"**
Comprova la versió de Python que estàs fent servir:
```bash
python3 --version
```
`signalflow` només té wheels fins a Python 3.13 (a data d'avui). Si el teu Python és 3.14 o superior (per exemple, si fas servir directament el Python intern de Thonny), no hi haurà cap versió compatible. Cal crear el `venv` amb un Python 3.13 o anterior explícit — busca'n un:
```bash
ls /opt/homebrew/bin/python3.13       # si tens Homebrew
ls /opt/homebrew/bin/python3*         # per veure totes les versions disponibles
```

**Problema 2 — El `venv` "es crea bé" però Thonny diu `ModuleNotFoundError: No module named 'signalflow'`**
Causa: per defecte, `python3 -m venv` crea l'executable `python3` del `venv` com un **symlink** cap al Python que el va crear. Si aquell Python ve de Conda, Xcode Command Line Tools, o una cadena de symlinks llarga, Thonny pot acabar seguint l'enllaç fins a l'intèrpret "real" final i **sortir del context del `venv`** — perdent l'accés als paquets instal·lats. Comprova-ho:
```bash
ls -la signalflow-env/bin/python3
```
Si veus una fletxa cap a una ruta llarga fora de `signalflow-env` (per exemple cap a `/Applications/Xcode.app/...` o `/opt/homebrew/Cellar/...`), aquest és el problema.

**Solució (validada):** primer, surt explícitament de Conda (pot caldre fer-ho més d'un cop si hi ha entorns niats):
```bash
conda deactivate
conda deactivate
echo $CONDA_DEFAULT_ENV   # hauria de sortir buit
```
Després, recrea el `venv` amb l'opció `--copies`, que fa una **còpia real** de l'intèrpret en lloc d'un symlink — això evita el problema independentment de si Conda interfereix o no:
```bash
rm -rf signalflow-env
/opt/homebrew/bin/python3.13 -m venv signalflow-env --copies
source signalflow-env/bin/activate
ls -la signalflow-env/bin/python3
```
Aquesta vegada hauria de mostrar un fitxer real (sense `->`). Si és així, instal·la i comprova:
```bash
pip3 install signalflow
python3 -c "import signalflow; print(signalflow.__file__)"
```

**Problema 3 (parany subtil) — `import signalflow` falla amb un `NameError` estrany en lloc de `ModuleNotFoundError`**
Si veus un error com `NameError: name 'AudioGraph' is not defined` apuntant a un fitxer `signalflow.py` a la teva carpeta personal (`~/signalflow.py` o similar), **tens un fitxer propi amb el mateix nom que el paquet**, fent-li "ombra" — Python sempre busca primer al directori actual abans que als paquets instal·lats. Solució: renombra el teu fitxer (no cal esborrar-lo):
```bash
mv ~/signalflow.py ~/signalflow_prova_propia.py
```

### Configurar Thonny perquè faci servir aquest `venv`

Un cop el `venv` funciona correctament des de terminal:
1. Esbrina la ruta exacta: `which python3` (amb el `venv` actiu) — hauria de donar una ruta del tipus `/Users/usuari/signalflow-env/bin/python3`
2. A Thonny: `Tools` → `Options...` → pestanya `Interpreter`
3. Selecciona `Alternative Python 3 interpreter or virtual environment`
4. Introdueix la ruta (o usa `Find executable...`) i accepta
5. Comprova amb una Shell nova: `import signalflow` no hauria de donar cap error

**Important:** amb aquest canvi, Thonny deixa d'usar el seu Python intern i passa a usar el del `venv`. Si vols continuar fent els exercicis normals del curs des del mateix Thonny sense canviar d'intèrpret, cal instal·lar-hi també la resta de llibreries:
```bash
pip3 install numpy scipy sounddevice matplotlib mido rtmidi2
```
Alternativa més senzilla: deixa el Thonny normal per als exercicis del curs, i només canvia a l'intèrpret de `signalflow-env` quan vulguis treballar específicament amb aquesta llibreria.

---

**Repte 1 — Reproduir la FM de la Sessió 9, amb `signalflow`:**
```python
from signalflow import *

graph = AudioGraph()

fm = 80
I = 2.5                                         # índex de Chowning: excursió = I × fm = 200 Hz
modulator = SineOscillator(fm) * (I * fm)
carrier = SineOscillator(440 + modulator)
carrier.play()

graph.wait()
```
Compara-ho amb el teu `fm_synth(440, 80, 2.5, ...)` de la Sessió 9 (la versió amb `process_freqs`). Han de sonar igual: totes dues actualitzen la freqüència a cada mostra. I amb la versió per blocs (`vibrato(440, 80, 200, ...)`)?

**Repte 2 — Envolvent ADSR amb `signalflow`:**
```python
graph = AudioGraph()

gate = 1
env = ADSREnvelope(attack=0.01, decay=0.1, sustain=0.6, release=0.3, gate=gate)
osc = SineOscillator(440) * env
osc.play()

graph.wait(1.0)
env.set_input("gate", 0)   # equivalent al nostre note_off()
graph.wait(1.0)
```
Compara amb la classe `Envelope` pròpia: en lloc de mètodes `note_on()`/`note_off()`, `signalflow` fa servir un paràmetre `gate` (1=premuda, 0=alliberada) que es pot canviar en qualsevol moment amb `set_input()`. Quines diferències d'API trobes? Quins avantatges/inconvenients té cada disseny?

**Repte 3 (obert) — MIDI amb `signalflow`:**
La pròpia llibreria té un exemple oficial de teclat MIDI: `examples/midi-keyboard-example.py` al repositori (https://github.com/ideoforms/signalflow), que combina `MidiNoteToFrequency(note)` amb `ADSREnvelope(..., gate=gate)` — fent servir `mido`, la mateixa llibreria MIDI que ja coneixeu de les Sessions 6-7. Descarrega l'exemple, i compara la quantitat de codi necessària amb la nostra integració manual (el `Reproductor` i el callback de l'`assignment.py` de la Sessió 9). Atenció: l'exemple oficial obre el port amb `mido.open_input`, que necessita `python-rtmidi` (sense versió per a Python 3.13); adapta'l amb `rtmidi2` i `mido.Message.from_bytes`, com a la Sessió 7.

---

## Per què aquests challenges queden fora de classe

El docent ha decidit explícitament no incloure'ls a la Sessió 10: el Challenge 1 reforça el profiling d'avui però amb una implementació més llarga; el 2 amplia el repte amb un so addicional que no aporta cap concepte nou; el 3 i el 4 conviden a explorar `signalflow` lliurement, cosa que requereix temps d'instal·lació i exploració personal que no encaixa en una sessió de consolidació ja densa. Són aquí per a qui vulgui aprofundir-hi pel seu compte, especialment de cara al projecte final.
