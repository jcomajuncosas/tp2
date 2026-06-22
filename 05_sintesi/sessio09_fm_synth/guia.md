# Sessió 9 — Bloc 5b: Arquitectura UGen, FM i integració temps real + MIDI

**Bloc temàtic:** 05_sintesi
**Tipus de sessió:** ⚠️ DENSA — 5 blocs de contingut nou en 2h. Menys workshop lliure que de costum; prioritzar avançar la demo guiada per davant del repte obert.
**Durada:** 2h

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:28 | Mini-teoria (Slides): UGen, control rate | `recursos/slides_outline.md` |
| 0:28 – 1:15 | Demo guiada (extensa — és el cos de la sessió) | `exemples.py` (Thonny) |
| 1:15 – 1:45 | Mini-repte curt i acotat | `assignment.py` |
| 1:45 – 2:00 | Tancament + preview Sessió 10 (consolidació Bloc 5) | — |

**Nota sobre el repartiment:** a diferència de la S8, aquí el pes principal recau en la **demo guiada**, no en el workshop. El contingut (UGen + control rate + FM + integració MIDI + tast signalflow) és dens; millor garantir que tothom ha vist i entès els 5 punts en directe que deixar mig grup encallat en un repte llarg. El mini-repte de S9 és intencionadament més curt que els habituals — la consolidació real arriba a la Sessió 10.

---

## Objectius

1. Entendre per què `generate(duration)` (S8) provoca discontinuïtats de fase si s'encadena, i com `process(n_samples)` ho resol mantenint estat persistent
2. Conèixer l'arquetip **UGen**: una interfície comuna (`process()`) que qualsevol component d'un sintetitzador modular pot implementar — connexió directa amb el model mental de Max/Pd
3. Distingir **control rate** (un LFO modulant suaument un paràmetre — vibrato) d'**audio rate** (el so que sentim directament), amb un exemple net on l'efecte és clarament perceptible com a "control", no com a timbre
4. Construir FM synthesis com **a cas d'UGens encadenats a audio rate** (NO com a exemple de control rate): un modulador d'índex de modulació gran (`I`) varia la freqüència d'un portador i genera un timbre nou, tots dos amb la mateixa interfície `process()`
5. Connectar les classes UGen al callback de `sounddevice` (Bloc 3) i a `note_on`/`note_off` (Bloc 4) — el punt on tot el curs conflueix pràcticament
6. Veure un tast breu de `signalflow` com a contrast: la mateixa idea, implementada professionalment (i activament mantinguda, a diferència de `pyo`)

## Decisions de disseny importants (llegir abans d'ensenyar)

**Per què "conveni sense herència formal" i no `class Oscillator(UGen)`:** es va valorar fer-ho amb herència real (classe base `UGen` amb `process()` abstracte), però es descarta conscientment. Aquest grup només té TP1 (Python bàsic) com a base — l'experiència prèvia del docent amb herència en cohorts antigues (Processing+MINIM) **no aplica als alumnes actuals**, que no l'han vist. Ensenyar herència real aquí seria afegir mecànica de llenguatge nova en una sessió ja densa. En lloc d'això, `Oscillator`, `LFO` i `Envelope` simplement **comparteixen el mateix nom de mètode (`process`) per conveni** — la idea de "interfície comuna" s'ensenya com a disseny, no com a herència Python. Si en el futur el grup tingués més bagatge OOP, val la pena revisar aquesta decisió.

**Per què es mostra explícitament l'evolució "abans/després":** en lloc d'introduir `process()` directament, `exemples.py` comença recordant `OscillatorBatch.generate()` (S8) i fa sentir el click de fase real abans de mostrar la solució. Costa ~3 minuts més que anar directe al UGen, però fa molt més evident *per què* calia el canvi — no és arquitectura per arquitectura.

**Per què cal explicar primer "control rate" de debò abans de mostrar el nostre codi:** en un motor DSP real, un generador de control (LFO, envolupant) calcula els SEUS PROPIS valors a una freqüència molt inferior a la d'àudio (p.ex. 100-200 valors/segon en lloc de 44100/s) — perquè el paràmetre que controla no necessita més resolució que aquesta. **El nostre `LFO` a `exemples.py` NO fa això — és un híbrid pedagògic**: reutilitza exactament la mateixa lògica que `Oscillator` (calcula a 44100Hz igual que el portador) i només "fingim" que està a control rate llegint-ne l'última mostra de cada bloc (`lfo_out[-1]`). És important dir-ho explícitament als alumnes per evitar que pensin que el codi fa quelcom que no fa.

**Per què la Secció 3 (vibrato) i la Secció 4 (FM) NO són el mateix exemple amb diferents números, un cop aclarit l'híbrid:** la diferència NO és perceptiva ni d'estalvi de CPU (en cap dels dos casos hi ha estalvi: el `process(n)` del modulador calcula sempre el bloc sencer, només en llegim l'última mostra). El motiu real és **si llegir el modulador a baixa resolució (1 valor/bloc) perd informació rellevant o no**:
- **Vibrato (Secció 3):** el modulador (LFO, 5Hz) es mou tan lent que el seu valor amb prou feines canvia entre la primera i l'última mostra del bloc — llegir-ne només 1 valor per bloc no perd res perceptible.
- **FM (Secció 4):** el modulador es mou a freqüència d'àudio (80Hz) — entre la primera i l'última mostra del bloc de 512 ja ha canviat prou com perquè agafar només `[-1]` sigui un sota-mostreig real, amb aliasing/artefactes coneguts.

**Important per evitar confusió amb els alumnes:** un senyal no "és" control rate per naturalesa — `LFO` i `Oscillator` són exactament la mateixa classe; el que distingeix els dos usos és la freqüència a què es mou el modulador. **L'estalvi de CPU real de processar en blocs** (menys overhead de crida Python/NumPy que mostra a mostra) és un tema diferent que ja apliquem des de la Secció 2 (tant pel modulador com pel portador, sense distinció) i que es quantificarà amb profiling a la Sessió 10 — no s'ha de confondre amb la qüestió de pèrdua d'informació al llegir el modulador a 1 valor/bloc.

Verificat objectivament amb anàlisi espectral: el vibrato per defecte (`depth=6`) ocupa ~20Hz d'amplada de banda al voltant de la fonamental; la FM per defecte (`I=200`) n'ocupa ~480Hz — gairebé 24 vegades més (conseqüència del sota-mostreig del modulador, no la causa). **Referència real per ancorar-ho amb els alumnes:** el Yamaha DX7 té un únic LFO global que es pot enrutar com a vibrato (pitch) i/o tremolo (amplitud) de qualsevol operador.

**Per què FM amb índex de modulació (`I`, no `beta`) i no la versió més mínima:** es decideix incloure el paràmetre clàssic `I` (notació estàndard de Chowning i dels sintetitzadors FM clàssics com el DX7; `beta` apareix en alguns textos però `I` és la més habitual) malgrat la simplicitat general, perquè dona rigor conceptual sense complicar el codi (és només un multiplicador més). Es manté deliberadament **lluny** de FM "de veritat" mostra-a-mostra (això és Challenge opcional) — a `exemples.py` el portador actualitza la freqüència un cop per bloc (cada 512 mostres), no cada mostra; cal ser explícit amb els alumnes que això introdueix artefactes coneguts, no és l'FM "real" dels sintetitzadors clàssics.

**Per què `Envelope` també es reescriu com a UGen (`process()` enlloc de `generate()`):** a S8 `Envelope.generate(note_duration)` calculava tota la corba ADSR d'un cop, coneixent par endavant la durada de la nota. Però en temps real (callback) no sabem quan arribarà el `note_off` — cal que l'envolvent avanci bloc a bloc i reaccioni a `note_on()`/`note_off()` quan arriben, mantenint un `stage` intern (`'idle' | 'attack' | 'decay' | 'sustain' | 'release'`). Aquest redisseny és necessari per a la integració amb MIDI temps real (Secció 6), no un caprici arquitectònic.

**Per què hi ha una Secció 6b (simulació) a banda de la 6 (MIDI real):** no tots els ordinadors/aules tindran un teclat MIDI connectat. La 6b reprodueix exactament el mateix patró (`note_on`/`note_off` disparant l'envolvent dins un callback de `sounddevice`) però amb una seqüència de notes programada en lloc d'un port MIDI físic — així ningú es queda sense veure la integració completa per manca de hardware.

## Connexions amb sessions anteriors

- **Sessió 8:** `Oscillator`/`Envelope` es recuperen i es redissenyen explícitament — no són classes noves, és la mateixa idea amb una interfície més robusta.
- **Sessió 5 (callback, `sd.Stream`):** el patró `outdata[:, 0] = ...` dins un callback és exactament el de la Secció 6/6b d'avui, ara alimentat per les classes UGen en lloc d'efectes de senyal directe.
- **Sessió 7 (MIDI, timing):** `note_to_freq` ja es coneixia de S8; avui es connecta amb un port MIDI real via `mido` (lectura, no escriptura com a S6-S7).
- **Max/Pd (any de gap):** l'arquetip UGen es presenta explícitament com "programar així és cablejar un sintetitzador modular" — connexió conceptual directa amb el patching.

## Materials necessaris

- Cap fitxer d'àudio nou necessari aquesta sessió.
- **Opcional:** un controlador MIDI USB/Bluetooth per a qui en tingui, per provar la Secció 6 amb hardware real (la 6b cobreix qui no en tingui).

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `exemples.py` — demo per a Thonny (sounddevice + mido opcional), 7 seccions progressives
- `assignment.py` — mini-repte curt per a Thonny (temps real, com S4-S5): completar una FM senzilla amb `process()`
- `recursos/cheat_sheet.md` — arquetip UGen, control rate, FM, integració MIDI
- `recursos/warmup_quiz.md` — 7 preguntes per a Google Forms
- `recursos/slides_outline.md` — diapositives
- `recursos/patches_bloc5b.ipynb` — demo Colab (teoria/FM conceptual; NO la part de temps real/MIDI, que només funciona a Thonny)
- `recursos/challenges.md` — Challenges opcionals: rendiment sample-by-sample vs. buffered, implementació completa amb `signalflow`

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Provar `exemples.py` localment, incloent la Secció 6 amb un teclat MIDI real si n'hi ha disponible a l'aula
- [ ] Decidir si `signalflow` s'instal·la a l'ordinador de l'aula per a la demo de la Secció 7 (NO és exercici, però la demo en directe és més efectiva que només mostrar codi)
- [ ] **Per a Sessió 10:** dos pendents relacionats però diferents, a NO confondre:
  1. Comparativa quantitativa de quan llegir un modulador a baixa resolució (1 valor/bloc) introdueix artefactes audibles vs. quan no (depèn de la freqüència del modulador) — relacionat amb aliasing, no amb CPU.
  2. Profiling real de l'estalvi de processar en blocs (com fem des de la Secció 2) vs. mostra a mostra en Python pur — això sí és una qüestió de CPU/rendiment, i ja hi ha un Challenge relacionat (`recursos/challenges.md`, Challenge 1) que es pot ampliar o consolidar aquí.
  Decisió presa explícitament de NO incloure cap dels dos a S9 per no sobrecarregar-la més.
