# Pràctica de Python (prototip, nov. 2026)

Bateries d'exercicis amb variants aleatòries i progrés individual per domini, com qui es prepara el carnet de conduir. Tot el Python s'executa **al navegador de l'alumne** (Pyodide): al servidor no s'hi executa res. Els resultats van a un Google Sheet de l'ESMUC.

- **Banc TP1** (9 conceptes): mecànica de Python en context musical neutre. Serveix per a l'**anivellament** a l'inici de TP2 en properes edicions (`BANCS: ['tp1']`).
- **Banc TP2** (9 conceptes): la mateixa mecànica dins dels conceptes del curs: arrays i mostres, blocs, buffers circulars, **sintaxi de classes** (constructors, `self`, objectes dins d'objectes, àlies, arreglar errors de `self`), objectes amb estat, callbacks.
- **Tres tipus d'exercici:** *predir* (què imprimeix?), *escriure* (una funció o classe, provada amb casos ocults) i *ordenar* (línies desordenades, *Parsons problems*, amb diverses estructures per plantilla i una línia que sobra).
- **Correcció de *predir* tolerant amb el format:** decimals arrodonits, coma decimal, `0.` vs `0.0` i tuples o llistes sense el format exacte. Es dona per bo, però amb una nota que explica com ho escriuria Python. Amb els valors continua sent estricta.
- **Interfície:** quant falta per dominar el concepte, exercicis de repàs marcats com a extra, punts i quatre insígnies, enunciat no seleccionable i enganxar desactivat a les respostes (`BLOQUEJA_COPIA` a `config.js`). Es registra el temps de cada exercici al Sheet.
- **Domini:** 3 encerts seguits, i almenys un ha de ser escrivint codi. Els conceptes dominats tornen a sortir de tant en tant com a repàs.

Ningú no pot impedir que facin servir IA a casa. Per això aquesta eina és de **pràctica formativa**, i els mínims es certifiquen a classe.

## Estructura

| Fitxer | Què és |
|---|---|
| `index.html`, `style.css`, `app.js` | la pàgina |
| `worker.js` | executa Python (Pyodide) en un fil a part; si el codi de l'alumne es penja, es mata i es reinicia |
| `config.js` | **l'únic fitxer que cal tocar**: URL d'Apps Script, bancs actius, ratxa de domini… |
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

Les pestanyes `Esdeveniments` (un registre de cada exercici, amb la resposta i els segons que hi ha dedicat) i `Progrés` (una fila per alumne i una columna per concepte: `✓` si l'ha dominat; si no, `ratxa · encerts/intents`) es creen soles.

### 2. Servidor (cada vegada que canviï alguna cosa)

És una carpeta estàtica dins `/apps/`, que nginx ja serveix amb HTTPS. **No cal tocar la configuració de nginx.**

```bash
cd ~/TP2_2627/eines/practica
rsync -av --delete --exclude '__pycache__' --exclude 'codis.csv' --exclude 'enllacos.txt' \
  ./ root@5.180.173.59:/var/www/html/apps/practica-tp2/
```
URL: <https://moodle22569.hostkey.in/apps/practica-tp2/>

Quan actualitzis el banc, canvia `VERSIO` a `config.js` perquè els navegadors no facin servir la còpia antiga.

### 3. Classroom

Hi ha dues opcions:
- **Enllaç personal:** a cada alumne, en un comentari privat, la seva línia d'`enllacos.txt`. L'enllaç ja porta el codi (`?a=K7M2QX`) i el navegador el recorda.
- **Enllaç comú + codi:** un material amb l'URL comú. Cada alumne hi escriu el seu codi la primera vegada.

El progrés es desa al navegador (localStorage) i, a més, al Sheet. Si un alumne canvia d'ordinador, en aquest navegador comença el mapa de zero, però el registre del Sheet hi és sencer.

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
