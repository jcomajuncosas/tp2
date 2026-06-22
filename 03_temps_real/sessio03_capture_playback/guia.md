# Sessió 3 — Bloc 3a: Captura, playback i efectes offline

**Bloc temàtic:** 03_temps_real
**Tipus de sessió:** Estàndard
**Durada:** 2h

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:25 | Mini-teoria (Slides) | `recursos/slides_outline.md` |
| 0:25 – 1:05 | Demo guiada: gravar + catàleg d'efectes | `exemples.py` / `recursos/patches_bloc3a.ipynb` |
| 1:05 – 1:50 | Workshop: mini-repte (implementar + explorar) | `notebook.ipynb` |
| 1:50 – 2:00 | Tancament: pregunta oberta sobre reverse → preview callback | — |

---

## Objectius

- Entendre i usar el model blocking (`sd.rec`, `sd.play`, `sd.wait`)
- Entendre la diferència entre còpia i referència en NumPy (`np.copy`)
- Conèixer i aplicar un catàleg de 8 efectes offline (amplitud, retard, distorsió, modulació, velocitat)
- Encadenar efectes (composició de funcions)
- Deixar oberta la pregunta que obre la Sessió 4: reverse impossible en temps real → per on caldria pensar diferent?

## Connexions amb TP1

- Encadenar efectes (`fade_out(echo(data))`) ↔ composició de funcions de TP1
- `np.copy` ↔ distinció còpia/referència de llistes Python (TP1)
- El model blocking (lineal, seqüencial) ↔ tots els programes de TP1

## Catàleg d'efectes (resum per al docent)

| Efecte | Novetat conceptual | Connexió amb Bloc 5 |
|---|---|---|
| `reverse` | Ninguna — però fa pensar en temps real | — |
| `fade_in/out` | Cap (ja vist Sessions 1-2) | — |
| `echo` | Retard + còpia (np.copy important) | — |
| `delay_multi` | Bucle + potències de decay | — |
| `distortion` | `np.clip` | — |
| `tremolo` | LFO lent (modulació d'amplitud) | ✅ Preview Bloc 5 |
| `ring_modulation` | LFO com a portadora (freqüències noves) | ✅ Preview Bloc 5 |
| `playback_speed` | Relació sr/to (Sessió 1) | — |

## Notes importants

**Part 4 (Reflexió) del mini-repte:** és text lliure, no té autotest. Llegir les respostes a la pregunta sobre `reverse` dona informació valuosa sobre si el model mental blocking vs. temps real s'ha assentat — és bon indicador per calibrar el ritme de la Sessió 4.

**`playback_speed`:** presenta-la com "canvi de velocitat de reproducció, NO pitch shift real", i aprofita per recordar la relació freq/sample_rate de la Sessió 1. Un pitch shift real requereix resampling amb interpolació — mencionat al Challenge 1.

**Tancament de la sessió (últims 10 min):** la pregunta "i si volguessis aplicar echo en temps real?" és la llavor de la Sessió 4. No cal respondre-la — deixa-la oberta.

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `exemples.py` — demo per a Thonny (sounddevice)
- `notebook.ipynb` — mini-repte: implementar echo+distortion + exploració lliure + reflexió
- `recursos/cheat_sheet.md` — model blocking + catàleg d'efectes complet
- `recursos/warmup_quiz.md` — 7 preguntes per a Google Forms
- `recursos/slides_outline.md` — 11 diapositives
- `recursos/patches_bloc3a.ipynb` — versió Colab de la demo

## Pendent / a revisar

- [ ] Provar gravació a Colab (Part 0 del notebook) — pot tenir problemes de permisos de micròfon
- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
