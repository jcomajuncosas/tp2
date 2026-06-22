# Sessió 4 — Bloc 3b: El model callback

**Bloc temàtic:** 03_temps_real
**Tipus de sessió:** Estàndard (conceptualment la més densa del curs)
**Durada:** 2h

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:30 | Mini-teoria (Slides) — més llarg que habitual | `recursos/slides_outline.md` |
| 0:30 – 1:00 | Demo guiada a Thonny (pass-through, gain, glitch deliberat) | `exemples.py` |
| 1:00 – 1:05 | Exercicis conceptuals a Colab (Parsons, predicció, latència) | `recursos/teoria_exercicis.ipynb` |
| 1:05 – 1:50 | Mini-repte a Thonny | `assignment.py` |
| 1:50 – 2:00 | Tancament: preview Sessió 5 (efectes reals + sliders) | — |

---

## Objectius

- Entendre la inversió de control: de "tu crides" a "el sistema crida"
- Conèixer l'estructura d'un callback (`indata`, `outdata`, `frames`, `time`, `status`)
- Implementar un pass-through i un gain en temps real
- Entendre el trade-off blocksize ↔ latència/glitch
- Entendre per qué Colab no és vàlid per a temps real (contrast amb WebAudio)
- Assentar la variable global com a mecanisme de comunicació simple (i honest sobre les seves limitacions)

## Notes pedagògiques clau

**Aquesta és la sessió conceptualment més densa del curs.** La inversió de control (el sistema crida la teva funció) és un salt de paradigma real. Preveure que alguns alumnes necessitaran escoltar l'explicació del mapa mental 2-3 vegades. La demo del glitch deliberat (Demo 4 de `exemples.py`) és molt efectiva: *sentir* el problema és molt més clar que *explicar-lo*.

**La demo del comptador de blocs** (Demo 3) és opcional però útil: mostra experimentalment que el callback es crida exactament `sample_rate/blocksize` vegades per segon, connectant el concepte abstracte de "periodicitat" amb un número mesurable.

**La variable global:** presentar-la amb honestedat — "funciona, és lleig, en producció faríem servir cues, però ara ens serveix". No passar per alt el problema, però tampoc entrar en threading ara.

**Colab vs. Thonny:** la diapositiva 12 i la pregunta 7 del warm-up aborden explícitament per qué canviem d'entorn. El contrast amb WebAudio és pertinent per a sonòlegs (moltes eines d'àudio web que coneixeran es basen en WebAudio).

## Format de l'assignment: .py, no notebook

L'assignment d'aquesta sessió és un fitxer `.py` per a Thonny, no un notebook de Colab. Els alumnes el pengen directament al Classroom (adjunt al lliurament). Les comprovacions funcionals (`assert`) validen la implementació del callback sense necessitat de hardware.

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `exemples.py` — demo guiada per a Thonny (5 demos progressives)
- `assignment.py` — mini-repte per a Thonny (pass-through + gain + observacions blocksize + reflexió)
- `recursos/cheat_sheet.md` — mapa mental complet blocking vs. callback + taula de referència
- `recursos/warmup_quiz.md` — 7 preguntes per a Google Forms
- `recursos/slides_outline.md` — 13 diapositives (lleugerament més llarg que altres sessions)
- `recursos/teoria_exercicis.ipynb` — notebook Colab amb exercicis conceptuals (Parsons, predicció, càlcul de latència)

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Provar `exemples.py` localment: verificar que el micròfon funciona i que la Demo 4 (glitch) és prou clara
- [ ] Configurar l'entrega al Classroom com a "fitxer adjunt" (no Colab) per a l'`assignment.py`
