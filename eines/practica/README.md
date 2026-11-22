# Pràctica de Python (prototip, nov. 2026)

Bateries d'exercicis amb variants aleatòries i progrés individual per domini, com qui es prepara el carnet de conduir. Tot el Python s'executa **al navegador de l'alumne** (Pyodide): al servidor no s'hi executa res. Els resultats van a un Google Sheet de l'ESMUC.

- **Banc TP1** (9 conceptes): mecànica de Python en context musical neutre. Serveix per a l'**anivellament** a l'inici de TP2 en properes edicions (`BANCS: ['tp1']`).
- **Banc TP2** (9 conceptes): la mateixa mecànica dins dels conceptes del curs: arrays i mostres, blocs, buffers circulars, **sintaxi de classes** (constructors, `self`, objectes dins d'objectes, àlies, arreglar errors de `self`), objectes amb estat, callbacks.
- **Tres tipus d'exercici:** *predir* (què imprimeix?), *escriure* (una funció o classe, provada amb casos ocults) i *ordenar* (línies desordenades, *Parsons problems*, amb diverses estructures per plantilla i una línia que sobra).
- **Correcció de *predir* tolerant amb el format:** decimals arrodonits, coma decimal, `0.` vs `0.0` i tuples o llistes sense el format exacte. Es dona per bo, però amb una nota que explica com ho escriuria Python. Amb els valors continua sent estricta.
- **Interfície:** quant falta per dominar el concepte, exercicis de repàs marcats com a extra, punts i quatre insígnies, enunciat no seleccionable i enganxar desactivat a les respostes (`BLOQUEJA_COPIA` a `config.js`). Es registra el temps de cada exercici al Sheet.
- **Domini:** 3 encerts seguits, i almenys un ha de ser escrivint codi. Els conceptes dominats tornen a sortir de tant en tant com a repàs.

Ningú no pot impedir que facin servir IA a casa. Per això aquesta eina és de **pràctica formativa**, i els mínims es certifiquen a classe.

## Blocs i calendari

Els conceptes s'agrupen en tres blocs (`blocs.json`) que s'obren segons el calendari, canviant `BLOCS_OBERTS` a `config.js` (i `VERSIO`, perquè els navegadors no facin servir la còpia antiga):

| Fase | `BLOCS_OBERTS` | Blocs oberts | Checkpoint en paper |
|---|---|---|---|
| Sessió 1 | 1 | Base de Python | — |
| Sessió 2 | 2 | + Arrays i so | **CP1** (Base de Python) |
| Sessió 3 | 3 | + Classes i estat | — |
| Sessió 4 | 3 | (tots) | **CP2** (Arrays i so + Classes i estat) |
| Dia d'exàmens | 3 | (tots) | Recuperació de les àrees no superades + prova oral |

Dins d'un bloc obert, tots els conceptes són accessibles. L'eina proposa l'ordre, però l'alumne en pot triar un altre si s'encalla. Els blocs tancats es veuen en gris, amb un cadenat.

## Checkpoints en paper

```bash
python3 genera_checkpoint.py CP1 codis.csv                                  # un full diferent per alumne
python3 genera_checkpoint.py CP1 codis.csv --recuperacio --arees A,C        # variants noves, només aquestes àrees
python3 genera_checkpoint.py CP1 codis.csv --recuperacio --nomes K7M2QX     # només aquest alumne
```

Genera `checkpoints/CP1_fulls.html` (un full per alumne: obre'l al navegador i imprimeix-lo) i `checkpoints/CP1_claus.html` (taula de recollida + clau de cada alumne). Necessita NumPy (el venv del curs ja el té).

- **3 àrees per checkpoint, 2 exercicis per àrea:** un de "què imprimeix?" i un d'escriure o ordenar, de conceptes diferents. Una àrea se supera si tots dos són correctes. A la recuperació només es repeteixen les àrees no superades, amb variants noves.
- **Cada alumne té una variant diferent,** que depèn del seu codi: copiar del del costat no serveix de res. Tornar a executar l'script dona exactament els mateixos fulls.
- Les àrees i els minuts són a `blocs.json`.

## Estructura

| Fitxer | Què és |
|---|---|
| `index.html`, `style.css`, `app.js` | la pàgina |
| `worker.js` | executa Python (Pyodide) en un fil a part; si el codi de l'alumne es penja, es mata i es reinicia |
| `config.js` | **l'únic fitxer que cal tocar**: URL d'Apps Script, blocs oberts, ratxa de domini… |
| `blocs.json` | blocs de conceptes i àrees dels checkpoints (eina i paper) |
| `genera_checkpoint.py` | fulls en paper per alumne + claus de correcció |
| `py/motor.py` | genera variants i corregeix (el mateix codi a Pyodide i a CPython) |
| `py/banc_tp1.py`, `py/banc_tp2.py` | les plantilles d'exercici |
| `validar_banc.py` | valida tot el banc amb CPython (vegeu més avall) |
| `apps_script/Code.gs` | receptor de resultats → Google Sheet |
| `genera_codis.py` | codis personals i enllaços per a cada alumne |

## Desplegament

### 1. Google Sheet + Apps Script (una vegada)

1. Crea un Google Sheet al Drive de l'ESMUC (p. ex. "Pràctica Python TP2 — resultats").
2. Genera els codis:
   ```bash
   cd eines/practica
   python3 genera_codis.py alumnes.txt https://moodle22569.hostkey.in/apps/practica-tp2/
   ```
   `alumnes.txt` té un nom per línia. Crea `codis.csv` i `enllacos.txt`. **No els comitis** (ja són al `.gitignore`).
3. Al Sheet, crea una pestanya **`Alumnes`** i importa-hi `codis.csv` (Fitxer → Importa → Substitueix el full actual).
4. Extensions → Apps Script. Enganxa-hi `apps_script/Code.gs` i desa.
5. Desplega → Nova implementació → tipus **Aplicació web**:
   - *Executa com a:* **Jo**
   - *Qui hi té accés:* **Qualsevol usuari** (cal perquè l'alumne no ha d'iniciar sessió; el script rebutja qualsevol codi que no sigui a la pestanya `Alumnes`)
6. Copia l'URL que acaba en `/exec` a `config.js` → `ENDPOINT`.

Les pestanyes `Estat` (l'últim progrés de cada alumne, per recuperar-lo des de qualsevol ordinador), `Esdeveniments` (un registre de cada exercici, amb la resposta i els segons que hi ha dedicat) i `Progrés` (una fila per alumne i una columna per concepte: `✓` si l'ha dominat; si no, `ratxa · encerts/intents`) es creen soles.

### 2. Servidor (cada vegada que canviï alguna cosa)

És una carpeta estàtica dins `/apps/`, que nginx ja serveix amb HTTPS. **No cal tocar la configuració de nginx.**

```bash
cd ~/TP2_2627/eines/practica
rsync -av --delete --exclude '__pycache__' --exclude 'codis.csv' --exclude 'enllacos.txt' --exclude 'checkpoints' \
  ./ root@5.180.173.59:/var/www/html/apps/practica-tp2/
```
URL: <https://moodle22569.hostkey.in/apps/practica-tp2/>

Quan actualitzis el banc, canvia `VERSIO` a `config.js` perquè els navegadors no facin servir la còpia antiga.

### 3. Classroom

Hi ha dues opcions:
- **Enllaç personal:** a cada alumne, en un comentari privat, la seva línia d'`enllacos.txt`. L'enllaç ja porta el codi (`?a=K7M2QX`) i el navegador el recorda.
- **Enllaç comú + codi:** un material amb l'URL comú. Cada alumne hi escriu el seu codi la primera vegada.

El progrés es desa al navegador i també al Sheet (pestanya `Estat`, l'últim estat de cada alumne). En entrar, la web agafa el més recent dels dos, així que el progrés segueix l'alumne a qualsevol ordinador (casa, escola). La capçalera mostra el nom de l'alumne (de la pestanya `Alumnes`), perquè en un ordinador compartit ningú treballi amb el codi d'un altre sense adonar-se'n; l'enllaç «No ets tu? Canvia d'usuari» oblida el codi recordat; un enllaç personal (`?a=`) sempre mana sobre el codi recordat.

## Validar el banc (abans de cada desplegament)

```bash
python3 validar_banc.py          # 200 variants per plantilla
python3 validar_banc.py 1000     # més exhaustiu
```
Per a cada plantilla comprova que:
- genera variants diverses sense errors;
- la solució de referència passa;
- l'esquelet buit falla;
- **cada error típic d'alumne (mutant) falla**;
- el codi que veu l'alumne no fa servir idiomes vetats al curs (comprehensions, lambda, dict, try, with…).

## Afegir un exercici

Una plantilla és una funció Python decorada amb `@plantilla(id, concepte, tipus, numpy=...)` que rep un `random.Random` i retorna un diccionari:

- **`predir`:** `enunciat`, `codi`. La resposta correcta s'obté executant el codi, així que no cal escriure-la.
- **`escriure`:** `enunciat`, `esquelet`, `referencia`, `funcio`, `casos` (crides com a text) i `mutants` (com a mínim 2 errors típics). Opcionals:
  - `preambul` (p. ex. `import numpy as np`);
  - `ajudants` (funcions ocultes per provar classes o efectes laterals);
  - `requereix: ['For', 'While']` (obliga a fer servir un bucle);
  - `prohibeix: ['max']` (prohibeix una funció).
- **`ordenar`:** com `escriure`, però sense esquelet. Les línies de la referència es barregen.

L'esperat de cada cas surt d'executar la referència. Per tant, no hi ha cap clau escrita a mà que es pugui equivocar. Després d'afegir una plantilla, executa `validar_banc.py`.

## Provat (nov. 2026)

- **Validador:** 72 plantilles × 200 variants, 0 problemes. Cada mutant falla, i les línies que sobren als exercicis d'ordenar fan fallar el codi.
- **Chrome headless (Playwright):**
  - el primer exercici apareix en ~3 s (Pyodide des del CDN);
  - 40 encerts seguits → 9 conceptes dominats;
  - una resposta incorrecta mostra la sortida correcta;
  - un bucle infinit es talla i Python es reinicia (~8 s);
  - NumPy i *ordenar* funcionen;
  - el progrés es manté quan es recarrega la pàgina;
  - cap error JS.
- **Esdeveniments reals capturats de la pàgina i passats per `Code.gs`** (amb una imitació de l'API de Sheets): el registre i la matriu de progrés surten correctes, i els codis desconeguts es rebutgen. **El desplegament real a Apps Script encara no s'ha provat.**

## Pendent (idees, no fet)

- Simulacre final (examen aleatori amb el format del midterm).
- Exercicis de *trobar l'error*.
- Ordenar amb línies distractores.
- Vista docent amb el resum del Sheet (o un *dashboard*).
