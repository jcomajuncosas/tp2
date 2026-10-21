# Sessió 5 — Bloc 3c: Efectes amb memòria

**Bloc temàtic:** 03_temps_real
**Tipus de sessió:** Estàndard
**Durada:** 2h

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:30 | **Bloc A — Memòria d'un número**: slides 1-6 intercalades amb demos | Slides · `exemples.py` (demos sinus, ringmod) · Colab secció 1 |
| 0:30 – 0:55 | **Bloc B — Memòria d'una cinta**: slides 7-12 intercalades amb demos | Slides · `exemples.py` (demos eco) · Colab secció 2-3 |
| 0:55 – 1:50 | Mini-repte a Thonny | `assignment.py` |
| 1:50 – 2:00 | Tancament Bloc 3 + preview Bloc 4 (MIDI) | — |

**Dinàmica: cada eina té un paper i no es repeteixen.**
- **Thonny (`exemples.py`)** = l'orella: *què* passa. Se sent primer, abans d'explicar.
- **Colab (`patches_bloc3c.ipynb`)** = la càmera lenta: *per què* passa. Només coses que en temps real no es poden veure (la frontera entre blocs, la cinta amb etiquetes numèriques). No té ipywidgets ni so en directe.
- **Slides** = el fil conductor que les lliga. Les 🎤 de cada diapositiva diuen quan canviar d'eina.

Ordre de les demos: `demo_sinus_sense_memoria` → (Colab §1) → `demo_sinus` → `demo_ringmod` → (Colab §2) → `demo_eco` → `demo_eco_control` → `demo_disto_eco` → `demo_dos_ecos`.

---

## Objectius

- Entendre que la callback no recorda res entre crides, i classificar els efectes per la memòria que necessiten: **res** (distorsió, S04), **un número** (fase d'un oscil·lador), **una cinta** (eco)
- Generar un oscil·lador continu entre blocs guardant la fase (sinus, ring modulator, trèmolo)
- Implementar un eco amb una cinta de retard (`np.roll`), i entendre per què el retard és exactament la mida de la cinta
- Passar d'eco d'una repetició a eco amb realimentació
- Comprovar a l'orella que l'ordre dels efectes importa (efectes no lineals)
- Motivar les classes del Bloc 5: l'estat escampat en globals no escala

## Notes pedagògiques clau

**Sentir abans d'explicar.** `demo_sinus_sense_memoria()` s'ha de fer sonar abans de mostrar el codi o el gràfic: la pregunta 4 del warm-up els ha deixat amb el dubte i el brunzit el resol. Després el Colab §1 mostra la discontinuïtat i el càlcul dels 43 Hz. El 🧪 de `freq_sinus = 430.6640625` (10 cicles exactes per bloc → el brunzit desapareix) és una trampa deliberada: funciona per casualitat i deixa de funcionar en canviar qualsevol cosa.

**Per què ring mod i no filtre.** El ring mod ensenya la memòria mínima (un número) amb codi vectoritzat, i l'error d'oblidar l'estat se sent clarament. Un filtre recursiu (one-pole) obligaria a un bucle mostra a mostra o a `lfilter` amb `zi`; es reserva per al Bloc 5, on una classe amb `self.y_prev` és natural. A més, l'oscil·lador és la peça bàsica de la síntesi.

**La cinta: etiquetes, no valors.** La taula del Colab §2 fa servir números 1, 2, 3... en lloc de mostres d'àudio, perquè es pugui seguir cada mostra: el bloc `[1 2]` que entra a la crida 1 surt a la crida 4. La segona taula (cinta de 5, blocs de 2) mostra que el retard és exacte encara que la cinta no sigui múltiple del bloc. La tercera fa petar una cinta més curta que un bloc → retard mínim.

**Honestedat: no és un buffer circular.** `np.roll` és una cinta transportadora (FIFO per desplaçament). Ho diem així; el buffer circular de veritat (moure l'índex, no les dades) apareix al stutter (`%`) i al Bloc 5.

**Demo 5 (eco amb control).** El bucle només canvia números; la callback és l'única que toca la cinta (si el bucle substituís el buffer, la callback el podria trepitjar amb la versió vella). L'entrada accepta `r 0.5`, `r=0.5`, amb o sense cometes, i respon "No t'entenc" en lloc d'ignorar en silenci. Retard mínim = un bloc (si no, la callback petaria).

**Demo 7 (dos ecos) i la pregunta de les classes.** Comptar les globals de la sessió i preguntar "i si en volem 5?". No explicar la solució amb classes ara. Si algun alumne avançat observa que dos ecos simples de la mateixa entrada es poden llegir d'una sola cinta en dues posicions (multitap): és correcte, i el comentari del codi ho reconeix. L'argument es manté perquè amb realimentació (Part 2 de l'assignment) cada eco guarda la seva pròpia sortida i necessita la seva cinta.

**Assignment: cada part afegeix alguna cosa als exemples.**
- Part 1, trèmolo: mateix patró que el ring mod (fase), efecte nou, i control del rate en directe. L'autotest crida la callback dues vegades i detecta específicament "la fase torna a començar".
- Part 2, eco amb realimentació: canviar UNA cosa (què s'escriu a la cinta) i passar d'una repetició a infinites. L'autotest distingeix "llegeixes el lloc equivocat" de "només hi ha una repetició".
- Part 3, eco → distorsió: la fan sencera; la referència disto → eco hi és ja feta per comparar a l'orella. Reutilitza la `tanh` de la S04 (no és repetició de contingut: és una peça coneguda dins d'una cadena nova).
- Reflexió `tremolo_sense_fase`: els fem trencar el trèmolo a propòsit. Amb l'LFO a 5 Hz, en un bloc només fa ~0.12 cicles: desapareix l'ondulació i queda una vibració aspra a ~43 Hz. És la resposta a la trampa A de la pregunta 7 del warm-up.

**El stutter (Challenge):** introdueix una segona memòria (la posició de lectura) i la primera lectura en bucle amb `%`: l'avantsala del buffer circular. Si algun alumne l'implementa, val la pena posar-ho en comú a la sessió 6. Solució a `_solucions/S05_challenges_solucio.py`.

## Tancament del Bloc 3 (últims 10 min)

El Bloc 3 (Sessions 3-5) ha cobert el viatge complet: offline → callback → efectes amb memòria → control interactiu. El model de callback és el motor de tot el que faran al projecte final. Preview Sessió 6: canviem de domini → MIDI i control musical.

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `exemples.py` — 7 demos per a Thonny, cridades des de la Shell (sinus sense/amb memòria, ring mod, eco, eco amb control, distorsió → eco, dos ecos)
- `assignment.py` — mini-repte Thonny: trèmolo, eco amb realimentació, eco → distorsió, reflexió + challenge stutter
- `recursos/cheat_sheet.md` — memòria d'un número (fase), cinta de retard, control en directe, ordre d'efectes, regles d'or
- `recursos/warmup_quiz.md` — 7 preguntes per a Google Forms (opcions aleatòries)
- `recursos/slides_outline.md` — 12 diapositives
- `recursos/patches_bloc3c.ipynb` — Colab "càmera lenta": frontera entre blocs + cinta amb etiquetes + eco simulat
- `../../_solucions/S05_solucio.py`, `S05_challenges_solucio.py` — solucions (docent)

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md` (activar ordre aleatori de les opcions)
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Provar `exemples.py` amb micròfon real — especialment que el brunzit de `demo_sinus_sense_memoria()` és prou evident amb els auriculars de l'aula
- [ ] Provar a l'orella la Part 3 (disto → eco vs eco → disto) amb `drive = 8`: comprovar que la diferència s'aprecia amb veu
