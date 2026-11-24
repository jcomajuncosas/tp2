# Challenges opcionals — Sessió 10
### Per a qui vulgui anar més enllà (no avaluat)

Tots tres parteixen del teu `assignment.py` d'avui.

---

## Challenge 1 — Un hi-hat a la tecla 42

La tecla 42 és el *closed hi-hat* al mapa General MIDI. Un hi-hat sintètic és **soroll** amb una envolvent molt curta.

1. Escriu una classe `Noise` amb `process(n_samples)`, que retorni soroll blanc entre −1 i 1 (`np.random.uniform`). Fixa't: és el primer UGen del curs **sense estat**. No ha de recordar res entre blocs. Per què l'`Oscillator` sí que en necessita, i el soroll no?
2. Escriu una classe `HiHat` amb la mateixa interfície que el `Kick` (`note_on(velocity)`, `note_off()`, `process(n)`), feta amb un `Noise` i una `Envelope` sense sustain.
3. Fes-la sonar a la tecla 42. Caldrà que l'`Instrument` i `gestiona` la coneguin.

Per pensar: una caixa (*snare*) combina una part tonal (com el kick, però més aguda) i una de soroll. Te'n surts amb el que ja tens?

---

## Challenge 2 — `process_freqs` sense bucle

`process_freqs` té un bucle de Python mostra a mostra. La fase de cada mostra és la fase inicial **més la suma de tots els increments anteriors**, i NumPy té una funció que fa justament sumes acumulades: `np.cumsum`.

1. Escriu `process_freqs_rapid(self, freqs)` sense cap bucle. Ha de donar **el mateix resultat** que la teva (comprova-ho amb `np.allclose` sobre uns quants blocs seguits, no només el primer: la fase ha de continuar bé d'un bloc a l'altre).
2. Fes que la `VeuFM` el faci servir i torna a executar `mesura_cost`. Quantes vegades més ràpid és? Quantes veus hi cabrien ara?

---

## Challenge 3 — Polifonia

Ara la veu toca una sola nota. Fes una classe `Polifonic` amb una **llista** de 4 `VeuFM` (és el challenge de la S09, ara amb teclat):
- cada nota nova va a la veu següent (l'operador `%` és el teu amic);
- un final de nota ha d'aturar la veu que toca **aquella** nota (el que has après a la Part E);
- `process(n)` suma les 4 veus.

Pensa on ha de viure ara la comprovació de la Part E: amb 4 veus, `gestiona` ja no pot preguntar a *una* veu quina nota toca. Si el `Polifonic` té `note_on`, `note_off` i `process`, l'`Instrument` el pot fer servir com si fos una sola veu. Toca un acord!

---

## Annex — Instal·lar i provar `signalflow` (abans era el Challenge 2 de la Sessió 9)

Instruccions completes per instal·lar `signalflow` (incloent-hi els problemes reals trobats en un Mac M-series) i tres reptes per començar.

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
