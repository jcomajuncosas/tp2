# Warm-up — Projecte final, presentació de l'ensemble
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 8-10 minuts. Repàs ampli de tot el curs — avui no s'introdueix cap concepte tècnic nou, només arquitectura d'ensemble, per això les preguntes cobreixen tot el recorregut.

---

### Pregunta 1 — Repàs Bloc 3 (temps real)

**Per processar àudio en directe (micro o sortida), quina funció és la peça central que es crida repetidament, sola, sense que tu la cridis explícitament?**

- A) `main()`
- ✅ B) El `callback` que passes a `sd.Stream`
- C) `process(n)`
- D) `sd.play()`

---

### Pregunta 2 — Repàs Bloc 4 (MIDI)

**Quin missatge MIDI rebs quan deixes anar una tecla d'un controlador?**

- A) `note_on` amb velocity 0 o `note_off` (totes dues formes existeixen)
- B) Sempre `note_off`, mai `note_on`
- C) `control_change`
- D) MIDI no envia res en deixar anar una tecla

*(Nota: l'opció correcta és la A — algun controlador envia `note_on` amb velocity 0 en lloc de `note_off`, per això cal gestionar-los tots dos.)*

---

### Pregunta 3 — Repàs Bloc 5 (síntesi amb classes)

**Quina és la diferència principal entre un `Oscillator` i un `Envelope`?**

- A) Són la mateixa cosa amb noms diferents
- ✅ B) L'`Oscillator` "sona sempre"; l'`Envelope` dona forma temporal a la nota (Attack a note_on, Release a note_off)
- C) L'`Envelope` genera so; l'`Oscillator` només el modula
- D) Un treballa en temps real i l'altre no

---

### Pregunta 4 — Repàs Bloc 6-7 (features i classificació)

**Per distingir automàticament un cop de kick d'un cop de hi-hat a partir del so, quin tipus d'enfocament hem fet servir tot el curs?**

- A) Heurístiques fixes (per exemple "si l'energia supera un llindar fix, és un kick")
- ✅ B) Classificació supervisada: l'usuari ensenya exemples reals abans de fer servir el sistema
- C) Clustering automàtic sense exemples previs
- D) Sempre s'ha fet a ull, mai amb codi

---

### Pregunta 5 — Intuïció: instruments autònoms

**Si cinc persones toquen cinc instruments diferents en un concert, sense cap connexió de xarxa entre els seus ordinadors, com es manté tot sincronitzat?**

- A) No es pot fer música en grup sense sincronitzar els ordinadors per codi
- ✅ B) Com qualsevol ensemble musical real: escoltant-se els uns als altres
- C) Cal un servidor central que marqui el tempo a tothom
- D) Cal que tots toquin exactament la mateixa partitura nota a nota

---

### Pregunta 6 — Intuïció: un vocoder

**Si sents una veu robòtica que canta exactament les notes que es toquen amb un teclat, però la lletra/timbre ve d'algú parlant per un micro alhora, quina creus que és la font del "to" (l'alçada) que sents?**

- A) El micro, exclusivament
- ✅ B) Un oscil·lador controlat pel teclat MIDI, "esculpit" amb el timbre captat pel micro
- C) Sempre és la veu original sense cap processament
- D) Un sample pregravat fix

---

### Pregunta 7 — Repàs TP1

**Per fer que un comptador de "pas" torni a 0 després d'arribar al darrer pas d'una seqüència (per exemple, un cicle de 8 passos), quina operació matemàtica ja coneguda de TP1 és la clau?**

- A) Divisió
- ✅ B) Mòdul (`%`)
- C) Resta
- D) Potència
