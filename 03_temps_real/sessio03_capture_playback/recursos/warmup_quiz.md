# Warm-up — Sessió 3
### Format: Google Forms (mode Quiz, autocorrecció activada)

> **Instruccions de muntatge:** Igual que Sessions 1-2. Temps suggerit: 5-8 minuts.

---

### Pregunta 1 — Repàs Sessió 2 (mixing)

**Tenim `so1` de 44100 mostres i `so2` de 88200 mostres. Fem `mix = so1 + so2`. Què passa?**

- A) Funciona: `mix` té 88200 mostres (les que falten s'omplen amb zeros)
- B) Funciona: `mix` té 44100 mostres (es retalla el més llarg)
- ✅ C) Error: les longituds no coincideixen
- D) Funciona: `mix` té 132300 mostres (es concatenen)

---

### Pregunta 2 — Repàs Sessió 2 (np.tile)

**`np.tile(np.array([1,2]), 3)` — quin resultat dona?**

- A) `[3, 6]`
- ✅ B) `[1, 2, 1, 2, 1, 2]`
- C) `[1, 2, 3]`
- D) Error

---

### Pregunta 3 — Nou: blocking (ordre d'operacions)

**En el model blocking, quin és l'ordre correcte?**

- A) `sd.play()` → `sd.rec()` → `sd.wait()`
- B) `sd.wait()` → `sd.rec()` → processar → `sd.play()`
- ✅ C) `sd.rec()` → `sd.wait()` → processar → `sd.play()` → `sd.wait()`
- D) `sd.rec()` → processar → `sd.play()` → `sd.wait()`

*(Comentari: sense el primer `sd.wait()`, processaries un array buit — la gravació encara no ha acabat.)*

---

### Pregunta 4 — Intuïció: gravar pot tenir més d'un canal

**Quan graves amb el micròfon, el resultat podria tenir més d'una "columna" de dades (per exemple, un canal esquerre i un de dret), encara que el micròfon sigui mono?**

- A) No, mai — un array d'àudio només pot ser una llista plana de números
- ✅ B) Sí, és habitual que les funcions de gravació retornin sempre una estructura amb "files i columnes" (mostres × canals), encara que hi hagi un sol canal
- C) Només si el sample rate és superior a 44100
- D) No, això només passa amb fitxers MP3

*(Comentari: avui veurem que `sd.rec()` sempre retorna un array 2D (mostres, canals) — cal aplanar-lo per treballar en mono, com ja fèieu amb `data.flatten()`.)*

---

### Pregunta 5 — Detecció d'error (echo)

```python
def echo(data, delay_seconds, decay=0.5, sample_rate=44100):
    delay_samples = int(delay_seconds * sample_rate)
    result = data
    result[delay_samples:] += data[:-delay_samples] * decay
    return result
```

**Hi ha un problema subtil en aquesta implementació. Quin és?**

- A) `int()` hauria de ser `float()`
- B) `decay` hauria de ser més gran que 1
- ✅ C) `result = data` no fa una còpia — modifica l'array original
- D) No hi ha cap problema

*(Comentari: `result = data` és una referència, no una còpia. Cal `result = np.copy(data)`. És un error molt comú amb NumPy.)*

---

### Pregunta 6 — Concepte (blocking vs temps real)

**Per quin motiu `reverse` és impossible d'aplicar en temps real (streaming)?**

- ✅ A) Per invertir el so cal tenir totes les mostres — però en temps real les mostres futures encara no han arribat
- B) Perquè `data[::-1]` és massa lent per a temps real
- C) Perquè `sounddevice` no permet arrays invertits
- D) No és impossible, es pot fer igual que en blocking

---

### Pregunta 7 — Encadenar efectes

```python
resultat = fade_out(echo(data, delay_seconds=0.2), duration=0.5)
```

**En quin ordre s'apliquen els efectes?**

- A) `fade_out` primer, després `echo`
- ✅ B) `echo` primer, després `fade_out`
- C) S'apliquen simultàniament
- D) Depèn de la mida de l'array

*(Comentari: les funcions s'avaluen de dins cap a fora — igual que les funcions matemàtiques compostes.)*
