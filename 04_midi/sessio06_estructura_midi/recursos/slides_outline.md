# Slides — Bloc 4a, Sessió 6
### Estructura MIDI i `mido`

> **Instruccions de muntatge:** Mateix estil (referència: Sessió 8). Temps estimat: 20 min de teoria + 10 min de l'exercici en paper (diapositives 8–9).

---

### Diapositiva 1 — Portada
**Bloc 4 — MIDI i control musical (I)**
*El protocol MIDI i `mido`*

---

### Diapositiva 2 — Canvi de domini
- Sessions 1-5: treballàvem amb **so** (arrays de mostres, callbacks d'àudio)
- Sessions 6-7: treballem amb **instruccions musicals** (MIDI)
- MIDI no és so: és el protocol que diu "toca aquesta nota, amb aquesta intensitat, ara"
- El so el genera qui rep les instruccions (DAW, sintetitzador, sistema operatiu...)
- Analogia: MIDI és la partitura; WAV és la gravació de la interpretació

---

### Diapositiva 3 — Colab o Thonny?
- **Fitxers** `.mid` → **Colab**: no hi ha rellotge ni hardware, i podem dibuixar i escoltar al moment
- **Ports** MIDI (teclat, DAW) → **Thonny**: són dispositius del vostre ordinador, com la targeta de so
- El criteri de sempre: offline → Colab, temps real → Thonny
- 🎤 *Avui: tot el workshop a Colab. Els ports, en una demo final a Thonny.*

---

### Diapositiva 4 — Una mica d'història
- 1983: primer estàndard MIDI, una revolució per a músics i productors
- Protocol sèrie de 31,25 kbps: senzill i robust
- 2020: MIDI 2.0 (més resolució, bidireccional), però MIDI 1.0 continua sent universal
- Per què us importa: tots els DAW, sintetitzadors, controladors i instal·lacions sonores el parlen

---

### Diapositiva 5 — Els números MIDI que cal saber
- **Nota:** 0–127. Do central = 60. Cada octava = 12 semitons
- **Velocity:** 0–127. 0 = silenci, 127 = màxim. L'equivalent de la dinàmica
- **Canal:** 0–15. 16 canals independents. Canal 9 = percussió (General MIDI)
- **Tempo:** en microsegons per beat. 120 bpm = 500.000 µs/beat
- Visual: teclat de piano amb els números MIDI marcats

---

### Diapositiva 6 — Connexió amb TP1
- A TP1: `piano(60, 0.7, 0.25)` → nota, velocity (0–1), durada en segons
- Amb MIDI: `note_on(note=60, velocity=89, time=0)` + `note_off(note=60, time=240)`
- La **lògica** és la mateixa: canvien el rang de la velocity i la unitat de temps
- Una nota ara són **dos** missatges: un l'obre i un altre la tanca
- 🎤 *Quina informació ens amagava `piano()`?*

---

### Diapositiva 7 — Estructura d'un fitxer MIDI
- Un fitxer `.mid` conté **tracks** (pistes)
- Cada track és una seqüència de **missatges** ordenats en el temps
- Cada missatge porta un **delta time**: ticks des del missatge anterior
- Diagrama: fitxer → tracks → missatges → (tipus, dades, delta time)

---

### Diapositiva 8 — ✏️ En paper: dels deltes al piano roll
Taula a la pissarra (o fotocòpia). 1 casella de la quadrícula = 1 corxera = 240 ticks.

| # | missatge | nota | time |
|---|---|---|---|
| 1 | note_on | Do4 | 0 |
| 2 | note_on | Mi4 | 0 |
| 3 | note_off | Do4 | 480 |
| 4 | note_off | Mi4 | 0 |
| 5 | note_on | Sol4 | 240 |
| 6 | note_off | Sol4 | 240 |
| 7 | note_on | Do5 | 0 |
| 8 | note_off | Do5 | 960 |

- Escriviu el **tick absolut** de cada missatge i dibuixeu el piano roll
- 🎤 *On és l'acord? On és el silenci? Quins missatges els fan possibles?*
- Solució (per al docent): ticks 0, 0, 480, 480, 720, 960, 960, 1920. Acord Do-Mi de 0 a 480; silenci de 480 a 720; Sol de 720 a 960; Do5 de 960 a 1920
- Ho comprovem a la secció 2 dels patches

---

### Diapositiva 9 — ✏️ En paper: al revés
- Piano roll a la pissarra: Re4 negra · silenci de corxera · acord Fa4-La4 corxera · Do5 blanca
- Escriviu la taula de missatges amb el seu `time`
- 🎤 *Quin `time` porta el `note_on` que ve després del silenci?*
- Solució: on Re4 0 · off Re4 480 · on Fa4 **240** · on La4 0 · off Fa4 240 · off La4 0 · on Do5 0 · off Do5 960
- Això és exactament la Part 4 del workshop

---

### Diapositiva 10 — Delta time: dos errors típics
- **Error 1:** `note_on time=480` + `note_off time=480` → silenci d'una negra *abans* de cada nota
- **Error 2:** `note_on time=480` + `note_off time=0` → cada nota dura **0 ticks**: el fitxer no sona
- 🎤 *L'error 1 és sempre un error? (No: és com s'escriu un silenci.)*
- Ho escoltem a la secció 5 dels patches

---

### Diapositiva 11 — `mido`: llegir un fitxer
```python
import mido
mid = mido.MidiFile('example_scale.mid')
for track in mid.tracks:
    for msg in track:
        print(msg)
```
- Demo en directe: llegir `example_scale.mid` i mirar-ne els missatges
- Identificar: `note_on`, `note_off`, `set_tempo`, `end_of_track`

---

### Diapositiva 12 — `mido`: crear un fitxer
```python
mid = mido.MidiFile(ticks_per_beat=480)
track = mido.MidiTrack()
track.append(mido.Message('note_on',  note=60, velocity=80, time=0))
track.append(mido.Message('note_off', note=60, velocity=0,  time=480))
mid.tracks.append(track)
mid.save('el_meu.mid')
```
- Demo: crear un arpegi i escoltar-lo a Colab
- Per enviar-lo a un DAW o synth cal un port (diapositiva 14)

---

### Diapositiva 13 — Ticks ↔ segons
- `ticks_per_beat`: resolució temporal (habitual: 480)
- `tempo`: µs per beat (120 bpm = 500.000)
- `segons = ticks × tempo / ticks_per_beat / 1.000.000` → `mido.tick2second()`
- `for msg in mid:` dona `msg.time` en segons, però **encara delta**: cal acumular per tenir el temps des de l'inici

---

### Diapositiva 14 — MIDI en temps real (demo a Thonny)
- Dues llibreries, dues feines: `rtmidi2` obre els ports i mou els **bytes**; `mido` els tradueix a missatges
- El que viatja pel cable: `[144, 60, 100]` → `mido.Message.from_bytes(...)` → `note_on note=60 velocity=100`
- Dues maneres de rebre:
  - **preguntant** (`get_message()`): el programa mira si ha arribat res, com el `block=False` de TP1
  - **callback**: el sistema crida la teva funció quan arriba cada missatge, des d'un altre fil
- **Callback MIDI vs. callback d'àudio (S04):**
  - àudio → el crida el rellotge, regularment, i ha d'omplir un buffer abans d'un deadline
  - MIDI → el crida cada esdeveniment, quan arriba, i només ha de reaccionar
- Arquitectura d'un sintetitzador: el callback MIDI escriu l'estat (nota, gate) i el callback d'àudio el llegeix
- Sense teclat: el IAC Driver de macOS és un cable virtual (el que surt torna a entrar) → `prova_iac()`
- Els ports s'obren pel **número**: el nom canvia amb l'idioma del sistema
- Preview del projecte final: els instruments reben MIDI en temps real

---

### Diapositiva 15 — Preview Sessió 7
- `mido` és potent però verbós: gestionar ticks a mà és pesat
- `pretty_midi`: capa d'alt nivell, amb notes en segons i instruments per nom
- Sessió 7: un arpegiador i un seqüenciador amb molt menys codi
- La mateixa idea que `soundfile` (Sessió 2) vs. generar els arrays a mà
