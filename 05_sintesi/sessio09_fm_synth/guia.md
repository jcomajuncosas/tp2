# Sessió 9 — Bloc 5b: Síntesi FM i envolvents amb estat

**Bloc temàtic:** 05_sintesi
**Tipus de sessió:** Midterm de diagnòstic + workshop intercalat. Cicles curts de mini-explicació → predicció → picar → escoltar junts. No hi ha bloc de teoria llarg ni demo per mirar: el notebook dels alumnes **és** la demo (el docent el projecta i avança amb ells).
**Entorn:** Colab per al nucli (parts 1-6: arrays, espectres, inspecció d'objectes) + Thonny als darrers 15' (la mateixa veu, en temps real).
**Durada:** 2h

> **Redisseny (nov. 2026).** Aquesta versió substitueix la sessió "densa" original (UGen + control rate + FM per blocs + MIDI real + signalflow). Motius: (1) les tasques de la S08 es van percebre com una estafa: copiar exemples i enunciats que donaven el codi; (2) el model magistral desconnecta el grup; (3) **la "FM" original no era FM**: actualitzant el portador un cop per bloc, el modulador de 80 Hz es llegeix a 86 Hz i el que sona és un àlies de ~6 Hz, una sirena entre 240 i 640 Hz sense cap banda lateral (verificat numèricament). Aquest error s'ha convertit en el fil conductor de la sessió. Signalflow i el MIDI amb teclat real passen a la S10.

---

## Estructura de la sessió

| Temps | Activitat | Material | Mode |
|---|---|---|---|
| 0:00 – 0:20 | **Midterm** de diagnòstic (substitueix el warm-up) | `recursos/midterm.md` (imprès) | individual, en paper |
| 0:20 – 0:23 | On som: de `generate` a `process(n)` | slides 1-2 | |
| 0:23 – 0:35 | **Part 1**: `process(n)`, `_ona`, vibrato | `notebook.ipynb` | piquen |
| 0:35 – 0:50 | **Part 2**: "FM" per blocs → sirena → paper → detectius | notebook + `recursos/full_aliasing.pdf` | predicció oral + paper + piquen |
| 0:50 – 1:05 | **Part 3**: el canvi estructural → FM de debò | notebook, slides 4-5 | piquen |
| 1:05 – 1:15 | **Part 4**: `Envelope` amb estat (donada): predir i inspeccionar | notebook, slide 6 | prediuen + executen |
| 1:15 – 1:30 | **Part 5**: `VeuFM` (esbós en paper 3' + codi) | notebook, slide 7 | paper + piquen |
| 1:30 – 1:45 | **Thonny**: la seva veu en temps real | `assignment.py` | piquen |
| 1:45 – 1:50 | Tancament + preview S10 | slide 8 | |
| 1:50 – 2:00 | Marge | | |

**Mínim a classe:** parts 1-4. Les parts 5-6 i Thonny es poden acabar a casa (el notebook ho permet sense dependre de la classe). Si el grup va lent, retalla la taula de timbres de la Part 5 (fer-ne només una fila a classe) abans que la Part 4.

---

## Objectius

1. Canviar la interfície de l'oscil·lador a `process(n_samples)` (el callback parla en mostres) i **refactoritzar** el codi repetit en un mètode intern `_ona`.
2. Sentir i entendre per què llegir un modulador ràpid un cop per bloc no és FM: **aliasing del modulador**. Connexió directa amb la S02 (mostreig) i amb el paper de la S05.
3. Fer el **canvi estructural** que ho arregla (freqüència per a cada mostra, `process_freqs`) i percebre'n l'efecte: la "sirena" es converteix en un timbre amb bandes laterals a `fc ± k·fm`.
4. Fer servir l'**índex de modulació de Chowning** (`I`, sense unitats: excursió = `I × fm`) i la relació **C:M** (`ratio`) per explorar timbres harmònics i inharmònics.
5. Llegir i entendre una **màquina d'estats** (`Envelope` amb `stage`), feta per a temps real.
6. Muntar una classe composta (`VeuFM`) amb el **nivell d'abstracció adequat** (una veu, no un sintetitzador), reutilitzant les classes que ja tenen.
7. Tocar-la en temps real dins un callback, amb la velocity controlant volum **i** brillantor.

## Decisions de disseny (llegir abans d'ensenyar)

**Regla de tasques (des d'aquesta sessió, "no pot tornar a passar").** Cap TODO és una còpia d'un exemple ni dona el codi a l'enunciat. Cada tasca combina: (a) **variacions de paràmetres** que obliguen a recórrer el codi; (b) **fragments picats** on l'enunciat diu *què* i amb quina signatura, mai *com*; (c) com a mínim una **intervenció estructural** amb efecte audible. Prova de control: si una pista conté línies de la solució, no és una pista. Les pistes només poden donar noms d'API.

**Per què el fil conductor és un error.** La "FM" per blocs de la versió anterior era el mateix codi que el vibrato amb altres números. Ara és exactament això, però a propòsit: els alumnes reutilitzen la seva funció `vibrato`, prediuen un timbre metàl·lic i senten una sirena. La sorpresa obre la necessitat del canvi estructural, i el canvi té recompensa sonora immediata. És el "moment de flow" que buscàvem.

**Les xifres de la Part 2 (verificades).** Bloc de 512 mostres a 44,1 kHz → el modulador es llegeix 86,13 cops/s. Modulador de 80 Hz → àlies a 86,13 − 80 = 6,13 Hz; el portador oscil·la entre ~240 i ~640 Hz (440 ± 200). Amb el modulador a 86,13 Hz **la sirena es congela**: tots els blocs el llegeixen a la mateixa fase i la nota queda fixa (a 437,5 Hz si llegeixen l'últim valor del bloc; amb un altre valor, a una altra afinació; amb la mitjana del bloc, exactament a 440 Hz). L'enunciat deixa triar quin valor del bloc es llegeix i l'autotest accepta qualsevol mostra o la mitjana. Si algú fa servir la **mitjana**, la sirena a 80 Hz queda molt atenuada (±15 Hz en lloc de ±200): mitjanar és un filtre passa-baixos rudimentari, és a dir, un **antialiasing**. Bon moment per comentar-ho, però no resol el problema: continua sense haver-hi bandes laterals. Al doble, 172,27 Hz, **es torna a congelar** (435,1 Hz): qualsevol múltiple de la freqüència de bloc fa el mateix. Amb 70 Hz, sirena de ~16 Hz; amb 90 Hz, de ~4 Hz. (No fer servir la meitat, 43 Hz, com a pregunta: el modulador es llegeix gairebé a fase 0 i π i la diferència és de ±1 Hz, inaudible.)

**Per què `process_freqs` és un mètode nou i no un canvi a `process`.** Mantenir `process(n)` vectoritzat (ràpid, per a freqüència constant) i afegir `process_freqs(freqs)` amb un bucle mostra a mostra fa visible l'estructura: el bucle és el preu d'una freqüència que canvia a cada mostra. És un bucle sobre un array amb estat, just el tipus de codi on se senten útils. La versió vectoritzada (`np.cumsum`) i el profiling de totes dues es fan a la **S10** sobre el seu propi codi (Challenge 4 com a avançament: ~24 vegades més lent, verificat, però molt dins el temps real).

**Per què el refactor `_ona` a la Part 1.** Sense ell, `process_freqs` hauria de tornar a copiar l'`if/elif` de formes d'ona (tercera còpia). Amb ell, a la Part 3 el mètode nou només calcula fases i crida `_ona`: el refactor de la Part 1 "paga" a la Part 3, i ho noten. També els fa cridar un mètode des d'un altre (`self._ona(...)`), cosa nova per a ells.

**Per què `I` sense unitats (correcció respecte a la versió anterior).** El material antic deia "I = índex, en Hz d'excursió" i feia servir I = 200. És incorrecte: l'índex de Chowning és **excursió / freqüència del modulador** (adimensional). 200 Hz d'excursió amb fm = 80 Hz és **I = 2,5**. Amb aquesta definició, els parcials depenen només de I (via les funcions de Bessel), i la relació C:M i I són independents de la nota: és el que permet que un preset soni igual a tot el teclat.

**Per què l'`Envelope` es dona feta, però s'inspecciona.** Escriure una màquina d'estats és massa per a aquesta sessió, però entendre-la és imprescindible per a la S10 (kit de percussió) i el projecte. La Part 4 obliga a **predir** el bloc de cada transició (attack 0,01 s = 441 mostres → decay ja al bloc 0; 441 + 4410 = 4851 → sustain al bloc 9) i a observar dos casos que només passen en temps real (note_off durant l'attack, note_on durant el release). El midterm 1c (una mini-màquina d'estats amb `if/elif`) prepara exactament aquesta lectura.

**Correcció de l'`Envelope` respecte a la versió anterior (clics).** L'antiga feia `continue` en canviar d'estat i deixava **una mostra a 0**: salt 1,0 → 0,0 → 1,0 en passar a decay, i 0,7 → 0,0 → 0,7 en passar a sustain (mostres 441 i 4852; verificat). La nova és **per increments** (`self._pas`): cap mostra es perd, el release parteix del nivell actual (sense salt si es deixa anar a mitja pujada) i un note_on a mig release puja des d'on és (sense clic). ⚠️ **La S10 en té una còpia de la versió antiga** (pendent a la revisió de la S10).

**Per què "una veu" i l'esbós en paper de la Part 5.** A la S08, al disseny de la groovebox, els alumnes no sabien que podien reutilitzar les classes existents ni quin nivell d'abstracció calia (una classe Groovebox? Sequencer?). Aquí l'enunciat ho diu explícitament: una sola veu, i la pregunta "quines classes ja tens i quantes de cada". Solució esperada: 2 `Oscillator` + 1 `Envelope` a dins; configuració = `ratio`, `I_max`, ADSR; estat = la nota i el guany actuals (i, a dins, les fases i l'stage).

**Per què `I = I_max × envolvent`.** És la troballa de Chowning (1973) per a metalls i campanes: l'espectre s'enriqueix amb la intensitat. Una línia de codi, i la diferència entre "un so" i "un instrument". Verificat: amb `ratio 1`, `I_max 5`, la brillantor (amplada de banda a −20 dB) passa de ~1540 Hz a l'atac a ~660 Hz a la cua.

**La taula de timbres (verificat a 196 Hz, I = 3):** ratio 1 i 2 → parcials harmònics (multiples de 196); ratio 1,41 → parcials inharmònics (81, 357, 472, 632… Hz): campana. Ratio **3,5 → la nota sona una octava més greu**: els parcials (490, 882, 1176, 1568…) són tots múltiples de 98 Hz. Bona pregunta per a classe: "quina nota sents?".

**Thonny: lliurable curt.** Enganxen les seves classes (comprovació que el codi viu fora del notebook), piquen una peça (velocity → índex, corba lliure; l'autotest accepta qualsevol corba creixent amb un mínim de timbre) i trien preset i seqüència. El `Reproductor` (un UGen que dispara note_on/off dins el callback, amb precisió de bloc) i el callback es donen fets i visibles. Cost mesurat: la `VeuFM` amb bucle mostra a mostra fa ~0,25 ms per bloc (límit 11,6 ms); 4 veus, ~0,9 ms.

**Què s'ha mogut a la S10.** Signalflow (el tast de la S09 es fusiona amb el de la S10; ara té més sentit: ja saben distingir FM de debò de la falsa) i el MIDI amb teclat real (passa a ser el context del kit de percussió de la S10). Les instruccions d'instal·lació de signalflow (venv `--copies`, Conda, Thonny) s'han mogut a `sessio10_consolidacio/recursos/challenges.md`.

**Aproximacions a dir en veu alta:**
- El `Reproductor` dispara les notes amb precisió de **bloc** (11,6 ms), no de mostra. Per a precisió de mostra: el lookahead de la S07.
- Les ones quadrada i de dent de serra de `scipy` són ingènues (aliasing a notes agudes). En FM fem servir sinus.
- Amb `ratio = 1` apareix una component a 0 Hz (DC): la banda lateral fc − fm. És real, no un error.

---

## Midterm (0:00 – 0:20)

Full: `recursos/midterm.md` (imprimir-ne un per alumne; `build.sh` en genera el .docx). Solucions verificades i graella: `recursos/midterm_graella.md` (privat).

- **No compta per a la nota.** Serveix per avaluar les nostres accions correctives (aquest curs i els vinents), no per penalitzar el que no s'ha dissenyat bé didàcticament. Dir-ho així als alumnes: un raonament a mitges ens informa més que una resposta en blanc.
- Individual, sense ordinador, 20' estrictes.
- Tres parts: (1) llegir i predir (bucle amb `%` i llista, talls NumPy, `if/elif` dins un bucle); (2) seguir l'estat d'un objecte en una taula + trobar un `self.` oblidat; (3) escriure `compta_pics(so, llindar)` des de zero (+ índex del primer pic si sobra temps).
- Correcció amb la graella: puntuació 0/1/2 i, sobretot, **lletres de tipus d'error** (B, T, N, C, E, L, F, A, X). L'anàlisi es fa sobre les lletres.

## Guió de la sessió, part per part

**Part 1 (12').** Slide 2: el callback demana mostres. Que piquin `process`. Quan ho tinguin, pregunta oral: "teniu ara el mateix `if/elif` dues vegades: què passa si demà trobeu un error a la dent de serra?" → refactor `_ona`. Pregunta de l'enunciat: `generate` pot ser una línia (`return self.process(...)`). El vibrato: només l'especificació; si s'encallen, la pregunta és "què demana el callback a cada crida?" (no el codi).

**Part 2 (15').** Votació a mà alçada abans d'executar (timbre nou / vibrato ràpid / altra cosa). Executar junts. Repartir `full_aliasing.pdf` (per parelles): marquen els punts, els copien a la gràfica buida, uneixen → ~1,2 cicles en 0,2 s = ~6 Hz. Pregunta 4 del full = `freq_congelada`. Detectius: deixar-los provar valors; el que s'ha d'emportar és "86,13 = blocs per segon".

**Part 3 (15').** Slides 4-5 (què cal canviar; índex de Chowning). Que piquin `process_freqs` (el bucle) i `fm_synth`. El moment clau és la cel·la "abans/després": fer-la sonar en gran, amb els dos espectres. Variacions: I = 0,3 / 1 / 2,5 / 6; `mod_freq` = 440, 880, 620.

**Part 4 (10').** Slide 6 (diagrama d'estats). Prediccions abans d'executar (escriure-les a la pissarra, de diverses persones). Després els dos casos de temps real: que busquin la línia de `process` que evita cada salt (`self._pas = self.level / n_release` i que l'attack suma des del nivell actual).

**Part 5 (15').** Slide 7. Esbós en paper 3' (2 preguntes de l'enunciat). Posada en comú d'un minut: quantes classes a dins? Després piquen. Taula de timbres: si no hi ha temps, una fila a classe i la resta a casa.

**Thonny (15').** Copiar les tres classes a la Part A, `comprova_classes()`, `escolta_demo()`. Part B (velocity → índex). La Part D es pot acabar a casa.

**Tancament (5').** Slide 8: què ha canviat avui a l'estructura (`_ona`, `process_freqs`, la veu composta) i preview de la S10 (mesurarem quant costa el vostre bucle, MIDI real, signalflow).

## Connexions amb sessions anteriors

- **S02 (mostreig):** l'àlies de la Part 2 és el mateix fenomen que el de mostrejar un senyal per sota de Nyquist, aquí aplicat al modulador.
- **S05:** la fase persistent (`fase_sinus`) i els moments en paper; el callback amb `with sd.Stream`.
- **S07:** `note_to_freq`; precisió de bloc vs. lookahead.
- **S08:** `Oscillator` (amb `_phase`), `Envelope`, `Veu` (composició) → `VeuFM`; polimorfisme pel nom de mètode (`process`).

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia (docent)
- `notebook.ipynb` — el workshop i lliurable principal (Colab): parts 1-6, 6 autotests, 4 challenges
- `assignment.py` — la part de Thonny (lliurable curt): parts A-E + challenge de polifonia
- `recursos/cheat_sheet.md` — referència ràpida (alumnes)
- `recursos/slides_outline.md` — 8 diapositives curtes, intercalades (docent)
- `recursos/midterm.md` — full del midterm (privat: només imprès)
- `recursos/midterm_graella.md` — solucions verificades i graella (docent)
- `recursos/full_aliasing.pdf` — full en paper de la Part 2 (privat: només imprès); es regenera amb `recursos/genera_full_aliasing.py`
- Solucions: `_solucions/S09_fm_synth/solucio.ipynb` (notebook), `solucio.py` (Thonny), `S09_challenges_solucio.py`

Retirats en el redisseny: `recursos/exemples.py` i `recursos/patches_bloc5b.ipynb` (la demo ara és el notebook), `recursos/warmup_quiz.md` (el midterm ocupa el seu lloc), `recursos/challenges.md` (els challenges són al notebook i a `assignment.py`; signalflow → S10).

## Pendent / a revisar

- [ ] Imprimir `midterm.md` (un per alumne) i `full_aliasing.pdf` (un per parella)
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Provar `assignment.py` en un ordinador de l'aula (Thonny + sounddevice)
- [ ] Després de la sessió: passar els resultats del midterm a la graella i analitzar-los
- [ ] **Revisió de la S10** (derivada d'aquest redisseny): còpia antiga de l'`Envelope` (clics); el seu Challenge 1 ("FM mostra a mostra") ja és contingut de la S09; absorbir el MIDI real (context del kit) i el tast de signalflow; profiling sobre el `process_freqs` dels alumnes i `np.cumsum`; aplicar la regla de tasques al repte
