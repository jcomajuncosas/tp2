"""Genera full_aliasing.pdf: el full en paper de la Part 2 de la S09 (privat, per imprimir).

    python3 genera_full_aliasing.py
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sample_rate = 44100
block = 512
f_mod = 80
durada = 0.2

t = np.linspace(0, durada, 4000)
talls = np.arange(0, durada + 1e-9, block / sample_rate)

fig = plt.figure(figsize=(8.27, 11.69))   # A4
fig.text(0.08, 0.95, "S09 — El modulador, mirat un cop per bloc", fontsize=15, weight='bold')
fig.text(0.08, 0.915, "Nom: ______________________________", fontsize=10)
fig.text(0.08, 0.865,
         "A dalt hi ha el modulador: un sinus de 80 Hz durant 0,2 s (16 cicles).\n"
         "Cada línia vertical és l'inici d'un bloc de 512 mostres (cada 11,6 ms).\n"
         "El nostre vibrato() només mira el modulador en aquests instants.",
         fontsize=10, va='top')

ax1 = fig.add_axes([0.08, 0.58, 0.86, 0.2])
ax1.plot(t * 1000, np.sin(2 * np.pi * f_mod * t), color='0.55', lw=1)
for x in talls:
    ax1.axvline(x * 1000, color='tab:red', lw=0.8)
ax1.set_xlim(0, durada * 1000)
ax1.set_ylim(-1.15, 1.15)
ax1.set_yticks([-1, 0, 1])
ax1.set_xlabel("temps (ms)")
ax1.set_title("1. Marca amb un punt on cada línia vermella talla el sinus", fontsize=10, loc='left')

ax2 = fig.add_axes([0.08, 0.30, 0.86, 0.2])
for x in talls:
    ax2.axvline(x * 1000, color='tab:red', lw=0.8)
ax2.axhline(0, color='0.8', lw=0.8)
for y in [-1, 1]:
    ax2.axhline(y, color='0.85', lw=0.6, ls='--')
ax2.set_xlim(0, durada * 1000)
ax2.set_ylim(-1.15, 1.15)
ax2.set_yticks([-1, 0, 1])
ax2.set_xlabel("temps (ms)")
ax2.set_title("2. Copia aquí NOMÉS els punts, a la mateixa altura, i uneix-los", fontsize=10, loc='left')

fig.text(0.08, 0.22,
         "3. Quants cicles fa la corba que has dibuixat en 0,2 s? A quina freqüència (Hz) correspon?\n\n"
         "     ____________________________________________\n\n"
         "4. Quina freqüència hauria de tenir el modulador perquè tots els punts quedessin a la\n"
         "    mateixa altura (la sirena s'aturaria)? Pista: quants blocs hi ha en un segon?\n\n"
         "     ____________________________________________",
         fontsize=10, va='top')

fig.savefig('full_aliasing.pdf')
print("full_aliasing.pdf generat")
