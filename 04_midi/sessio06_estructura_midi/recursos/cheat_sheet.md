# Cheat sheet — Sessió 6
### Bloc 4a: Estructura MIDI i `mido`

> **Instruccions de muntatge:** Crea un Google Doc i penja'l com a "book" al tema "Sessió 6".

---

## 1. Què és MIDI?

MIDI (Musical Instrument Digital Interface, 1983) **no és so** — és un protocol de missatges que descriuen accions musicals:

- "Toca la nota 60 amb velocity 80 al canal 1"
- "Atura la nota 60 al canal 1"
- "Canvia el tempo a 120 bpm"

Un fitxer `.mid` és una seqüència d'aquests missatges amb timestamps. El so el genera qui rep els missatges (un sintetitzador, un DAW, el sistema operatiu...).

**Contrast amb WAV:** un `.wav` és el so ja generat (mostres d'àudio). Un `.mid` és la partitura (instruccions). El mateix `.mid` pot sonar molt diferent segons qui l'interpreta.

---

## 2. Els números MIDI essencials

| Concepte | Rang | Notes |
|---|---|---|
| Nota (note number) | 0–127 | 60 = Do central (C4), +1 = semitò |
| Velocity | 0–127 | 0 = silenci, 127 = màxim |
| Canal | 0–15 | 16 canals independents; canal 9 = percussió |
| Tempo | microsegons/beat | `mido.bpm2tempo(120)` = 500000 |
| Ticks | — | Subdivisió interna del temps; `ticks_per_beat` defineix la resolució |

**Fórmula nota ↔ nom:**
```python
notes = ['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa',
         'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']
nom = notes[midi_num % 12]
octava = midi_num // 12 - 1
```

**Connexió amb TP1:** a TP1 usàveu `piano(60, 0.7, 0.25)` — nota, velocity (0–1), durada. MIDI fa el mateix però amb velocity 0–127 i el temps mesurat en ticks, no en segons.

---

## 3. `mido`: llegir un fitxer MIDI

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

## 4. Tipus de missatges MIDI principals

```python
# note_on: comença una nota
msg = mido.Message('note_on', channel=0, note=60, velocity=80, time=0)

# note_off: atura una nota (o note_on amb velocity=0)
msg = mido.Message('note_off', channel=0, note=60, velocity=0, time=480)

# control_change: potenciòmetres, pedals, etc.
msg = mido.Message('control_change', channel=0, control=7, value=100, time=0)

# program_change: canvia l'instrument (General MIDI)
msg = mido.Message('program_change', channel=0, program=40, time=0)  # violí

# MetaMessage: informació del fitxer (no sona)
tempo_msg = mido.MetaMessage('set_tempo', tempo=500000, time=0)  # 120 bpm
```

**El camp `time`:** en un fitxer MIDI, `time` és el **delta time** — ticks *des del missatge anterior*, no des de l'inici. `time=0` vol dir "al mateix instant que l'anterior".

---

## 5. `mido`: crear un fitxer MIDI

```python
import mido

mid = mido.MidiFile(ticks_per_beat=480)
tempo = mido.bpm2tempo(120)  # 500000 µs/beat

# Track de metadades
meta = mido.MidiTrack()
meta.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
mid.tracks.append(meta)

# Track de notes
track = mido.MidiTrack()
quarter = 480  # 1 negra = ticks_per_beat

for note in [60, 64, 67, 72]:  # acord Do major arpegiado
    track.append(mido.Message('note_on',  channel=0, note=note, velocity=80, time=0))
    track.append(mido.Message('note_off', channel=0, note=note, velocity=0,  time=quarter))

mid.tracks.append(track)
mid.save('el_meu_midi.mid')
```

---

## 6. Ticks ↔ segons

```python
# De ticks a segons
tempo = 500000  # µs per beat (120 bpm)
ticks_per_beat = 480

def ticks_to_seconds(ticks, tempo, ticks_per_beat):
    return ticks * tempo / ticks_per_beat / 1_000_000

# Exemple: 480 ticks (1 negra) a 120bpm = 0.5s
print(ticks_to_seconds(480, 500000, 480))  # 0.5

# mido té una funció per iterar amb temps absolut en segons:
for msg in mid:  # itera el fitxer sencer (no track a track)
    print(msg.time, msg)  # msg.time és en SEGONS aquí
```

---

## 7. MIDI en temps real amb `mido` (demo)

```python
import mido

# Llistar ports disponibles
print("Inputs:", mido.get_input_names())
print("Outputs:", mido.get_output_names())

# Rebre missatges d'un teclat MIDI
with mido.open_input() as port:
    for msg in port:
        print(msg)
        if msg.type == 'note_on' and msg.velocity > 0:
            print(f"Nota: {msg.note}, Velocity: {msg.velocity}")
```

**Nota macOS:** per enviar MIDI a un DAW cal crear un port virtual IAC (Audio MIDI Setup → MIDI Studio → IAC Driver). A Windows: LoopMIDI. Veurem-ho a classe si el temps ho permet.

---

## 8. Connexió amb TP1 i preview

| TP1 (`musica`) | TP2 (`mido`) |
|---|---|
| `piano(60, 0.7, 0.25)` | `note_on(note=60, velocity=89, time=0)` + `note_off(time=quarter)` |
| `for note in pattern:` | `for note in pattern: track.append(...)` |
| `wait(0.5)` | `time=ticks` (delta time entre missatges) |
| `while True:` loop infinit | `for msg in port:` loop de missatges en temps real |

La lògica és idèntica — canvia el protocol i la granularitat del temps.

**Sessió 7:** amb `pretty_midi` podrem fer tot això expressant les durades directament en segons (sense gestionar ticks manualment), i generarem seqüències musicals molt més ràpidament.
