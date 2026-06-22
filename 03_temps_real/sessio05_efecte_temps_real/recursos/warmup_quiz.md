# Warm-up — Sessió 5
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 5-8 minuts.

---

### Pregunta 1 — Repàs Sessió 4 (callback)

**Quin és el problema principal si el callback tarda més que la durada del buffer?**

- A) El programa s'atura amb un error
- ✅ B) Hi ha glitches (salts/interrupcions) en l'àudio
- C) El gain s'aplica incorrectament
- D) El stream es reinicia automàticament

---

### Pregunta 2 — Repàs Sessió 4 (variable global)

```python
gain = 0.5

def callback(indata, outdata, frames, time, status):
    outdata[:] = indata * gain
```

**Si des del programa principal fem `gain = 0.0`, qué passarà al so en la propera crida al callback?**

- A) Res — el callback no veu el canvi fins que el stream es reinicia
- ✅ B) La sortida serà silenci — el callback llegeix la variable global actualitzada
- C) Error: no es pot modificar una variable usada dins un callback
- D) La sortida serà soroll aleatori

---

### Pregunta 3 — Nou: per qué cal un buffer per a l'eco en temps real

**Per qué no podem implementar eco en temps real de la mateixa manera que offline (`result[delay:] += data[:-delay] * decay`)?**

- A) Perquè `np.copy` no funciona dins un callback
- B) Perquè el callback no pot usar NumPy
- ✅ C) Perquè el callback rep un bloc curt (~23ms) i no té accés a les mostres passades — que ja han marxat
- D) Perquè la suma de arrays és massa lenta per a temps real

---

### Pregunta 4 — Intuïció: un buffer que es va omplint

**Imagina una cinta curta on vas gravant trossos nous d'àudio, un darrere l'altre, sense parar mai. Quan la cinta s'omple, què té més sentit que passi amb el tros més antic?**

- A) Es queda per sempre al mateix lloc, no es pot esborrar
- ✅ B) Surt fora (es perd) per deixar espai al tros nou que entra
- C) Es duplica i ocupa el doble d'espai
- D) Es converteix automàticament en silenci però no desapareix

*(Comentari: això és exactament un buffer circular — avui veurem com `np.roll` fa precisament aquest "desplaçar i sobreescriure" amb el buffer de retard.)*

---

### Pregunta 5 — Concepte (distorsió vs eco en temps real)

**Per quin motiu la distorsió és més simple d'implementar en temps real que l'eco?**

- A) Perquè `np.clip` és més ràpid que `np.roll`
- ✅ B) Perquè la distorsió no té memòria — cada bloc és independent i no necessita recordar mostres passades
- C) Perquè la distorsió no necessita un callback
- D) No hi ha diferència de complexitat

---

### Pregunta 6 — ipywidgets (concepte)

**Quan usem `@widgets.interact` a Colab per visualitzar l'efecte d'un eco, estem fent àudio en temps real?**

- ✅ A) No — estem modificant paràmetres i veient el resultat en un gràfic, però el codi s'executa al servidor de Colab (no hi ha so real)
- B) Sí — ipywidgets activa WebAudio al navegador
- C) Sí — Colab té accés al micròfon via ipywidgets
- D) No — ipywidgets no pot mostrar gràfics

---

### Pregunta 7 — Preview Bloc 5 (per qué classes)

**Si volem tenir DOS ecos simultanis (delays de 0.2s i 0.5s) usant l'enfocament de buffer global, quants buffers globals necessitem?**

- A) 1 — podem reutilitzar el mateix buffer
- ✅ B) 2 — un per a cada delay diferent
- C) 0 — podem calcular-ho sense buffer
- D) Depèn del `blocksize`

*(Comentari: amb classes, cadascuna portaria el seu propi buffer intern. Veurem com al Bloc 5.)*
