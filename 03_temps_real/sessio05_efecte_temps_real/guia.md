# Sessió 5 — Bloc 3c: Efectes en temps real

**Bloc temàtic:** 03_temps_real
**Tipus de sessió:** Estàndard
**Durada:** 2h

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:25 | Mini-teoria (Slides) | `recursos/slides_outline.md` |
| 0:25 – 0:55 | Demo guiada a Thonny (distorsió, eco, combo, dos ecos) | `exemples.py` |
| 0:55 – 1:05 | Demo visual a Colab (simulació + ipywidgets) | `recursos/patches_bloc3c.ipynb` |
| 1:05 – 1:50 | Mini-repte a Thonny | `assignment.py` |
| 1:50 – 2:00 | Tancament Bloc 3 + preview Bloc 4 (MIDI) | — |

---

## Objectius

- Entendre per qué els efectes amb memòria necessiten un buffer extern al callback
- Implementar eco en temps real amb buffer de retard global + `np.roll`
- Implementar distorsió en temps real (sense memòria — cas simple)
- Combinar efectes en un sol callback (ordre important)
- Usar `ipywidgets` per visualitzar paràmetres (Colab, demo visual sense so real)
- Motivar les classes del Bloc 5: dos ecos simultanis → problema del buffer global

## Notes pedagògiques clau

**La Demostració 5 de `exemples.py` (dos ecos simultanis)** és la peça pedagògica més important de la sessió per al Bloc 5: mostrar en directe que dos ecos simultanis requereixen dos parells de variables globals, i preguntar "i si en volem 5?" és la motivació natural per a les classes. No explicar la solució amb classes ara — deixar la pregunta oberta.

**L'ordre distorsió→eco vs eco→distorsió** (Demo 4 i Part 3 del challenge): sonen diferent perquè distorsió→eco aplica l'eco sobre un senyal ja saturat (ecos distorsionats), mentre eco→distorsió distorsiona el senyal + els seus ecos junts. Val la pena dedicar 2 minuts a escoltar les dues variants.

**El stutter (Challenge):** és complex però possible. Les pistes de l'enunciat indiquen l'arquitectura. Si algun alumne avançat l'implementa, val la pena posar-ho en comú a la sessió 6 com a exemple.

**ipywidgets a Colab:** primer cop que apareix. Explicar clarament que és visualització (el codi s'executa al servidor), no so real. La contradicció aparent ("un slider que canvia paràmetres... però sense so real?") és pedagògicament útil per reforçar per qué Colab no serveix per a temps real.

## Tancament del Bloc 3 (últims 10 min)

El Bloc 3 (Sessions 3-5) ha cobert el viatge complet: offline → callback → efectes amb memòria → control interactiu. El model de callback és el motor de tot el que faran al projecte final. Preview Sessió 6: canviem de domini → MIDI i control musical.

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `exemples.py` — 5 demos per a Thonny (distorsió, eco, eco interactiu, combo, dos ecos)
- `assignment.py` — mini-repte Thonny: distorsió + eco + combo, amb asserts + challenge stutter
- `recursos/cheat_sheet.md` — buffer de retard, `np.roll`, ipywidgets, regles d'or del callback
- `recursos/warmup_quiz.md` — 7 preguntes per a Google Forms
- `recursos/slides_outline.md` — 12 diapositives
- `recursos/patches_bloc3c.ipynb` — Colab: simulació del buffer + ipywidgets slider

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Provar `exemples.py` localment — especialment Demo 3 (control interactiu) i Demo 5 (dos ecos)
- [ ] Provar `recursos/patches_bloc3c.ipynb` a Colab — verificar que `ipywidgets` funciona amb `@widgets.interact`
