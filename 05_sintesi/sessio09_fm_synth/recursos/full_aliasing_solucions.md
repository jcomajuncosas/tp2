# Full de l'aliasing (S09, Part 2) — Solucions (docent)

Valors calculats amb el mateix muntatge del full: sinus de 80 Hz, llegit cada 512 mostres (512 / 44100 = 11,61 ms), durant 0,2 s.

## 1–2. Els punts

18 línies vermelles, de 0 a 197 ms. Altura on cada línia talla el sinus:

| Línia | Temps (ms) | Altura |
|---|---|---|
| 0 | 0,0 | 0,00 |
| 1 | 11,6 | −0,43 |
| 2 | 23,2 | −0,78 |
| 3 | 34,8 | −0,97 |
| 4 | 46,4 | −0,98 |
| 5 | 58,0 | −0,79 |
| 6 | 69,7 | −0,44 |
| 7 | 81,3 | −0,01 |
| 8 | 92,9 | +0,42 |
| 9 | 104,5 | +0,77 |
| 10 | 116,1 | +0,97 |
| 11 | 127,7 | +0,98 |
| 12 | 139,3 | +0,79 |
| 13 | 150,9 | +0,45 |
| 14 | 162,5 | +0,02 |
| 15 | 174,1 | −0,41 |
| 16 | 185,8 | −0,77 |
| 17 | 197,4 | −0,97 |

Units, dibuixen una ona lenta i suau que **comença baixant**. Baixa perquè entre línia i línia el sinus fa una mica **menys** d'un cicle sencer (80 × 0,01161 = 0,93 cicles): cada punt queda una mica "enrere" respecte a l'anterior.

## 3. Freqüència de la corba

**~1,2 cicles en 0,2 s → uns 6 Hz.** Exacte: 86,13 − 80 = **6,13 Hz** (1,23 cicles en 0,2 s): la diferència entre els cops per segon que mirem el modulador i la seva freqüència. És la sirena de la Part 2.

## 4. Quan s'atura la sirena

**86,13 Hz** (44100 / 512 = blocs per segon). El modulador fa exactament un cicle per bloc: cada línia el talla a la mateixa altura. També qualsevol múltiple (172,27 Hz…). És la resposta a `freq_congelada` del notebook.

## Errors probables

- Unir els punts seguint el sinus gris, en lloc de traçar la corba suau que passa només pels punts.
- Respondre "80 Hz" o "16 cicles" a la pregunta 3.
- Respondre "80 Hz" o "0 Hz" a la pregunta 4, en lloc de pensar en blocs per segon.
