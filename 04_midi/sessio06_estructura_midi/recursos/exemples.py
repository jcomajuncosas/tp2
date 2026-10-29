"""
Exemples — Bloc 4a, Sessió 6 (Thonny) — MIDI EN TEMPS REAL
==========================================================

Els FITXERS .mid es treballen a Colab (patches i assignment).
Aquí només hi ha el que necessita un port MIDI real: teclat, DAW, sintetitzador.

Dues llibreries, cadascuna per a una feina:
  rtmidi2 → obre els PORTS i rep / envia els bytes
  mido    → tradueix aquests bytes a missatges que entenem (note_on, note=60...)

PREPARACIÓ (un sol cop):
  Thonny → Tools → Manage packages → instal·la `mido` i `rtmidi2`

SENSE TECLAT? macOS té un "cable MIDI virtual": el IAC Driver.
  Audio MIDI Setup → Finestra → MIDI Studio → IAC Driver → "Dispositiu en línia"
  El que envies per la sortida IAC torna a entrar per l'entrada IAC.
  (Windows: instal·la loopMIDI i crea-hi un port.)

ON SONA el MIDI de sortida?
  Windows: hi ha el port "Microsoft GS Wavetable Synth" — sona directament.
  macOS:   no hi ha cap sintetitzador exposat com a port: envia'l al IAC i
           obre GarageBand o el vostre DAW escoltant-lo.

Els ports s'obren pel NÚMERO de la llista, no pel nom: el nom canvia segons
l'idioma del sistema ("IAC Driver Bus 1", "Controlador IAC Bus 1"...).

COM FUNCIONA: F5 només defineix les funcions. Després crida-les des del Shell:
  >>> llista_ports()
  >>> prova_iac()                          # comprova que tot funciona, sense teclat
  >>> escolta_preguntant()                 # el programa pregunta (com block=False a TP1)
  >>> escolta_callback()                   # el callback MIDI (compara amb la S04!)
  >>> toca_escala()
  >>> reprodueix_fitxer('midi/example_scale.mid')
  >>> silencia()                           # si queden notes penjades
"""

import time
import mido
import rtmidi2

NOMS = ['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa', 'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']


def nom_nota(n):
    return f"{NOMS[n % 12]}{n // 12 - 1}"


def descriu(msg):
    """Text curt per a un missatge mido (el fem servir a totes les demos)."""
    if msg.type == 'note_on' and msg.velocity > 0:
        return f"▶ {nom_nota(msg.note):>5}  vel {msg.velocity:>3}"
    if msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        return f"■ {nom_nota(msg.note):>5}"
    if msg.type == 'control_change':
        return f"CC {msg.control:>3} = {msg.value}"
    return str(msg)


# ---------------------------------------------------------------
# 0. Ports
# ---------------------------------------------------------------
def llista_ports():
    print("Entrades:")
    entrades = rtmidi2.MidiIn().ports
    for i in range(len(entrades)):
        print(f"  {i}: {entrades[i]}")
    print("Sortides:")
    sortides = rtmidi2.MidiOut().ports
    for i in range(len(sortides)):
        print(f"  {i}: {sortides[i]}")


def obre_entrada(numero=0):
    entrada = rtmidi2.MidiIn()
    if numero >= len(entrada.ports):
        print(f"No hi ha l'entrada {numero}. Crida llista_ports() per veure quines hi ha.")
        return None
    entrada.open_port(numero)
    print(f"Entrada oberta: {entrada.ports[numero]}")
    return entrada


def obre_sortida(numero=0):
    sortida = rtmidi2.MidiOut()
    if numero >= len(sortida.ports):
        print(f"No hi ha la sortida {numero}. Crida llista_ports() per veure quines hi ha.")
        return None
    sortida.open_port(numero)
    print(f"Sortida oberta: {sortida.ports[numero]}")
    return sortida


def envia(sortida, msg):
    """Envia un missatge mido: el convertim a bytes, que és el que viatja pel cable."""
    sortida.send_message(msg.bytes())


# ---------------------------------------------------------------
# 1. PREGUNTANT: el programa mira de tant en tant si ha arribat alguna cosa
#    (la mateixa idea que block=False a TP1). Qui manda és el programa.
# ---------------------------------------------------------------
def escolta_preguntant(numero=0, segons=10):
    entrada = obre_entrada(numero)
    if entrada is None:
        return
    print(f"Durant {segons} s el programa compta voltes i, a cada volta, pregunta si hi ha missatges.")
    voltes = 0
    fi = time.time() + segons
    while time.time() < fi:
        dades = entrada.get_message()           # retorna els bytes, o None si no hi ha res
        while dades is not None:
            msg = mido.Message.from_bytes(dades)
            print(f"volta {voltes:>4}: {descriu(msg)}   (bytes: {dades})")
            dades = entrada.get_message()
        voltes = voltes + 1
        time.sleep(0.01)                        # "la resta del programa"
    entrada.close_port()
    print(f"Fet: {voltes} voltes")


# ---------------------------------------------------------------
# 2. CALLBACK MIDI: el sistema crida la teva funció cada vegada que arriba un missatge
#
#    Compara-ho amb el callback d'àudio de la S04:
#      àudio → el crida el RELLOTGE de la targeta, regularment, i ha d'omplir
#              un buffer abans d'un deadline (si no: dropout)
#      MIDI  → el crida cada ESDEVENIMENT, quan arriba (irregular), i no ha
#              d'omplir res: només reaccionar
#    Corre en UN ALTRE FIL: el programa principal continua lliure.
# ---------------------------------------------------------------
class Estat:
    """L'estat compartit entre el callback i el programa principal."""
    def __init__(self):
        self.nota = None
        self.velocity = 0
        self.missatges = 0


estat = Estat()


def callback_midi(dades, timestamp):
    # Feina curta: traduir, anotar i prou (com a la S04, res de lent aquí dins)
    msg = mido.Message.from_bytes(dades)
    estat.missatges = estat.missatges + 1
    if msg.type == 'note_on' and msg.velocity > 0:
        estat.nota = msg.note
        estat.velocity = msg.velocity
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note == estat.nota:
            estat.nota = None
            estat.velocity = 0
    print(f"  [callback] {descriu(msg)}")


def escolta_callback(numero=0, segons=10):
    entrada = obre_entrada(numero)
    if entrada is None:
        return
    estat.missatges = 0
    entrada.callback = callback_midi            # a partir d'ara, el sistema crida callback_midi
    print("El programa principal només dorm i mira l'estat cada segon.")
    for s in range(segons):
        time.sleep(1)                           # el principal "fa la seva"; el callback treballa sol
        nota = '—'
        if estat.nota is not None:
            nota = nom_nota(estat.nota)
        print(f"[principal] t={s + 1:>2}s  nota sonant: {nota:>5}  missatges rebuts: {estat.missatges}")
    entrada.callback = None
    entrada.close_port()
    # Aquest és l'esquema d'un sintetitzador: el callback MIDI escriu `estat`,
    # i el callback d'àudio el llegeix per decidir quina freqüència generar.


# ---------------------------------------------------------------
# 3. Prova sense teclat: ens enviem notes a nosaltres mateixos pel IAC
#    (cal que l'entrada i la sortida siguin el mateix port IAC)
# ---------------------------------------------------------------
def prova_iac(entrada_num=0, sortida_num=0):
    entrada = obre_entrada(entrada_num)
    sortida = obre_sortida(sortida_num)
    if entrada is None or sortida is None:
        return
    entrada.callback = callback_midi
    for n in [60, 64, 67]:
        envia(sortida, mido.Message('note_on', note=n, velocity=90))
        time.sleep(0.3)                         # mentre el principal dorm, el callback imprimeix
        envia(sortida, mido.Message('note_off', note=n, velocity=0))
    time.sleep(0.3)
    entrada.callback = None
    entrada.close_port()
    sortida.close_port()
    print("fet")


# ---------------------------------------------------------------
# 4. Sortida: enviar notes a un port (el temps el portem nosaltres amb sleep)
# ---------------------------------------------------------------
def toca_escala(numero=0, durada=0.25):
    sortida = obre_sortida(numero)
    if sortida is None:
        return
    for note in [60, 62, 64, 65, 67, 69, 71, 72]:
        envia(sortida, mido.Message('note_on', note=note, velocity=80))
        time.sleep(durada)
        envia(sortida, mido.Message('note_off', note=note, velocity=0))
    sortida.close_port()


# ---------------------------------------------------------------
# 5. Reproduir un fitxer .mid per un port
#    mid.play() NO fa so: retorna els missatges esperant el temps que toca
#    (el delta en segons de la secció 6 dels patches). Nosaltres els enviem.
# ---------------------------------------------------------------
def reprodueix_fitxer(fitxer='midi/example_scale.mid', numero=0):
    mid = mido.MidiFile(fitxer)
    sortida = obre_sortida(numero)
    if sortida is None:
        return
    print(f"Reproduint {fitxer} ({mid.length:.1f} s)")
    for msg in mid.play():                      # play() ja s'adorm entre missatges
        envia(sortida, msg)
    sortida.close_port()


def silencia(numero=0):
    """Envia 'totes les notes fora' (CC 123) als 16 canals."""
    sortida = obre_sortida(numero)
    if sortida is None:
        return
    for canal in range(16):
        envia(sortida, mido.Message('control_change', channel=canal, control=123, value=0))
    sortida.close_port()
