# Slides — Projecte final: presentació de l'ensemble
### L'ensemble de 5 instruments autònoms

> **Instruccions de muntatge:** Mateix estil que la resta del curs. Temps estimat: 20-25 min (és més llarga que una sessió normal perquè presenta 5 rols sencers, no un sol concepte).

---

### Diapositiva 1 — Portada
**Projecte final TP2**
*Un ensemble de 5 instruments autònoms, programats per vosaltres*

---

### Diapositiva 2 — On érem
- Heu après a generar so (Blocs 1-2), processar-lo en temps real (Bloc 3), controlar-lo per MIDI (Bloc 4), sintetitzar-lo amb classes pròpies (Bloc 5), i analitzar-lo (Blocs 6-7)
- Avui: ajuntar-ho tot en un instrument real, pensat per a un concert
- 🎤 *Aquest no és un exercici més — és la peça que tocareu en directe*

---

### Diapositiva 3 — L'ensemble: 5 rols
- **Sinte** — síntesi clàssica controlada per MIDI
- **Drum-replacer** — beatbox amb classificació de cops en temps real
- **Looper/bassline** — seqüenciador melòdic amb tempo propi
- **Efecte adaptatiu** — un instrument acústic transformat pel seu propi timbre
- **Vocoder** — veu + nota MIDI, l'efecte robòtic clàssic

---

### Diapositiva 4 — Regla d'or: autonomia total
- **Cap instrument depèn d'un altre**
- Sense xarxa entre ordinadors, sense tempo compartit per codi
- 🎤 *Sou músics: us heu d'escoltar i ajustar els uns als altres, com en qualsevol ensemble real — no com un sistema sincronitzat per software*

---

### Diapositiva 5 — Com és cada template
- `<rol>.py` — el codi, amb un **nucli mínim** (TODO) ja arquitecturat
- `README.md` — com funciona, controls, què cal completar, extensions opcionals
- Les peces de disseny difícils ja estan resoltes — el TODO és la part amb més valor d'aprenentatge, no tota la feina

---

### Diapositiva 6 — Rol 1: Sinte
- `signalflow` + MIDI — la "graduació" cap a una llibreria professional
- Mateix concepte de S8-S9 (Oscillator/Envelope), ara amb eines reals
- Nota MIDI → freqüència, velocity → amplitud, ADSR amb `gate`

---

### Diapositiva 7 — Rol 2: Drum-replacer
- Beatbox: tu fas els sons amb la boca, l'ordinador els substitueix
- Fase ENSENYAR (graves exemples de kick/hihat) abans de fase TOCAR
- Classificació **supervisada real** — no heurístiques fixes

---

### Diapositiva 8 — Rol 3: Looper/bassline
- Step-sequencer melòdic (no percussiu — això ja ho fa el Drum-replacer)
- Tu marques el tempo amb un tap manual, com un baixista real
- Cada pas: la nota que vulguis, lliure

---

### Diapositiva 9 — Rol 4: Efecte adaptatiu
- Un instrument acústic connectat (jack/interface)
- 3 descriptors del teu propi so → 3 efectes simultanis
- El "cablejat" descriptor→efecte és una decisió musical vostra

---

### Diapositiva 10 — Rol 5: Vocoder
- "Cantant solista": veu (timbre) + nota MIDI (alçada)
- Banc de 16 filtres, igual concepte que els vocoders clàssics dels anys 70-80
- 🎤 *Pensa en Kraftwerk, Daft Punk — és exactament aquest mecanisme*

---

### Diapositiva 11 — Ara: tria de rol
- Grup → repartiu-vos els 5 rols (individual o en parelles segons la mida real)
- Llegiu el `README.md` sencer del vostre rol ABANS de tocar codi
- Després, obriu el `.py` i llegiu-lo sencer abans del primer TODO

---

### Diapositiva 12 — A partir d'ara
- Feina autònoma, al vostre ritme — no hi ha "avui toca arribar fins aquí"
- Si acabeu el nucli mínim, hi ha extensions opcionals al vostre `README.md`
- I si voleu anar més enllà encara, `recursos/reptes_opcionals.md` té reptes transversals
