# Midterm S09 — Solucions i graella de correcció (docent)

**Objectiu:** diagnosticar, no qualificar. No compta per a la nota. Les respostes s'han verificat executant el codi.

---

## Solucions

**1a**
```
[60, 64, 67, 60, 64]
5 64
```

**1b**
```
[0. 0. 1. 1. 1. 0. 0. 3.]
3.0 8
```
Detalls que diagnostiquen: `2:5` inclou el 2 i exclou el 5; `-1` és l'últim; NumPy imprimeix floats (`0.`, `3.0`).

**1c**
```
0 2
1 4
2 6
3 7
4 8
5 9
6 0
7 2
```
És una màquina d'estats en miniatura (com l'`Envelope` d'avui): a cada volta només s'executa **una** branca. Error típic: aplicar dues branques a la mateixa volta (`4 → 6 → 7`).

**2a**

| Línia | `a._valor` | `b._valor` |
|---|---|---|
| creació | 0 | 0 |
| `a.avanca()` | 3 | 0 |
| `b.avanca()` | 3 | 4 |
| `a.avanca()` | 6 | 4 |
| `b.pas = 1` | 6 | 4 |
| `b.avanca()` | 6 | 5 |
| `x = a.avanca()` | 9 | 5 |
| `y = a.avanca()` | 2 | 5 |

`x = 9`, `y = 2` (12 % 10).

**2b**
- S'atura a `self._valor = self._valor + self.pas`, dins d'`avanca` (a l'última línia, `c.avanca()`). **No** s'atura en crear `c`.
- `AttributeError: 'Comptador2' object has no attribute 'pas'`. A `__init__`, `pas = pas` és una variable local que es perd en acabar el mètode.
- Arreglar: `self.pas = pas`.

**3**
```python
def compta_pics(so, llindar):
    compte = 0
    primer = -1
    for i in range(len(so)):
        if abs(so[i]) > llindar:
            compte = compte + 1
            if primer == -1:
                primer = i
    return compte, primer      # versió bàsica: return compte
```
Respostes vàlides alternatives: `for mostra in so:` (versió bàsica), `np.abs(so[i])`. Una solució vectoritzada (`np.sum(np.abs(so) > llindar)`) és correcta, però no respon "amb un bucle": anota-la a part, perquè diu una altra cosa (sap NumPy, potser no sap escriure el bucle).

---

## Graella

Puntuació per ítem: **2** = correcte · **1** = idea bona amb error menor · **0** = incorrecte o en blanc. A més, marca el **tipus d'error** amb les lletres de sota (pot ser més d'una). El que ens interessa més per a l'anàlisi són les lletres.

| Codi | Tipus d'error | Exemples |
|---|---|---|
| **B** | Model de bucle | `range(5)` → 1…5; `%` mal entès; índex fora de rang |
| **T** | Talls i índexs | `2:5` incloent el 5; `-1` no entès |
| **N** | NumPy | no sap que `np.zeros` dona floats; `np.max` / `len` |
| **C** | Condicionals | més d'una branca per volta; ordre de l'`elif` |
| **E** | Estat i objectes | instàncies que comparteixen valor; `b.pas = 1` afecta `a`; el `return` canvia l'estat |
| **L** | Atribut vs. variable local | 2b: no veu que falta `self.`; diu que falla en crear l'objecte |
| **F** | Estructura de funció | sense `return`, `print` en lloc de `return`, paràmetres ignorats |
| **A** | Acumulador / patró | no inicialitza el comptador; el reinicia dins el bucle |
| **X** | Sintaxi | `:`, indentació, parèntesis (només si impedeix entendre la intenció) |

### Full de recollida

| Alumne | 1a | 1b | 1c | 2a | 2b | 3 | 3+ | Lletres d'error | Observacions |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |

### Què mirar a l'anàlisi

- **Part 1 bé, Part 3 malament** → llegeixen però no escriuen: més "piquen" guiat per l'enunciat (què, no com), fragments curts freqüents.
- **Part 2 malament (E, L)** → el model d'objectes de la S08 no s'ha assentat: abans de continuar amb el Bloc 5, cal un moment de traça d'estat (com la Part 4 del notebook d'avui).
- **1c malament (C)** → afecta directament la lectura de l'`Envelope` i de tot el que sigui màquina d'estats.
- **Errors B/T generalitzats** → falta de base TP1: valorar exercicis curts de repàs a casa (el "mini-curs de picar codi" pendent).
