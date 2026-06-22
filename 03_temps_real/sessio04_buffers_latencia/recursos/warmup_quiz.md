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

- A) `data` hauria de ser un float, no un array
- ✅ B) `result = data` és una referència, no una còpia — modifica l'array original
- C) No hi ha cap problema
- D) `decay` hauria de ser negatiu per a un eco

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
def process(indata, outdata, frames, time, status):
    outdata[:] = indata
```

**Qué fa aquest callback?**

- A) Grava l'entrada a un fitxer WAV
- B) Silencia la sortida (envia zeros)
- ✅ C) Copia l'entrada directament a la sortida sense modificar-la (pass-through)
- D) Reprodueix un so generat sintetitzament

---

### Pregunta 5 — Detecció d'error (callback lent)

```python
def process(indata, outdata, frames, time, status):
    import time as t
    t.sleep(0.5)          # espera 0.5 segons
    outdata[:] = indata
```

**Qué passarà si `blocksize=512` i `sample_rate=44100` (buffer de ~11ms)?**

- A) Funcionarà perfectament — sounddevice esperarà que acabi
- ✅ B) Hi haurà glitches (salts/interrupcions en l'àudio) perquè el callback triga 500ms però el buffer dura 11ms
- C) El programa donarà error i s'aturarà
- D) La latència augmentarà a 500ms però el so serà correcte

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

### Pregunta 7 — Concepte (per que Colab no funciona per a temps real)

**Per quin motiu el codi de temps real (`sd.Stream` amb callback) no funciona a Colab?**

- A) Colab no té instal·lat `sounddevice`
- B) Els notebooks de Jupyter no permeten bucles infinits
- ✅ C) El codi de Colab s'executa en un servidor remot — el so hauria de viatjar per la xarxa, cosa incompatible amb latències de ~10ms
- D) Python no suporta threads en entorns de núvol

*(Comentari: contrast amb WebAudio API del navegador, que sí que és temps real perquè s'executa localment al client.)*
