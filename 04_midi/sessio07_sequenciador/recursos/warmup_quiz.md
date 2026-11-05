# Warm-up — Sessió 7
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 5-8 minuts. Preguntes 1–3: repàs. Preguntes 4–7: preview (el dubte es resol durant la sessió).

---

### Pregunta 1 — Repàs Sessió 6 (delta time)

**A `mido`, si un `note_on` té `time=480`, què significa?**

- A) La nota sona durant 480 ticks i després s'atura
- ✅ B) Comença 480 ticks després del missatge anterior
- C) La nota té una velocity de 480 unitats
- D) El missatge s'envia 480 vegades seguides

---

### Pregunta 2 — Repàs Sessió 6 (números MIDI)

**Quina nota MIDI correspon al Do central (C4)?**

- A) 48
- ✅ B) 60
- C) 64
- D) 72

---

### Pregunta 3 — Repàs Bloc 3 (termini del callback)

**Què passava si el callback d'àudio trigava més que la durada del seu bloc?**

- ✅ A) Se sentia un tall o un espetec
- B) El so baixava una octava una estona
- C) Python aturava l'stream amb un error
- D) El volum baixava a la meitat sol

*(Comentari: avui ho tornarem a sentir... provocat des d'un lloc inesperat: fora del callback.)*

---

### Pregunta 4 — Preview: `pretty_midi.Note`

```python
nota = pretty_midi.Note(velocity=90, pitch=64, start=1.0, end=1.5)
```

**Quant dura aquesta nota?**

- A) 90 segons
- B) 1.0 segons
- ✅ C) 0.5 segons
- D) 1.5 segons

---

### Pregunta 5 — Preview: temps absolut

**A `pretty_midi`, què vol dir `start=1.0`?**

- A) Un segon després de la nota anterior
- ✅ B) Un segon des de l'inici de la peça
- C) Un tick des de l'inici de la peça
- D) Una negra després de la nota anterior

*(Comentari: compareu-ho amb la pregunta 1. La diferència entre "des de l'anterior" i "des de l'inici" és la clau de tota la sessió.)*

---

### Pregunta 6 — Intuïció: una espera repetida

**Un programa fa `time.sleep(0.1)` 100 vegades seguides. Quant esperes que trigui en total?**

- A) Exactament 10.0 segons, cada vegada
- ✅ B) Una mica més de 10 segons
- C) Una mica menys de 10 segons
- D) Depèn dels nuclis del processador

*(Comentari: avui mesurarem quant "una mica" és al teu ordinador, i per què es nota tant en un seqüenciador.)*

---

### Pregunta 7 — Intuïció: arribar a un instant exacte

**Vols que un so soni exactament 5.0 segons després de començar. Què és més fiable?**

- A) Sumar petites esperes fins que en surtin 5
- ✅ B) Calcular l'hora d'arribada i esperar-la
- C) Repetir-ho molts cops i fer-ne la mitjana
- D) Esperar que l'usuari premi una tecla

*(Comentari: l'opció B és l'estratègia B d'avui: l'objectiu es calcula des de l'inici, no sumant esperes.)*
