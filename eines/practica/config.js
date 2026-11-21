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

  // Encerts seguits per dominar un concepte (com a mínim un ha de ser d'escriure codi,
  // si el concepte en té).
  RATXA_DOMINI: 3,

  // Intents màxims perquè un exercici d'escriure/ordenar compti com a encert.
  INTENTS_ESCRIURE: 3,

  // Segons màxims d'execució del codi de l'alumne (bucle infinit → es talla).
  TIMEOUT_S: 6,

  PYODIDE: 'https://cdn.jsdelivr.net/pyodide/v0.28.3/full/',
  VERSIO: '2026-11-21',
};
