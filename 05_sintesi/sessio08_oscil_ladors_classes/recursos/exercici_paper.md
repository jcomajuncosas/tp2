# Exercici en paper — Sessió 8
### Dissenyar classes abans de programar-les

Per parelles, sense ordinador. Llapis, goma i ganes de dibuixar caixes.

---

## La descripció

> Volem construir una petita **groovebox** per a un directe.
>
> Té un **baix sintetitzat**: una ona de dent de serra amb una envolvent curta, que toca les notes MIDI d'un patró. Cada nota té la seva velocity.
>
> Té dos **sons de percussió gravats**, un bombo i un charles, que es disparen als passos del patró on toqui. Cadascun té el seu volum.
>
> A la sortida del baix hi ha un **eco** (delay) amb un temps de retard i una realimentació que es poden regular.
>
> El **patró** té 16 passos i un tempo en bpm. Volem poder canviar el patró i el tempo mentre sona.

---

## Part A — Substantius i verbs

Subratlla a la descripció:

- amb una línia, els **substantius** → candidats a ser una **classe** o un **atribut**
- amb dues línies, els **verbs** → candidats a ser un **mètode**

No tots els substantius seran classes! Alguns seran dades d'una altra classe.

---

## Part B — Una caixa per classe

Per a cada classe que decidiu crear, dibuixeu una caixa amb tres franges:

```
┌──────────────────────────────┐
│ NomDeLaClasse                │   ← nom (amb majúscula)
├──────────────────────────────┤
│ atribut1, atribut2, ...      │   ← quines DADES guarda
│ ★ _estat                     │
├──────────────────────────────┤
│ metode(param1, param2)       │   ← què SAP FER
│   → què retorna              │      (signatura: nom + paràmetres + resultat)
└──────────────────────────────┘
```

- Marqueu amb una **★** els atributs que són **estat intern**: valors que l'objecte fa canviar sol mentre treballa (com la fase d'un oscil·lador), i que ningú de fora hauria de tocar. Escriviu-los amb guió baix: `_phase`.
- Si una classe en conté una altra, dibuixeu una fletxa entre les caixes.

---

## Part C — L'esquelet, a mà

Tria **dues** de les vostres caixes i escriu-ne l'esquelet en Python, sense omplir els mètodes. Model:

```python
class Metronom:
    def __init__(self, bpm=120):
        self.bpm = bpm               # configuració
        self._comptador = 0          # ★ estat intern

    def durada_pas(self):
        pass                         # (ho omplirem més endavant)

    def tic(self):
        pass
```

Fixa't en els tres detalls que més s'obliden: el `self` com a primer paràmetre de **cada** mètode, el `self.` davant de cada atribut, i els dos punts `:` al final de `class` i de `def`.

---

## Part D — Compareu amb una altra parella

1. Quantes classes teniu cadascú? Per què?
2. Teniu una classe per al bombo i una altra per al charles, o **una sola classe amb dues instàncies**?
3. Hi ha alguna dada que hàgiu posat com a atribut i que potser hauria de ser un paràmetre d'un mètode (o al revés)?
4. Quins mètodes de classes **diferents** fan la mateixa mena de feina? Els heu posat el mateix nom?
5. On viu el tempo? On viu la fase? On viu la "cinta" de l'eco?
