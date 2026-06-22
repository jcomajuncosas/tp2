# Sessió 7 — Bloc 4b: `pretty_midi`, seqüenciador i timing precís

**Bloc temàtic:** 04_midi
**Tipus de sessió:** Estàndard
**Durada:** 2h

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:28 | Mini-teoria (Slides) | `recursos/slides_outline.md` |
| 0:28 – 1:00 | Demo guiada (Colab: pretty_midi + timing simulat) | `recursos/patches_bloc4b.ipynb` |
| 1:00 – 1:10 | Demo Thonny (MidiSynth real, timing A vs B audible) | `exemples.py` |
| 1:10 – 1:50 | Workshop / mini-repte (Colab) | `notebook.ipynb` |
| 1:50 – 2:00 | Tancament Bloc 4 + preview Bloc 5 | — |

---

## Objectius

- Crear seqüències MIDI amb `pretty_midi` (alt nivell, temps en segons)
- Implementar un arpegiador (up/down/updown)
- Escoltar MIDI amb `MidiSynth`/`MidiSynthRender` (FluidSynth) sense IAC/LoopMIDI
- Entendre per què `time.sleep()` no és prou precís per a seqüenciació en temps real
- Conèixer l'Estratègia B (`perf_counter` + temps objectiu absolut) com a referència
- Conèixer (sense implementar) threads dedicats i MIDI Clock per a casos més avançats

## Per què `pretty_midi` aquí torna a Colab com a entorn principal

A diferència de Sessions 4-5 (Bloc 3, temps real d'àudio), aquí **no hi ha el problema de Colab vs. servidor remot**: el mini-repte genera fitxers MIDI i els renderitza a àudio amb `pm.fluidsynth()` — no requereix hardware en temps real. Per això el notebook (`notebook.ipynb`, Colab) torna a ser el format principal de l'assignment, com a Sessions 1-3 i 6.

## La classe `MidiSynth` / `MidiSynthRender`

Es proporciona **ja feta** (`recursos/midisynth.py`) — els alumnes l'usen, no la implementen. Dues variants:
- `MidiSynth`: temps real, per a Thonny, so directe per l'altaveu via FluidSynth
- `MidiSynthRender`: renderitza a array NumPy, per a Colab (sense accés a hardware d'àudio, igual que la resta del Bloc 3)

**Instal·lació prèvia necessària** (documentada al capçal de `midisynth.py`):
- macOS: `brew install fluid-synth` + descarregar un soundfont a part (Homebrew NO n'inclou cap)
- Linux: `sudo apt install fluidsynth fluid-soundfont-gm` (inclou soundfont)
- Windows: instal·lador de GitHub releases + soundfont a part
- Tots: `pip install pyfluidsynth`

**Important:** verificar abans de la sessió que tots els alumnes (o almenys els que treballaran a Thonny per al Challenge 3) tenen FluidSynth + soundfont instal·lat. És un pas d'instal·lació nou que no havíem necessitat fins ara.

## Timing: el que s'ensenya vs. el que s'implementa

**S'ensenya i es compara (demo, no avaluat):** Estratègia A (`time.sleep`) vs. Estratègia B (`perf_counter` + temps objectiu absolut). La comparació és doblement evident: visual (gràfic de deriva al notebook de Patches) i auditiva (Demo 4 de `exemples.py` a Thonny).

**Es menciona només (cheat sheet, sense implementar):** thread dedicat per a seqüenciadors interactius, MIDI Clock per a sincronització amb DAW.

**El Challenge 3 i 4** del notebook ofereixen el camí per a qui vulgui anar més enllà (implementar Estratègia B en temps real, o integrar amb el callback d'àudio del Bloc 3) — pensat especialment per a alumnes que ja tinguin experiència prèvia amb seqüenciació (per exemple, qui ja hagi fet un seqüenciador de bateria abans).

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `exemples.py` — Thonny: MidiSynth, canvi d'instrument, reproduir PrettyMIDI, comparació timing A/B audible
- `notebook.ipynb` — Assignment Colab: `arpegiador`, `notes_a_midi`, seqüenciador propi (16+ notes), reflexió, challenges
- `recursos/cheat_sheet.md` — `pretty_midi` API, comparació amb `mido`, timing (A, B, i mencions de thread/MIDI Clock)
- `recursos/warmup_quiz.md` — 7 preguntes per a Google Forms
- `recursos/slides_outline.md` — 12 diapositives
- `recursos/patches_bloc4b.ipynb` — Colab: pretty_midi, arpegiador, simulació timing amb gràfic, comparació audible A/B/ideal
- `recursos/midisynth.py` — classe `MidiSynth`/`MidiSynthRender` (proporcionada feta, no és exercici)

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] **Important:** verificar instal·lació de FluidSynth + soundfont en almenys un Mac i un Windows abans de la sessió
- [ ] Provar `notebook.ipynb` a Colab — verificar que `fluidsynth` i el soundfont s'instal·len correctament amb `apt-get`
- [ ] Provar `exemples.py` a Thonny amb `MidiSynth` real
- [ ] Considerar documentar a banda un soundfont recomanat concret (enllaç de descàrrega directa) per estalviar temps de cerca als alumnes
