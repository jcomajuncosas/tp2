# Warm-up — Sessió 2
### Format: Google Forms (mode Quiz, autocorrecció activada)

> **Instruccions de muntatge:** Crea un Google Form nou en mode Quiz (igual que la Sessió 1). Temps suggerit: 5-8 minuts a l'inici de la sessió.

---

### Pregunta 1 — Repàs Sessió 1 (gain)

**Tenim `wave` amb amplitud màxima 0.8. Volem reduir el volum a la meitat. Quina línia ho fa?**

- A) `wave = wave + 0.5`
- ✅ B) `wave = wave * 0.5`
- C) `wave = wave / 2 + 1`
- D) `wave = wave - 0.5`

---

### Pregunta 2 — Repàs Sessió 1 (longitud d'array)

**`t = np.linspace(0, 2.0, int(44100*2.0), endpoint=False)`. Quant val `len(t)`?**

- A) 2
- B) 44100
- ✅ C) 88200
- D) 88201

---

### Pregunta 3 — Intuïció: desar i recuperar dades

**Si desem un array a un fitxer i després el tornem a llegir, esperaries recuperar les mateixes dades, dades diferents, o no es pot saber sense provar-ho?**

- A) Sempre dades diferents — desar a disc sempre introdueix petits canvis
- ✅ B) Les mateixes dades (o pràcticament idèntiques) — és la idea bàsica de "desar i carregar"
- C) Només si el fitxer es llegeix en menys d'1 segon des que s'ha escrit
- D) No es pot saber — depèn de l'extensió del fitxer

*(Comentari: és el mateix principi que `open()`/`read()`/`write()` de TP1, ara aplicat a `soundfile` amb arrays sencers.)*

---

### Pregunta 4 — Detecció d'error (mixing)

```python
so1 = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
so2 = np.array([0.1, 0.1, 0.1])

mix = so1 + so2
```

**Què passa en executar la línia `mix = so1 + so2`?**

- A) Es retalla automàticament `so1` a 3 elements i se sumen
- B) S'allarga automàticament `so2` amb zeros fins a 5 elements
- ✅ C) Dona error (`ValueError`: les formes (shapes) no coincideixen)
- D) Funciona i `mix` té 8 elements (concatenats)

*(Comentari per a la correcció en directe: a diferència de les llistes de Python, NumPy NO concatena amb `+` — i tampoc ajusta longituds automàticament. Cal igualar-les abans amb `[:n]`.)*

---

### Pregunta 5 — Predicció (np.tile)

```python
loop = np.array([1, 2, 3])
resultat = np.tile(loop, 3)
print(resultat)
```

**Què s'imprimirà?**

- A) `[3, 6, 9]`
- ✅ B) `[1, 2, 3, 1, 2, 3, 1, 2, 3]`
- C) `[1, 2, 3]`
- D) Error

---

### Pregunta 6 — Connexió amb TP1

**A TP1, per repetir un patró de notes 4 vegades féieu `for _ in range(4): tocar(pattern)`. Quina és la diferència principal de fer-ho amb `np.tile(loop_array, 4)`?**

- A) `np.tile` és més lent
- B) `np.tile` només funciona amb números enters
- ✅ C) `np.tile` genera tot l'array repetit d'un cop, sense bucle explícit
- D) No hi ha cap diferència, és exactament el mateix

---

### Pregunta 7 — Ordenació (estil Parsons)

Tens aquestes 4 línies (en desordre) que llegeixen un fitxer, l'escalen i en desen un de nou:

```
1. data_quiet = data * 0.3
2. sf.write("sortida.wav", data_quiet, sr)
3. data, sr = sf.read("entrada.wav")
4. import soundfile as sf
```

**¿Quin és l'ordre correcte?**

- A) 1, 2, 3, 4
- ✅ B) 4, 3, 1, 2
- C) 4, 1, 3, 2
- D) 3, 4, 1, 2
