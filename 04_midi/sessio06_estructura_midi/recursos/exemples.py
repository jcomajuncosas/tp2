"""
Exemples — Bloc 4a, Sessió 6 (Thonny) — MIDI EN TEMPS REAL
==========================================================

Els FITXERS .mid es treballen a Colab (patches i assignment).
Aquí només hi ha el que necessita un port MIDI real: teclat, DAW, sintetitzador.

PREPARACIÓ (un sol cop):
  Thonny → Tools → Manage packages → instal·la `mido` i `python-rtmidi`
  (sense python-rtmidi, mido no veu cap port: ModuleNotFoundError: rtmidi)

ON SONA el MIDI de sortida?
  Windows: hi ha el port "Microsoft GS Wavetable Synth" — sona directament.
  macOS:   no hi ha cap sintetitzador exposat com a port. Activa el IAC Driver
           (Audio MIDI Setup → Finestra → MIDI Studio → IAC Driver → "Dispositiu en línia")
           i obre GarageBand o el vostre DAW escoltant el port IAC.

COM FUNCIONA: F5 només defineix les funcions. Després crida-les des del Shell:
  >>> llista_ports()
  >>> escolta_teclat()                    # bloquejant (Ctrl+C per aturar)
  >>> escolta_teclat_sense_bloquejar()    # com el block=False de TP1
  >>> escolta_teclat_callback()           # callback MIDI (compara amb la S04!)
  >>> toca_escala()
  >>> reprodueix_fitxer('example_scale.mid')
"""

import time
import threading
import mido

NOMS = ['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa', 'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']


def nom_nota(n):
    return f"{NOMS[n % 12]}{n // 12 - 1}"


def descriu(msg):
    """Text curt per a un missatge (el fem servir a totes les demos)."""
    if msg.type == 'note_on' and msg.velocity > 0:
        return f"▶ {nom_nota(msg.note):>5}  vel {msg.velocity:>3}"
    if msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        return f"■ {nom_nota(msg.note):>5}"
    if msg.type == 'control_change':
        return f"CC {msg.control:>3} = {msg.value}"
    return str(msg)


# ---------------------------------------------------------------
# 0. Quins ports tinc?
# ---------------------------------------------------------------
def llista_ports():
    print("Entrades:", mido.get_input_names())
    print("Sortides:", mido.get_output_names())


def tria_sortida(nom=None):
    """Retorna el nom del port de sortida a fer servir (el primer si no en dius cap)."""
    sortides = mido.get_output_names()
    if not sortides:
        raise RuntimeError("Cap port de sortida. macOS: activa l'IAC Driver. Windows: hauria d'existir el GS Wavetable Synth.")
    return nom or sortides[0]


# ---------------------------------------------------------------
# 1. Entrada BLOQUEJANT: el programa es queda esperant cada missatge
# ---------------------------------------------------------------
def escolta_teclat(nom_port=None):
    print("Toca el teclat. Ctrl+C per aturar.")
    try:
        with mido.open_input(nom_port) as port:
            print(f"Port obert: {port.name}")
            for msg in port:                      # aquí el programa s'atura fins que arriba un missatge
                print(descriu(msg))
    except KeyboardInterrupt:
        print("Aturat")


# ---------------------------------------------------------------
# 2. Entrada SENSE BLOQUEJAR: el programa fa altres coses i mira de tant en tant
#    (la mateixa idea que block=False a TP1)
# ---------------------------------------------------------------
def escolta_teclat_sense_bloquejar(nom_port=None, segons=10):
    print(f"Durant {segons} s el programa compta voltes i, de passada, llegeix el teclat.")
    voltes = 0
    with mido.open_input(nom_port) as port:
        fi = time.time() + segons
        while time.time() < fi:
            for msg in port.iter_pending():       # retorna el que hagi arribat i NO s'espera
                print(f"volta {voltes:>4}: {descriu(msg)}")
            voltes += 1
            time.sleep(0.01)                      # "la resta del programa"
    print(f"Fet: {voltes} voltes")


# ---------------------------------------------------------------
# 3. CALLBACK MIDI: mido crida la teva funció cada vegada que arriba un missatge
#
#    Compara-ho amb el callback d'àudio de la S04:
#      àudio → el crida el RELLOTGE de la targeta, regularment, i ha d'omplir
#              un buffer abans d'un deadline (si no: dropout)
#      MIDI  → el crida cada ESDEVENIMENT, quan arriba (irregular), i no ha
#              d'omplir res: només reaccionar
#    Corre en UN ALTRE FIL: el programa principal continua lliure.
# ---------------------------------------------------------------
estat = {'nota': None, 'velocity': 0, 'missatges': 0}   # estat compartit


def callback_midi(msg):
    # Feina curta: anotar i prou (com a la S04, res de lent aquí dins)
    estat['missatges'] += 1
    if msg.type == 'note_on' and msg.velocity > 0:
        estat['nota'], estat['velocity'] = msg.note, msg.velocity
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note == estat['nota']:
            estat['nota'], estat['velocity'] = None, 0
    print(f"  [fil {threading.current_thread().name}] {descriu(msg)}")


def escolta_teclat_callback(nom_port=None, segons=10):
    port = mido.open_input(nom_port, callback=callback_midi)
    print(f"Port obert: {port.name}. El fil principal ({threading.current_thread().name}) llegeix l'estat cada segon.")
    try:
        for s in range(segons):
            time.sleep(1)
            nota = nom_nota(estat['nota']) if estat['nota'] is not None else '—'
            print(f"[principal] t={s + 1:>2}s  nota sonant: {nota:>5}  missatges rebuts: {estat['missatges']}")
    finally:
        port.close()
    # Aquest és l'esquema d'un sintetitzador: el callback MIDI escriu `estat`,
    # i el callback d'àudio el llegeix per decidir quina freqüència generar.


# ---------------------------------------------------------------
# 4. Sortida: enviar notes a un port (el temps el portem nosaltres amb sleep)
# ---------------------------------------------------------------
def toca_escala(nom_port=None, durada=0.25):
    with mido.open_output(tria_sortida(nom_port)) as port:
        print(f"Enviant a: {port.name}")
        for note in [60, 62, 64, 65, 67, 69, 71, 72]:
            port.send(mido.Message('note_on', note=note, velocity=80))
            time.sleep(durada)
            port.send(mido.Message('note_off', note=note, velocity=0))


# ---------------------------------------------------------------
# 5. Reproduir un fitxer .mid per un port
#    mid.play() NO fa so: retorna els missatges esperant el temps que toca
#    (el delta en segons de la cel·la 6 dels patches). Nosaltres els enviem.
# ---------------------------------------------------------------
def reprodueix_fitxer(fitxer='example_scale.mid', nom_port=None):
    mid = mido.MidiFile(fitxer)
    with mido.open_output(tria_sortida(nom_port)) as port:
        print(f"Reproduint {fitxer} ({mid.length:.1f} s) a: {port.name}")
        try:
            for msg in mid.play():               # play() ja s'adorm entre missatges
                port.send(msg)
        except KeyboardInterrupt:
            port.reset()                         # silencia les notes que han quedat obertes
            print("Aturat")
