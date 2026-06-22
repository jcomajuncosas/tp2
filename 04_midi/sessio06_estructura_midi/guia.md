# Sessió 6 — Bloc 4a: Estructura MIDI i `mido`

**Bloc temàtic:** 04_midi
**Tipus de sessió:** Estàndard
**Durada:** 2h

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:28 | Mini-teoria (Slides) — inclou breu recordatori protocol MIDI | `recursos/slides_outline.md` |
| 0:28 – 1:05 | Demo guiada (Colab + Thonny per a MIDI real) | `recursos/patches_bloc4a.ipynb` + `exemples.py` |
| 1:05 – 1:50 | Workshop / mini-repte | `notebook.ipynb` (Colab) |
| 1:50 – 2:00 | Tancament + preview `pretty_midi` (Sessió 7) | — |

---

## Objectius

- Entendre el protocol MIDI: missatges, nota/velocity/canal, delta time
- Llegir i analitzar fitxers `.mid` amb `mido`
- Crear fitxers `.mid` des de zero amb `mido`
- Entendre la relació ticks ↔ segons ↔ bpm
- Connectar el model MIDI amb la experiència de TP1 (`piano(note, vel, dur)`)
- Demo opcional: MIDI en temps real (ports, teclat controlador)

## Connexió explícita amb TP1

La diapositiva 5 i la secció 8 del cheat sheet estableixen el pont explícit entre la llibreria `musica` de TP1 i el protocol MIDI real. Els alumnes reconeixeran la lògica (for note in pattern → tocar) i entendran que la llibreria `musica` era una abstracció sobre exactament aquest protocol.

## Notes sobre MIDI en temps real

La Demo 4 i 5 de `exemples.py` (MIDI in/out) estan comentades per defecte. Descomenta-les a classe si:
- Tens teclats MIDI connectats a l'aula (per MIDI in)
- Els alumnes han configurat IAC Driver (macOS) o LoopMIDI (Windows) per MIDI out

No cal forçar-ho si hi ha problemes de configuració — el mini-repte és completament offline (fitxers `.mid`).

## Sobre `pretty_midi` al notebook

El notebook usa `pretty_midi` per escoltar el resultat (convertint MIDI a àudio amb `fluidsynth`). Això requereix `FluidSynth` instal·lat al sistema de Colab — habitualment ja hi és. Si falla:
```python
!apt-get install -y fluidsynth
```

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `exemples.py` — lectura/escriptura MIDI + ports MIDI (Thonny)
- `notebook.ipynb` — mini-repte: `compta_notes`, `rang_notes`, crear seqüència pròpia
- `recursos/cheat_sheet.md` — protocol MIDI, números essencials, `mido` API, connexió TP1
- `recursos/warmup_quiz.md` — 7 preguntes per a Google Forms
- `recursos/slides_outline.md` — 12 diapositives
- `recursos/patches_bloc4a.ipynb` — demo Colab: llegir, analitzar, piano roll, crear, delta time bug
- `recursos/midi/example_scale.mid` — fitxer MIDI d'exemple (escala Do major + baix, 3 tracks)

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Provar `notebook.ipynb` a Colab — verificar que `fluidsynth` funciona per escoltar el MIDI
- [ ] Provar `exemples.py` localment — verificar que `mido` llegeix el fitxer correctament
- [ ] Decidir si es fa la demo de MIDI en temps real (ports) segons equipament de l'aula
