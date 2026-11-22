// Configuració de la pràctica. És l'únic fitxer que cal tocar per desplegar.
window.CONFIG = {
  TITOL: 'Pràctica de Python — TP2',

  // URL de l'aplicació web d'Apps Script que desa els resultats al Google Sheet
  // (vegeu apps_script/Code.gs i README.md). Buit = no s'envia res (només progrés local).
  ENDPOINT: '',

  // Quins bancs d'exercicis s'ofereixen, en ordre.
  //   ['tp1']          → anivellament a l'inici del curs (només mecànica de Python)
  //   ['tp1', 'tp2']   → consolidació durant TP2
  BANCS: ['tp1', 'tp2'],

  // Quants blocs (de blocs.json) estan oberts. Obre'n un de nou a cada fase del calendari:
  //   1 → Base de Python · 2 → + Arrays i so · 3 → + Classes i estat
  BLOCS_OBERTS: 1,

  // Encerts seguits per dominar un concepte (com a mínim un ha de ser d'escriure codi,
  // si el concepte en té).
  RATXA_DOMINI: 3,

  // Intents màxims perquè un exercici d'escriure/ordenar compti com a encert.
  INTENTS_ESCRIURE: 3,

  // Segons màxims d'execució del codi de l'alumne (bucle infinit → es talla).
  TIMEOUT_S: 6,

  // Dificulta copiar l'enunciat i enganxar codi a les respostes (no ho impedeix del tot:
  // només fa que passar-ho per una IA no sigui immediat). false = desactivat.
  BLOQUEJA_COPIA: true,

  // Punts (petita gamificació)
  PUNTS: { predir: 10, escriure: 20, ordenar: 15, domini: 50 },

  PYODIDE: 'https://cdn.jsdelivr.net/pyodide/v0.28.3/full/',
  VERSIO: '2026-11-22b',
};
