# Cheat sheet — Sessió 7
### Bloc 4b: `pretty_midi`, seqüenciador/arpegiador i timing precís

> **Instruccions de muntatge:** Crea un Google Doc i penja'l com a "book" al tema "Sessió 7".

---

## 1. `pretty_midi`: MIDI d'alt nivell

A diferència de `mido` (missatges individuals, ticks, delta time), `pretty_midi` treballa amb **notes completes** i **temps en segons**:

```python
import pretty_midi

pm = pretty_midi.PrettyMIDI()
piano = pretty_midi.Instrument(program=0)  # 0 = Acoustic Grand Piano (General MIDI)

nota = pretty_midi.Note(velocity=80, pitch=60, start=0.0, end=0.5)
piano.notes.append(nota)

pm.instruments.append(piano)
pm.write('resultat.mid')
```

Cap gestió de ticks, cap delta time — cada nota porta el seu `start` i `end` en segons directament. És molt més ràpid per a composició algorísmica.

---

## 2. Comparació `mido` vs `pretty_midi`

| | `mido` | `pretty_midi` |
|---|---|---|
| Nivell | Baix (missatges individuals) | Alt (notes completes) |
| Temps | Ticks + delta time | Segons (start, end) |
| Ús típic | Protocol, temps real, ports | Composició, anàlisi musical |
| Crear una nota | 2 missatges (on/off) + gestió de ticks | 1 objecte `Note(start, end)` |

**Connexió amb TP1:** `pretty_midi.Note(velocity, pitch, start, end)` s'assembla molt a `piano(pitch, velocity, duration)` — és, de fet, més proper a la llibreria `musica` que `mido`.

---

## 3. Crear una seqüència amb `pretty_midi`

```python
pm = pretty_midi.PrettyMIDI(initial_tempo=120)
instrument = pretty_midi.Instrument(program=0)

pattern = [60, 64, 67, 72]
note_duration = 0.25

t = 0.0
for pitch in pattern:
    note = pretty_midi.Note(velocity=90, pitch=pitch, start=t, end=t+note_duration)
    instrument.notes.append(note)
    t += note_duration

pm.instruments.append(instrument)
pm.write('sequencia.mid')
```

---

## 4. Un arpegiador simple

```python
def arpegiador(acord, n_repeticions, note_duration, mode='up'):
    """Genera una llista de notes a partir d'un acord."""
    if mode == 'up':
        seq = acord
    elif mode == 'down':
        seq = acord[::-1]
    elif mode == 'updown':
        seq = acord + acord[::-1][1:-1]

    return seq * n_repeticions

# Exemple: Do major arpegiado, amunt i avall, 3 cops
acord = [60, 64, 67]
notes = arpegiador(acord, n_repeticions=3, note_duration=0.2, mode='updown')
```

---

## 5. Escoltar MIDI: dues vies

**A Colab**, amb `pretty_midi.fluidsynth()` (ja usat a Sessió 6):
```python
audio = pm.fluidsynth(fs=44100)
Audio(audio, rate=44100)
```

**A Thonny**, amb la classe `MidiSynth` (proporcionada, veure `midisynth.py`):
```python
from midisynth import MidiSynth
synth = MidiSynth()
synth.note_on(60, velocity=80)
time.sleep(0.5)
synth.note_off(60)
synth.close()
```

`MidiSynth` és un embolcall de FluidSynth que reprodueix directament per l'altaveu, **sense necessitar IAC Driver ni LoopMIDI**. Internament fa exactament el que fa `pm.fluidsynth()` a Colab, però en temps real.

---

## 6. El problema del timing precís en Python

Quan vols reproduir una seqüència MIDI **en temps real** (no generar un fitxer), cal esperar el temps just entre nota i nota. Python no és un sistema de temps real — hi ha diverses estratègies, de pitjor a millor:

### Estratègia A — `time.sleep()` (la més senzilla, la menys precisa)

```python
for nota, durada in seqüencia:
    synth.note_on(nota)
    time.sleep(durada)
    synth.note_off(nota)
```

**Problema:** `time.sleep()` no és precís (pot dormir més del demanat) i **l'error s'acumula**: si cada `sleep` es retarda 2ms, després de 50 notes ja portes 100ms de desfasament. A tempos ràpids o patrons densos (bateria), és audible.

### Estratègia B — `time.perf_counter()` amb compensació d'error acumulat

```python
import time

t_inici = time.perf_counter()
t_acumulat = 0.0

for nota, durada in seqüencia:
    t_objectiu = t_inici + t_acumulat
    while time.perf_counter() < t_objectiu:
        pass  # espera activa (busy-wait)

    synth.note_on(nota)
    t_acumulat += durada

print("Fet")
```

**Per qué és millor:** en lloc d'esperar "durada" cada vegada (que acumula error), calculem el **temps objectiu absolut** des de l'inici, i esperem fins arribar-hi. Qualsevol petit retard en una nota NO s'acumula a les següents — es corregeix sol. `time.perf_counter()` també té més resolució que `time.sleep()`.

**Cost:** el busy-wait (`while ... pass`) consumeix CPU activament mentre espera. Acceptable per a un sol fil de seqüenciació, problemàtic si en tens molts.

### Altres estratègies (només per conèixer-les — no les implementarem)

- **Thread dedicat al timing:** per a seqüenciadors interactius (canviar el patró mentre sona), es necessita un fil separat que gestiona el rellotge, comunicant-se amb el fil principal via `queue.Queue`. Més robust, més complex.
- **MIDI Clock:** un missatge MIDI especial (`clock`) que sincronitza diversos dispositius/programes al mateix tempo — és com fan els DAWs professionals per sincronitzar-se entre ells o amb hardware extern. Python pot actuar com a "clock slave" (seguir el tempo d'un DAW) o "master" (marcar el tempo a altres). És el que permetria, per exemple, que el teu seqüenciador Python toqui perfectament sincronitzat amb Ableton Live. No ho implementarem ara — la configuració (ports virtuals, sincronització) és un projecte en si mateix.

---

## 7. Quan triar cada enfocament

| Situació | Enfocament |
|---|---|
| Generar un fitxer `.mid` (sense reproduir en directe) | `pretty_midi`, sense preocupar-se del timing |
| Demo simple, tempo lent, poces notes | Estratègia A (`time.sleep`) |
| Seqüenciador/bateria en temps real, tempo mitjà-alt | Estratègia B (`perf_counter` + compensació) |
| Seqüenciador interactiu (canviar patró en directe) | Thread dedicat (no implementat aquí) |
| Sincronitzar amb un DAW extern | MIDI Clock (no implementat aquí) |

---

## 8. Connexió amb TP1 i tancament del Bloc 4

| TP1 | TP2 Bloc 4 |
|---|---|
| `piano(pitch, vel, dur)` | `pretty_midi.Note(velocity, pitch, start, end)` |
| `for note in pattern: piano(...)` | `for pitch in pattern: instrument.notes.append(Note(...))` |
| Llibreria `musica` (abstracció pròpia) | `mido` (baix nivell) + `pretty_midi` (alt nivell) |
| Performance de live-coding (Sessió 10, TP1) | El vostre seqüenciador d'avui — la mateixa lògica, ara amb MIDI real |

**Preview Bloc 5:** el `MidiSynth` d'avui rep notes i les sintetitza amb un soundfont (timbres pregravats). Al Bloc 5 construirem el **nostre propi** sintetitzador (oscil·ladors, ADSR, FM) — controlat per les mateixes notes MIDI que ja sabeu generar.
