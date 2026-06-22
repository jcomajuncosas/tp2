# Challenges opcionals — Sessió 9
### Per a qui vulgui aprofundir fora de classe (NO avaluat, NO contingut de classe)

---

## Challenge 1 — Rendiment: sample-by-sample vs. buffered

A `exemples.py` i `assignment.py`, `Oscillator.process(n_samples)` genera un **bloc sencer** de cop fent servir NumPy vectoritzat (`np.arange`, `np.sin` sobre tot el bloc).

**Repte:** implementa una versió alternativa que generi el so **mostra a mostra**, amb un bucle `for` explícit en Python pur (sense vectorització):

```python
def process_sample_by_sample(self, n_samples):
    out = np.zeros(n_samples)
    for i in range(n_samples):
        out[i] = np.sin(self.phase)
        self.phase += 2 * np.pi * self.freq / self.sample_rate
        self.phase %= 2 * np.pi
    return out
```

Cronometra totes dues versions amb `time.perf_counter()` generant, per exemple, 10 segons de so (440100 mostres) i compara:

```python
import time

t0 = time.perf_counter()
# ... versió vectoritzada ...
t1 = time.perf_counter()
print(f"Vectoritzada: {t1-t0:.4f}s")

t0 = time.perf_counter()
# ... versió sample-by-sample ...
t1 = time.perf_counter()
print(f"Sample-by-sample: {t1-t0:.4f}s")
```

**Pregunta per reflexionar:** quants cops més lenta és la versió sample-by-sample? Per què creus que NumPy vectoritzat és tan més ràpid? Relaciona-ho amb per què el temps real (blocsize ~512, no 1 mostra) és una solució de compromís pràctica.

---

## Challenge 2 — Implementació completa amb `signalflow`

A classe només hem vist `signalflow` com a tast de 10 minuts, sense instal·lar-lo ni executar-lo. Aquest challenge és fer-ho de debò.

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
pip3 install numpy sounddevice matplotlib mido python-rtmidi
```
Alternativa més senzilla: deixa el Thonny normal per als exercicis del curs, i només canvia a l'intèrpret de `signalflow-env` quan vulguis treballar específicament amb aquesta llibreria.

---

**Repte 1 — Reproduir la FM de la sessió, amb `signalflow`:**
```python
from signalflow import *

graph = AudioGraph()

I = 200
modulator = SineOscillator(80) * I
carrier = SineOscillator(440 + modulator)
carrier.play()

graph.wait()
```
Compara aquest so amb el de `fm_synth()` de `assignment.py` (mateixos `carrier_freq=440`, `mod_freq=80`, `I=200`). Sonen igual? Si no, per què creus que hi ha diferències (pensa en la diferència entre actualitzar `freq` un cop per bloc vs. mostra a mostra real — el nostre `fm_synth()` sota-mostreja el modulador, `signalflow` no).

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
La pròpia llibreria té un exemple oficial de teclat MIDI: `examples/midi-keyboard-example.py` al repositori (https://github.com/ideoforms/signalflow), que combina `MidiNoteToFrequency(note)` amb `ADSREnvelope(..., gate=gate)` — fent servir `mido`, la mateixa llibreria MIDI que ja coneixeu de les Sessions 6-7. Instal·la `mido` i `python-rtmidi` (`pip install mido python-rtmidi`), descarrega l'exemple, i compara la quantitat de codi necessària amb la nostra integració manual (Secció 6 de `exemples.py`).

---

## Per què aquests dos challenges queden fora de classe

El docent ha decidit explícitament no incloure aquests dos punts com a contingut obligatori de la Sessió 9: el primer és interessant per entendre rendiment però no imprescindible per avançar amb l'arquitectura UGen; el segon requereix instal·lació i temps d'exploració que no encaixen en una sessió ja densa. Són aquí per a qui vulgui aprofundir-hi pel seu compte.
