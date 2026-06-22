# Projecte final — Presentació de l'ensemble i inici de la implementació

**Bloc temàtic:** 07_projecte_final
**Tipus de sessió:** Tram multi-sessió, NO una classe tancada de 2h — s'estén tants dies com calguin segons el ritme real del grup (orientativament 2 sessions, però sense data de tall fixa entre elles).
**Entorn:** Thonny (tots els templates necessiten temps real/MIDI/àudio en directe — cap és apte per a Colab).
**Continuació:** `07_projecte_final/sessio13_implementacio_rols/` — mateixa dinàmica, mateixa guia, sense contingut diferenciat (veure nota a aquella carpeta).

---

## Estructura del tram (fases, no minutatge fix)

| Fase | Activitat | Material |
|---|---|---|
| 1 | Warm-up (Google Forms) | `recursos/warmup_quiz.md` |
| 2 | Presentació de l'ensemble (Slides) | `recursos/slides_outline.md` |
| 3 | Presentació dels 5 rols (Slides, mateix outline) | `recursos/slides_outline.md` |
| 4 | Tria de rol per grup/parella | — (gestió a classe, veure més avall) |
| 5 | Feina autònoma: implementar el template del rol triat | `templates/<rol>/<rol>.py` + `templates/<rol>/README.md` |
| 6 | (Per qui acabi abans) Reptes opcionals de refinament | `recursos/reptes_opcionals.md` |

Les fases 1-4 ocupen una sola sessió. La fase 5 s'estén tantes sessions com calgui — cada grup avança al seu propi ritme, sense imposar quin TODO ha d'estar fet a quina sessió.

---

## Objectius

1. Que cada alumne/parella entengui l'**arquitectura completa de l'ensemble**: 5 instruments autònoms, sense sincronització de tempo ni dependències de codi entre ells — "que ho facin d'oïda, són músics".
2. Que cada grup triï **un rol** i comprengui la seva arquitectura concreta abans de tocar codi (llegir `README.md` + el fitxer `.py` sencer, no només saltar al primer TODO).
3. Completar el **nucli mínim** del seu template (els TODO marcats), arribant a tenir un instrument que soni i respongui en temps real.
4. (Opcional, per qui vagi més ràpid) Explorar extensions pròpies del template o reptes de refinament transversals.

## Gestió de grups i tria de rol

- Grup de 5-8 alumnes → individual o en parelles segons la mida real del grup (amb 5 persones, 5 individuals; amb 8, fins a 3 parelles + la resta individual — a repartir segons el cas concret).
- **Cada rol el pot agafar només un alumne/parella** (no té sentit duplicar instruments dins del mateix ensemble).
- Si el grup és petit (5), tria directa d'un rol diferent cadascú. Si és més gran, cal acordar repartiment — es recomana deixar-los triar per interès/instrument propi (qui toca guitarra/veu pot preferir Efecte adaptatiu o Vocoder; qui ve de percussió, Drum-replacer; etc.) abans d'assignar res arbitràriament.

## Decisions de disseny importants (llegir abans d'ensenyar)

**Per què templates amb forats, i no rols oberts:** un rol completament obert ("fes un instrument generatiu") seria inviable de completar amb garanties en 2-3 sessions amb sonòlegs (no enginyers). Cada template dona un **nucli mínim ja arquitecturat** (les peces difícils de disseny ja resoltes) i deixa com a TODO només la part amb valor pedagògic real — coherent amb la resta del curs (mai s'ha deixat un repte sense estructura de suport).

**Per què 5 instruments autònoms, sense xarxa ni sincronització de tempo:** es va descartar explícitament qualsevol forma de "network music" (OSC entre instruments, tempo compartit per codi) perquè (a) afegiria una capa tècnica sencera no ensenyada al curs, i (b) no cal — són músics, poden escoltar-se i ajustar-se els uns als altres com en qualsevol ensemble real. Cada template és 100% independent: cap codi d'un rol llegeix ni envia res a un altre.

**Per què aquest repartiment de tecnologia per rol:**
- **Sinte i Vocoder → `signalflow`**. Són els dos casos on construir-ho tot a mà seria o bé pura repetició (el Sinte ja és Oscillator/Envelope fets a mà a S8-S9; signalflow n'és la "graduació" cap a una llibreria professional) o bé desproporcionat per al temps disponible (un vocoder STFT de fase real és nivell de tesi; el banc de filtres "vintage" amb `signalflow` el fa abastable sense perdre el concepte).
- **Drum-replacer, Looper/bassline, Efecte adaptatiu → NumPy pur** (cap signalflow). Es va considerar explícitament signalflow per als dos darrers (té `Clip`/`Fold`/`SVFilter`/`CombDelay`/`SamplePlayer` ja fets), però es va descartar: si tot l'ensemble passés a signalflow, el Sinte deixaria de ser l'única "graduació" especial i el contracte pedagògic del curs ("primer ho construïu a mà, després us gradueu cap a una llibreria") es trencaria. Construir l'efecte/playback a mà també és, en si mateix, el repte més valuós d'aquests dos rols concrets.

**Per què el Looper és un bassline melòdic i no un segon kit de percussió:** el disseny inicial (passos = kick/hihat amb `SamplePlayer`) es va descartar per xocar directament amb el Drum-replacer (dos rols fent percussió en un ensemble de 5 és redundant). Es va redefinir com a seqüenciador de notes (`Oscillator`+`Envelope`, alçada lliure per pas, no lligada a l'índex), que aporta una funció diferent (melòdica/harmònica) i evita introduir pitch-shifting de samples (no ensenyat al curs).

**Per què l'Efecte adaptatiu fa servir RMS + centroide + spectral flatness, i no ZCR ni onsets:** es va discutir partint del cas d'un instrument acoblat real (corda pinçada o vent — l'instrument concret dependrà de qui agafi el rol). ZCR es va descartar per ser un proxy massa indirecte del timbre per a modulació contínua (útil per a percussió tonal/sorollosa, que ja és terreny del Drum-replacer, però poc interessant aquí). Onsets es van descartar explícitament per no duplicar feina amb el Drum-replacer ("que ho explotin ells; aquí ens centrem en modulació tímbrica contínua"). Spectral flatness és l'únic descriptor que el curs no havia calculat mai abans — encaixa com el TODO tècnic real del rol (FFT, ja coneguda de S11, aplicada d'una manera diferent).

**Per què el mapeig descriptor→efecte de l'Efecte adaptatiu NO és un TODO tècnic:** és la decisió musical/creativa del rol. El template dona una connexió per defecte ja feta (per validar que tot funciona end-to-end) explícitament convidada a canviar-se — coherent amb el principi "templates amb forats, no rols oberts": el forat tècnic és com es calcula/escala cada descriptor, no quin va connectat a on.

**Per què el Vocoder és un banc de filtres "vintage" (16 bandes) i no STFT amb fase:** `signalflow` té nodes FFT/IFFT natius de fase real (`FFTContinuousPhaseVocoder`, etc.), però manipular magnitud i fase per separat és contingut de nivell molt superior al curs. Un vocoder clàssic de banc de filtres (com el Bode/Moog Vocoder o l'EMS Vocoder 5000) aconsegueix el mateix efecte perceptiu amb una arquitectura molt més directa: les mateixes 16 bandes es filtren tant al modulador (veu) com al carrier (oscil·lador MIDI), se'n segueix l'envolupant amb `Abs`+`Smooth`, i s'aplica banda a banda. Banc de filtres, envelope follower i aplicació al carrier es tracten com **un sol TODO** (una cadena de passos relacionats), no TODO separats — paral·lel al pipeline únic del Drum-replacer.

**Sobre signalflow + llibreries d'anàlisi (librosa) en cadena:** és viable de forma seqüencial per blocs (analitzar un bloc capturat amb `librosa.feature.X()`, fer servir el valor resultant per actualitzar un paràmetre d'un node signalflow amb `set_input()`) — exactament el que fa l'Efecte adaptatiu si s'imaginés amb signalflow. NO és viable intercalar-los dins del mateix graf en temps real continu (signalflow processa en el seu propi motor C++; caldria un node Python custom amb cost de latència/GIL, no usat enlloc del curs).

## Connexions amb sessions anteriors

Cada rol reaprofita explícitament contingut ja ensenyat — cap template introdueix res que el curs no hagi cobert abans:

- **Sinte:** Bloc 5 sencer (Oscillator/Envelope/process(), S8-S9), MIDI (Bloc 4), `signalflow` (introduït a S9 com a tast).
- **Drum-replacer:** Bloc 3 (captura/callback temps real), Bloc 5 (Oscillator/Envelope per generar el so de substitució), Bloc 6-7 (features + classificació supervisada), patró de màquina d'estats ja vist al llarg del curs.
- **Looper/bassline:** S8 (`SamplePlayer`, ara estès amb un patró `process(n)`), Bloc 5 (Oscillator/Envelope per al bassline sintetitzat), TP1 (mòdul `% n` per al cicle de passos).
- **Efecte adaptatiu:** S5 (distorsió per clipping, eco amb buffer circular), S9 (LFO, esmentat explícitament per a vibrato i/o tremolo), S11 (FFT manual, RMS i centroide ja coneguts via librosa).
- **Vocoder:** Bloc 4 (MIDI), Bloc 5 (envolupants/ADSR), S9 (`signalflow`, LFO), S11 (concepte de banda de freqüència i envolupant espectral, ara aplicat en temps real banda a banda).

## Materials necessaris

- 5 templates ja construïts i validats a `templates/<rol>/` (`<rol>.py` + `README.md` cadascun): `sinte`, `drum_replacer`, `looper_bassline`, `efecte_adaptatiu`, `vocoder`.
- Per Sinte i Vocoder: `pip3 install signalflow mido python-rtmidi`.
- Per Drum-replacer, Looper, Efecte adaptatiu: `numpy`, `sounddevice`, `librosa` (només Efecte adaptatiu), `scipy`/`sklearn` (només Drum-replacer).
- Maquinari: cada grup necessita el seu propi controlador/instrument segons el rol (controlador MIDI per Sinte/Looper/Vocoder; micro per Drum-replacer/Vocoder; instrument acoblat via interface d'àudio per Efecte adaptatiu).

## Fitxers d'aquesta carpeta

- `guia.md` — aquesta guia
- `templates/sinte/` — Sinte (signalflow + MIDI)
- `templates/drum_replacer/` — Drum-replacer (classificació supervisada en dues fases)
- `templates/looper_bassline/` — Looper/bassline (step-sequencer melòdic, NumPy)
- `templates/efecte_adaptatiu/` — Efecte adaptatiu (3 descriptors → 3 efectes simultanis, NumPy)
- `templates/vocoder/` — Vocoder (banc de filtres de 16 bandes, signalflow)
- `recursos/warmup_quiz.md` — preguntes per a Google Forms (repàs ampli de tot el curs)
- `recursos/slides_outline.md` — diapositives (presentació de l'ensemble + els 5 rols)
- `recursos/reptes_opcionals.md` — reptes de refinament transversals, per a qui acabi abans

## Pendent / a revisar

- [ ] Muntar Google Form a partir de `warmup_quiz.md`
- [ ] Muntar Google Slides a partir de `slides_outline.md`
- [ ] Decidir el mecanisme concret de tria de rol amb el grup real (depèn de la mida final i dels instruments propis de cadascú)
- [ ] Provar cada template amb hardware real (controlador MIDI, interface d'àudio) abans de la sessió — la validació feta fins ara és lògica/funcional amb `backend_name="null"` (signalflow) o harnesses amb senyals sintètics (NumPy), no amb maquinari real
- [ ] Confirmar disponibilitat de prou controladors MIDI/interfaces per a tots els grups simultàniament
