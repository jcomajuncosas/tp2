# Slides — Bloc 3c, Sessió 5
### Efectes en temps real: eco, distorsió i control amb sliders

> **Instruccions de muntatge:** Mateix estil. Temps estimat: 15-20 min.

---

### Diapositiva 1 — Portada
**Bloc 3c — Efectes en temps real**
*Eco, distorsió i control interactiu*

---

### Diapositiva 2 — On som
- Sessió 3: efectes offline (tot l'array disponible)
- Sessió 4: model callback, pass-through, gain
- Avui: efectes *amb memòria* en temps real — el repte del buffer de retard
- Diagrama de progressió: offline → pass-through → efectes sense memòria → efectes amb memòria

---

### Diapositiva 3 — El problema: el callback no té memòria
- El callback rep ~23ms de so cada crida
- Les mostres anteriors ja han marxat — el callback no les "veu"
- Per a efectes sense memòria (distorsió, gain): cap problema
- Per a efectes amb memòria (eco, reverb, delay): cal guardar mostres passades
- Pregunta: *on les guardem?* → fora del callback, en una variable que persisteix

---

### Diapositiva 4 — La distorsió: l'efecte sense memòria
```python
def distorsio_callback(indata, outdata, frames, time, status):
    mono = indata[:, 0]
    clipped = np.clip(mono * drive, -threshold, threshold)
    outdata[:, 0] = clipped / threshold
```
- Cada bloc és independent — cap estat extern
- És el cas ideal per a un callback: simple, ràpid, sense risc
- Demo en directe: veu distorsionada en temps real

---

### Diapositiva 5 — El buffer de retard: la idea
- Necessitem "recordar" N mostres passades (N = delay en mostres)
- Solució: array global de mida N, que el callback llegeix i actualitza cada crida
- Diagrama: buffer circular amb el cap de lectura i d'escriptura
- Analogia: una cinta de casset de longitud fixa que es va sobreescrivint

---

### Diapositiva 6 — El buffer de retard: en codi
```python
delay_buffer = np.zeros(delay_samples)  # viu FORA del callback

def eco_callback(indata, outdata, frames, time, status):
    global delay_buffer
    mono = indata[:, 0]
    eco = delay_buffer[-frames:]          # llegim el passat
    out = mono + eco * decay              # sumem
    delay_buffer = np.roll(delay_buffer, -frames)  # desplacem
    delay_buffer[-frames:] = mono         # escrivim el present
    outdata[:, 0] = out
```
- `np.roll`: desplaça el buffer com una cinta circular
- La mida del buffer = delay en mostres = `delay_seconds * sample_rate`

---

### Diapositiva 7 — Visualització del buffer (pas a pas)
*(Diapositiva animada o sèrie de diagrames)*

- Instant 0: buffer = [0, 0, 0, 0, 0], entrada = [A, B]
- Crida 1: eco = [0, 0], out = [A, B], buffer → [0, 0, 0, A, B]
- Crida 2: eco = [A, B], out = [C+A·d, D+B·d], buffer → [0, A, B, C, D]
- ...el buffer porta la "memòria" del passat

---

### Diapositiva 8 — Control en temps real: sliders a Colab
- A Thonny: `input()` per canviar paràmetres (ja vist a Sessió 4)
- A Colab (per a demos visuals sense so real): `ipywidgets`
- `@widgets.interact(delay_ms=(50,500,10))` → slider automàtic
- Demo: slider de delay i decay que actualitza un gràfic de l'eco en temps real
- **Important:** això és visualització, no so real — Colab és al servidor

---

### Diapositiva 9 — Combinar efectes en temps real
- Es pot combinar distorsió + eco dins d'un sol callback
- Ordre important: distorsió primer, eco sobre el resultat (o a l'inrevés — sona diferent)
- Regla: el clipping final de seguretat (`np.clip(out, -1.0, 1.0)`) sempre al final
- Demo: combo en directe

---

### Diapositiva 10 — El stutter (challenge d'avui)
- Stutter: repetir ràpidament un fragment curt mentre el so continua
- Requereix: detectar/triar un fragment, guardar-lo en un buffer separat, reproduir-lo N vegades
- Més complex que l'eco — però possible amb el que ja sabeu
- Avui: és el Challenge del mini-repte (opcional)

---

### Diapositiva 11 — Preview: per qué les classes al Bloc 5
- Ara: un buffer global per efecte → difícil de gestionar si en volem molts
- Si volem dos ecos simultanis: dos buffers globals amb noms diferents
- Solució natural: una **classe** que porta el seu propi buffer intern
- Al Bloc 5 construirem oscil·ladors com a classes — l'eco d'avui és la motivació
- *"Si hagués existit la classe `EcoEffect`, el codi d'avui seria molt més net"*

---

### Diapositiva 12 — Tancament del Bloc 3
- Sessions 3-5: el viatge complet del so en temps real
- Blocking (offline) → callback (temps real) → efectes amb memòria → control interactiu
- El model de callback és el cor del que farem al projecte final:
  looper, sintetitzador, drum-replacement — tots basats en callbacks
- Sessió 6: canviem de domini → MIDI i control musical
