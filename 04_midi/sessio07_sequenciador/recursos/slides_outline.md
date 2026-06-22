# Slides — Bloc 4b, Sessió 7
### `pretty_midi`, seqüenciador/arpegiador i timing precís

> **Instruccions de muntatge:** Mateix estil. Temps estimat: 20 min.

---

### Diapositiva 1 — Portada
**Bloc 4 — MIDI i control musical (II)**
*`pretty_midi`, seqüenciador i timing precís*

---

### Diapositiva 2 — De `mido` a `pretty_midi`
- Sessió 6: `mido` — baix nivell, ticks, delta time
- Avui: `pretty_midi` — alt nivell, notes amb start/end en segons
- Mateixa idea que `soundfile` (Sessió 2): una capa que estalvia gestió manual
- `pretty_midi.Note(velocity, pitch, start, end)` ≈ `piano(pitch, vel, dur)` de TP1

---

### Diapositiva 3 — Crear una nota amb pretty_midi
```python
pm = pretty_midi.PrettyMIDI()
instrument = pretty_midi.Instrument(program=0)  # 0 = piano

nota = pretty_midi.Note(velocity=80, pitch=60, start=0.0, end=0.5)
instrument.notes.append(nota)

pm.instruments.append(instrument)
pm.write('resultat.mid')
```
- Sense ticks, sense delta time — directe en segons

---

### Diapositiva 4 — El sintetitzador d'avui: MidiSynth
- Us donem fet un sintetitzador MIDI (`midisynth.py`) basat en FluidSynth
- Rep notes i les sintetitza **directament a l'altaveu** — sense IAC, sense LoopMIDI
- A Colab: `MidiSynthRender` (genera array, com `pm.fluidsynth()`)
- A Thonny: `MidiSynth` (temps real)
- És com el "sinte MIDI" que potser heu fet servir a Pure Data

---

### Diapositiva 5 — L'arpegiador
```python
def arpegiador(acord, n_repeticions, mode='up'):
    if mode == 'up':
        seq = acord
    elif mode == 'down':
        seq = acord[::-1]
    elif mode == 'updown':
        seq = acord + acord[::-1][1:-1]
    return seq * n_repeticions
```
- Connexió amb TP1: és el mateix patró que generar seqüències amb llistes i bucles
- Demo: escoltar els 3 modes amb el mateix acord

---

### Diapositiva 6 — El problema del timing en temps real
- Generar un fitxer `.mid`: cap problema de timing (es desa, no es reprodueix "en directe")
- Reproduir en directe (seqüenciador, bateria): cal esperar el temps just entre notes
- Python NO és un sistema de temps real — `time.sleep()` no és perfecte
- Avui: comparem dues estratègies, NO les implementem totes — és per conèixer-les

---

### Diapositiva 7 — Estratègia A: time.sleep() (la més senzilla)
```python
for nota, durada in seqüencia:
    synth.note_on(nota)
    time.sleep(durada)
    synth.note_off(nota)
```
- Problema: l'error de cada `sleep` s'acumula nota rere nota
- A tempos ràpids (bateria, 140bpm+): audible i molest
- Demo: simulació de timestamps (gràfic) mostrant la deriva acumulada

---

### Diapositiva 8 — Estratègia B: temps objectiu absolut
```python
t_inici = time.perf_counter()
t_acumulat = 0.0

for nota, durada in seqüencia:
    t_objectiu = t_inici + t_acumulat
    while time.perf_counter() < t_objectiu:
        pass  # espera activa
    synth.note_on(nota)
    t_acumulat += durada
```
- Clau: calculem el temps objectiu des de l'INICI, no acumulem esperes
- Els petits errors NO s'acumulen — es corregeixen sols
- Demo: mateixa simulació, ara sense deriva

---

### Diapositiva 9 — Comparativa visual (gràfic)
*(Diapositiva amb el gràfic generat al notebook: timestamps esperats vs. reals, A vs B)*
- Estratègia A: la línia "real" s'allunya progressivament de la "esperada"
- Estratègia B: la línia "real" es manté enganxada a la "esperada"
- Aquesta diferència, a 140bpm en un patró de 16 notes, és clarament audible

---

### Diapositiva 10 — Altres estratègies (només per conèixer)
- **Thread dedicat:** per a seqüenciadors interactius (canviar patró mentre sona) — requereix coordinar fils
- **MIDI Clock:** sincronitzar Python amb un DAW extern (Ableton, Logic...) — protocol professional
- No les implementem avui — són referència per al futur (projecte final o més enllà)
- Si voleu aprofundir-hi: és exactament el que necessitareu si feu un looper/sequenciador seriós

---

### Diapositiva 11 — Connexió amb TP1
- Sessió 10 de TP1: la performance de live-coding amb la llibreria `musica`
- El seqüenciador d'avui és la mateixa idea, amb MIDI real i un sintetitzador real
- `for note in pattern: piano(...)` ↔ `for pitch in pattern: instrument.notes.append(Note(...))`

---

### Diapositiva 12 — Tancament Bloc 4, preview Bloc 5
- Bloc 4 complet: protocol MIDI, lectura/escriptura, seqüenciació, timing
- El `MidiSynth` d'avui usa timbres pregravats (soundfont)
- Bloc 5: construirem el NOSTRE sintetitzador — oscil·ladors, ADSR, FM — controlat per MIDI
- Les notes que genereu avui podran controlar el vostre propi so
