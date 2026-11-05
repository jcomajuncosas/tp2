# Sessió 7 — Bloc 4b: seqüenciació MIDI en temps real i timing precís

**Bloc temàtic:** 04_midi
**Tipus de sessió:** Estàndard
**Durada:** 2h
**Entorn:** 100% Thonny

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material | Què se n'ha d'endur l'alumne |
|---|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` | Repàs de delta time i del termini del callback; dubtes oberts sobre temps absolut |
| 0:08 – 0:25 | Mini-teoria 1: `pretty_midi`, arpegiador, `sinte.py` | Diapositives 1–6 + `demo_1_notes()`, `demo_2_arpegiador()` | Temps absolut vs. delta; el sinte d'avui és el callback del Bloc 3 |
| 0:25 – 0:35 | Mini-teoria 2: estratègies A i B | Diapositives 7–9 | Dues maneres d'esperar; la B calcula l'objectiu des de l'inici |
| 0:35 – 0:50 | ✏️ Exercici en paper: la deriva | Diapositives 10–11 | Predir a mà quant deriva A i per què B no |
| 0:50 – 1:05 | Demos a Thonny (cada alumne a la seva màquina) | `recursos/exemples.py`: `demo_3`, `demo_4`, `demo_5` | Comprovar la predicció; sentir A vs. B; la trampa del GIL |
| 1:05 – 1:50 | Assignment | `assignment.py` | Construir i fer sonar un seqüenciador propi |
| 1:50 – 2:00 | Tancament Bloc 4 + preview Bloc 5 | Diapositives 15–16 | — |

---

## Objectius

- Crear seqüències amb `pretty_midi` (notes amb `start`/`end` en segons, temps absolut)
- Ampliar l'arpegiador (octaves) i donar-li forma musical (tempo, gate, accents)
- Reproduir una seqüència en directe amb precisió (estratègia B, espera híbrida)
- Entendre per què `time.sleep()` repetit acumula error, predir-ho a mà i mesurar-ho
- Entendre que el termini del callback d'àudio depèn de tot el programa (GIL)

## Per què tota la sessió és a Thonny

Criteri del curs, explícit per als alumnes (és a la capçalera d'`exemples.py`, d'`assignment.py` i al cheat sheet):

> **Si la sessió necessita so en directe o ports, tot es fa a Thonny, encara que també s'escriguin fitxers. Colab només per a sessions del tot offline.**

La Sessió 6 (llegir, escriure i dibuixar fitxers `.mid`) era offline: Colab. Avui el tema és el timing en temps real, i Colab corre en un servidor sense altaveu: el seu rellotge no és el de l'alumne i el so només es pot renderitzar, no reproduir en directe. Canviar d'entorn dins d'una mateixa sessió seria fricció sense guany, de manera que també la part de `pretty_midi` es fa a Thonny (`pm.write()` funciona igual).

## El fil conceptual de la sessió

| Sessió 6 (`mido`) | Sessió 7 (`pretty_midi`) |
|---|---|
| `time` = **delta**: "espera això des del missatge anterior" | `start` = **absolut**: "toca a aquest instant des de l'inici" |
| Encaixa amb l'**estratègia A** (`sleep` de cada durada) | Encaixa amb l'**estratègia B** (`espera_fins(inici + start)`) |
| Cada error s'arrossega | Cada error es queda a la seva nota |

`pretty_midi` no és "una altra llibreria per escriure fitxers": és l'estructura de dades que alimenta el seqüenciador en directe. A la Part 3 de l'assignment, `t_inici + nota.start` és literalment el temps objectiu de l'estratègia B.

## El sintetitzador: `recursos/sinte.py`

Es proporciona fet, però es llegeix a classe (diapositiva 6). És un callback de `sounddevice` amb el mateix model del Bloc 3:

- el fil principal no toca l'àudio: només deixa **encàrrecs** (`note_on`, `note_off`) en una llista que el callback recull a cada bloc;
- cada nota és un sinus amb el 2n harmònic i un decaïment exponencial;
- opcionalment, el callback genera un **metrònom comptant mostres** (`mostra % P`): el rellotge de la targeta, independent de Python. És la referència per escoltar si el seqüenciador va a temps. Click i notes surten pel mateix stream, de manera que la latència de sortida és la mateixa per a tots dos i no afecta la comparació.

**Per què no FluidSynth** (la versió anterior de la sessió en feia servir): cap instal·lació nova per als alumnes. FluidSynth necessita una biblioteca del sistema (brew a Mac, DLL a Windows) més un soundfont. A més, s'ha comprovat al codi de `pyfluidsynth` 1.4.0 que, en un Mac M1 amb un Python que no és de Homebrew, només troba la biblioteca si la variable `HOMEBREW_PREFIX` existeix, cosa que no passa amb Thonny obert des del Dock. L'única alternativa instal·lable amb pip (`tinysoundfont`) no té paquets compilats per a Mac ni Windows. El sinte propi, en canvi, només fa servir `numpy` i `sounddevice`, ja instal·lats al Bloc 3, i fa de repàs del callback i de preview del Bloc 5.

## Timing: què s'ensenya i per què

- **Estratègia A** — `time.sleep(durada)` darrere de cada nota. És el que fa `toca_amb_sleep()` a les demos 1 i 2: funciona, i per això és bona per descobrir-ne el problema després.
- **Estratègia B** — `espera_fins(t_inici + i * pas)`: l'objectiu es calcula des de l'inici i les durades **previstes**, mai des de quan ha acabat l'espera anterior. Un retard puntual no s'arrossega.
- **L'espera de B és híbrida** (dorm fins a 2 ms abans de l'instant objectiu i fa espera activa els darrers 2 ms). Dues raons, totes dues mesurades:
  1. no fa treballar la CPU per res;
  2. l'espera activa pura reté el GIL i **bloqueja el callback d'àudio**. En un MacBook M1, 2 s d'espera activa van fer perdre 1,67 s d'àudio (intervals entre callbacks de 8,7 ms per a blocs d'1,45 ms). Amb l'espera híbrida, 0 ms perduts.
- **La trampa** (`demo_5_la_trampa`) — estratègia B amb 4 ms de feina de CPU per nota: segons Python, retard 0,0 ms; segons el metrònom de la targeta, −199 ms acumulats i 206 ms d'àudio perdut, amb espetecs audibles. És la lliçó del Bloc 3 vista des de l'altra banda: el termini del callback depèn de **tot** el que fa el programa.
- **Mesures de referència** (MacBook M1, Thonny, 140 bpm, 32 corxeres): `time.sleep` es passa uns 4 ms per crida, A acumula 121–128 ms de deriva sense cap feina i 256 ms amb 4 ms de feina per nota; B es manté entre 1 i 5 ms respecte al metrònom. A Linux, l'excés del `sleep` va ser molt menor (6–22 ms en total), i a Windows amb Python ≥ 3.11 també pot ser petit. **Per això la `feina_simulada` calibrada és la garantia** que la diferència se senti a qualsevol màquina; la deriva natural és un bonus que depèn de l'ordinador.
- **macOS no avisa dels talls:** en totes aquestes proves, el senyal `output_underflow` de `sounddevice` no va saltar ni una vegada. Per això `sinte.py` mesura l'àudio perdut comparant el rellotge amb les mostres generades (`perdut_ms()`).

**Es mencionen sense implementar a classe:** fil dedicat amb `queue.Queue` (seqüenciadors interactius) i MIDI Clock (sincronitzar amb un DAW). El clock és el Challenge 2 de l'assignment, i un alumne que va fer un seqüenciador enviant clock des d'una placa Arduino té una font real per provar-lo.

## Moment per moment

### Warm-up (8 min)
Tres preguntes de repàs (delta time, Do central, termini del callback del Bloc 3) i quatre de preview que deixen el dubte obert: temps absolut, durada d'una `Note`, `sleep` repetit i "esperar una hora calculada". Les respostes es tanquen durant la mini-teoria.

### Mini-teoria 1 (17 min)
- Diapositives 2–4 amb `demo_1_notes()`: la taula de `start`/`end` que s'imprimeix ja mostra que el temps és absolut.
- Diapositiva 5 amb `demo_2_arpegiador()` en els tres modes. Avançar que a l'assignment hi afegiran octaves.
- Diapositiva 6: obrir `sinte.py` a Thonny i llegir junts el callback (recollir encàrrecs → sumar veus → metrònom amb `% P`). És repàs del Bloc 3; no s'ha d'explicar tot, només on és cada cosa.

### Mini-teoria 2 (10 min)
Diapositives 7–9. Remarcar que `toca_amb_sleep()` de les demos 1 i 2 **és** l'estratègia A.

### ✏️ Exercici en paper (15 min)
Es fa abans de mesurar, perquè la mesura confirmi (o no) una predicció pròpia. Enunciat a les diapositives 10–11.

**Dades:** 140 bpm, corxeres (pas = 214 ms). Amb l'estratègia A, cada `sleep` es passa 4 ms.

| Nota | Instant ideal (ms) | A: instant real | A: retard | B: retard |
|---|---|---|---|---|
| 1 | 0 | 0 | 0 | 0 |
| 2 | 214 | 218 | 4 | 0–2 |
| 3 | 428 | 436 | 8 | 0–2 |
| 4 | 642 | 654 | 12 | 0–2 |
| 5 | 856 | 872 | 16 | 0–2 |
| 6 | 1070 | 1090 | 20 | 0–2 |
| 7 | 1284 | 1308 | 24 | 0–2 |
| 8 | 1498 | 1526 | 28 | 0–2 |

**Respostes:**
1. Retard de la nota 32 amb A: 31 esperes × 4 ms = **124 ms** (mesurat al MacBook: 121–128 ms).
2. Nota on A ha perdut una semicorxera sencera (107 ms): 4·(n−1) ≥ 107 → **nota 28**.
3. Amb 4 ms de feina entre notes: A deriva 8 ms per nota → **nota 15**. B no canvia: la feina cap dins dels 214 ms del pas.
4. (Per pensar, oralment) I si la feina durés 250 ms? Cap estratègia arriba: B també va tard, perquè no hi ha marge. B corregeix errors puntuals, no fa miracles.

### Demos a Thonny (15 min)
Cada alumne a la seva màquina, amb auriculars si és possible:
- `demo_3_mesura()` i `demo_3_mesura(feina_ms=4)`: el gràfic de la pròpia màquina, comparat amb el paper. Les diferències entre ordinadors (Mac, Windows) són part de la lliçó, no un problema.
- `demo_4_escolta('A')` i `demo_4_escolta('B')`: el hi-hat se separa del click, o s'hi queda enganxat.
- `demo_5_la_trampa()`: espetecs, i la contradicció entre el que diu Python i el que diu l'altaveu.

### Assignment (45 min)
`assignment.py`, a Thonny. Cada part té `escolta_partN()` (🔊) i `comprova_partN()` (✅):
1. **`arpegiador` amb octaves** (extra respecte de la demo): construir la llista estesa i aplicar-hi el mode.
2. **`notes_a_midi` amb tempo, gate i accent** (extra respecte de la demo): `durada = 60/tempo/subdivisio`, `end = start + durada·gate`, accent amb `i % cada == 0`. La invitació a provar `cada=3` sobre 4 notes (3 contra 4) en dona el sentit musical.
3. **`reprodueix` amb l'estratègia B**: per a cada nota, `espera_fins(t_inici + nota.start)` → `note_on` → `espera_fins(t_inici + nota.end)` → `note_off`. L'autotest fa servir un synth fals que **s'encalla 25 ms a la 6a nota**: si les notes següents tornen a lloc, és B; si totes van tard, el retard s'arrossega i l'error ho explica. Això fa que la comprovació sigui determinista a qualsevol màquina, sense dependre de la precisió del `sleep` de cada ordinador.
4. **`el_meu_sequenciador()`**, escrit de principi a fi per l'alumne: ho munta tot, ho escolta i desa el `.mid`.
5. **Reflexió**: delta/absolut ↔ A/B, la trampa, i les mesures de la pròpia màquina comparades amb el paper.

**Criteris mínims:** autotests 1–3 en verd; seqüència final de ≥ 16 notes amb ≥ 3 alçades diferents; reflexió escrita.

**Challenges:** (1) baix + arpegi: esdeveniments de dos instruments en ordre de temps; (2) clock extern amb `rtmidi2` (DAW per IAC o Arduino); (3) seqüenciador precís a la mostra, dins el callback: la base per a la plantilla Looper/bassline del projecte final.

### Tancament (10 min)
Bloc 4 complet: protocol MIDI, fitxers, seqüenciació, timing. Preview del Bloc 5: el callback de `sinte.py` és el germà petit del sintetitzador que construiran (oscil·ladors, ADSR, FM).

## Preparació

- Entorn de Thonny dels alumnes: `numpy`, `sounddevice`, `matplotlib`, `mido` (ja hi són dels blocs anteriors) + **`pretty_midi`**, que és Python pur i s'instal·la des de *Tools → Manage packages*. Cap instal·lació fora de Thonny.
- `sinte.py` ha d'estar a la mateixa carpeta que `exemples.py` i `assignment.py`.
- Auriculars per a les demos 4 i 5 (amb 6–8 ordinadors sonant alhora, la diferència A/B es perd per l'altaveu).

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `assignment.py` — assignment Thonny (5 parts + challenges)
- `recursos/sinte.py` — sintetitzador mínim + metrònom + `espera_fins` + `feina_simulada` (proporcionat, es llegeix)
- `recursos/exemples.py` — demo guiada a Thonny: `demo_1` … `demo_5`
- `recursos/cheat_sheet.md` — referència per als alumnes
- `recursos/slides_outline.md` — 16 diapositives (incloent-hi l'exercici en paper)
- `recursos/warmup_quiz.md` — 7 preguntes per a Google Forms
- `_solucions/solucio.py` i `_solucions/S07_challenges_solucio.py`

**Eliminats respecte de la versió anterior:** `notebook.ipynb` (substituït per `assignment.py`), `recursos/patches_bloc4b.ipynb` (substituït per `exemples.py`), `recursos/midisynth.py` (substituït per `sinte.py`).

## Validació feta

- Totes les demos, l'assignment i els challenges s'han executat contra un stream d'àudio simulat. Autotests: en verd amb la solució; amb l'assignment buit i amb versions errònies (estratègia A, sense `note_off`), fallen amb missatges que orienten.
- Les mesures de timing, el metrònom, l'espera híbrida i la trampa s'han provat en un MacBook M1 amb Thonny.

## Pendent / a revisar

- [ ] Muntar el Google Form a partir de `warmup_quiz.md`
- [ ] Muntar les Google Slides a partir de `slides_outline.md` (el gràfic de la diapositiva 12 es pot capturar de `demo_3_mesura()`)
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Provar `exemples.py` i `assignment.py` en almenys un Windows: latència del stream, excés de `time.sleep` i `demo_5_la_trampa()`
- [ ] Comprovar que `sync-public.sh` inclou `assignment.py`, `recursos/sinte.py` i `recursos/exemples.py`
