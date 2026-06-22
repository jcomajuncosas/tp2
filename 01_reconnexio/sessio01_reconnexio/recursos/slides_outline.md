# Slides — Bloc 1, Sessió 1
### Fonaments de Python per a l'àudio: el so com a array

> **Instruccions de muntatge:** Crea una presentació de Google Slides amb una diapositiva per secció. Mantén el mateix estil visual que les Slides de TP1 (mateixa plantilla/colors) per a continuïtat visual. Temps total estimat: 20-25 min (10-20% de la sessió de 2h).

---

### Diapositiva 1 — Portada
**Bloc 1 — El so com a array**
*Programació per a Sonòlegs (Python)*

---

### Diapositiva 2 — Què és "so" per a un ordinador?
- Un so és una vibració de l'aire → una ona contínua
- Un ordinador no pot emmagatzemar "continu" → ho converteix en **números discrets**
- Imatge: ona analògica amb punts marcats a sobre (mostreig)
- Aquests punts = **mostres (samples)**

---

### Diapositiva 3 — Sampling: quantes mostres?
- **Sample rate**: nombre de mostres per segon → estàndard: **44100 Hz**
- Exemple: 1 segon d'àudio = 44100 números
- (Breu, sense entrar en Nyquist en detall — ja ho han vist a Síntesi)
- Idea clau: *més sample rate = més resolució temporal*

---

### Diapositiva 4 — Representar so = array de números
- Un so d'1 segon → un array de 44100 valors
- Cada valor = amplitud en aquell instant (entre -1 i 1, normalment)
- Visual: gràfic d'ona amb l'array de sota mostrant alguns valors numèrics alineats

---

### Diapositiva 5 — NumPy: l'eina per treballar amb arrays
- `import numpy as np`
- Per què NumPy i no llistes normals?
- Recordatori ràpid: `llista * 2` duplica; `array * 2` multiplica cada element
- → Connexió directa amb la Pregunta 4/5 del warm-up

---

### Diapositiva 6 — Generar l'eix de temps
```python
sample_rate = 44100
duration = 1.0
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
```
- `t` és un array: [0, 0.0000226, 0.0000453, ...] fins a 1.0
- Cada valor de `t` és un "instant" on calcularem l'amplitud

---

### Diapositiva 7 — Generar una ona: `np.sin`
```python
freq = 440
wave = np.sin(2 * np.pi * freq * t)
```
- Per a cada instant `t`, calcula el sinus → resultat: array `wave`
- Visual: fórmula al costat del gràfic resultant
- Sense bucle `for` — NumPy ho fa per a tots els valors alhora

---

### Diapositiva 8 — Paràmetres: freqüència i amplitud
- **Freqüència** → to (Hz). Més alt = més agut
- **Amplitud** → volum. `wave * amplitude`
- Demo en directe aquí (passar a Patches): canviar `freq` de 220 a 880, escoltar diferència
- Canviar `amplitude` de 1.0 a 0.1, escoltar diferència

---

### Diapositiva 9 — Altres formes d'ona (preview)
- Sinus → to "pur"
- Quadrada (`square`), serra (`sawtooth`), soroll (`noise`) → timbres diferents
- No entrarem en detall avui — apareixeran al Bloc 5 (síntesi)
- Imatge comparativa de les 4 formes d'ona

---

### Diapositiva 10 — Connexió amb TP1
- A TP1: `pattern = [60, 64, 67]` (llista) i `for` per recórrer-la
- A TP2: `wave = np.array([...])` (array) i operacions sobre tot l'array alhora
- El `for`/`range` no desapareix: tornarà al **Bloc 4** (seqüenciació MIDI)
- Avui: de "llista de notes" a "array de mostres" — mateix llenguatge, nova escala
