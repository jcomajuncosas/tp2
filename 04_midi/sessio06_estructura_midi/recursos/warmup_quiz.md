# Warm-up — Sessió 6
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 5-8 minuts.

---

### Pregunta 1 — Repàs Sessió 5 (buffer circular)

**Per llegir l'eco del buffer de retard dins el callback, quina línia és correcta?**

- ✅ A) `eco = delay_buffer[:frames]`
- B) `eco = delay_buffer[-frames:]`
- C) `eco = delay_buffer[frames:]`
- D) `eco = delay_buffer[::frames]`

*(Comentari: llegim les mostres més antigues, que estan a l'inici del buffer. Les més recents estan al final i acabem d'escriure-les nosaltres.)*

---

### Pregunta 2 — Nou: MIDI vs. WAV (concepte)

**Quina és la diferència fonamental entre un fitxer `.mid` i un fitxer `.wav`?**

- A) `.mid` és sempre de més qualitat sonora que `.wav`
- B) `.wav` triga més a carregar que `.mid`
- ✅ C) `.mid` conté instruccions musicals; `.wav` conté mostres d'àudio ja generades
- D) `.mid` necessita un micròfon per gravar-se, `.wav` no

---

### Pregunta 3 — Números MIDI

**Quina nota MIDI correspon al Do central (C4)?**

- A) 48
- ✅ B) 60
- C) 64
- D) 72

---

### Pregunta 4 — Intuïció: mesurar el temps en "unitats pròpies"

**Un metrònom marca el tempo en "beats per minut" (bpm), no directament en segons. Si algú et diu "aquesta nota dura 1 beat" a un tempo concret, què necessites saber per calcular quants segons són?**

- A) Només la nota MIDI (el pitch)
- ✅ B) El tempo (bpm) — un beat dura més o menys segons segons si el tempo és lent o ràpid
- C) El canal MIDI que s'està usant
- D) No es pot calcular, "beat" i "segon" són unitats incompatibles

*(Comentari: avui veurem que MIDI fa exactament això — mesura el temps en "ticks" relatius al tempo, no en segons directament.)*

---

### Pregunta 5 — Detecció d'error (delta time)

```python
track.append(mido.Message('note_on',  note=60, velocity=80, time=480))
track.append(mido.Message('note_off', note=60, velocity=0,  time=480))
```

**Quin efecte té `time=480` al `note_on`?**

- A) La nota sona durant 480 ticks
- ✅ B) Hi ha un silenci abans que comenci la nota
- C) La nota sona dues vegades seguides
- D) El missatge queda descartat per `mido`

*(Comentari: `time` és sempre delta time — ticks des del missatge anterior. Si el primer `note_on` té `time=480`, vol dir "espera 480 ticks i llavors toca la nota".)*

---

### Pregunta 6 — Intuïció: rangs diferents per al mateix concepte

**A TP1, `velocity` anava de 0 a 1 (per exemple, 0.7). En MIDI real, `velocity` va de 0 a 127. Si algú et dona velocity=0.7 i et demana "el seu equivalent en MIDI", què hauries de fer?**

- A) Deixar-ho tal qual, 0.7, MIDI accepta decimals
- ✅ B) Convertir-ho a una escala diferent (multiplicar per 127, aproximadament)
- C) Restar-li 1 perquè MIDI comença a comptar des de -1
- D) És impossible convertir-ho, són sistemes incompatibles

*(Comentari: igual que heu vist amb sample_rate i freqüències, sovint cal traduir entre "el rang que fa servir una eina" i "el rang que en fa servir una altra".)*

---

### Pregunta 7 — Canal MIDI

**Quin canal MIDI té una convenció especial per a percussió (General MIDI)?**

- A) Canal 0
- B) Canal 1
- ✅ C) Canal 9
- D) Canal 16

*(Comentari: el canal 9, dins el rang 0-15, és el reservat per percussió a l'estàndard General MIDI. El "canal 16" no existeix com a tal — els canals van de 0 a 15.)*
