"""
Exemples — Bloc 4a, Sessió 6 (Thonny)
Estructura MIDI i mido

Complementa el notebook Colab (patches_bloc4a.ipynb).
Aquí: reproducció de fitxers MIDI i connexió a ports MIDI reals.
"""

import mido
import time

# ---------------------------------------------------------------
# 1. Llegir i reproduir un fitxer MIDI (blocking)
#    Requereix: 'example_scale.mid' a la mateixa carpeta
#    (descarrega'l de recursos/midi/)
# ---------------------------------------------------------------
print("=== 1. Llegir example_scale.mid ===")

mid = mido.MidiFile('example_scale.mid')
print(f"Tracks: {len(mid.tracks)}")
print(f"Ticks per beat: {mid.ticks_per_beat}")
print(f"Durada: {mid.length:.2f}s")

for i, track in enumerate(mid.tracks):
    print(f"\nTrack {i}: '{track.name}' ({len(track)} msgs)")
    for msg in track[:8]:  # primers 8 missatges
        print(f"  {msg}")
    if len(track) > 8:
        print(f"  ... ({len(track)-8} més)")


# ---------------------------------------------------------------
# 2. Crear un fitxer MIDI i reproduir-lo
# ---------------------------------------------------------------
print("\n=== 2. Crear i reproduir un fitxer MIDI ===")

mid_nou = mido.MidiFile(ticks_per_beat=480)
tempo = mido.bpm2tempo(120)
quarter = 480
eighth  = 240

meta = mido.MidiTrack()
meta.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
mid_nou.tracks.append(meta)

track = mido.MidiTrack()
pattern = [60, 62, 64, 65, 67, 69, 71, 72]  # Do major ascendent

for note in pattern:
    track.append(mido.Message('note_on',  channel=0, note=note, velocity=80, time=0))
    track.append(mido.Message('note_off', channel=0, note=note, velocity=0,  time=eighth))

track.append(mido.MetaMessage('end_of_track', time=0))
mid_nou.tracks.append(track)
mid_nou.save('escala.mid')
print("Creat escala.mid")

# Reproduir per consola (simulat: mostra els missatges amb timing)
print("\nMissatges amb timing real (en segons):")
for msg in mid_nou:
    if not msg.is_meta:
        print(f"  t={msg.time:.3f}s  {msg}")


# ---------------------------------------------------------------
# 3. MIDI en temps real — llistar ports disponibles
# ---------------------------------------------------------------
print("\n=== 3. Ports MIDI disponibles ===")
print("Inputs:", mido.get_input_names())
print("Outputs:", mido.get_output_names())


# ---------------------------------------------------------------
# 4. MIDI in: rebre missatges d'un teclat controlador
#    Descomenta si tens un teclat connectat
# ---------------------------------------------------------------
# print("\n=== 4. MIDI In — teclat controlador ===")
# print("Toca notes al teclat. Ctrl+C per aturar.")
#
# try:
#     with mido.open_input() as port:
#         print(f"Port obert: {port.name}")
#         for msg in port:
#             if msg.type == 'note_on' and msg.velocity > 0:
#                 noms = ['Do','Do#','Re','Re#','Mi','Fa','Fa#','Sol','Sol#','La','La#','Si']
#                 nom = f"{noms[msg.note % 12]}{msg.note // 12 - 1}"
#                 print(f"  Nota: {msg.note} ({nom})  Velocity: {msg.velocity}")
#             elif msg.type == 'control_change':
#                 print(f"  CC: {msg.control} = {msg.value}")
# except KeyboardInterrupt:
#     pass
# except Exception as e:
#     print(f"Error obrint port: {e}")
#     print("Comprova: Audio MIDI Setup (macOS) o LoopMIDI (Windows)")


# ---------------------------------------------------------------
# 5. MIDI out: enviar notes a un sintetitzador extern
#    Descomenta si tens un port de sortida disponible
# ---------------------------------------------------------------
# print("\n=== 5. MIDI Out ===")
# outputs = mido.get_output_names()
# if outputs:
#     with mido.open_output(outputs[0]) as port:
#         print(f"Enviant notes a: {outputs[0]}")
#         for note in [60, 64, 67, 72]:
#             port.send(mido.Message('note_on', note=note, velocity=80))
#             time.sleep(0.5)
#             port.send(mido.Message('note_off', note=note, velocity=0))
#             time.sleep(0.1)
# else:
#     print("Cap port de sortida disponible")
#     print("macOS: crea IAC Driver a Audio MIDI Setup")
#     print("Windows: instal·la LoopMIDI")
