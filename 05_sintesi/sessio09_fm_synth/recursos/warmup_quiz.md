# Warm-up — Sessió 9
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 5-8 minuts.

---

### Pregunta 1 — Repàs Sessió 8 (Oscillator vs Envelope)

**Per què `Envelope` és una classe separada d'`Oscillator`, i no un mètode dins d'`Oscillator`?**

- A) Perquè Python no permet que una classe tingui més de tres mètodes
- ✅ B) Perquè són components diferents (timbre vs. forma temporal) que es combinen, com en un sintetitzador modular
- C) Perquè `Envelope` necessita accedir a internet per funcionar
- D) Perquè així s'executa més ràpid que si fossin la mateixa classe

---

### Pregunta 2 — Repàs Sessió 8 (MIDI i envolvent)

**Quan arriba un `note_off`, què passa segons el disseny de la Sessió 8?**

- A) L'oscil·lador deixa de generar la seva ona immediatament
- ✅ B) Comença la fase de Release de l'envolvent; l'oscil·lador continua igual
- C) Es crea una nova instància d'`Oscillator` per a la nota següent
- D) `note_off` només té efecte si la nota dura menys d'un segon

---

### Pregunta 3 — Intuïció: per què calen blocs en temps real

**Imagina que vols generar so contínuament mentre parles en directe (com a la Sessió 5), no tot d'un cop com fins ara. Quin problema esperaries si cada "tros" de so es generés començant sempre des de zero, sense recordar res de l'anterior?**

- A) Cap problema — el so sonaria perfectament continu igualment
- ✅ B) Es podria sentir un petit salt o "click" entre un tros i el següent
- C) L'ordinador es bloquejaria immediatament
- D) Els trossos sonarien cada cop més fluixos

---

### Pregunta 4 — Intuïció: ràpid vs. lent en un control

**Penseu en un efecte de vibrato (la freqüència d'una nota oscil·la suaument amunt i avall uns quants cops per segon). Comparat amb el so audible en si (que oscil·la centenars de cops per segon), creus que aquest "moviment lent" necessita la mateixa precisió/resolució que el so?**

- A) Sí, exactament la mateixa, perquè tot és "freqüència" igualment
- ✅ B) No, com que canvia molt més lentament, no cal actualitzar-lo tan sovint
- C) No es pot saber res d'això sense escoltar-ho primer
- D) El vibrato no té cap relació amb el concepte de freqüència

---

### Pregunta 5 — Predicció (lectura de codi)

```python
osc = Oscillator(freq=440)
bloc1 = osc.process(100)
bloc2 = osc.process(100)
```

**Si `process()` recorda la fase entre crides (a diferència de `generate()` de la S8), què esperes de la relació entre `bloc1` i `bloc2`?**

- A) Seran exactament idèntics, mostra per mostra
- ✅ B) `bloc2` continuarà l'ona just on `bloc1` l'havia deixat, sense salts
- C) `bloc2` sempre començarà en silenci (valor 0)
- D) És impossible saber-ho sense executar el codi

---

### Pregunta 6 — Concepte clau: FM com a combinació de dues idees

**Si un "modulador" canvia lleugerament la freqüència d'un "portador" de manera repetida, i el portador és qui realment sentim... quina creus que és la relació entre tots dos?**

- A) Són exactament el mateix component, amb noms diferents
- ✅ B) El modulador controla un paràmetre del portador; el portador és qui produeix el so final
- C) El portador només serveix per controlar el volum del modulador
- D) No tenen cap relació — sonen de manera completament independent

---

### Pregunta 7 — Detecció d'error (callback temps real)

```python
def synth_callback(outdata, frames, time, status):
    wave = osc.process(frames)
    outdata[:, 0] = wave

osc = Oscillator(freq=440)
osc.note_on()   # <- aquesta línia dona error
```

**Sabent que a la Sessió 8 `Oscillator` "sona sempre" (no té concepte de nota), per què aquesta línia fallaria?**

- A) `Oscillator` no admet la freqüència 440 com a valor vàlid
- ✅ B) `note_on()` és un mètode de l'envolvent, no de l'oscil·lador
- C) `note_on()` només es pot cridar dins d'un callback de temps real
- D) Cal cridar `process()` abans de poder cridar `note_on()`
