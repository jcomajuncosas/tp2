"""
Prova de signalflow per a Thonny
================================

Obre aquest fitxer a Thonny i prem F5. No cal saber res de signalflow.

Fa tres coses:
  1. et diu quin Python fa servir el teu Thonny (és el que compta!)
  2. mira si hi tens les llibreries del curs
  3. si hi ha signalflow, fa sonar 2 segons de FM

Si alguna cosa surt amb ❌, mira la guia signalflow_thonny.md: busca-hi
el missatge que t'ha sortit.
"""

import sys
import platform
import importlib.util

# ---------------------------------------------------------------
# 1. Quin Python fa servir Thonny?
# ---------------------------------------------------------------
versio = sys.version_info
bits = 64
if sys.maxsize <= 2 ** 32:
    bits = 32

print("=" * 60)
print("Python", str(versio.major) + "." + str(versio.minor) + "." + str(versio.micro),
      "-", bits, "bits")
print("Sistema:", platform.system(), platform.release(), "-", platform.machine())
if platform.system() == "Darwin":
    print("macOS:", platform.mac_ver()[0])
print("Intèrpret:", sys.executable)
print("=" * 60)

es_pot = True
if versio.minor < 9:
    print("❌ Python massa antic per a signalflow (cal 3.9 o més nou)")
    es_pot = False
if bits == 32:
    print("❌ Python de 32 bits: signalflow només existeix per a 64 bits")
    es_pot = False
if platform.system() == "Darwin":
    major_macos = int(platform.mac_ver()[0].split(".")[0])
    if major_macos < 12:
        print("❌ macOS", platform.mac_ver()[0], "- signalflow necessita macOS 12 o més nou")
        es_pot = False
if es_pot:
    print("✅ Aquest Python pot tenir signalflow")

# ---------------------------------------------------------------
# 2. Hi ha les llibreries del curs?
# ---------------------------------------------------------------
print()
falten = []
for nom in ["numpy", "scipy", "sounddevice", "mido", "rtmidi2", "matplotlib", "signalflow"]:
    if importlib.util.find_spec(nom) is None:
        print("   ❌", nom)
        falten.append(nom)
    else:
        print("   ✅", nom)
if len(falten) > 0:
    print()
    print("Falten:", falten)
    print("Instal·la-les amb Tools → Manage packages... (una per una)")
    print("i torna a prémer F5.")

# ---------------------------------------------------------------
# 3. Fa sonar signalflow (2 segons)
# ---------------------------------------------------------------
if importlib.util.find_spec("signalflow") is not None:
    print()
    print("signalflow és a:", importlib.util.find_spec("signalflow").origin)
    print("Sonant 2 segons de FM (portadora 440 Hz, modulador 110 Hz, I = 3)...")
    from signalflow import AudioGraph, SineOscillator

    graph = AudioGraph()
    fm = 110
    I = 3
    modulador = SineOscillator(fm) * (I * fm)
    portadora = SineOscillator(440 + modulador) * 0.2
    portadora.play()
    graph.wait(2)
    portadora.stop()
    print("✅ signalflow funciona. Si no has sentit res, mira l'apartat")
    print("   «No sona res» de la guia.")
