# Programació per a Sonòlegs (Python) — TP2 2026/27

Material docent organitzat per blocs temàtics i sessions (15 sessions de 2h).

## Estructura de carpetes

```
TP2_2627/
├── 01_reconnexio/
│   └── sessio01_reconnexio/
├── 02_numpy_audio/
│   └── sessio02_wav_io/
├── 03_temps_real/
│   ├── sessio03_capture_playback/
│   ├── sessio04_buffers_latencia/
│   └── sessio05_efecte_temps_real/
├── 04_midi/
│   ├── sessio06_estructura_midi/
│   └── sessio07_sequenciador/
├── 05_sintesi/
│   ├── sessio08_oscil_ladors_classes/
│   ├── sessio09_fm_synth/
│   └── sessio10_consolidacio/
├── 06_analisi_ml/
│   ├── sessio11_fft_features/
│   └── sessio12_classificador/
└── 07_projecte_final/
    ├── sessio12_arquitectura_comuna/   ← templates + guia multi-sessió
    └── sessio13_implementacio_rols/    ← redirecció a sessio12
```

## Sessions

| # | Sessió | Bloc | Carpeta |
|---|---|---|---|
| 1 | Setup/reconnexió + Bloc 1 (so com a array, NumPy) | 01_reconnexio | sessio01_reconnexio |
| 2 | Bloc 2 — WAV I/O, mixing, loop, librosa bàsic | 02_numpy_audio | sessio02_wav_io |
| 3 | Bloc 3a — Captura/playback blocking, catàleg 8 efectes offline | 03_temps_real | sessio03_capture_playback |
| 4 | Bloc 3b — Model callback, pass-through, gain, blocksize/latència | 03_temps_real | sessio04_buffers_latencia |
| 5 | Bloc 3c — Efectes en temps real (eco+buffer circular, distorsió) | 03_temps_real | sessio05_efecte_temps_real |
| 6 | Bloc 4a — Estructura MIDI, mido, notes/velocity/canals | 04_midi | sessio06_estructura_midi |
| 7 | Bloc 4b — pretty_midi, arpegiador, timing, MidiSynth | 04_midi | sessio07_sequenciador |
| 8 | Bloc 5a — Oscillator, Envelope (ADSR), SamplePlayer, MIDI→freq | 05_sintesi | sessio08_oscil_ladors_classes |
| 9 | Bloc 5b — Arquitectura UGen/process(), control rate, FM, signalflow | 05_sintesi | sessio09_fm_synth |
| 10 | Bloc 5c — Consolidació: kit de percussió sintètica (Kick+Noise+MIDI) | 05_sintesi | sessio10_consolidacio |
| 11 | Bloc 6 — FFT pràctic, extracció de features (centroid, MFCC, ZCR) | 06_analisi_ml | sessio11_fft_features |
| 12 | Bloc 7 — Classificador KNN/decision tree/SVM, fronteres de decisió | 06_analisi_ml | sessio12_classificador |
| 13-14 | Projecte final — presentació de l'ensemble, implementació dels rols | 07_projecte_final | sessio12_arquitectura_comuna |

Les sessions 15 (assaig) i el concert final es realitzen fora del calendari lectiu i no generen material de programació.

## Estructura de cada sessió

| Fitxer | Format | Ús |
|---|---|---|
| `guia.md` | Markdown | Pla de la sessió: objectius, horari, decisions pedagògiques, connexions amb TP1 |
| `exemples.py` | Script Python | Demo per a Thonny (entorn local, temps real) |
| `notebook.ipynb` | Jupyter/Colab | Mini-repte amb autotest. Sessions S4-S5 usen `assignment.py` per a Thonny |
| `build.sh` | Script | `./build.sh` genera `docx/` (ignorat per git) a partir dels `.md` |
| `recursos/` | Variat | `cheat_sheet.md`, `warmup_quiz.md`, `slides_outline.md`, `patches_blocX.ipynb`, `audio/` |

## Accés als notebooks des de Google Colab

```
https://colab.research.google.com/github/jcomajuncosas/tp2/blob/main/RUTA/AL/NOTEBOOK.ipynb
```

Exemple:
```
https://colab.research.google.com/github/jcomajuncosas/tp2/blob/main/06_analisi_ml/sessio11_fft_features/notebook.ipynb
```

## Projecte final

**5 instruments autònoms** (Sinte, Drum-replacer, Looper/bassline, Efecte adaptatiu, Vocoder) en format template amb forats (TODO + nucli mínim + extensions opcionals). Cap instrument depèn d'un altre per codi — l'ensemble es coordina musicalment, com qualsevol ensemble real.

Templates i guia completa a `07_projecte_final/sessio12_arquitectura_comuna/`. Repartiment de tecnologia per rol:

| Rol | Tecnologia | "Punt fort" pedagògic |
|---|---|---|
| Sinte | `signalflow` + MIDI | Graduació cap a una llibreria de síntesi professional |
| Drum-replacer | NumPy + librosa + sklearn | Pipeline complet de classificació supervisada en temps real |
| Looper/bassline | NumPy + sounddevice | Seqüenciació loopejada amb timing manual (tap-to-tempo) |
| Efecte adaptatiu | NumPy + librosa | 3 descriptors tímbrics continus → 3 efectes simultanis a mà |
| Vocoder | `signalflow` | Banc de filtres "vintage" de 16 bandes (Bode/Moog, EMS Vocoder 5000) |

## Instal·lació

Sessions S1-S12 (Colab): sense instal·lació local.

Sessions S3-S12 (Thonny): `pip3 install numpy sounddevice scipy librosa scikit-learn mido python-rtmidi soundfile`.

Projecte final (Thonny):
- Rols NumPy: com a dalt.
- Rols signalflow (Sinte, Vocoder): `pip3 install signalflow mido python-rtmidi`.
- **Nota Mac Apple Silicon:** crear un venv amb Python 3.13 explícit i `--copies` (no symlinks). Veure instruccions detallades a `05_sintesi/sessio09_fm_synth/recursos/challenges.md` (Challenge 2).

## Pendents transversals (post-curs)

1. **Solucions de referència:** generar fitxers `solucio.py`/`solucio.ipynb` per a tots els `assignment.py`/`notebook.ipynb` amb TODO (S1-S12 + 5 templates del projecte final) — per ús exclusiu del docent, no distribuïts als alumnes.

2. **Minicurset de mecanografia de codi** (opcional, fora de l'abast de TP2): recurs autoadministrat per practicar fluïdesa motriu amb patrons sintàctics del curs (`for i in range(n)`, `def process(self, n):`, l'esquelet ADSR, el bucle de blocs...). Disseny acordat (còpia conscient → reproducció de memòria), format final pendent de decidir.
