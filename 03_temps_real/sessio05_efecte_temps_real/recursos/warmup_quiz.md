# Warm-up — Sessió 5
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 5-8 minuts.
> ⚙️ Al Form: activa **"Ordena les opcions aleatòriament"** a cada pregunta.

Criteri: les opcions tenen llargades semblants i cada distractor és un **error real** que fan els alumnes (o una intuïció raonable però falsa). Les preguntes 4, 6 i 7 són *preview*: no s'espera que les encertin; el dubte es resol a classe.

---

### Pregunta 1 — Repàs S04 (deadline)

**La callback tarda més que la durada d'un bloc. Què passa?**

- A) L'stream augmenta el blocksize per compensar-ho
- B) El so arriba una mica més tard, però sense talls
- ✅ C) Hi ha talls perquè la sortida no arriba a temps
- D) Python llança una excepció i l'stream s'atura

---

### Pregunta 2 — Repàs S04 (variables globals)

```python
gain = 0.5

def callback(indata, outdata, frames, time_info, status):
    outdata[:] = indata * gain
```

**Amb l'stream obert, el bucle principal fa `gain = 0.0`. Què se sent?**

- A) Res canvia: l'stream va copiar `gain` en obrir-se
- B) Res canvia: falta `global gain` dins la callback
- C) Un error: no es pot canviar una variable en ús
- ✅ D) Silenci, des de la següent crida de la callback

*(Comentari: el distractor B és el més perillós. `global` només cal per ESCRIURE una global des de dins d'una funció; per llegir-la no cal. Avui la callback haurà d'escriure-hi, i llavors sí.)*

---

### Pregunta 3 — Repàs S04 (distorsió)

```python
def disto_callback(indata, outdata, frames, time_info, status):
    outdata[:] = np.tanh(indata * drive)
```

**Aquesta callback, ha de recordar alguna cosa del bloc anterior?**

- ✅ A) No: cada mostra depèn només d'ella mateixa
- B) Sí: l'última mostra, per evitar clics entre blocs
- C) Sí: el `drive` anterior, per si ha canviat
- D) Depèn del blocksize: amb blocs petits, sí

---

### Pregunta 4 — Preview (oscil·lador)

**A cada crida generes un sinus de 440 Hz amb `t = np.arange(frames) / sample_rate`. Què sents?**

- A) Un 440 Hz net, idèntic al que generaries offline
- ✅ B) Un 440 Hz, però amb un brunzit greu superposat
- C) Un to més agut, perquè els blocs s'encavalquen
- D) Talls de silenci, cada vegada que `t` torna a 0

*(Comentari: es comprova en directe amb `demo_sinus_sense_memoria()`. El brunzit és de ~43 Hz: les crides per segon.)*

---

### Pregunta 5 — Repàs S03/S04 (eco offline)

**Per què l'eco de la S03 (`resultat[d:] += x[:-d] * v`) no funciona tal qual dins la callback?**

- A) La indexació `[:-d]` és massa lenta per al temps real
- B) Dins la callback no es pot modificar un array amb `+=`
- C) Caldria convertir el bloc a mono abans de sumar-lo
- ✅ D) `d` és més llarg que el bloc: aquelles mostres ja no hi són

---

### Pregunta 6 — Preview (la cinta)

**Tens una cinta de 6 caselles. A cada crida hi entren 2 mostres noves per un extrem i en surten 2 per l'altre. Una mostra que entra ara, quantes crides després surt?**

- A) 1
- B) 2
- ✅ C) 3
- D) 6

*(Comentari: es comprova a la taula de la secció 2 del Colab. Retard = mida de la cinta = 6 mostres = 3 crides de 2.)*

---

### Pregunta 7 — Preview (estat)

**Una callback fa un trèmolo (un LFO de 5 Hz) i després un eco de 0.3 s. Què ha de sobreviure d'una crida a la següent?**

- A) Només la cinta de l'eco: un LFO tan lent no es nota
- ✅ B) La fase de l'LFO i també la cinta de l'eco
- C) Res, si el blocksize és prou gran (2048 o més)
- D) El bloc d'entrada anterior, per a tots dos efectes

*(Comentari: A és la trampa: com més lent és l'LFO, PITJOR sona si s'oblida la fase. En un bloc de 23 ms un LFO de 5 Hz només fa ~0.12 cicles i tornaria a començar. Ho comprovaran a la reflexió de l'assignment.)*

---

**Distribució de respostes correctes:** A (1), B (2), C (2), D (2).
