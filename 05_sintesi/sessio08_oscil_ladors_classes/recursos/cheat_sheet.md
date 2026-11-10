# Cheat sheet — Sessió 8
### Bloc 5a: Síntesi amb classes — Oscillator, Envelope, SamplePlayer

---

## 1. Per què classes, ara?

Fins ara hem fet servir **funcions**: reben paràmetres, retornen un array i **obliden** tot en acabar. Quan calia recordar alguna cosa d'una crida a la següent, la guardàvem en una **global**. A la S05:

```python
fase_sinus = 0.0      # la memòria del sinus
fase_ringmod = 0.0    # cada oscil·lador nou necessita una global nova...
```

I si en volguéssim cinc? Cinc globals, cinc noms, i molt fàcil equivocar-se. Una **classe** resol això: cada objecte porta les seves pròpies dades a dins.

```python
osc_a = Oscillator(freq=440)
osc_b = Oscillator(freq=660)   # cada un té la seva freq i la seva fase
```

---

## 2. Classes en Python: el mínim imprescindible

```python
class Fader:                          # la CLASSE: el motlle
    def __init__(self, nivell=1.0):   # s'executa en crear cada objecte
        self.nivell = nivell          # ATRIBUT: dada que guarda l'objecte

    def aplica(self, so):             # MÈTODE: funció que pertany a la classe
        return so * self.nivell       # fa servir les dades de l'objecte

f1 = Fader(1.0)                       # una INSTÀNCIA (un objecte concret)
f2 = Fader(0.2)                       # una altra, independent
f1.nivell = 0.5                       # canviem NOMÉS f1
so_fluix = f2.aplica(so)              # cridem un mètode
```

| Paraula | Què és |
|---|---|
| classe | El motlle (`Fader`). Nom amb majúscula |
| instància / objecte | Cada peça feta amb el motlle (`f1`, `f2`) |
| `__init__` | El mètode que prepara l'objecte quan es crea |
| `self` | "Aquest objecte en concret". Primer paràmetre de **tots** els mètodes |
| atribut | Una dada de l'objecte: `self.nivell` |
| mètode | Una funció de l'objecte: `f1.aplica(so)` |

### Errors típics

| Escrius | Passa | Correcte |
|---|---|---|
| `def aplica(so):` | Error en cridar-lo (rep un paràmetre de més) | `def aplica(self, so):` |
| `nivell = nivell` dins `__init__` | La dada es perd: `AttributeError: ... has no attribute 'nivell'` | `self.nivell = nivell` |
| `f1.aplica` | No s'executa res (falten parèntesis) | `f1.aplica(so)` |
| `return so * nivell` | `NameError`: dins el mètode, `nivell` no existeix | `return so * self.nivell` |

---

## 3. L'esquelet d'una classe (el ritual)

Abans d'omplir res, escriu l'esquelet: quines dades guarda i què sap fer.

```python
class NomDeLaClasse:
    def __init__(self, param1, param2=valor_per_defecte):
        self.param1 = param1         # configuració
        self.param2 = param2
        self._estat = 0.0            # estat intern

    def metode(self, argument):
        pass                         # (ho omplirem després)
```

Una manera de pensar-ho en paper: una caixa amb tres franges — **nom / atributs / mètodes amb signatura** (`metode(argument) → què retorna`).

---

## 4. Configuració i estat intern (visibilitat)

```python
self.freq = freq      # configuració: la tria qui fa servir l'objecte
self._phase = 0.0     # estat intern: l'objecte el fa evolucionar sol
```

- El **guió baix** inicial és un **conveni**: vol dir "és intern, no el toquis des de fora". Python no ho impedeix: confia en tu.
- Altres llenguatges (C++, Java) tenen `private` i és el compilador qui ho fa complir.
- Per canviar la configuració, accedeix directament a l'atribut: `osc.freq = 880`. A Python **no** cal escriure mètodes `get_freq()` / `set_freq()`.

---

## 5. La classe `Oscillator` (amb memòria de fase)

```python
class Oscillator:
    def __init__(self, freq=440.0, waveform='sine', sample_rate=44100):
        self.freq = freq
        self.waveform = waveform
        self.sample_rate = sample_rate
        self._phase = 0.0                     # on som del cicle (0 … 2π)

    def generate(self, duration):
        n = int(round(self.sample_rate * duration))
        increment = 2 * np.pi * self.freq / self.sample_rate
        fases = self._phase + increment * np.arange(n)            # continuem on ho vam deixar
        self._phase = (self._phase + increment * n) % (2 * np.pi) # recordem per a la propera

        if self.waveform == 'sine':
            return np.sin(fases)
        elif self.waveform == 'square':
            return signal.square(fases)
        elif self.waveform == 'sawtooth':
            return signal.sawtooth(fases)
        else:
            print("Forma d'ona desconeguda:", self.waveform, "→ retorno silenci")
            return np.zeros(n)
```

Són les mateixes línies de `fase_sinus` de la S05, però ara la fase viu **dins** l'objecte. Si demanem el so tros a tros (com farà un callback), els trossos encaixen sense salts:

```python
osc = Oscillator(freq=440)
tros1 = osc.generate(512 / 44100)
tros2 = osc.generate(512 / 44100)   # comença just on va acabar tros1
```

Sense `_phase`, cada tros tornaria a començar a zero: un salt cada 512 mostres, ~86 salts per segon → un brunzit.

**Important:** `Oscillator` per si sol **no té forma de nota** — només sona contínuament. Li falta l'envolvent.

*(Nota: les ones quadrada i de dent de serra de `scipy` són "ingènues": a notes molt agudes fan aliasing. Al registre que fem servir no es nota.)*

---

## 6. La classe `Envelope` (ADSR)

ADSR = **A**ttack, **D**ecay, **S**ustain, **R**elease:

```
amplitud
   |    /\
   |   /  \___________
   |  /                \
   | /                  \
   |/____________________\___ temps
     A   D    S          R
```

- **Attack:** temps per pujar de 0 al màxim
- **Decay:** temps per baixar del màxim al nivell de sustain
- **Sustain:** **nivell** (no temps!) que es manté mentre la nota està premuda
- **Release:** temps per baixar de sustain a 0, després de deixar anar la nota

```python
class Envelope:
    def __init__(self, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release

    def generate(self, note_duration, sample_rate=44100):
        n_attack  = int(self.attack  * sample_rate)
        n_decay   = int(self.decay   * sample_rate)
        n_sustain = max(0, int(note_duration * sample_rate) - n_attack - n_decay)
        n_release = int(self.release * sample_rate)

        env_attack  = np.linspace(0, 1, n_attack)
        env_decay   = np.linspace(1, self.sustain, n_decay)
        env_sustain = np.full(n_sustain, self.sustain)
        env_release = np.linspace(self.sustain, 0, n_release)

        return np.concatenate([env_attack, env_decay, env_sustain, env_release])
```

- `note_duration` és el temps que la nota està premuda; el release s'afegeix **després**.
- Si la nota és més curta que attack + decay, l'envolvent fa igualment A i D sencers: la nota dura una mica més.
- **Aproximació:** aquí l'envolvent sap la durada de la nota per endavant. En temps real (S09) no la sabrem.

---

## 7. Combinar-los: una nota completa

```python
osc = Oscillator(freq=440, waveform='sine')
env = Envelope(attack=0.02, decay=0.1, sustain=0.6, release=0.3)

corba = env.generate(note_duration=0.5)
ona = osc.generate(len(corba) / 44100)   # tantes mostres com la corba
nota = ona * corba
```

**La idea central:** l'oscil·lador defineix el *timbre*; l'envolvent, la *forma temporal*. Es combinen multiplicant, sense barrejar la lògica dins una sola classe.

### Objectes dins d'objectes (composició)

Un atribut pot ser un altre objecte. Així es construeix un instrument a partir de peces:

```python
class Instrument:
    def __init__(self):
        self.osc = Oscillator(waveform='sawtooth')   # l'instrument TÉ un oscil·lador
        self.env = Envelope(attack=0.005)            # ...i una envolvent
```

Les peces es creen **un cop**, a `__init__`, i es reutilitzen a cada nota.

---

## 8. MIDI controla l'envolvent, no l'oscil·lador

```python
def note_to_freq(note_number):
    return 440.0 * (2 ** ((note_number - 69) / 12))

note_to_freq(60)   # ~261.6 Hz (Do central)
```

- `note_on` → comença l'Attack de l'envolvent; `note_off` → comença el Release.
- L'oscil·lador, conceptualment, sona sempre: és l'envolvent qui decideix quan el sentim.
- La velocity (0-127) es pot convertir en volum: `nota * (velocity / 127)`.

---

## 9. La classe `SamplePlayer`

L'`Oscillator` **genera** so amb matemàtiques. El `SamplePlayer` **reprodueix** un so ja gravat (un WAV curt: un cop de bombo, una veu...).

```python
kick = SamplePlayer('kick_sample.wav', gain=0.8)
pas = kick.generate(0.5)    # exactament 0.5 s: el sample i, si sobra temps, silenci
kick.gain = 0.3             # el volum és un atribut: es canvia directament
```

`generate(duration)` retorna sempre `duration` segons: si el sample és més llarg, el retalla; si és més curt, hi afegeix silenci. Així encaixa en un pas d'un seqüenciador.

---

## 10. Mateix nom per a la mateixa feina

`Oscillator.generate(duration)` i `SamplePlayer.generate(duration)` fan la mateixa mena de feina: retornar `duration` segons de so. Com que es diuen igual, es poden fer servir sense saber qui és qui:

```python
fonts = [Oscillator(55, 'sawtooth'), SamplePlayer('kick_sample.wav')]
mescla = np.zeros(int(0.5 * 44100))
for font in fonts:
    mescla = mescla + font.generate(0.5)
```

No cal cap mecanisme especial: a Python n'hi ha prou que el mètode es digui igual (*duck typing*: "si camina com un ànec..."). A la S09 ho convertirem en conveni per a tots els components.

---

## 11. Taula resum

| Classe | Funció | Genera o reprodueix? | Estat intern | Té forma de nota? |
|---|---|---|---|---|
| `Oscillator` | Timbre (forma d'ona, freqüència) | Genera | `_phase` | No — sona sempre |
| `Envelope` | Forma temporal (ADSR) | Genera una corba | — | És qui dona forma de nota |
| `SamplePlayer` | So pregravat | Reprodueix | — | Depèn del sample |

---

## 12. Preview: Sessió 9

- **Temps real (Thonny):** el callback demana el so en mostres (`frames`), no en segons → `generate(duration)` es converteix en `process(n_samples)`, el mateix nom per a tots els components
- L'envolvent amb `note_on`/`note_off` de debò (sense saber la durada per endavant)
- FM synthesis i MIDI en directe
- Un tast de `signalflow`: la mateixa idea, en una llibreria professional
