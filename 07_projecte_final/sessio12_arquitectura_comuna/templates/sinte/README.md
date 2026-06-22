# Sinte

Sintetitzador polifònic controlat per MIDI, construït amb `signalflow` — la
llibreria professional a la qual us "gradueu" després d'haver construït
`Oscillator`/`Envelope`/`process()` a mà a les Sessions 8-9.

## Instal·lació

```bash
pip3 install signalflow mido python-rtmidi
```

Si tens problemes (Mac amb Conda/Miniforge, Python massa recent...), consulta
la guia de troubleshooting validada a
`05_sintesi/sessio09_fm_synth/recursos/challenges.md` (Challenge 2).

## Com s'executa

```bash
python3 sinte.py -l                    # llista dispositius MIDI disponibles
python3 sinte.py -i "Nom del dispositiu"
```

Toca el teu controlador MIDI — cada nota crea una veu nova (polifonia real,
fins a 128 notes simultànies). Ctrl+C per aturar.

**Instrument autònom:** no envia ni rep res d'altres instruments de l'ensemble.

## Què has de completar (NUCLI MÍNIM, TODO 1-3)

A `NotePatch.__init__()`:
1. **TODO 1** — tria l'oscil·lador portador (`SineOscillator`/`SawOscillator`/`SquareOscillator`).
2. **TODO 2** — defineix l'envolvent ADSR (`ADSREnvelope(attack, decay, sustain, release, gate=gate)`). Recordatori de S8: sustain és un NIVELL (0-1), no un temps.
3. **TODO 3** — combina senyal × envolvent × amplitud i posa'l a `set_output()`.

## Extensions opcionals (si vas sobrat de temps)

4. **Vibrato** (Secció 3 de S9): `SineLFO` modulant lleugerament la freqüència del portador.
5. **FM senzilla** (Secció 4 de S9): un segon oscil·lador com a modulador, sumat a la freqüència del portador amb un índex `I`.
6. **Filtre amb cutoff modulat per una envolvent pròpia**: `SVFilter` amb el cutoff controlat per un `ADSREnvelope` independent (igual que fa l'exemple oficial de `signalflow`).

Les tres extensions tenen el codi suggerit comentat directament al fitxer, a sota dels TODO del nucli.

## Connexió amb el curs

Aquest template és deliberadament el rol que reutilitza més directament el
contingut més dens del curs (Bloc 5, Sessions 8-9): la distinció
oscil·lador/envolvent, el patró "un node alimenta el paràmetre d'un altre"
(vibrato, FM), i la integració amb MIDI en temps real — ara amb una API
professional en lloc de les classes que vau construir a mà.

## Per què `signalflow` i no les vostres pròpies classes

A `Oscillator`/`Envelope`, `process()` (Bloc 5) heu après l'arquitectura per
dins. `signalflow` resol exactament el mateix amb un motor optimitzat en
C++, mostra a mostra real (sense els compromisos de blocs que vau haver
d'acceptar a S9-S10). Si algú es pregunta "per què no hem fet servir
`signalflow` des del principi?": perquè ara sabeu llegir `ADSREnvelope(...)`
i entendre exactament què fa per dins, no és una caixa negra.
