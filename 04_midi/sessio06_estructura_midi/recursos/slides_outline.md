# Slides — Bloc 4a, Sessió 6
### Estructura MIDI i `mido`

> **Instruccions de muntatge:** Mateix estil. Temps estimat: 20 min (hi ha contingut conceptual nou — el protocol MIDI).

---

### Diapositiva 1 — Portada
**Bloc 4 — MIDI i control musical (I)**
*El protocol MIDI i `mido`*

---

### Diapositiva 2 — Canvi de domini
- Sessions 1-5: treballàvem amb **so** (arrays de mostres, callbacks d'àudio)
- Sessions 6-7: treballem amb **instruccions musicals** (MIDI)
- MIDI no és so — és el protocol que diu "toca aquesta nota, amb aquesta intensitat, ara"
- El so el genera qui rep les instruccions (DAW, sintetitzador, sistema operatiu...)
- Analogia: MIDI és la partitura; WAV és la gravació de la interpretació

---

### Diapositiva 3 — Una mica d'història
- 1983: primer estàndard MIDI, revolució per a músics i productors
- Protocol serial de 31.25 kbps — senzill i robust
- 2020: MIDI 2.0 (més resolució, bidireccional) — però MIDI 1.0 segueix sent universal
- Per qué és important per a sonòlegs: tots els DAWs, sintetitzadors, controladors i instal·lacions sonores el parlen

---

### Diapositiva 4 — Els números MIDI que cal saber
- **Nota:** 0–127. Do central = 60. Cada octava = 12 semitots
- **Velocity:** 0–127. 0 = silenci, 127 = màxim. Equivalent a la dinàmica
- **Canal:** 0–15. 16 canals independents. Canal 9 = percussió (General MIDI)
- **Tempo:** en microsegons per beat. 120bpm = 500.000 µs/beat
- Visual: teclat de piano amb números MIDI marcats

---

### Diapositiva 5 — Connexió directa amb TP1
- A TP1: `piano(60, 0.7, 0.25)` — la mateixa idea
- `piano(nota, velocity_0_1, durada_segons)`
- Amb MIDI: `note_on(note=60, velocity=89, time=0)` + `note_off(note=60, time=240 ticks)`
- La **lògica** és exactament la mateixa — canvia el protocol i la unitat de temps
- La llibreria `musica` de TP1 era un embolcall al voltant de MIDI (o similar)

---

### Diapositiva 6 — Estructura d'un fitxer MIDI
- Un fitxer `.mid` conté **tracks** (pistes)
- Cada track conté una seqüència de **missatges** ordenats en el temps
- Cada missatge té un **delta time** (ticks des del missatge anterior)
- Diagrama: fitxer → tracks → missatges → (type, data, delta_time)

---

### Diapositiva 7 — Delta time: el concepte clau
- `time` en mido = ticks DES DEL MISSATGE ANTERIOR (no des de l'inici)
- `time=0` = "al mateix instant que l'anterior"
- `time=480` = "480 ticks després de l'anterior"
- Error típic: posar `time=480` al `note_on` en lloc del `note_off`
- → Resultat: silenci de 1 negra ABANS de la nota, nota instantània

---

### Diapositiva 8 — `mido`: llegir un fitxer
```python
import mido
mid = mido.MidiFile('example_scale.mid')
for track in mid.tracks:
    for msg in track:
        print(msg)
```
- Demo en directe: llegir `example_scale.mid` i veure els missatges
- Identificar: `note_on`, `note_off`, `set_tempo`, `end_of_track`

---

### Diapositiva 9 — `mido`: crear un fitxer
```python
mid = mido.MidiFile(ticks_per_beat=480)
track = mido.MidiTrack()
track.append(mido.Message('note_on',  note=60, velocity=80, time=0))
track.append(mido.Message('note_off', note=60, velocity=0,  time=480))
mid.tracks.append(track)
mid.save('el_meu.mid')
```
- Demo: crear una escala i obrir-la al DAW o reproduir-la amb `mid.play()`

---

### Diapositiva 10 — Ticks ↔ segons
- `ticks_per_beat`: resolució temporal (habitual: 480)
- `tempo`: µs per beat (120bpm = 500.000)
- `durada_s = ticks × tempo / ticks_per_beat / 1_000_000`
- `mido` permet iterar el fitxer sencer amb temps en segons: `for msg in mid:`

---

### Diapositiva 11 — MIDI en temps real (demo si funciona)
```python
print(mido.get_input_names())   # ports disponibles
with mido.open_input() as port:
    for msg in port:
        print(msg)
```
- macOS: IAC Driver (Audio MIDI Setup)
- Windows: LoopMIDI
- Ho veiem si els ports funcionen — sense pressió
- Preview projecte final: el looper i el drum-replacement reben MIDI en temps real

---

### Diapositiva 12 — Preview Sessió 7
- `mido` és potent però verbose (gestionar ticks manualment és pesat)
- `pretty_midi`: capa d'alt nivell sobre MIDI — notes en segons, instruments per nom
- Sessió 7: construirem un arpegiador i un seqüenciador amb `pretty_midi` en molt menys codi
- La mateixa idea que `soundfile` (Sessió 2) vs. generar arrays manualment
