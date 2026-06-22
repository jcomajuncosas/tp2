# Sessió 2 — Bloc 2: El so com a fitxer

**Bloc temàtic:** 02_numpy_audio
**Tipus de sessió:** Estàndard (sense warm-up de reconnexió addicional — ja vam fer la base a Sessió 1, però mantenim el Questionari de repàs)
**Durada:** 2h

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up / Questionari (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:25 | Mini-teoria (Slides) | `recursos/slides_outline.md` |
| 0:25 – 1:05 | Demo guiada | `exemples.py` (Thonny) o `recursos/patches_bloc2.ipynb` (Colab) |
| 1:05 – 1:50 | Workshop pràctic / mini-repte: Audio Manipulator | `notebook.ipynb` |
| 1:50 – 2:00 | Tancament, dubtes, preview Sessió 3 | — |

---

## Objectius

- Llegir/escriure fitxers WAV amb `soundfile` (array ↔ fitxer)
- Visualitzar la forma d'ona amb `librosa` (ús mínim, preview del Bloc 6)
- Combinar sons (mixing): gestió de longituds diferents i normalització
- Repetir fragments (`np.tile`) com a base d'un "loop"
- Aplicar gain i fade (reaprofitant la Sessió 1) sobre àudio carregat de fitxer

## Continuïtat amb la Sessió 1

Aquesta sessió **no repeteix** gain/fade des de zero: reutilitza `generate_tone` i el concepte d'envolvent de la Sessió 1, ara aplicats a `data` llegit d'un fitxer en lloc d'un array generat. La novetat real és I/O (`soundfile`), mixing i `np.tile`.

## Connexions amb TP1

- `soundfile.write/read` ↔ `open()`/`write()`/`read()` (Files & I/O)
- `np.tile(array, N)` ↔ `for _ in range(N): tocar(pattern)` — repetició sense bucle explícit

## Materials d'àudio proporcionats

A `recursos/audio/`:
- `perc_loop.wav` — loop de percussió sintètic (kick + hi-hat, 2s, 120bpm), generat amb codi (sense problemes de llicència)
- `example_pad.wav` — pad harmònic de 2s, com a alternativa si algú no pot enregistrar la seva veu a la Part 0 del mini-repte

Aquests fitxers es descarreguen dins els notebooks via `raw.githubusercontent.com` (no cal Drive).

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `exemples.py` — demo per a Thonny (sounddevice + soundfile + librosa). **Requereix** `perc_loop.wav` i `example_pad.wav` a la mateixa carpeta (copiar-los de `recursos/audio/`)
- `notebook.ipynb` — mini-repte "Audio Manipulator" amb autotest (Colab)
- `recursos/cheat_sheet.md` — material de reconnexió/referència
- `recursos/warmup_quiz.md` — preguntes per a Google Forms
- `recursos/slides_outline.md` — contingut per a Google Slides
- `recursos/patches_bloc2.ipynb` — versió Colab de la demo
- `recursos/audio/` — fitxers WAV d'exemple

## Notes sobre el mini-repte (Part 0 — gravació)

L'Opció A (gravar amb micròfon a Colab) usa `MediaRecorder` + `ffmpeg` per convertir webm→wav. Si dona problemes (permisos de navegador, `ffmpeg` no disponible), l'Opció B (descarregar `example_pad.wav`) és el fallback immediat — cap alumne ha de quedar bloquejat en aquest pas.

## Pendent / a revisar

- [ ] Provar l'Opció A de gravació a Colab (permisos micròfon, ffmpeg) abans de la sessió
- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Per a `exemples.py`: assegurar que els alumnes tenen `perc_loop.wav`/`example_pad.wav` localment (Thonny no descarrega de GitHub automàticament)
