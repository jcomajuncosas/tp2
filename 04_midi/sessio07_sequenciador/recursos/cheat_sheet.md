# Cheat sheet — Sessió 7
### Bloc 4b: seqüenciació MIDI en temps real i timing precís

---

## 1. Per què avui tot és a Thonny

| Si la feina és... | Entorn |
|---|---|
| Fitxers `.mid` sense temps real: llegir, escriure, dibuixar (Sessió 6) | Colab o Thonny |
| So en directe, ports MIDI, timing precís (avui) | **Thonny** |

Colab corre en un servidor de Google: no té el teu altaveu ni el teu rellotge. Si una sessió necessita temps real, **tota** la sessió es fa a Thonny, encara que també desem algun fitxer.

Avui necessites, a la mateixa carpeta: `sinte.py`, `exemples.py`, `assignment.py`. L'únic paquet nou és `pretty_midi` (Thonny → Tools → Manage packages).

---

## 2. `pretty_midi`: notes completes, temps en segons

```python
import pretty_midi

pm = pretty_midi.PrettyMIDI(initial_tempo=120)
piano = pretty_midi.Instrument(program=0)        # 0 = piano (General MIDI)

nota = pretty_midi.Note(velocity=80, pitch=60, start=0.0, end=0.5)
piano.notes.append(nota)

pm.instruments.append(piano)
pm.write('resultat.mid')
```

Cada nota porta el seu `start` i `end` **en segons des de l'inici**. `initial_tempo` només serveix per a la graella de ticks del fitxer: no mou les notes. Si vols que el tempo compti, calcula les durades a partir del tempo (una negra = `60 / tempo` segons).

---

## 3. Delta contra absolut

| | `mido` (Sessió 6) | `pretty_midi` (avui) |
|---|---|---|
| Nivell | missatges (`note_on`, `note_off`) | notes completes |
| Temps | **delta**: des del missatge anterior | **absolut**: des de l'inici |
| On és la 3a nota? | suma de les tres primeres deltes | `notes[2].start` |
| Ús típic | protocol, ports, temps real | composició, anàlisi, seqüenciació |

---

## 4. Un arpegiador

```python
def arpegiador(acord, n_repeticions, mode='up'):
    if mode == 'up':
        seq = acord
    elif mode == 'down':
        seq = acord[::-1]                   # [::-1]: la llista al revés
    elif mode == 'updown':
        seq = acord + acord[::-1][1:-1]     # [1:-1]: sense el primer ni l'últim
    else:
        print("Mode desconegut:", mode)
        seq = []
    return seq * n_repeticions              # llista * n: repetida n vegades

arpegiador([60, 64, 67], 2, 'updown')       # [60, 64, 67, 64, 60, 64, 67, 64]
```

---

## 5. El sinte d'avui: `sinte.py`

```python
from sinte import SinteSimple, espera_fins

synth = SinteSimple()                # SinteSimple(bpm_click=120): amb metrònom
synth.note_on(60, 90)                # nota, velocity
time.sleep(0.5)
synth.note_off(60)
synth.close()                        # sempre al final
```

Per dins és el callback del Bloc 3:
1. El fil principal **no toca l'àudio**: `note_on` i `note_off` només afegeixen un encàrrec a una llista.
2. El callback, a cada bloc de 64 mostres (1,45 ms), recull els encàrrecs nous, suma totes les veus (sinus amb decaïment) i escriu el buffer.
3. Si hi ha metrònom, el click és un bucle de `P` mostres: `ona_click[(mostra) % P]`. El marca **la targeta de so** comptant mostres, no Python. Per això serveix de referència.

---

## 6. Tocar en directe: dues estratègies

### Estratègia A — `time.sleep(durada)`

```python
for nota in notes:
    synth.note_on(nota.pitch)
    time.sleep(nota.end - nota.start)
    synth.note_off(nota.pitch)
```

Cada espera comença quan acaba l'anterior. `time.sleep` mai dorm menys del demanat i sovint una mica més (en un MacBook s'han mesurat uns 4 ms per crida). **L'error s'acumula:** 32 notes × 4 ms = 124 ms de retard, més d'una semicorxera a 140 bpm.

### Estratègia B — temps objectiu absolut

```python
t_inici = time.perf_counter()
for i in range(n_notes):
    espera_fins(t_inici + i * pas)       # l'objectiu es calcula des de l'INICI
    synth.note_on(84)
```

Amb `pretty_midi` l'objectiu ja ve donat: `t_inici + nota.start`.

L'objectiu de cada nota no depèn de quan ha acabat l'espera anterior: si una nota surt tard, **la següent torna al seu lloc**. L'error no s'acumula.

### `espera_fins`: l'espera híbrida

```python
def espera_fins(t_objectiu):
    falta = t_objectiu - time.perf_counter()
    if falta > 0.002:
        time.sleep(falta - 0.002)        # 1) dorm fins a 2 ms abans
    while time.perf_counter() < t_objectiu:
        pass                             # 2) els darrers 2 ms, espera activa
```

- L'espera activa (`while ... pass`) és molt precisa, però mentre dura la CPU treballa i, sobretot, **el callback d'àudio no pot executar-se** (secció 7).
- Dormint fins a 2 ms abans, tenim la precisió de l'espera activa sense bloquejar res.

---

## 7. La trampa: el GIL i el termini del callback

Python només deixa executar codi a **un fil alhora** (el GIL, *Global Interpreter Lock*). El callback d'àudio és un altre fil: si el fil principal està calculant sense parar (espera activa llarga, un càlcul pesant en Python), el callback ha d'esperar torn.

- El callback té un **termini**: 1,45 ms per bloc. Si arriba tard, la targeta sona silenci → espetecs.
- Python no ho veu: el seu rellotge diu que tot va a temps.
- Mesurat en un MacBook: 2 s d'espera activa pura → **1,67 s d'àudio perdut**. Amb `espera_fins` → 0 ms.

Regla pràctica: el fil principal ha de **dormir** mentre espera, i la feina pesant s'ha de fer abans de tocar o a trossos petits.

---

## 8. Quan triar cada enfocament

| Situació | Enfocament |
|---|---|
| Generar un `.mid` (sense sonar en directe) | `pretty_midi`, sense preocupar-se del timing |
| Demo curta, tempo lent | Estratègia A (`time.sleep`) |
| Seqüenciador en directe, tempo mitjà o ràpid | Estratègia B amb `espera_fins` |
| Molta feina de càlcul entre notes | Fer-la abans de tocar, o dins el callback a la mostra exacta (challenge 3) |
| Canviar el patró mentre sona | Un fil dedicat al rellotge (no l'implementem) |
| Seguir el tempo d'un DAW o d'una placa | MIDI Clock: 24 missatges per negra (challenge 2) |

---

## 9. Connexió amb TP1 i amb el Bloc 5

| TP1 | Avui |
|---|---|
| `for note in pattern: piano(...)` | `for pitch in seq: instrument.notes.append(Note(...))` |
| Mòdul `%` | accent a la primera nota de cada grup: `i % cada == 0` |
| Performance de live-coding | el vostre seqüenciador: la mateixa idea, amb un rellotge precís |

**Bloc 5:** el callback de `sinte.py` és el germà petit del sintetitzador que construireu (oscil·ladors, ADSR, FM), controlat per les mateixes notes que ja sabeu generar.
