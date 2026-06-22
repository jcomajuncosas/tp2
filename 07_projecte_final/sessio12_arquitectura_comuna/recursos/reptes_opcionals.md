# Reptes opcionals — Projecte final
### Per a qui acabi el nucli mínim del seu rol abans que la resta (NO avaluat, NO contingut obligatori)

Aquests reptes són transversals — no depenen de quin rol tinguis, però cadascun encaixa més bé amb alguns rols que d'altres (indicat a cada un). Primer mira les **extensions opcionals del teu propi `README.md`** — normalment són el pas més natural. Aquests reptes són per quan ja les has explorat i vols anar encara més enllà.

---

## Repte 1 — Control extern dels teus paràmetres

**Encaixa especialment amb:** Efecte adaptatiu, Vocoder, Sinte.

Ara mateix, molts paràmetres del teu instrument són constants fixades al codi (per exemple `RESONANCIA_BANDES` al Vocoder, o el `threshold` de la Distorsió a l'Efecte adaptatiu). Tria'n un parell i fes-los controlables en directe amb un potenciòmetre MIDI (Control Change) del teu controlador, en lloc de tenir-los fixos.

Recordatori de Bloc 4: un missatge `control_change` té un `control` (número de potenciòmetre) i un `value` (0-127) — només cal escalar aquest valor (`escala()`, si el teu template ja en té una, o una versió pròpia) al rang útil del paràmetre que vulguis controlar.

## Repte 2 — Visualització en directe

**Encaixa amb:** qualsevol rol.

Mentre toques, mostra en pantalla (amb `matplotlib` en mode interactiu, o simplement `print()` d'una barra de text feta amb caràcters) algun valor intern del teu instrument en temps real: l'envolupant del Vocoder, l'estat dels passos del Looper, els valors dels 3 descriptors de l'Efecte adaptatiu...

Avís: `matplotlib` en temps real dins d'un callback d'àudio pot introduir glitches si no vas amb compte (el rendering no és instantani). Si et passa, prova d'actualitzar la visualització en un fil (`thread`) separat del callback d'àudio, llegint només l'últim valor calculat.

## Repte 3 — Polifonia real (si el teu rol és monofònic)

**Encaixa amb:** Vocoder (és monofònic per disseny).

El Vocoder, tal com està plantejat, només toca una nota a la vegada. Si vols, intenta estendre'l a polifonia real: una `VocoderPatch` (o el carrier que toqui) per cada nota activa, sumant totes les veus a la sortida — el mateix patró que ja fa servir el Sinte (`veus_actives = [None] * 128`).

Compte amb el cost de càlcul: cada veu addicional repeteix tot el banc de 16 bandes — amb poques veus simultànies hauria d'anar bé, però val la pena vigilar-ho si sents glitches.

## Repte 4 — Gravar i exportar la teva sessió

**Encaixa amb:** qualsevol rol.

Afegeix la possibilitat de gravar tota la sortida del teu instrument a un fitxer WAV mentre toques (Bloc 2, `soundfile`/`scipy.io.wavfile`), per poder escoltar-te després o fer-ne un petit muntatge per al concert. Pots fer-ho acumulant cada bloc de sortida en una llista i escrivint-la sencera al fitxer quan acabis (Ctrl+C), o escrivint directament a un fitxer obert en mode streaming si vols evitar consumir memòria en sessions molt llargues.

## Repte 5 — Un segon "color" per al teu instrument

**Encaixa amb:** qualsevol rol, especialment Sinte i Vocoder.

Defineix una segona configuració de paràmetres del teu instrument (per exemple, un segon carrier al Sinte/Vocoder, o un segon joc d'efectes a l'Efecte adaptatiu) i fes que una nota o un control concret alterni entre el "color A" i el "color B" — útil per donar variació dins d'una mateixa peça al concert sense haver de parar i canviar codi en directe.
