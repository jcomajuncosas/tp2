"""
Exemples — Bloc 3c, Sessió 5 (Thonny)
Efectes en temps real: eco, distorsió i combinació

IMPORTANT: executa amb Thonny (entorn local). NO funciona a Colab.
Ctrl+C per aturar qualsevol stream.
"""

import sounddevice as sd
import numpy as np

sample_rate = 44100
blocksize = 1024


# ---------------------------------------------------------------
# 1. Distorsió en temps real (sense memòria — el cas simple)
# ---------------------------------------------------------------
print("=== DEMO 1: Distorsió en temps real ===")
print("Parla o fes un so. Ctrl+C per aturar.\n")

drive = 4.0
threshold = 0.7

def distorsio_callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    mono = indata[:, 0]
    clipped = np.clip(mono * drive, -threshold, threshold)
    outdata[:, 0] = clipped / threshold

try:
    with sd.Stream(samplerate=sample_rate, blocksize=blocksize,
                   channels=1, dtype='float32', callback=distorsio_callback):
        sd.sleep(8000)
except KeyboardInterrupt:
    pass


# ---------------------------------------------------------------
# 2. Eco en temps real (amb buffer de retard global)
# ---------------------------------------------------------------
print("\n=== DEMO 2: Eco en temps real ===")
print("Parla i escolta l'eco. Ctrl+C per aturar.\n")

delay_seconds = 0.3
decay = 0.5
delay_samples = int(delay_seconds * sample_rate)
delay_buffer = np.zeros(delay_samples, dtype='float32')

def eco_callback(indata, outdata, frames, time, status):
    global delay_buffer
    if status:
        print(status)
    mono = indata[:, 0]

    eco = delay_buffer[:frames]
    out = mono + eco * decay

    delay_buffer = np.roll(delay_buffer, -frames)
    delay_buffer[-frames:] = mono

    outdata[:, 0] = np.clip(out, -1.0, 1.0)

try:
    with sd.Stream(samplerate=sample_rate, blocksize=blocksize,
                   channels=1, dtype='float32', callback=eco_callback):
        sd.sleep(10000)
except KeyboardInterrupt:
    pass


# ---------------------------------------------------------------
# 3. Eco amb control interactiu del delay i decay
# ---------------------------------------------------------------
print("\n=== DEMO 3: Eco amb control interactiu ===")
print("Canvia delay_seconds i decay mentre el so passa.")
print("Escriu 'q' per sortir.\n")

delay_seconds = 0.3
decay = 0.5
delay_samples = int(delay_seconds * sample_rate)
delay_buffer = np.zeros(delay_samples, dtype='float32')

def eco_control_callback(indata, outdata, frames, time, status):
    global delay_buffer, delay_samples, decay
    if status:
        print(status)
    mono = indata[:, 0]

    # Adaptem el buffer si delay_samples ha canviat
    if len(delay_buffer) != delay_samples:
        delay_buffer = np.zeros(delay_samples, dtype='float32')

    eco = delay_buffer[:frames]
    out = mono + eco * decay
    delay_buffer = np.roll(delay_buffer, -frames)
    delay_buffer[-frames:] = mono
    outdata[:, 0] = np.clip(out, -1.0, 1.0)

with sd.Stream(samplerate=sample_rate, blocksize=blocksize,
               channels=1, dtype='float32', callback=eco_control_callback):
    while True:
        try:
            cmd = input(f"delay={delay_seconds:.2f}s decay={decay:.2f} → "
                       f"'d 0.5' per delay, 'c 0.7' per decay, 'q' per sortir: ")
            if cmd.lower() == 'q':
                break
            parts = cmd.strip().split()
            if len(parts) == 2:
                if parts[0] == 'd':
                    delay_seconds = float(parts[1])
                    delay_samples = int(delay_seconds * sample_rate)
                elif parts[0] == 'c':
                    decay = float(parts[1])
        except (ValueError, KeyboardInterrupt):
            break

print("Stream tancat.")


# ---------------------------------------------------------------
# 4. Distorsió + eco combinats
# ---------------------------------------------------------------
print("\n=== DEMO 4: Distorsió + Eco combinats ===")
print("Prova l'ordre distorsió→eco vs eco→distorsió. Sonen diferent? Per qué?\n")

drive = 3.0
threshold = 0.7
delay_seconds = 0.25
decay = 0.45
delay_samples = int(delay_seconds * sample_rate)
delay_buffer = np.zeros(delay_samples, dtype='float32')

def combo_callback(indata, outdata, frames, time, status):
    global delay_buffer
    if status:
        print(status)
    mono = indata[:, 0]

    # Distorsió primer
    dist = np.clip(mono * drive, -threshold, threshold) / threshold

    # Eco sobre la distorsió
    eco = delay_buffer[:frames]
    out = dist + eco * decay
    delay_buffer = np.roll(delay_buffer, -frames)
    delay_buffer[-frames:] = dist  # guardem la distorsió, no el raw

    outdata[:, 0] = np.clip(out, -1.0, 1.0)

try:
    with sd.Stream(samplerate=sample_rate, blocksize=blocksize,
                   channels=1, dtype='float32', callback=combo_callback):
        sd.sleep(10000)
except KeyboardInterrupt:
    pass


# ---------------------------------------------------------------
# 5. DEMO: per qué les classes seran millors (preview Bloc 5)
#    Volem DOS ecos simultanis → dos buffers globals separats
# ---------------------------------------------------------------
print("\n=== DEMO 5: Dos ecos simultanis (limitació del buffer global) ===")
print("Necessitem dos buffers globals separats — un per delay.")
print("Al Bloc 5 ho encapsularem en una classe EcoEffect.\n")

delay_samples_1 = int(0.15 * sample_rate)
delay_samples_2 = int(0.4 * sample_rate)
delay_buffer_1 = np.zeros(delay_samples_1, dtype='float32')
delay_buffer_2 = np.zeros(delay_samples_2, dtype='float32')
decay_1 = 0.5
decay_2 = 0.3

def dos_ecos_callback(indata, outdata, frames, time, status):
    global delay_buffer_1, delay_buffer_2
    if status:
        print(status)
    mono = indata[:, 0]

    eco1 = delay_buffer_1[:frames]
    delay_buffer_1 = np.roll(delay_buffer_1, -frames)
    delay_buffer_1[-frames:] = mono

    eco2 = delay_buffer_2[:frames]
    delay_buffer_2 = np.roll(delay_buffer_2, -frames)
    delay_buffer_2[-frames:] = mono

    out = mono + eco1 * decay_1 + eco2 * decay_2
    outdata[:, 0] = np.clip(out, -1.0, 1.0)

print("Funcionarà, però imagina 5 ecos... 5 parells de variables globals.")
print("La solució: classes. Les veurem al Bloc 5.\n")

try:
    with sd.Stream(samplerate=sample_rate, blocksize=blocksize,
                   channels=1, dtype='float32', callback=dos_ecos_callback):
        sd.sleep(8000)
except KeyboardInterrupt:
    pass
