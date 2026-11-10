# Warm-up — Sessió 8
### Format: Google Forms (mode Quiz, autocorrecció activada)
> Temps suggerit: 5-8 minuts. Q1-Q2 repassen la S07; Q3-Q7 anticipen la sessió d'avui (es queden amb el dubte i ho aclarim en pocs minuts).

---

### Pregunta 1 — Repàs Sessió 7 (pretty_midi)

**Quina és la diferència principal entre crear una nota amb `mido` i amb `pretty_midi`?**

- A) `pretty_midi` no permet canviar mai la velocity de les notes
- ✅ B) `pretty_midi` treballa directament en segons, sense ticks
- C) `mido` només serveix per llegir fitxers, no per crear-ne
- D) Cap: les dues llibreries fan exactament el mateix

---

### Pregunta 2 — Repàs Sessió 7 (timing)

**Quina és la idea central de calcular cada temps objectiu des de l'origen (temps absolut)?**

- A) Fer que `time.sleep()` deixi de consumir CPU mentre espera
- ✅ B) Que els petits errors de cada espera no es vagin sumant
- C) Poder executar el seqüenciador en un fil a part del principal
- D) Reduir el tempo perquè el sistema tingui més marge de temps

---

### Pregunta 3 — Intuïció: per què calen classes

**Una funció "oblida" tot quan acaba. A la S05, per recordar la fase d'un oscil·lador, la guardàvem en una global. Si en volguéssim cinc, què seria més pràctic?**

- A) Cinc variables globals separades, una per a cada oscil·lador
- B) Cridar la funció cinc vegades seguides cada cop
- ✅ C) Cinc objectes, cadascun amb la seva pròpia fase a dins
- D) Una sola fase compartida per tots cinc oscil·ladors

---

### Pregunta 4 — Predicció (dues instàncies)

```python
class Fader:
    def __init__(self, nivell):
        self.nivell = nivell

f1 = Fader(1.0)
f2 = Fader(0.5)
f1.nivell = 0.2
print(f2.nivell)
```

**Què s'imprimirà?**

- A) 0.2
- ✅ B) 0.5
- C) 1.0
- D) Error

---

### Pregunta 5 — Concepte clau: oscil·lador vs envolvent

**Si només tens un `Oscillator` (sense cap envolvent) i li demanes 2 segons de so, què sentiràs?**

- A) Silenci, perquè li falta l'envolvent per poder sonar
- ✅ B) Un so que entra i surt de cop, sense atac ni final suau
- C) Un clic molt curt seguit de silenci fins al final
- D) Un error, perquè sense envolvent l'ona no es pot generar

---

### Pregunta 6 — MIDI i l'envolvent (no l'oscil·lador)

**Quan arriba un `note_off`, què té més sentit que passi, en un sintetitzador modular?**

- A) L'oscil·lador deixa de generar la seva ona a l'instant
- ✅ B) Comença el Release de l'envolvent; l'oscil·lador continua
- C) Es crea un oscil·lador nou de trinca per a la nota següent
- D) Res: `note_off` només afecta els sons gravats

---

### Pregunta 7 — Oscillator vs SamplePlayer

**Quina és la diferència fonamental entre `Oscillator` i `SamplePlayer`?**

- A) `SamplePlayer` s'executa molt més de pressa que no pas l'`Oscillator`
- ✅ B) Un calcula el so amb matemàtiques; l'altre en reprodueix un de gravat
- C) `Oscillator` només funciona amb MIDI i `SamplePlayer` sense
- D) Són la mateixa classe, però amb dos noms diferents
