# Sessió 8 — Bloc 5a: Síntesi amb classes

**Bloc temàtic:** 05_sintesi
**Tipus de sessió:** Introducció a les classes (OOP aplicat). Ritme tranquil, amb un moment en paper per dissenyar classes abans de programar-les.
**Entorn:** Colab (demo i workshop). Res d'aquesta sessió necessita temps real: tot es genera com a arrays sencers. El temps real arriba a la S09 (Thonny).
**Durada:** 2h

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:28 | Mini-teoria (Slides) | `recursos/slides_outline.md` |
| 0:28 – 0:45 | Demo guiada | `recursos/patches_bloc5a.ipynb` (Colab) |
| 0:45 – 1:00 | Exercici en paper: dissenyar classes | `recursos/exercici_paper.md` (imprès) |
| 1:00 – 1:35 | Workshop | `notebook.ipynb` |
| 1:35 – 1:50 | Marge (15') | Tasca pendent de la S07 / acabar el notebook |
| 1:50 – 2:00 | Tancament + preview S09 | — |

Si el workshop no s'acaba, la Part 5 (seqüència pròpia) i els challenges es poden acabar a casa. Les parts 0–4 són les que cal fer a classe.

---

## Objectius

- Entendre què és una classe (motlle), una instància (objecte concret), `self`, `__init__`, atributs i mètodes
- Entendre **per què** calen: un objecte guarda dades pròpies entre crides, i cada instància les seves
- Distingir **configuració** (`self.freq`, es tria des de fora) d'**estat intern** (`self._phase`, l'objecte el fa evolucionar sol)
- Construir `Oscillator` (timbre, amb fase pròpia), `Envelope` (forma temporal ADSR) i `SamplePlayer` (reproducció de so gravat)
- Combinar objectes dins d'objectes (composició): la classe `Veu`
- Intuir el valor de posar el **mateix nom** a mètodes que fan la mateixa feina (`generate`) — la S09 ho converteix en conveni (`process`)
- Practicar el ritual: esbossar classes a mà (caixes nom / atributs / mètodes) i escriure'n l'esquelet

## Decisions de disseny (llegir abans d'ensenyar)

**Per què Colab i no Thonny:** tot el contingut és offline (arrays sencers, gràfics, `Audio()`), i el dia que s'introdueixen classes convé poder executar cel·la a cel·la, inspeccionar objectes (`osc._phase`, `veu.osc`) i tenir autotests immediats. El problema "tros a tros" del callback es reprodueix offline concatenant trossos de 512 mostres: el brunzit és el mateix que en temps real. Seguint el criteri de la S06, no hi ha versió Thonny d'aquesta sessió (s'ha retirat `exemples.py`).

**Per què la fase (`_phase`) entra ja a la S08 i no a la S09:** sense fase, `Oscillator` només guarda configuració (`freq`, `waveform`) i una funció amb paràmetres faria exactament el mateix — un alumne espavilat preguntaria "per què em compliques la vida amb `self`?". La fase és l'estat que justifica la classe. A més, la S05 ja ho deixava plantejat literalment ("cada oscil·lador necessita la seva [global]… guarda't aquest pensament" / "Pregunta per al Bloc 5"): avui es respon, amb el mateix codi (`increment * np.arange(n)`, `% (2 * np.pi)`). Abans aquest bloc era l'obertura de la S09; s'ha mogut aquí per alleugerir la S09, que era densa. La S09 ara comença des de "ja tenim fase; canviem la interfície a `process(n_samples)` perquè el callback parla en mostres i perquè l'envolvent en temps real també ho necessita".

**Per què `_phase` amb guió baix:** és la manera més barata d'ensenyar visibilitat. Python no té atributs privats: el guió baix és un **conveni** ("estat intern, no el toquis des de fora"). Altres llenguatges (C++, Java) ho fan complir el compilador amb `private`; Python confia en el programador. N'hi ha prou amb una frase i amb el contrast `osc.freq = 880` (correcte) vs `osc._phase = 0` (funciona, però trenca el conveni).

**Per què no hi ha getters/setters (s'ha retirat `set_freq`):** a Python s'accedeix directament als atributs (`osc.freq = 880`). El ritual `get_x()/set_x()` és un hàbit de Java que aquí només afegiria cerimònia. (Si algun dia cal validar un valor en assignar-lo, Python té `property` — fora de l'abast del curs.)

**Per què `SamplePlayer.generate(duration)` (abans `play(gain)`):** fa la mateixa feina que `Oscillator.generate` — retornar `duration` segons de so — i per això porta el mateix nom. Això permet el bucle "polimòrfic" de la demo (secció 9), on una llista barreja oscil·ladors i samples i el bucle no necessita saber qui és qui. És el polimorfisme implícit de Python (*duck typing*): no cal herència, n'hi ha prou que el mètode es digui igual. L'anècdota del `tick()` de STK hi encaixa: allà la idea era bonica però a nivell d'implementació no era polimòrfica; a Python ho és de franc. **No** s'introdueix herència (coherent amb la decisió de la S09). El `gain` passa a ser atribut (`kick.gain = 0.5`), i `generate` retalla o afegeix silenci perquè la durada sigui exacta: així un sample encaixa en un pas de seqüenciador.

**Per què `Envelope` ve feta al notebook:** no aporta res d'OOP (és NumPy de concatenar fases) i el temps del workshop es reserva per a les dues coses noves: escriure una classe sencera des de zero (`SamplePlayer`) i la composició (`Veu`).

**Per què `Veu` és l'extra respecte a la demo:** a la demo, `tocar_nota()` és una funció que crea un oscil·lador i una envolvent nous a cada nota i els llença. L'alumne la converteix en un instrument que es construeix un cop (timbre triat a `__init__`) i toca moltes notes, i hi afegeix la velocity. L'autotest comprova explícitament que l'oscil·lador es crea un sol cop (`veu.osc is osc_inicial`).

**Aproximacions a dir en veu alta (honestedat):**
- `Envelope.generate(note_duration)` coneix la durada de la nota per endavant. En temps real no la sabem (el `note_off` arriba quan arriba): la S09 la reescriu amb estat (`stage`). Avui "`note_on`/`note_off` controlen l'envolvent" és una idea, no codi.
- Si la nota és més curta que attack + decay, l'envolvent fa igualment A i D sencers: la nota dura una mica més del demanat.
- Les ones quadrada i de dent de serra de `scipy` són "ingènues": a notes agudes fan aliasing. Per al registre que fem servir no es nota.

**Per què classes pròpies i no una llibreria:** decisió confirmada. STK (C++) era massa abstracte i Processing+MINIM massa alt nivell (no es copsava l'arquitectura). Construir-ho en NumPy, al mateix nivell que la resta del curs, és l'equilibri correcte. `signalflow` apareix a la S09 com a tast de contrast.

**Per què `SamplePlayer` s'introdueix aquí:** cobreix un forat del disseny original — mai s'havia tractat "disparar un sample sencer com a resposta a un esdeveniment" (model mental de samplers/drum machines), necessari per al rol de drum-replacement del projecte final.

## Connexions amb sessions anteriors

- **Sessió 5:** `fase_sinus` i `fase_ringmod` (globals) → `self._phase` (dins l'objecte). La pregunta oberta de la S05 ("i si en volguéssim 5?") es respon avui: cinc `Oscillator()`, cinc fases, zero globals noves.
- **Sessió 2 (WAV/soundfile):** `SamplePlayer` reutilitza `sf.read`, ara encapsulat.
- **Bloc 4 (MIDI):** `note_to_freq` i la velocity; l'arpegi de la demo reutilitza el patró de seqüenciació.
- **TP1:** classes poc treballades (de fet, per a aquest grup, noves) — aquí cobren sentit per primera vegada.

---

## Exercici en paper — guia per al docent

Full per als alumnes: `recursos/exercici_paper.md` (imprimir-ne un per parella; `build.sh` en genera el .docx). Es fa just després de la demo, per parelles, **sense ordinador**. Durada: ~15'. No s'avalua: és un moment de pensar, com els moments en paper de la S05.

### Per què aquest exercici

- Separa pensar *què és* un objecte (quines dades guarda, què sap fer) de pensar *com ho fa* (el codi). És exactament el que no es va copsar amb STK ni amb MINIM.
- Escriure l'esquelet a mà unes quantes vegades fixa la sintaxi (`class`, `def __init__(self, ...)`, `self.x = x`, `pass`) abans d'haver-la d'escriure al notebook (Part 3, `SamplePlayer` des de zero).
- La posada en comú fa evident que **no hi ha una única descomposició correcta**, però sí descomposicions millors i pitjors.

### Com conduir-lo

1. **Part A (3')** — Llegir la descripció de la groovebox. Subratllar substantius (candidats a classe o atribut) i verbs (candidats a mètode). Tècnica clàssica i molt útil per començar.
2. **Part B (6')** — Una caixa per classe: nom / atributs / mètodes amb signatura (`nom(paràmetres) → retorna`). Marcar amb ★ l'estat intern.
3. **Part C (4')** — Esquelet a mà de dues de les seves classes, seguint el model del full.
4. **Part D (2')** — Comparar amb una altra parella amb les preguntes del full.
5. **Posada en comú a la pissarra (5')** — dibuixar una proposta (la d'una parella, corregida entre tots).

Si va bé de temps, es pot allargar: és el moment que més rendeix de la sessió.

### Solució orientativa (no única)

```
┌──────────────────────────┐   ┌──────────────────────────┐
│ Oscillator               │   │ Envelope                 │
├──────────────────────────┤   ├──────────────────────────┤
│ freq, waveform,          │   │ attack, decay,           │
│ sample_rate              │   │ sustain, release         │
│ ★ _phase                 │   │                          │
├──────────────────────────┤   ├──────────────────────────┤
│ generate(duration)       │   │ generate(note_duration)  │
│   → array                │   │   → array (corba)        │
└──────────────────────────┘   └──────────────────────────┘
          ▲  dins de                    ▲  dins de
┌──────────────────────────────────────────────────────┐
│ Veu  (el baix)                                       │
├──────────────────────────────────────────────────────┤
│ osc (un Oscillator), env (un Envelope)               │
├──────────────────────────────────────────────────────┤
│ nota(note_number, note_duration, velocity) → array   │
└──────────────────────────────────────────────────────┘

┌──────────────────────────┐   ┌──────────────────────────┐
│ SamplePlayer             │   │ Delay                    │
│  (2 instàncies:          │   ├──────────────────────────┤
│   bombo i charles)       │   │ temps_retard, feedback   │
├──────────────────────────┤   │ ★ _buffer, ★ _index      │
│ sample, gain,            │   ├──────────────────────────┤
│ sample_rate              │   │ process(so) → array      │
├──────────────────────────┤   └──────────────────────────┘
│ generate(duration)       │
│   → array                │   ┌──────────────────────────┐
└──────────────────────────┘   │ Patro                    │
                               ├──────────────────────────┤
                               │ notes (llista), tempo    │
                               │ ★ _pas_actual            │
                               ├──────────────────────────┤
                               │ durada_pas() → segons    │
                               │ seguent() → nota         │
                               └──────────────────────────┘
```

Opcionalment, una classe `Groovebox` que conté totes les altres (composició al nivell de dalt de tot).

### Punts de discussió i errors esperables

- **Una classe per sample** (`KickPlayer`, `HihatPlayer`) → és la mateixa classe amb dues instàncies. Regla pràctica: *si només canvien les dades, és la mateixa classe*. És la idea més important de l'exercici.
- **Atributs que haurien de ser paràmetres** (posar `duration` com a atribut de l'oscil·lador): distingir "què *és* l'objecte" (es fixa a `__init__`) de "què li demano *ara*" (paràmetres del mètode).
- **Configuració vs estat (★)**: `_phase`, `_buffer` (la cinta de l'eco de la S05!), `_pas_actual`. L'estat canvia sol mentre l'objecte treballa; la configuració la tria qui l'usa.
- **Composició**: la `Veu` conté un `Oscillator` i un `Envelope`. Moltes parelles posaran els paràmetres ADSR directament a la `Veu`: no és incorrecte, però perden la peça reutilitzable.
- **Noms iguals**: `Oscillator`, `SamplePlayer` i `Veu`... quins fan "la mateixa feina"? `generate` per a les fonts de so. El `Delay` no genera: transforma → `process(so)`. Deixar la pregunta oberta: a la S09 tots els components passen a compartir `process()`.
- **El tempo** és del patró, no de cada so. **"Mentre sona"** (canviar patró/tempo en directe) → estat que canvia en temps real: preview de la S09.
- **El `Delay` és el `delay_buffer` global de la S05** convertit en objecte: dos delays = dues instàncies, zero globals noves.

---

## Materials d'àudio proporcionats

`recursos/audio/kick_sample.wav` — generat sintèticament (mono, 44,1 kHz, 0,3 s), sense problemes de llicència.

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia (docent)
- `notebook.ipynb` — workshop Colab: Part 0 (escalfament), 1 `Oscillator` amb `_phase`, 2 `Envelope` (donada), 3 `SamplePlayer` des de zero, 4 `Veu`, 5 seqüència pròpia; 4 autotests + 1 de consolidació; 4 challenges
- `recursos/cheat_sheet.md` — classes en Python, esquelet, les 4 classes, ADSR, taula resum
- `recursos/warmup_quiz.md` — 7 preguntes per a Google Forms (docent)
- `recursos/slides_outline.md` — diapositives (docent)
- `recursos/patches_bloc5a.ipynb` — demo Colab, 9 seccions
- `recursos/exercici_paper.md` — full imprès de l'exercici en paper (privat: només es reparteix en paper)
- `recursos/audio/kick_sample.wav` — sample d'exemple
- Solució: `_solucions/S08_oscil_ladors_classes/solucio.ipynb`

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Imprimir `exercici_paper.md` (un per parella). És material privat: no és a la llista blanca de `sync-public.sh` i no arriba al repo públic (decisió: només en paper, a classe)
