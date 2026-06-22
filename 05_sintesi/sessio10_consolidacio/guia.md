# Sessió 10 — Bloc 5c: Consolidació de síntesi (tancament del Bloc 5)

**Bloc temàtic:** 05_sintesi
**Tipus de sessió:** Consolidació pràctica. Pes principal: repte ampli. Teoria nova mínima i guiada amb mesures reals (profiling).
**Durada:** 2h
**Entorn:** Thonny exclusivament (tot el contingut és temps real/MIDI, com el gruix de S9). No hi ha notebook Colab aquesta sessió.

---

## Estructura de la sessió

| Temps aprox. | Activitat | Material |
|---|---|---|
| 0:00 – 0:08 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 0:08 – 0:20 | Profiling guiat (mesures reals, no només teoria) | `exemples.py` Seccions 2-3 (Thonny) |
| 0:20 – 1:30 | **Repte de consolidació**: kit de percussió sintètica | `assignment.py` (Thonny) |
| 1:30 – 1:45 | Tast ampliat de `signalflow`: un altre tipus de síntesi | `exemples.py` Secció 5 (Thonny) |
| 1:45 – 2:00 | Tancament Bloc 5 + preview Bloc 6 | `recursos/cheat_sheet.md` |

**Nota sobre el repartiment:** a diferència de S9, aquí NO s'introdueix arquitectura nova — tot el contingut tècnic (UGen, `process()`, Envelope amb `stage`, integració MIDI) ja existeix de S8/S9. El pes de la sessió és consolidar-ho en un sol projecte ampli i tancar dos pendents tècnics que es van deixar explícitament oberts a S9.

---

## Objectius

1. Veure amb **mesures reals** (no només raonament) per què processar en blocs vectoritzats és molt més ràpid que mostra a mostra, i quan llegir un modulador a baixa resolució introdueix aliasing real — els dos pendents tècnics deixats oberts a S9.
2. Combinar en un sol projecte (`Oscillator`, `Envelope`, MIDI temps real) tot el que s'ha après al Bloc 5, demostrant que l'arquitectura UGen serveix per a registres tímbrics molt diferents (no només per a notes melòdiques): aquí, percussió.
3. Introduir `Noise` com el UGen més senzill possible (sense estat) — contrast pedagògic amb `Oscillator` (amb fase) i `Envelope` (amb `stage`).
4. Ampliar la mirada cap a `signalflow` amb un exemple d'un tipus de síntesi diferent de tot el que s'ha fet aquest curs (additiva massiva + efectes de modulació), com a motivació per explorar-ho de manera autònoma — NO com a contingut a aprofundir a classe.
5. Tancar el Bloc 5 amb una taula-resum de conjunt (S8+S9+S10) abans d'entrar al Bloc 6 (FFT).

## Decisions de disseny importants (llegir abans d'ensenyar)

**Per què percussió i no una altra ampliació (per exemple FM amb una segona variant):** es va decidir conscientment NO repetir FM (ja vista a fons a S9) i explorar en lloc d'això un **registre tímbric diferent** — això demostra que l'arquitectura UGen (`process()`, `Envelope` amb `stage`) és prou general per a sons molt diferents dels que s'havien fet fins ara (notes melòdiques sostingudes), sense necessitat de cap concepte nou. El kick (Oscillator amb pitch-drop) i el hi-hat (Noise) reutilitzen el 100% de la infraestructura de S8/S9.

**Per què `Noise` és deliberadament l'UGen MÉS senzill possible:** no té cap estat (`self.phase` o equivalent) — cada `process(n)` és independent. Es presenta explícitament com a contrast amb `Oscillator` (que sí necessita fase persistent) per reforçar la idea que "implementar `process()`" és el que defineix un UGen, no la complexitat interna.

**Per què el mapa de percussió és fix (nota 36=Kick, 42=Hi-hat) i no obert:** aquestes són les notes reals del mapa de percussió General MIDI (Kick 1 i Closed Hi-Hat respectivament), ja introduït conceptualment a `llista_instruments_gm()` de S7. Mantenir-ho fix permet autotests deterministes i connecta amb un estàndard real, no arbitrari.

**Per què el profiling es fa amb mesures reals (`perf_counter`) i no només es relata:** la pendència deixada explícitament a S9 era doble — (1) quantificar l'estalvi real de processar en blocs vs. mostra a mostra, i (2) quantificar quan llegir un modulador a baixa resolució introdueix aliasing. Tots dos es resolen aquí amb mesures numèriques i un gràfic comparatiu, no amb afirmacions genèriques — precisament perquè a S9 es van detectar errors conceptuals per haver raonat sense verificar contra el codi real (veure README per l'historial complet d'aquell episodi).

**Per què `signalflow` i no `pyo` (canvi respecte al pla original):** la primera versió d'aquest material usava `pyo` per al tast ampliat, igual que a S9. Es va descobrir, en provar-ho en un Mac amb Python recent (Thonny amb Python 3.14), que `pyo` no s'ha actualitzat des de fa anys i només té wheels compilats fins a Python 3.11 — `pip install pyo` falla amb "No matching distribution found", independentment del sistema operatiu o l'arquitectura. `signalflow` és una alternativa activament mantinguda (última versió: juliol 2025), amb suport real fins a Python 3.13 i instal·lació verificada en Mac Apple Silicon (confirmat amb `signalflow test` sonant correctament). Es va substituir `pyo` per `signalflow` a tot el material de S9 i S10.

**Per què el tast ampliat ara CONSTRUEIX un chorus en lloc de cridar un `Chorus` ja fet:** `signalflow` no té cap classe `Chorus`/`Phaser` directa (a diferència de `pyo`) — només delays (`OneTapDelay`, `CombDelay`, `AllpassDelay`). En lloc de ser una limitació, és una millora pedagògica: el chorus es construeix amb un `SineLFO` modulant el `delay_time` d'un `OneTapDelay`, exactament el mateix patró "un node alimenta el paràmetre d'un altre" que s'ha ensenyat tota la sessió. Es manté la referència històrica concreta (Solina/ARP String Ensemble, 1974-81) com a motivació per explorar-ho fora de classe, i la galeria d'exemples oficial de `signalflow` (`https://github.com/ideoforms/signalflow/tree/master/examples`) com a punt de partida.

**Per què el repte de percussió és autònom, sense connectar-lo amb els rols del projecte final:** malgrat que el rol "drum-replacement" del projecte final farà servir idees molt similars, es manté el repte de S10 com a consolidació de fonaments comuns a TOTS els alumnes (independentment de quin rol triïn després), no com a feina avançada d'un rol concret. Es pot esmentar la connexió breument a classe sense fer-ne el focus.

## Connexions amb sessions anteriors

- **Sessió 8:** `Oscillator`, `Envelope` (ADSR) — reutilitzats sense canvis a l'arquitectura, només noves instàncies amb paràmetres de percussió (decay curt, sense sustain).
- **Sessió 9:** `process(n_samples)`, l'estat persistent (`self.phase`), la integració amb el callback de `sounddevice` i `mido`, i els dos pendents tècnics que es tanquen avui (eficiència de blocs, aliasing per sota-mostreig).
- **Sessió 7:** el mapa General MIDI de percussió (`llista_instruments_gm()`) es recupera per justificar per què 36=Kick i 42=Hi-hat no són arbitraris.
- **Sessió 5:** el patró de processar en blocs dins un callback de temps real ja s'havia vist; avui se'n quantifica per primer cop l'avantatge real amb `perf_counter`.

## Materials necessaris

- Cap fitxer d'àudio nou necessari.
- `matplotlib` (ja usat des de S2) per als dos gràfics de profiling.
- **Opcional:** controlador MIDI per a qui en tingui, per disparar el kit de percussió en directe (el repte en si no ho exigeix — `assignment.py` no usa MIDI real, només timing programat, per mantenir els autotests deterministes; la integració amb MIDI real es pot fer com a extensió lliure un cop superat el repte).

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `exemples.py` — demo per a Thonny: profiling (Seccions 2-3), demo del kit de percussió (Secció 4, NO el repte en si), tast ampliat de `signalflow` (Secció 5)
- `assignment.py` — repte de consolidació: `Noise`, `Kick` (pitch-drop), `percussion_kit()` amb TODO + 4 autotests
- `recursos/cheat_sheet.md` — resum de tot el Bloc 5 (S8+S9+S10)
- `recursos/warmup_quiz.md` — preguntes per a Google Forms (repàs integrador S8+S9)
- `recursos/slides_outline.md` — diapositives
- `recursos/challenges.md` — Challenges opcionals (FM mostra-a-mostra real, ampliar el kit amb més sons, explorar més exemples de `signalflow`)

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Penjar `cheat_sheet.md` com a Google Doc
- [ ] Provar `exemples.py` localment, incloent els dos gràfics de profiling (es desen com a PNG al directori de treball)
- [ ] Confirmar quin és l'ordre de magnitud real del profiling vectoritzat/sample-by-sample a l'ordinador de l'aula (al contenidor de desenvolupament surt ~12-20x; pot variar segons maquinari)
