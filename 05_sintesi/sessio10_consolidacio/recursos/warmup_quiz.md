# Warm-up — Sessió 10
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 5-8 minuts.

---

### Pregunta 1 — Repàs Sessió 9 (UGen i process())

**Per què `process(n_samples)` necessita que la classe guardi `self.phase` entre crides?**

- A) Perquè Python esborra les variables locals en acabar cada funció
- ✅ B) Perquè cada bloc ha de continuar l'ona exactament on l'anterior la va deixar
- C) Perquè `self.phase` es fa servir per triar la forma d'ona
- D) No cal — `process()` sempre comença de zero a cada crida

---

### Pregunta 2 — Repàs Sessió 9 (vibrato vs. FM)

**Què determina si llegir un modulador a "1 valor per bloc" introdueix artefactes audibles o no?**

- A) Si el modulador és sinusoïdal o té una altra forma d'ona
- ✅ B) Si el modulador es mou prou lent perquè el valor amb prou feines canviï dins un bloc
- C) Si s'implementa amb la classe `Oscillator` o amb `LFO`
- D) El nombre de canals d'àudio que s'utilitzin

---

### Pregunta 3 — Intuïció: per què un kick pot ser només una sinusoide

**Un bombo electrònic clàssic sovint NO fa servir cap mostra gravada — només una ona pura. Quina propietat de l'ona creus que és clau per fer-la sonar "com un cop" i no com una nota sostinguda?**

- A) Que sigui una ona quadrada en lloc d'una sinusoide
- ✅ B) Que la freqüència baixi molt ràpid a l'inici, amb una envolvent curta
- C) Que tingui una freqüència molt aguda, per sobre dels 1000Hz
- D) Que s'hi apliqui molta reverberació abundant

---

### Pregunta 4 — Intuïció: el UGen més senzill possible

**Heu vist que `Oscillator` necessita recordar la seva fase entre crides, i `Envelope` necessita recordar en quina fase de l'ADSR es troba. Si volguéssiu generar soroll blanc (valors aleatoris) amb la mateixa interfície `process(n)`, creieu que caldria guardar algun estat entre crides?**

- A) Sí, cal guardar l'últim valor generat per continuar-lo
- ✅ B) No, cada crida pot generar valors aleatoris nous sense dependre de res anterior
- C) Sí, cal guardar quants cops s'ha cridat `process()`
- D) No es pot generar soroll amb aquesta interfície

---

### Pregunta 5 — Predicció (lectura de codi: profiling)

```python
import time
t0 = time.perf_counter()
# ... operació A ...
t1 = time.perf_counter()
print(t1 - t0)
```

**Què mesura exactament `t1 - t0`?**

- A) El nombre d'instruccions executades
- ✅ B) El temps real (en segons) que ha trigat a executar-se l'operació A
- C) La quantitat de memòria RAM utilitzada
- D) El nombre de mostres d'àudio generades

---

### Pregunta 6 — Concepte clau: per què el bucle Python és més lent

**NumPy executa `np.sin()` sobre tot un array de cop, en codi C compilat. Un bucle `for` en Python crida funcions repetidament, mostra a mostra. Per què la primera opció sol ser molt més ràpida per a moltes dades?**

- A) Perquè els arrays de NumPy ocupen menys espai en disc
- ✅ B) Perquè cada crida individual a una funció té un cost fix que es multiplica moltes vegades
- C) Perquè NumPy executa el codi en un servidor extern al núvol
- D) No hi ha cap diferència real de velocitat entre tots dos mètodes

---

### Pregunta 7 — MIDI i percussió (connexió amb Sessió 7)

**A diferència d'una nota melòdica, on cada altura té un sentit musical propi, en un mapa de percussió General MIDI cada número de nota sol representar...**

- A) Una freqüència diferent del mateix instrument fix
- ✅ B) Un instrument de percussió diferent (p.ex. 36=Kick, 42=Hi-Hat)
- C) Un canal MIDI diferent per a cada nota
- D) Una velocity diferent assignada per defecte
