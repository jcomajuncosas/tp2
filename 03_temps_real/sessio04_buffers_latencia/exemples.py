"""
Exemples — Bloc 3b, Sessió 4 (Thonny)
El model callback: àudio en temps real

IMPORTANT: aquest fitxer requereix Thonny + sounddevice instal·lat localment.
NO funciona a Colab (el codi s'executaria en un servidor remot sense accés
al teu hardware d'àudio).

Executa cada secció per parts (selecciona i "Run selection") o comenta/descomenta.
Ctrl+C per aturar qualsevol stream actiu.
"""

import sounddevice as sd
import numpy as np

sample_rate = 44100
blocksize = 1024  # prova 256, 512, 1024 — nota la diferència de latència


# ---------------------------------------------------------------
# 1. El callback més simple: pass-through
#    Copia l'entrada directament a la sortida, sense modificar res.
#    Si tot funciona: hauries de sentir la teva veu amb ~10-20ms de retard.
# ---------------------------------------------------------------
print("=== DEMO 1: Pass-through ===")
print("Parla o fes un so. Hauries de sentir-te amb poc retard.")
print("Ctrl+C per aturar.\n")

def passthrough(indata, outdata, frames, time, status):
    if status:
        print("STATUS:", status)
    outdata[:] = indata  # copia entrada → sortida, sense canvis

try:
    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   callback=passthrough):
        sd.sleep(8000)  # 8 segons
except KeyboardInterrupt:
    pass


# ---------------------------------------------------------------
# 2. Gain en temps real amb variable global
#    La variable 'gain' és llegida pel callback cada ~10ms.
#    La modifiquem des del programa principal (input) sense aturar el stream.
# ---------------------------------------------------------------
print("\n=== DEMO 2: Gain en temps real ===")
print("Pots canviar el gain mentre el so passa.")
print("Escriu un número entre 0.0 i 1.0 i prem Enter.")
print("Escriu 'q' per sortir.\n")

gain = 0.5  # variable global — accessible des del callback I des del main

def gain_control(indata, outdata, frames, time, status):
    if status:
        print("STATUS:", status)
    outdata[:] = indata * gain  # llegeix la variable global

with sd.Stream(samplerate=sample_rate,
               blocksize=blocksize,
               channels=1,
               dtype='float32',
               callback=gain_control):
    while True:
        try:
            entrada = input(f"Gain actual: {gain:.2f} → nou valor: ")
            if entrada.lower() == 'q':
                break
            nou_gain = float(entrada)
            if 0.0 <= nou_gain <= 2.0:
                gain = nou_gain
                print(f"Gain canviat a {gain:.2f}")
            else:
                print("Valor fora de rang (0.0 - 2.0)")
        except ValueError:
            print("Escriu un número vàlid")
        except KeyboardInterrupt:
            break

print("Stream tancat.")


# ---------------------------------------------------------------
# 3. DEMO: la variable global és "compartida" — il·lustració
#
#    Nota: en sistemes de producció real s'usaria queue.Queue o
#    variables atòmiques. Per ara, per a un float simple, la variable
#    global funciona en pràctica (Python GIL).
# ---------------------------------------------------------------
print("\n=== DEMO 3: La variable global — il·lustració ===")

comptador = 0  # modificada des de dins el callback

def compta_blocs(indata, outdata, frames, time, status):
    global comptador
    comptador += 1
    outdata[:] = indata

print("Comptant blocs de callback durant 3 segons...")
with sd.Stream(samplerate=sample_rate,
               blocksize=blocksize,
               channels=1,
               dtype='float32',
               callback=compta_blocs):
    sd.sleep(3000)

freqüencia_real = comptador / 3.0
freqüencia_esperada = sample_rate / blocksize
print(f"Blocs processats: {comptador}")
print(f"Freqüència real: {freqüencia_real:.1f} blocs/s")
print(f"Freqüència esperada: {freqüencia_esperada:.1f} blocs/s")
print(f"Coincideix? {'✅' if abs(freqüencia_real - freqüencia_esperada) < 5 else '⚠️ No exactament — el sistema operatiu té les seves pròpies prioritats'}")


# ---------------------------------------------------------------
# 4. DEMO: callback lenta → glitch
#    ATENCIÓ: això produirà soroll/glitches deliberadament.
#    És per demostrar qué passa quan el callback és massa lenta.
# ---------------------------------------------------------------
print("\n=== DEMO 4: Callback lenta → glitch (deliberat) ===")
print("Hauràs de sentir interrupcions i artefactes en l'àudio.")
print("Premeu Enter per continuar...")
input()

import time

def callback_lenta(indata, outdata, frames, time_info, status):
    time.sleep(0.05)  # 50ms — MOLT més lent que el buffer (~11ms)
    outdata[:] = indata

try:
    with sd.Stream(samplerate=sample_rate,
                   blocksize=blocksize,
                   channels=1,
                   dtype='float32',
                   callback=callback_lenta):
        sd.sleep(4000)
except Exception as e:
    print(f"Error (esperat): {e}")

print("\nAquest és el so del glitch: el sistema no pot esperar que el callback acabi.")
print("La solució: fer el mínim possible dins el callback.")


# ---------------------------------------------------------------
# 5. DEMO: blocksize i latència — compara
#    Canvia 'blocksize' al principi del fitxer i torna a executar.
#    Amb blocksize=256 la latència és menor però el risc de glitch és major.
# ---------------------------------------------------------------
print("\n=== DEMO 5: Latència calculada ===")
latència_ms = blocksize / sample_rate * 1000
print(f"blocksize actual: {blocksize}")
print(f"Latència teòrica: {latència_ms:.1f} ms")
print(f"Temps per processar: < {latència_ms:.1f} ms")
print("\nProva a canviar blocksize a 256 o 2048 al principi del fitxer i nota la diferència.")
