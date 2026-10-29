# Sessió 6 — Bloc 4a: Estructura MIDI i `mido`

**Bloc temàtic:** 04_midi
**Tipus de sessió:** Estàndard
**Durada:** 2h

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:25 | Mini-teoria (diapositives 1–7) | `recursos/slides_outline.md` |
| 0:25 – 0:35 | ✏️ **En paper**: dels deltes al piano roll, i al revés (diapositives 8–9) | pissarra / fotocòpia |
| 0:35 – 1:00 | Demo guiada a Colab (patches) + diapositives 10–13 | `recursos/patches_bloc4a.ipynb` |
| 1:00 – 1:45 | Workshop / mini-repte (Colab) | `notebook.ipynb` |
| 1:45 – 1:55 | Demo de MIDI en temps real a Thonny (diapositiva 14), si l'aula ho permet | `exemples.py` |
| 1:55 – 2:00 | Tancament + preview `pretty_midi` (Sessió 7) | — |

---

## Objectius

- Entendre el protocol MIDI: missatges, nota/velocity/canal, delta time
- Saber convertir deltes a temps absolut i al revés, també amb acords i silencis
- Llegir, analitzar, crear i transformar fitxers `.mid` amb `mido`
- Entendre la relació ticks ↔ segons ↔ bpm
- Connectar el model MIDI amb `piano(note, vel, dur)` de TP1
- Veure (demo) les tres maneres de rebre MIDI en temps real, incloent-hi el callback MIDI, i contrastar-lo amb el callback d'àudio de la S04

## Colab o Thonny (cal dir-ho explícitament)

Els alumnes saben que hem migrat a Thonny. Avui tornem a Colab i cal explicar-ne el motiu (diapositiva 3): **fitxers → Colab, ports → Thonny**, el mateix criteri de sempre. Tot el que han de fer avui és a Colab. `exemples.py` només conté la demo de temps real, que és opcional i la fa el docent.

## El moment en paper

En la línia del que va funcionar a la S05. La diapositiva 8 (deltes → piano roll) i la 9 (piano roll → deltes) inclouen un acord i un silenci perquè són precisament els dos casos que el patró `note_on time=0 / note_off time=durada` no resol. La secció 2 dels patches comprova la taula de la diapositiva 8. La diapositiva 9 és la preparació directa de la Part 4 del workshop.

## Workshop: què és nou respecte als patches

Els patches **no** donen la funció que aparella `note_on`/`note_off` (ara és la Part 3 del workshop). El piano roll dels patches el fa `pretty_midi`, que al workshop fa de "segona opinió" a l'autotest 3.

| Part | Què fan | Per què no és copiar |
|---|---|---|
| 1–2 | `compta_notes`, `rang_notes` | Escalfament. L'autotest inclou un `note_on` de velocity 0 |
| 3 ⭐ | `a_temps_absolut` | Han d'aparellar obertures i tancaments ells mateixos. El piano roll es dibuixa amb la **seva** llista |
| 4 | Seqüència pròpia amb **silenci + acord** | El patró dels patches no ho resol. L'autotest comprova l'acord, el silenci i les notes de durada 0 |
| 5 | `transposa` | Track nou (no modificar l'original), també els tancaments, `ValueError` fora de rang |
| 🎼 | Duo (frase + frase transposada) | Consolidació escrita per l'alumne, sense autotest |

## Challenges

Tots segueixen el patró **deltes → absolut → transforma → deltes**. El challenge 0 (`a_track`, el camí invers) desbloqueja la resta. Cadascun amaga un descobriment, verificat a `_solucions/solucio.ipynb`:

1. **Eco MIDI** (pont amb el delay de la S05): amb `feedback > 1` no explota, satura a 127. Amb un retard més curt que la nota, la Part 3 i `pretty_midi` veuen 64 notes però amb durades diferents (la Part 3 manté 0,5 s; `pretty_midi` talla els ecos a 0,125 s). Una Part 3 feta amb diccionari en veu 49. MIDI no diu quin `note_off` tanca quin `note_on`.
2. **Retrògrad**: `track[::-1]` fa que només sonin 8 de 16 notes, amb el ritme desplaçat. Cal passar pel temps absolut.
3. **Phasing (Reich)**: amb 480 vs. 470 ticks, la veu B cau a temps una nota per davant cada 4 repeticions (48 notes). El patró sencer no torna a coincidir fins a 48 repeticions.
4. **Humanitzador**: on és la frontera entre "humà" i "begut"?
5. **Accelerando**: trenca la Part 3 (tempo fix: 8,00 s, real: 8,92 s amb 60→180 bpm). Cal un mapa de tempo amb `mido.merge_tracks`.

## Notes sobre MIDI en temps real

- `exemples.py` està organitzat en funcions: F5 només les defineix i es criden des del Shell (`llista_ports()`, `escolta_teclat()`, `escolta_teclat_sense_bloquejar()`, `escolta_teclat_callback()`, `toca_escala()`, `reprodueix_fitxer()`).
- **Cal `python-rtmidi`** a Thonny. Sense aquest paquet, `mido` no veu cap port (`ModuleNotFoundError: rtmidi`, verificat).
- `mid.play()` **no fa so**: només espera entre missatges. A Windows es pot enviar al "Microsoft GS Wavetable Synth". A macOS cal IAC Driver + GarageBand/DAW.
- Validat amb un backend MIDI fals (sense hardware): llistar ports, entrada sense bloquejar, callback en un fil propi, sortida i reproducció d'un fitxer (8,0 s reals). **No s'ha provat amb un teclat ni un port real.**

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `exemples.py` — demo de MIDI en temps real (Thonny)
- `notebook.ipynb` — workshop (Colab)
- `recursos/cheat_sheet.md`
- `recursos/warmup_quiz.md` — 7 preguntes per a Google Forms (sense canvis)
- `recursos/slides_outline.md` — 15 diapositives
- `recursos/patches_bloc4a.ipynb` — demo Colab
- `recursos/midi/example_scale.mid` — fitxer d'exemple (escala de Do major + baix, 3 tracks)
- `_solucions/solucio.ipynb` — el notebook del workshop resolt, amb els challenges al final (no es publica; s'obre a Colab com el de l'alumne)

## Pendent / a revisar

- [ ] **Comprovar l'autotest 1 i 2 contra l'`example_scale.mid` real** (16 i 8 notes, melodia 60–72, baix per sota de 60). S'ha validat amb una reconstrucció coherent amb aquesta guia, no amb l'original.
- [ ] Publicar `recursos/midi/example_scale.mid` al repo públic abans de la classe (ara la URL de descàrrega dona 404)
- [ ] Muntar Google Form, Google Slides (diapositives 8–9: preparar fotocòpia amb quadrícula) i el cheat sheet com a Google Doc
- [ ] Provar els notebooks a Colab: el render amb fluidsynth s'ha validat al contenidor, no a Colab
- [ ] Provar `exemples.py` amb un teclat i un port reals a l'aula
- [ ] Decidir si es fa la demo de temps real segons l'equipament de l'aula
