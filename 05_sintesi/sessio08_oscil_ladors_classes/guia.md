# Sessió 8 — Bloc 5a: Síntesi amb classes

**Bloc temàtic:** 05_sintesi
**Tipus de sessió:** Estàndard (introdueix OOP aplicat — mereix una mica més de temps de teoria)
**Durada:** 2h

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:30 | Mini-teoria (Slides) | `recursos/slides_outline.md` |
| 0:30 – 1:05 | Demo guiada | `recursos/patches_bloc5a.ipynb` (Colab) o `exemples.py` (Thonny) |
| 1:05 – 1:50 | Workshop / mini-repte | `notebook.ipynb` |
| 1:50 – 2:00 | Tancament + preview Sessió 9 (FM, MIDI temps real, pyo) | — |

---

## Objectius

- Entendre per què les classes són l'eina natural quan cal recordar estat entre crides
- Construir `Oscillator` (genera timbre), `Envelope` (ADSR, dona forma temporal) i `SamplePlayer` (reprodueix so gravat)
- Entendre la distinció clau: l'oscil·lador "sona sempre"; l'envolvent dona forma de nota
- Connectar MIDI (number→freq) amb les classes: `note_on`/`note_off` controlen l'embolcall, no l'oscil·lador
- Distingir síntesi (`Oscillator`) de sampling (`SamplePlayer`) com a dos paradigmes complementaris

## Decisió de disseny important (llegir abans d'ensenyar)

**Per què classes pròpies i no una llibreria com `pyo`:** decisió discutida i confirmada amb el docent. L'experiència prèvia amb STK (C++, massa low-level/abstracte) i Processing+MINIM (massa alt nivell, no es copsava l'arquitectura) confirma que construir-ho amb NumPy pur, al mateix nivell que la resta del curs, és l'equilibri correcte per a aquest grup. `pyo` apareix a la **Sessió 9** com a "tast" pràctic de contrast (no aquí).

**Per què `Envelope` és una classe separada (no un mètode d'`Oscillator`):** disseny modular tipus sintetitzador físic — components petits que es combinen, no una classe monolítica. Reforça la distinció timbre/forma temporal.

**Per què `SamplePlayer` s'introdueix aquí:** es va detectar un gap real al disseny original del curs — mai s'havia tractat el concepte "disparar un sample sencer com a resposta a un esdeveniment" (model mental de samplers/drum machines), necessari per al rol de "drum-replacement per beatbox" del projecte final. Aquí s'introdueix de manera senzilla i en contrast directe amb `Oscillator`.

## Connexions amb sessions anteriors

- **Sessió 5 (buffer global de l'eco):** "per què les classes" es planteja explícitament aquí — el problema de "dos ecos = dues variables globals" es resol amb instàncies.
- **Sessió 2 (WAV/soundfile):** `SamplePlayer` reutilitza `sf.read` directament, ara encapsulat.
- **Bloc 4 (MIDI):** `note_to_freq` connecta amb els numbers MIDI ja treballats; l'arpegi de la demo reutilitza el patró de seqüenciació.
- **TP1:** classes poc treballades allà — aquí cobren sentit real per primera vegada al curs.

## Materials d'àudio proporcionats

`recursos/audio/kick_sample.wav` — generat sintèticament (mateixa tècnica que el `perc_loop.wav` de la Sessió 2), sense problemes de llicència.

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `exemples.py` — demo per a Thonny (sounddevice), 7 seccions progressives
- `notebook.ipynb` — mini-repte Colab: `Oscillator`, `Envelope`, `tocar_nota`, `SamplePlayer`, seqüència pròpia (5 autotests, tots validats)
- `recursos/cheat_sheet.md` — API completa de les 3 classes, ADSR explicat, taula resum
- `recursos/warmup_quiz.md` — 7 preguntes per a Google Forms (totes amb intuïció prèvia vàlida)
- `recursos/slides_outline.md` — 13 diapositives
- `recursos/patches_bloc5a.ipynb` — demo Colab
- `recursos/audio/kick_sample.wav` — sample d'exemple

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Provar `exemples.py` localment amb `kick_sample.wav` a la mateixa carpeta
