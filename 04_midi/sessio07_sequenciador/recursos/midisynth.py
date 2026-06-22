"""
midisynth.py — Sintetitzador MIDI senzill basat en FluidSynth

Aquesta classe es proporciona JA FETA — no cal implementar-la, només usar-la.
Embolcalla fluidsynth perquè puguis enviar notes MIDI i sentir-les
directament, sense necessitar IAC Driver, LoopMIDI, ni cap DAW extern.

DUES VARIANTS incloses en aquest fitxer:
  - MidiSynth        → temps real, per a Thonny (so directe per l'altaveu)
  - MidiSynthRender   → renderitzat a array, per a Colab (sense hardware d'àudio)

INSTAL·LACIÓ (cal fer-ho UN COP per ordinador):

  1) FluidSynth (el programa, a nivell de sistema):
     macOS:   brew install fluid-synth
     Linux:   sudo apt install fluidsynth fluid-soundfont-gm
     Windows: descarrega l'instal·lador de
              https://github.com/FluidSynth/fluidsynth/releases
              i afegeix la carpeta bin/ al PATH

  2) La llibreria Python:
     pip install pyfluidsynth

  3) Un soundfont (.sf2) — el fitxer amb els "timbres" dels instruments:
     - A Linux, 'fluid-soundfont-gm' ja n'instal·la un automàticament.
     - A macOS i Windows, Homebrew NO instal·la cap soundfont — cal
       descarregar-ne un a part. Recomanat (lliure, ~30MB):
       https://schristiancollins.com/generaluser.php
       Descarrega'l i indica la ruta amb soundfont_path= en crear MidiSynth,
       o desa'l a una de les rutes de SOUNDFONT_PATHS més avall.
"""

import numpy as np

try:
    import fluidsynth
except ImportError:
    fluidsynth = None
    print("AVÍS: pyfluidsynth no està instal·lat. Executa: pip install pyfluidsynth")


# Rutes habituals de soundfonts segons sistema operatiu — s'ajusta automàticament.
# Si el teu soundfont és en un altre lloc, passa soundfont_path= explícitament.
SOUNDFONT_PATHS = [
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",                      # Linux (apt fluid-soundfont-gm)
    "/usr/share/sounds/sf2/default-GM.sf2",                       # Linux (alt)
    "./GeneralUser.sf2",                                          # carpeta de treball (recomanat macOS/Windows)
    "/opt/homebrew/share/soundfonts/default.sf2",                 # macOS (si l'has copiat aquí)
    "/usr/local/share/soundfonts/default.sf2",                    # macOS Intel (si l'has copiat aquí)
]

# Driver d'àudio per sistema operatiu (per a MidiSynth en temps real, Thonny)
import platform

def _default_driver():
    sistema = platform.system()
    if sistema == "Darwin":
        return "coreaudio"
    elif sistema == "Windows":
        return "dsound"
    else:
        return "alsa"


def _troba_soundfont(soundfont_path=None):
    if soundfont_path:
        return soundfont_path
    for path in SOUNDFONT_PATHS:
        import os
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        "No s'ha trobat cap soundfont. Indica la ruta manualment:\n"
        "  synth = MidiSynth(soundfont_path='/ruta/al/teu/soundfont.sf2')\n"
        "Descarrega'n un de lliure (GeneralUser GS, ~30MB):\n"
        "  https://schristiancollins.com/generaluser.php"
    )


class MidiSynth:
    """
    Sintetitzador MIDI en TEMPS REAL — per a Thonny.
    Envia notes i les sents immediatament per l'altaveu del sistema.

    Ús:
        synth = MidiSynth()
        synth.note_on(60, velocity=80)
        time.sleep(0.5)
        synth.note_off(60)
        synth.close()
    """

    def __init__(self, soundfont_path=None, driver=None, gain=2.0):
        if fluidsynth is None:
            raise RuntimeError("pyfluidsynth no està instal·lat")

        self.fs = fluidsynth.Synth(gain=gain)
        driver = driver or _default_driver()
        self.fs.start(driver=driver)

        sf_path = _troba_soundfont(soundfont_path)
        self.sfid = self.fs.sfload(sf_path)
        self.fs.program_select(0, self.sfid, 0, 0)  # canal 0, preset 0 (piano)

    def note_on(self, note, velocity=80, channel=0):
        """Comença una nota. note: 0-127, velocity: 0-127."""
        self.fs.noteon(channel, note, velocity)

    def note_off(self, note, channel=0):
        """Atura una nota."""
        self.fs.noteoff(channel, note)

    def program(self, preset, channel=0, bank=0):
        """Canvia l'instrument (General MIDI: 0=piano, 24=guitarra, 40=violí...)."""
        self.fs.program_select(channel, self.sfid, bank, preset)

    def control_change(self, control, value, channel=0):
        """Envia un missatge de control (ex: sustain pedal control=64)."""
        self.fs.cc(channel, control, value)

    def close(self):
        """Tanca el sintetitzador. Crida-ho sempre al final."""
        self.fs.delete()


class MidiSynthRender:
    """
    Sintetitzador MIDI per RENDERITZAR a array — per a Colab.
    No reprodueix en temps real (Colab no té accés al hardware d'àudio);
    en lloc d'això, genera un array NumPy que pots reproduir amb
    IPython.display.Audio() o desar amb soundfile.

    Ús:
        synth = MidiSynthRender()
        synth.note_on(60, velocity=80)
        audio = synth.render(duration=0.5)  # array de 0.5s amb la nota sonant
        synth.note_off(60)
        audio2 = synth.render(duration=0.2)  # 0.2s més (release/silenci)
        tot = np.concatenate([audio, audio2])
        Audio(tot, rate=44100)
    """

    def __init__(self, soundfont_path=None, sample_rate=44100, gain=2.0):
        if fluidsynth is None:
            raise RuntimeError("pyfluidsynth no està instal·lat")

        self.sample_rate = sample_rate
        self.fs = fluidsynth.Synth(samplerate=float(sample_rate), gain=gain)
        sf_path = _troba_soundfont(soundfont_path)
        self.sfid = self.fs.sfload(sf_path)
        self.fs.program_select(0, self.sfid, 0, 0)

    def note_on(self, note, velocity=80, channel=0):
        self.fs.noteon(channel, note, velocity)

    def note_off(self, note, channel=0):
        self.fs.noteoff(channel, note)

    def program(self, preset, channel=0, bank=0):
        self.fs.program_select(channel, self.sfid, bank, preset)

    def render(self, duration):
        """
        Avança el render 'duration' segons i retorna l'array d'àudio (mono, float32, -1..1).
        Crida note_on/note_off ABANS de render() per controlar quan sonen les notes.
        """
        n_samples = int(duration * self.sample_rate)
        raw = self.fs.get_samples(n_samples)  # int16, estèreo intercalat
        stereo = raw.reshape(-1, 2).astype(np.float32) / 32768.0
        mono = stereo.mean(axis=1)
        return mono

    def close(self):
        self.fs.delete()


def llista_instruments_gm():
    """Retorna un diccionari amb alguns instruments General MIDI habituals."""
    return {
        0: "Acoustic Grand Piano",
        4: "Electric Piano",
        24: "Nylon Guitar",
        32: "Acoustic Bass",
        40: "Violin",
        56: "Trumpet",
        64: "Soprano Sax",
        73: "Flute",
        80: "Synth Lead (square)",
        88: "Synth Pad (warm)",
        118: "Synth Drum",
        # Percussió: canal 9 (índex 9), no requereix program_select
    }
