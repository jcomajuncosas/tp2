# _solucions — Solucions de referència (ÚS EXCLUSIU DEL DOCENT)

Aquesta carpeta conté les solucions de referència per a tots els reptes del curs TP2.

**No distribuir als alumnes.**

Cada fitxer `solucio.py` (o `solucio.ipynb`) resol tots els `# TODO` de l'assignment
o notebook corresponent, inclou els mateixos asserts automàtics que el fitxer original,
i s'executa de forma autònoma (sense necessitat de micròfon, altaveu ni Colab).

## Estat de generació

| Sessió | Fitxer original | Solució | TODOs | Validat |
|--------|----------------|---------|-------|---------|
| S01 — Reconnexió | `notebook.ipynb` | `S01_reconnexio/solucio.py` | 1–6 | ✅ |
| S02 — WAV i NumPy | `notebook.ipynb` | `S02_numpy_audio/solucio.py` | 1–4c | ✅ |
| S03 — Captura i efectes | `notebook.ipynb` | `S03_capture_playback/solucio.py` | 1–5 | ✅ |
| S04 — Buffers i latència | `assignment.py` | `S04_buffers_latencia/solucio.py` | 1–5 | ✅ |
| S05 — Efecte temps real | `assignment.py` | `S05_efecte_temps_real/solucio.py` | 1–9 | ✅ |
| S06 — Estructura MIDI | `notebook.ipynb` | — | — | ⏳ |
| S07 — Seqüenciador | `notebook.ipynb` | — | — | ⏳ |
| S08 — Oscil·ladors/Classes | `notebook.ipynb` | — | — | ⏳ |
| S09 — FM Synth | `assignment.py` + `challenges.md` | — | — | ⏳ |
| S10 — Consolidació | `assignment.py` + `challenges.md` | — | — | ⏳ |
| S11 — FFT i features | `notebook.ipynb` + `challenges.md` | — | — | ⏳ |
| S12 — Classificador | `notebook.ipynb` + `challenges.md` | — | — | ⏳ |
| Projecte — Sinte | `sinte.py` | — | — | ⏳ |
| Projecte — Drum replacer | `drum_replacer.py` | — | — | ⏳ |
| Projecte — Looper/Bassline | `looper_bassline.py` | — | — | ⏳ |
| Projecte — Efecte adaptatiu | `efecte_adaptatiu.py` | — | — | ⏳ |
| Projecte — Vocoder | `vocoder.py` | — | — | ⏳ |

## Notes

- Les reflexions obertes (S04, S05) inclouen respostes de referència i notes sobre
  variabilitat acceptable en la resposta de l'alumne.
- Els challenges purament exploratòrics/creatius (ex. "crea un so interessant")
  no generen solució única; els fitxers corresponents inclouen una nota docent.
- Les solucions de S04 i S05 no executen `sd.Stream` (requereix hardware);
  la lògica dels callbacks es valida amb arrays sintètics.
