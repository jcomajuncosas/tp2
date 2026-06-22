# Warm-up — Sessió 7
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 5-8 minuts.

---

### Pregunta 1 — Repàs Sessió 6 (delta time)

**A `mido`, si un `note_on` té `time=480`, qué significa?**

- A) La nota sona durant 480 ticks
- ✅ B) Hi ha un silenci de 480 ticks abans que comenci la nota
- C) La nota té velocity 480
- D) El missatge s'envia 480 vegades

---

### Pregunta 2 — Repàs Sessió 6 (números MIDI)

**Quina nota MIDI correspon al Do central (C4)?**

- A) 48
- ✅ B) 60
- C) 64
- D) 72

---

### Pregunta 3 — Nou: pretty_midi vs mido

**Quina és la diferència principal entre crear una nota amb `mido` i amb `pretty_midi`?**

- A) `pretty_midi` no permet velocitats per sota de 64
- ✅ B) `pretty_midi` usa segons (start, end) directament; `mido` requereix gestionar ticks i delta time
- C) `mido` només funciona amb fitxers de menys d'1 minut
- D) `pretty_midi` no es pot usar per crear fitxers, només per llegir-los

---

### Pregunta 4 — Predicció (pretty_midi.Note)

```python
nota = pretty_midi.Note(velocity=90, pitch=64, start=1.0, end=1.5)
```

**Quant dura aquesta nota?**

- A) 90 segons
- B) 1.0 segons
- ✅ C) 0.5 segons
- D) 1.5 segons

---

### Pregunta 5 — Intuïció: precisió d'una espera repetida

**Si un programa fa `time.sleep(0.1)` 100 vegades seguides (amb una mica de feina entre cada espera), esperaries que el temps total sigui exactament 10.0 segons, una mica més de 10 segons, o no es pot saber?**

- A) Exactament 10.0 segons, sempre
- ✅ B) Una mica més de 10 segons — cap espera real és perfectament exacta
- C) Una mica menys de 10 segons — el sistema "recupera" temps
- D) Depèn només de quants nuclis (cores) té el processador

*(Comentari: avui veurem per què aquest petit excés, repetit moltes vegades, es nota molt en un seqüenciador a tempo ràpid.)*

---

### Pregunta 6 — Intuïció: com fixar un esdeveniment a un instant exacte

**Vols que un esdeveniment passi exactament 5.0 segons després de començar. Quina estratègia et sembla més fiable?**

- A) Anar comptant "ja deuen haver passat 5 segons" sumant petites estones d'espera
- ✅ B) Consultar un rellotge, calcular quina hora serà als 5 segons, i esperar fins arribar-hi
- C) Repetir l'esdeveniment moltes vegades seguides perquè la mitjana surti als 5 segons
- D) Demanar a l'usuari que avisi quan creu que han passat 5 segons

*(Comentari: l'opció B és la idea central de l'Estratègia B que veurem avui — calcular el temps objectiu des de l'origen, no acumulant petites espere.)*

---

### Pregunta 7 — Concepte (MIDI Clock, sense implementar)

**Quina és la funció de MIDI Clock en un context professional?**

- ✅ A) Sincronitzar el tempo entre diversos dispositius o programes (per exemple, Python i un DAW)
- B) Marcar la durada màxima que pot durar un fitxer MIDI abans de tallar-se
- C) Convertir automàticament missatges MIDI en àudio sense necessitat de soundfont
- D) Establir quin dels ports MIDI disponibles té prioritat quan n'hi ha diversos connectats

*(Comentari: no l'implementarem — la configuració requereix ports virtuals i és un projecte en si mateix. Cal conèixer que existeix per a contextos professionals futurs, com sincronitzar Python amb Ableton Live.)*
