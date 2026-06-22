# Slides — Bloc 3a, Sessió 3
### Captura, playback i efectes offline (model blocking)

> **Instruccions de muntatge:** Mateix estil que Sessions 1-2. Temps estimat: 15-20 min.

---

### Diapositiva 1 — Portada
**Bloc 3a — El so en temps real (I)**
*Captura, playback i efectes offline*

---

### Diapositiva 2 — On som i cap a on anem
- Sessions 1-2: generàvem/llegíem arrays i els processàvem → tot offline
- Avui (Sessió 3): capturem so del micròfon, processem, reproduïm → **blocking**
- Sessió 4: processar mentre el so entra i surt → **streaming/callback**
- Sessió 5: efectes complexos en temps real
- Diagrama de tres passos: MIC → [array] → ALTAVEU (amb el processament enmig)

---

### Diapositiva 3 — El model blocking
- "Blocking" = el programa s'atura i espera que cada operació acabi
- Diagrama de flux lineal: `sd.rec()` → `sd.wait()` → processar → `sd.play()` → `sd.wait()`
- Mentre espera: **el programa no pot fer res més** (no respon a MIDI, controladors, UI...)
- És el model més simple — i suficient per a processament offline

---

### Diapositiva 4 — sd.rec i sd.wait
```python
recording = sd.rec(int(duration * sample_rate),
                   samplerate=sample_rate,
                   channels=1,
                   dtype='float32')
sd.wait()
```
- `sd.rec()` comença a gravar i retorna immediatament (l'array s'omple en segon pla)
- `sd.wait()` és el "bloqueig": espera que l'array estigui complet
- **Atenció:** `recording` té shape `(n_mostres, 1)` — cal aplanar: `.flatten()`

---

### Diapositiva 5 — sd.play i sd.wait
```python
sd.play(resultat, sample_rate)
sd.wait()  # espera que acabi de sonar
```
- Igual: `sd.play()` comença i retorna; `sd.wait()` espera que acabi
- Sense el segon `sd.wait()`, el programa podria acabar-se abans que el so soni

---

### Diapositiva 6 — Un error comú: la referència vs. la còpia
```python
# MAL: result es una referencia a data, no una copia
result = data
result[10:] += data[:-10] * 0.5  # modifica data!

# BE: copia independent
result = np.copy(data)
result[10:] += data[:-10] * 0.5
```
- Demo en directe: mostrar la diferència amb un array petit
- Connecta amb TP1: `llista2 = llista1` tampoc fa còpia en Python

---

### Diapositiva 7 — El catàleg d'efectes d'avui
- Tots treballen offline: reben un array, retornen un array
- Podem encadenar-los: `fade_out(echo(data, 0.3), 0.5)`
- Grups: amplitud/temps (reverse, fade), retard (echo, delay_multi), distorsió, modulació (tremolo, ring_mod), velocitat
- Demo: escoltar `distortion` sobre veu gravada — resultat immediat i impactant

---

### Diapositiva 8 — Echo: la idea
- Eco = senyal original + còpia retardada i atenuada
- Diagrama: `data` original → `+` → sortida, amb una fletxa retardada N mostres i multiplicada per `decay`
- En termes d'array: `result[delay:] += data[:-delay] * decay`
- Paràmetres musicals: `delay_seconds` (temps de retard), `decay` (volum de l'eco)

---

### Diapositiva 9 — Modulació (preview Bloc 5)
- Tremolo: multipliquem el so per una ona lenta → el volum "palpita"
- Ring modulation: multipliquem per una portadora → apareixen freqüències noves
- Connexió directa amb el Bloc 5 (síntesi): la modulació d'amplitud és la base de molts sons sintètics
- Demo: escoltar diferència entre tremolo (rate=4Hz) i ring_mod (carrier=200Hz)

---

### Diapositiva 10 — Reverse: la pregunta oberta
- `reverse(data)` = `data[::-1]` — trivial offline
- Pregunta: *per què és impossible aplicar reverse en temps real?*
- Resposta: per invertir cal tenir totes les mostres futures — però en temps real no han arribat encara
- Aquesta pregunta connecta directament amb el model de callback (Sessió 4)

---

### Diapositiva 11 — Connexió amb TP1 i preview
- Encadenar efectes (`fade_out(echo(data))`) ↔ composició de funcions de TP1
- `np.copy(data)` ↔ la distinció còpia/referència que veieu en qualsevol llista de Python
- Preview Sessió 4: *i si no volem esperar que la gravació acabi per processar? i si volem processar bloc a bloc, mentre entra el so?* → callbacks
