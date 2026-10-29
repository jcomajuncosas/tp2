# Cheat sheet — Sessió 6
### Bloc 4a: Estructura MIDI i `mido`

---

## 0. Colab o Thonny?

| Si treballes amb... | Eina | Per què |
|---|---|---|
| **Fitxers** `.mid` (llegir, analitzar, crear) | **Colab** | No hi ha rellotge ni hardware; podem dibuixar i escoltar al moment |
| **Ports** MIDI (teclat, DAW, sintetitzador) | **Thonny** | Els ports són dispositius del teu ordinador, com la targeta de so |

És el mateix criteri que fem servir des de la Sessió 1: offline → Colab, temps real → Thonny.

---

## 1. Què és MIDI?

MIDI (Musical Instrument Digital Interface, 1983) **no és so**: és un protocol de missatges que descriuen accions musicals.

- "Toca la nota 60 amb velocity 80 al canal 1"
- "Atura la nota 60 al canal 1"
- "Canvia el tempo a 120 bpm"

Un fitxer `.mid` és una seqüència d'aquests missatges amb el seu temps. El so el genera qui els rep: un sintetitzador, un DAW, el sistema operatiu...

**Contrast amb WAV:** un `.wav` és el so ja generat (mostres d'àudio). Un `.mid` és la partitura (instruccions). El mateix `.mid` pot sonar molt diferent segons qui l'interpreta.

---

## 2. Els números MIDI essencials

| Concepte | Rang | Notes |
|---|---|---|
| Nota (note number) | 0–127 | 60 = Do central (C4), +1 = un semitò |
| Velocity | 0–127 | 0 = silenci, 127 = màxim |
| Canal | 0–15 | 16 canals independents; canal 9 = percussió (General MIDI) |
| Tempo | microsegons/beat | `mido.bpm2tempo(120)` = 500000 |
| Ticks | — | Subdivisió interna del temps; `ticks_per_beat` defineix la resolució |

**Nota ↔ nom:**
```python
noms = ['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa',
        'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']
nom = noms[midi_num % 12]
octava = midi_num // 12 - 1
```

**Connexió amb TP1:** a TP1 fèieu `piano(60, 0.7, 0.25)`: nota, velocity (0–1), durada. MIDI diu el mateix, però amb velocity 0–127 i el temps mesurat en ticks, no en segons.

---

## 3. Llegir un fitxer

```python
import mido

mid = mido.MidiFile('example_scale.mid')
print(f"Tracks: {len(mid.tracks)}")
print(f"Ticks per beat: {mid.ticks_per_beat}")
print(f"Durada total: {mid.length:.2f} s")

for i, track in enumerate(mid.tracks):
    print(f"\nTrack {i}: '{track.name}' — {len(track)} missatges")
    for msg in track:
        print(f"  {msg}")
```

---

## 4. Tipus de missatges principals

```python
mido.Message('note_on',  channel=0, note=60, velocity=80, time=0)    # obre una nota
mido.Message('note_off', channel=0, note=60, velocity=0,  time=480)  # la tanca
# Atenció: molts fitxers tanquen les notes amb note_on de velocity 0

mido.Message('control_change', channel=0, control=7, value=100, time=0)  # potenciòmetres, pedals
mido.Message('program_change', channel=0, program=40, time=0)            # instrument GM (40 = violí)

mido.MetaMessage('set_tempo', tempo=500000, time=0)  # informació del fitxer: no sona
```

---

## 5. Delta time: la idea clau

`msg.time` = ticks **des del missatge anterior** (no des de l'inici).

| # | missatge | nota | `time` | tick absolut |
|---|---|---|---|---|
| 1 | note_on | Do4 | 0 | 0 |
| 2 | note_on | Mi4 | **0** | 0 ← acord |
| 3 | note_off | Do4 | 480 | 480 |
| 4 | note_off | Mi4 | 0 | 480 |
| 5 | note_on | Sol4 | **240** | 720 ← silenci abans |
| 6 | note_off | Sol4 | 240 | 960 |

- **Acord** → diversos `note_on` seguits amb `time=0`
- **Silenci** → el temps va al `note_on` que ve després
- **Durada** → el temps va al missatge que tanca la nota

Per saber el tick absolut, **acumula**:
```python
tick = 0
for msg in track:
    tick += msg.time      # a TOTS els missatges, també els meta
```

**Errors típics:**

| Codi | Resultat |
|---|---|
| `note_on time=480` + `note_off time=480` | silenci d'una negra abans de cada nota |
| `note_on time=480` + `note_off time=0` | cada nota dura **0**: el fitxer no sona |

---

## 6. Crear un fitxer

```python
mid = mido.MidiFile(ticks_per_beat=480)

meta = mido.MidiTrack()
meta.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(120), time=0))
mid.tracks.append(meta)

track = mido.MidiTrack()
for note in [60, 64, 67, 72]:                 # arpegi de Do major, negres
    track.append(mido.Message('note_on',  note=note, velocity=80, time=0))
    track.append(mido.Message('note_off', note=note, velocity=0,  time=480))
track.append(mido.MetaMessage('end_of_track', time=0))
mid.tracks.append(track)
mid.save('el_meu_midi.mid')
```

---

## 7. Ticks ↔ segons

```python
segons = mido.tick2second(480, 480, 500000)   # ticks, ticks_per_beat, tempo → 0.5
ticks  = mido.second2tick(0.5, 480, 500000)   # → 480.0
# a mà: segons = ticks * tempo / ticks_per_beat / 1_000_000
```

Si iteres **el fitxer sencer** (no un track), `mido` barreja tots els tracks i dona `msg.time` en **segons**. Però continua sent un **delta**:
```python
ara = 0.0
for msg in mid:
    ara += msg.time       # ara sí: segons des de l'inici
```

---

## 8. MIDI en temps real (Thonny)

Dues llibreries, cadascuna per a una feina (Thonny → Tools → Manage packages → `rtmidi2`):
- **`rtmidi2`** obre els ports i rep/envia **bytes**: `[144, 60, 100]`
- **`mido`** els tradueix: `mido.Message.from_bytes([144, 60, 100])` → `note_on note=60 velocity=100`

```python
import rtmidi2, mido

entrada = rtmidi2.MidiIn()
print(entrada.ports)          # llista de ports: s'obren pel NÚMERO
entrada.open_port(0)          # (el nom canvia segons l'idioma del sistema)
```

Dues maneres de rebre:
```python
# 1) Preguntant: el programa mira si ha arribat res (com block=False a TP1)
dades = entrada.get_message()          # bytes, o None si no hi ha res
if dades is not None:
    print(mido.Message.from_bytes(dades))

# 2) Callback: el sistema crida la teva funció a cada missatge, des d'un altre fil
def quan_arriba(dades, timestamp):
    print(mido.Message.from_bytes(dades))
entrada.callback = quan_arriba
```

| | Callback d'**àudio** (S04) | Callback **MIDI** |
|---|---|---|
| Qui el crida | El rellotge de la targeta, regularment | Cada esdeveniment, quan arriba |
| Què ha de fer | Omplir un buffer abans d'un deadline | Reaccionar (anotar estat) |
| Si va lent | Dropout | Retard i jitter |

**Enviar:**
```python
sortida = rtmidi2.MidiOut()
sortida.open_port(0)
sortida.send_message(mido.Message('note_on', note=60, velocity=80).bytes())
```
`mid.play()` espera entre els missatges d'un fitxer però **no fa so**: cal enviar-los a un port.

**Sense teclat?** macOS: activa el IAC Driver (Audio MIDI Setup → MIDI Studio). És un cable virtual: el que hi envies torna a entrar. Windows: loopMIDI.
**On sona?** Windows: port "Microsoft GS Wavetable Synth". macOS: IAC + GarageBand o un DAW.

---

## 9. Connexió amb TP1 i preview

| TP1 | TP2 (`mido`) |
|---|---|
| `piano(60, 0.7, 0.25)` | `note_on(note=60, velocity=89, time=0)` + `note_off(time=...)` |
| `for note in pattern:` | `for note in pattern: track.append(...)` |
| `wait(0.5)` | el `time` (delta) del missatge següent |
| `block=False` | `entrada.get_message()` |

**Sessió 7:** amb `pretty_midi` escriurem les notes directament amb inici i final en segons, sense gestionar ticks a mà.
