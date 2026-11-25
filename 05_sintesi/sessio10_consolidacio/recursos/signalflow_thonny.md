# signalflow a Thonny, pas a pas

`signalflow` és una llibreria de síntesi en temps real: oscil·ladors, envolvents i filtres ja fets, que es connecten com en un sintetitzador modular. A la propera sessió la farem sonar des de Thonny.

**Necessites:** Thonny, internet i uns 10 minuts. **No cal** ser administrador de l'ordinador, ni obrir cap terminal, ni crear cap entorn virtual (si en vas fer un a la S09, mira el cas D).

---

## 1. Primer, mira què tens (2 minuts)

Obre a Thonny el fitxer **`prova_signalflow.py`** (és en aquesta mateixa carpeta) i prem **F5**. Escriu a la Shell una cosa semblant a aquesta:

```
Python 3.14.0 - 64 bits
Sistema: Windows 11 - AMD64
...
✅ Aquest Python pot tenir signalflow
   ✅ numpy
   ...
   ❌ signalflow
```

La primera línia és la que compta: és el Python que fa servir **el teu Thonny**, que pot ser diferent del Python de l'ordinador. Amb aquesta línia, busca el teu cas:

| Què et surt | Cas |
|---|---|
| Python **3.9 o més nou**, **64 bits** | **A**: el cas normal (Thonny 5 porta Python 3.14 i Thonny 4.1 el 3.10; tots dos van bé) |
| Python **3.8**, o **32 bits** | **B**: cal un Thonny més nou |
| **macOS 11 o més antic** | **C**: signalflow no hi funciona |
| L'intèrpret és una carpeta teva (`signalflow-env`...) | **D**: un entorn virtual de la S09 |

---

## 2. Instal·la signalflow

### Cas A: el normal

1. A Thonny: **Tools → Manage packages...** (si tens Thonny en un altre idioma, és el menú equivalent d'*Eines*).
2. Escriu `signalflow` al cercador i prem **Search on PyPI**.
3. Clica `signalflow` a la llista de resultats i prem **Install**. Espera que acabi.
4. Torna a prémer **F5** amb `prova_signalflow.py`. Hauries de sentir 2 segons d'un so de FM.

Si a la llista t'hi falta alguna altra llibreria del curs (`sounddevice`, `mido`, `rtmidi2`...), instal·la-la de la mateixa manera.

**Als ordinadors de l'escola també funciona.** El gestor de paquets de Thonny instal·la a la *teva* carpeta d'usuari, no a la del sistema, i per això no demana permisos. Si la sessió de Windows de l'escola s'esborra en tancar-la, caldrà tornar-ho a fer cada dia: en aquest cas fes servir el Thonny portable del cas B, en un llapis USB.

### Cas B: Python 3.8 o 32 bits → Thonny nou, sense instal·lar res

No cal desinstal·lar el teu Thonny vell:

1. A **thonny.org**, baixa:
   - **Windows:** la versió **portable** (`thonny-...-windows-portable-x64.zip`). És un fitxer zip: no s'instal·la i no demana permisos.
   - **Mac:** l'instal·lador que toca: **Apple Silicon** (M1, M2...) o **Intel**. Ho veus a  → *Quant a aquest Mac*.
2. **Windows:** clic dret al zip → *Extreu-ho tot*, en una carpeta teva (Documents) o en un llapis USB. Obre el `thonny.exe` de dins.
3. Continua pel **cas A**.

Si fas servir el portable en un llapis, `prova_signalflow.py` et dirà on s'ha instal·lat signalflow («signalflow és a: ...»). Si la ruta comença per la lletra del llapis (`E:\...`), te l'emportes a qualsevol ordinador.

### Cas C: Mac amb macOS 11 o més antic

signalflow necessita macOS 12 (Monterey) o més nou. Si el teu Mac admet una actualització de macOS, aquesta és la solució. Si no, a classe treballaràs en parella o amb un ordinador de l'escola. La resta del curs et continua funcionant igual.

### Cas D: un entorn virtual de la S09

Si l'intèrpret de la primera línia és una carpeta teva (per exemple `.../signalflow-env/...`), Thonny fa servir aquell entorn, i per tant també pot funcionar. Fixa't, però, a la llista del pas 1: hi han de ser **totes** les llibreries del curs, no només signalflow.

Tornar al Python de Thonny és més senzill: clica la cantonada **de baix a la dreta** de Thonny, tria l'opció que diu **Thonny's Python** i continua pel **cas A**.

---

## 3. Com treballar amb signalflow a Thonny

Cinc regles que t'estalviaran problemes:

1. **Un sol `graph = AudioGraph()`, al principi del fitxer.** El graf és el motor de so i només n'hi pot haver un. Cada F5 reinicia el programa i el torna a crear de zero. Si crides des de la Shell una funció que en crea un altre, signalflow avisa amb `The global audio graph has already been created`. L'avís és inofensiu (el so funciona), però vol dir que el graf havia d'estar fora de la funció.
2. **`graph.wait(5)`, no `graph.wait()`.** Sense número, el programa espera per sempre.
3. **El botó vermell Stop** (o **Ctrl+F2**) atura el programa i el so.
4. **No anomenis mai cap fitxer `signalflow.py`.** Python el trobaria abans que la llibreria de debò.
5. **Un motor de so cada vegada.** No barregis en un mateix fitxer un `sd.OutputStream` (sounddevice) i signalflow: tots dos volen la mateixa sortida de so.

Una diferència respecte dels nostres programes: signalflow treballa a la freqüència de mostreig de la teva targeta de so, que sovint és 48000 Hz i no 44100. Ho pots saber amb `print(graph.sample_rate)`.

---

## 4. Si alguna cosa falla

| Missatge o símptoma | Què vol dir | Què cal fer |
|---|---|---|
| `No matching distribution found for signalflow` | El teu Python no té versió de signalflow | Pas 1: casos B, C |
| `ModuleNotFoundError: No module named 'signalflow'`, i en canvi l'has instal·lat | L'has instal·lat en un altre Python | Mira la cantonada de baix a la dreta; torna a instal·lar amb **Manage packages** *des d'aquest Thonny* |
| `NameError: name 'AudioGraph' is not defined`, amb un fitxer teu al missatge | Tens un fitxer anomenat `signalflow.py` | Canvia-li el nom (regla 4) |
| `AudioIOException: ... Error initialising output device` | signalflow no troba cap sortida de so | Connecta auriculars o altaveus, tanca les altres aplicacions de so i torna a prémer F5 |
| `prova_signalflow.py` diu ✅ però no sents res | El so va a una altra sortida | Mira la sortida de so del sistema i el volum |
| **Manage packages** està en gris | Thonny no fa servir un Python normal (per exemple, MicroPython) | Cantonada de baix a la dreta → **Local Python 3** |
| La cerca o la instal·lació no acaben mai, a l'escola | La xarxa no deixa baixar paquets | Avisa a classe: hi ha una còpia de les llibreries en un llapis |

Si et surt un altre error, copia el missatge **sencer** de la Shell i porta'l a classe.
