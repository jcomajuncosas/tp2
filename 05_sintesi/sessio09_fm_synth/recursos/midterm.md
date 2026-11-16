# TP2 — Revisió de mig curs

**Nom:** ______________________________

**No compta per a la nota.** Serveix perquè el professor sàpiga què cal reforçar, i com. Respon tu sol, sense ordinador. Si no ho saps, escriu què creus i per què: un raonament a mitges ens diu molt més que una resposta en blanc.

Temps: **20 minuts**.

---

## Part 1 — Què imprimeix? (6')

Escriu exactament què apareix a la pantalla.

**1a.**
```python
notes = [60, 64, 67]
resultat = []
for i in range(5):
    resultat.append(notes[i % 3])
print(resultat)
print(len(resultat), resultat[-1])
```

<br><br><br>

**1b.**
```python
import numpy as np
a = np.zeros(8)
a[2:5] = 1
a[-1] = 3
print(a)
print(np.max(a), len(a))
```

<br><br><br>

**1c.**
```python
nivell = 0
for k in range(8):
    if nivell < 5:
        nivell = nivell + 2
    elif nivell < 9:
        nivell = nivell + 1
    else:
        nivell = 0
    print(k, nivell)
```

<br><br><br><br><br>

---

## Part 2 — L'estat d'un objecte (6')

```python
class Comptador:
    def __init__(self, pas):
        self.pas = pas
        self._valor = 0

    def avanca(self):
        self._valor = (self._valor + self.pas) % 10
        return self._valor
```

**2a.** Omple la taula: el valor de `a._valor` i `b._valor` **després** d'executar cada línia.

| Línia | `a._valor` | `b._valor` |
|---|---|---|
| `a = Comptador(3)` <br> `b = Comptador(4)` | | |
| `a.avanca()` | | |
| `b.avanca()` | | |
| `a.avanca()` | | |
| `b.pas = 1` | | |
| `b.avanca()` | | |
| `x = a.avanca()` | | |
| `y = a.avanca()` | | |

Quant valen `x` i `y`? &nbsp;&nbsp; `x` = ______ &nbsp;&nbsp; `y` = ______

**2b.** Aquesta versió té un error.

```python
class Comptador2:
    def __init__(self, pas):
        pas = pas
        self._valor = 0

    def avanca(self):
        self._valor = self._valor + self.pas

c = Comptador2(3)
c.avanca()
```

- En quina línia s'atura el programa? ______________________________
- Per què? ______________________________________________________
- Com l'arreglaries? ______________________________________________

---

## Part 3 — Escriu-la tu (8')

Escriu la funció `compta_pics(so, llindar)`: rep un array NumPy `so` i un número `llindar`, i retorna **quantes mostres** tenen un valor absolut **més gran** que `llindar`. Fes-ho amb un bucle.

Exemple: `compta_pics(np.array([0.1, -0.9, 0.5, 0.95, -0.2]), 0.8)` → `2`

<br><br><br><br><br><br><br><br>

**Si et sobra temps:** fes que retorni també l'**índex de la primera** mostra que supera el llindar (o `-1` si no n'hi ha cap). Amb l'exemple de dalt: `(2, 1)`.

<br><br><br><br><br>
