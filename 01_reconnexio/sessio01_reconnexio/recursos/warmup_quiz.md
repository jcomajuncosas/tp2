# Warm-up — Sessió 1
### Format: Google Forms (mode Quiz, autocorrecció activada)

> **Instruccions de muntatge:**
> 1. Crea un Google Form nou → menú ⚙️ Configuració → activa "Converteix en qüestionari" (Quiz mode) → activa "Allibera la puntuació immediatament" i "Mostra respostes correctes".
> 2. Per a cada pregunta, marca l'opció correcta indicada (✅) a "Clau de correcció".
> 3. Temps suggerit: 5-8 minuts a l'inici de la sessió, resposta individual, comentari ràpid en gran grup després.
> 4. Pes: participació (no penalitza per encertar/errar, sí per no fer-ho).

---

### Pregunta 1 — Predicció (opció múltiple)

**¿Quants valors té `range(0, 10, 3)` i quins són?**

- A) [0, 3, 6, 9, 12] — 5 valors
- ✅ B) [0, 3, 6, 9] — 4 valors
- C) [0, 3, 6, 9, 10] — 5 valors
- D) [3, 6, 9] — 3 valors

---

### Pregunta 2 — Detecció d'error

```python
for i in range(5)
    print(i)
```

**¿Què passa quan s'executa aquest codi?**

- A) Imprimeix 0, 1, 2, 3, 4
- B) Imprimeix 0, 1, 2, 3, 4, 5
- ✅ C) Dona error de sintaxi (`SyntaxError`)
- D) No fa res, però no dona error

*(Comentari per a la correcció en directe: falta `:` al final de la línia `for`. És l'error més habitual i el primer que cal revisar.)*

---

### Pregunta 3 — Predicció (connectant amb el que ve)

**¿Quants elements té l'array `np.arange(0, 1, 0.1)`?**

- A) 0.1
- B) 9
- ✅ C) 10
- D) 11

*(Comentari: de 0 a 0.9 en passos de 0.1 → 10 valors. `arange`, com `range`, no inclou el límit superior.)*

---

### Pregunta 4 — Llistes vs. Arrays (concepte clau del bloc)

**Si `a = [1, 2, 3]` (llista normal de Python) i fem `a * 2`, què obtenim?**

- A) `[2, 4, 6]`
- ✅ B) `[1, 2, 3, 1, 2, 3]`
- C) Error
- D) `6`

---

### Pregunta 5 — Llistes vs. Arrays (la mateixa, amb NumPy)

**Ara `a = np.array([1, 2, 3])` i fem `a * 2`. Què obtenim?**

- ✅ A) `[2, 4, 6]`
- B) `[1, 2, 3, 1, 2, 3]`
- C) Error
- D) `6`

*(Comentari: aquesta parella de preguntes (4 i 5) és la clau de tota la sessió — el mateix operador `*` fa coses diferents segons el tipus. Val la pena aturar-se 1 minut a comentar-ho en veu alta.)*

---

### Pregunta 6 — Funcions (paràmetres per defecte)

```python
def generate_tone(freq, duration, amplitude=0.5, sample_rate=44100):
    ...
    return wave
```

**Si cridem `generate_tone(440, 1.0)`, quin valor pren `amplitude`?**

- A) Dona error, falten arguments obligatoris
- ✅ B) 0.5
- C) 1.0 (el mateix valor que `duration`)
- D) S'ha d'indicar explícitament o queda sense definir

---

### Pregunta 7 — Ordenació (estil Parsons)

Tens aquestes 4 línies de codi (en desordre) que generen i reprodueixen un to:

```
1. wave = np.sin(2 * np.pi * freq * t)
2. sd.play(wave, sample_rate)
3. t = np.linspace(0, duration, int(sample_rate * duration))
4. freq, duration, sample_rate = 440, 1.0, 44100
```

**¿Quin és l'ordre correcte d'execució?**

- A) 1, 2, 3, 4
- ✅ B) 4, 3, 1, 2
- C) 4, 1, 3, 2
- D) 3, 4, 1, 2

*(Comentari: primer definim paràmetres, després l'eix de temps, després l'ona, i finalment la reproduïm. Aquesta seqüència es repetirà sempre.)*
