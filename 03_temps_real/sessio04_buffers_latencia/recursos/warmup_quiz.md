# Warm-up — Sessió 4
### Format: Google Forms (mode Quiz, autocorrecció activada)

> **Instruccions de muntatge:** Igual que sessions anteriors. Temps: 5-8 minuts.

---

### Pregunta 1 — Repàs Sessió 3 (echo + np.copy)

```python
def echo(data, delay_samples, decay=0.5):
    result = data                          # línia A
    result[delay_samples:] += data[:-delay_samples] * decay
    return result
```

**Quin problema té la línia A?**

- A) `data` hauria de ser un float, no un array de NumPy
- ✅ B) `result` no és una còpia: modifica també `data`
- C) No hi ha cap problema, el codi és correcte
- D) `decay` hauria de ser negatiu per fer un eco

---

### Pregunta 2 — Repàs Sessió 3 (efectes encadenats)

**`fade_out(echo(distortion(data, drive=3), delay_seconds=0.2), duration=0.5)` — en quin ordre s'apliquen?**

- A) `fade_out` → `echo` → `distortion`
- B) `distortion` → `fade_out` → `echo`
- ✅ C) `distortion` → `echo` → `fade_out`
- D) S'apliquen en paral·lel

---

### Pregunta 3 — Nou: model callback (concepte)

**En el model callback, qui crida la funció de processament d'àudio?**

- A) Tu, explícitament, cada vegada que vols processar un bloc
- ✅ B) El sistema d'àudio, automàticament, cada vegada que necessita un bloc nou
- C) Un fil (thread) separat que tu has creat manualment
- D) `sd.wait()` quan detecta que hi ha dades noves

---

### Pregunta 4 — Predicció (pass-through)

```python
def process(indata, outdata, frames, time_info, status):
    outdata[:] = indata
```

**Què fa aquest callback?**

- A) Grava l'entrada a un fitxer WAV
- B) Silencia la sortida (envia zeros)
- ✅ C) Copia l'entrada a la sortida sense modificar-la
- D) Reprodueix un so sintetitzat

---

### Pregunta 5 — Detecció d'error (callback lent)

```python
import time

def process(indata, outdata, frames, time_info, status):
    time.sleep(0.5)       # espera 0.5 segons
    outdata[:] = indata
```

**Què passarà si `blocksize=512` i `sample_rate=44100` (buffer de ~11ms)?**

- A) Funcionarà bé: sounddevice esperarà que acabi
- ✅ B) El so es trencarà: hi haurà talls (glitches)
- C) Python donarà un error i el programa s'aturarà
- D) El retard pujarà a 500 ms, però el so serà net

*(Comentari: el sistema necessita el resultat cada 11ms. Si el callback triga 500ms, el sistema no pot esperar i els buffers es buiden o col·lapsen → glitch. És el risc principal del model callback.)*

---

### Pregunta 6 — Concepte (blocksize i latència)

**Si augmentem `blocksize` de 256 a 1024 (amb el mateix sample_rate), quines dues coses canvien?**

- A) La latència baixa i el risc de glitch baixa
- B) La latència puja i el risc de glitch puja
- ✅ C) La latència puja i el risc de glitch baixa
- D) La latència baixa i el risc de glitch puja

*(Comentari: buffer més gran = el sistema triga més a omplir-lo = més latència. Però el callback té més temps per processar = menys risc de glitch. És el trade-off fonamental.)*

---

### Pregunta 7 — Concepte (per què Colab no funciona per a temps real)

**Per quin motiu el codi de temps real (`sd.Stream` amb callback) no funciona a Colab?**

- A) Colab no té instal·lada la llibreria `sounddevice`
- B) Els notebooks de Jupyter no permeten bucles infinits
- ✅ C) El codi corre en un servidor remot, lluny del teu so
- D) Python no pot crear threads en entorns al núvol

*(Comentari: contrast amb WebAudio API del navegador, que sí que és temps real perquè s'executa localment al client.)*
