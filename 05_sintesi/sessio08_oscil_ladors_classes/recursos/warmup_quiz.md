# Warm-up — Sessió 8
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 5-8 minuts.

---

### Pregunta 1 — Repàs Sessió 7 (pretty_midi)

**Quina és la diferència principal entre crear una nota amb `mido` i amb `pretty_midi`?**

- A) `pretty_midi` no permet canviar la velocity d'una nota
- ✅ B) `pretty_midi` treballa amb segons (start, end) directament, sense gestionar ticks
- C) `mido` només es pot fer servir per llegir fitxers, no per crear-los
- D) No hi ha cap diferència pràctica entre les dues llibreries

---

### Pregunta 2 — Repàs Sessió 7 (timing)

**Quina és la idea central de l'estratègia de timing amb `perf_counter` i temps objectiu absolut?**

- A) Substituir `time.sleep()` per una versió que no consumeix CPU
- ✅ B) Calcular cada temps objectiu des de l'origen, perquè els petits errors no es vagin acumulant
- C) Executar el seqüenciador sempre en un fil (thread) diferent del principal
- D) Reduir el tempo perquè el sistema tingui més marge de reacció

---

### Pregunta 3 — Intuïció: per què calen classes aquí

**Una funció normal "oblida" tot un cop ha acabat d'executar-se. Si necessites que un component recordi un valor (per exemple, la seva freqüència actual) entre una crida i la següent, què té més sentit?**

- A) Cridar la funció dues vegades seguides per assegurar-te que el valor es guarda
- ✅ B) Fer servir un objecte (instància d'una classe), que pot guardar dades pròpies entre crides
- C) És impossible recordar res entre crides en Python
- D) Convertir la funció en una variable global de tipus text

---

### Pregunta 4 — Predicció (classes)

```python
class Oscillator:
    def __init__(self, freq):
        self.freq = freq

    def set_freq(self, freq):
        self.freq = freq

osc = Oscillator(440)
osc.set_freq(880)
print(osc.freq)
```

**Què s'imprimirà?**

- A) 440
- ✅ B) 880
- C) Error — no es pot canviar un atribut després de crear l'objecte
- D) `None`

---

### Pregunta 5 — Concepte clau: oscil·lador vs envolvent

**Si només tens un `Oscillator` (sense cap envolvent) i li demanes 2 segons de so, què sentiràs?**

- A) Silenci total, perquè li falta l'envolvent per activar-se
- ✅ B) Un so que comença i acaba sobtadament, sense atac ni final suaus
- C) Un "clic" curt seguit de silenci
- D) Un error, perquè un oscil·lador sense envolvent no es pot generar

---

### Pregunta 6 — MIDI i l'embolcall (no l'oscil·lador)

**Quan arriba un `note_off`, què té més sentit que passi, seguint el disseny modular d'aquesta sessió?**

- A) L'oscil·lador deixa de generar la seva ona immediatament
- ✅ B) Comença la fase de Release de l'envolvent; l'oscil·lador continua generant igual
- C) Es crea un nou `Oscillator` per a la següent nota
- D) `note_off` només afecta el `SamplePlayer`, mai l'`Oscillator`

---

### Pregunta 7 — Oscillator vs SamplePlayer

**Quina és la diferència fonamental entre `Oscillator` i `SamplePlayer`?**

- A) `SamplePlayer` és més ràpid d'executar que `Oscillator`
- ✅ B) `Oscillator` genera el so amb matemàtiques; `SamplePlayer` reprodueix un so ja gravat
- C) `Oscillator` només funciona amb MIDI; `SamplePlayer` no necessita MIDI
- D) Són exactament la mateixa cosa amb noms diferents
