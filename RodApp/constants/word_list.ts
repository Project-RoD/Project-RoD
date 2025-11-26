// A curated list of common Norwegian words (A1-B2 level)
// Ideally, this should be thousands of words, but this is enough for the prototype.
export const NORWEGIAN_WORDS = [
  "NORSK", "SKOLE", "LÆRER", "SPISE", "DRIKK", "REISE", "KVELD", "ALDRI", 
  "BORDET", "STOLT", "GLADE", "TRIST", "VREDE", "SNAKK", "HØRER", "SEES", 
  "JENTE", "GUTTE", "DAMER", "MANNE", "BARNA", "HUNDER", "KATTE", "HESTE", 
  "FUGLE", "FISKE", "BILEN", "BUSSE", "TOGET", "BÅTEN", "FLYET", "NORGE", 
  "HAMAR", "TUSEN", "ELLER", "ANDRE", "INGEN", "LITEN", "STORE", "MANGE", 
  "VOKSN", "BESTE", "RASKT", "SAKTE", "FINT", "STYGG", "DEILG", "KALD", 
  "VARMT", "SOLEN", "REGNE", "VINDU", "DØREN", "GULV", "TAKET", "VEGGE", 
  "LAMPE", "SENGE", "DYNEN", "PUTEN", "SOFA", "BOKEN", "PENNE", "PAPIR", 
  "BREV", "MOBIL", "NETTE", "STRØM", "VANNE", "BROØD", "SMØRE", "MELKE", 
  "KAFFE", "TEKOP", "EPLER", "BANAN", "PIZZA", "PASTA", "KJØTT", "KYLLG", 
  "GRØNT", "FARGE", "SVART", "HVITE", "RØDE", "BLÅTT", "GRØNN", "GULE", 
  "BRUNT", "LILLA", "ROSA", "ORANS", "GRÅTT", "KLÆR", "BUKSE", "JAKKE", 
  "SKJRT", "SKJRT", "GENSR", "SKONE", "SOKKE", "LUE", "VOTTE", "SKJER", 
  "KROPP", "HODET", "ARMER", "BEINA", "MAGEN", "RYGGE", "HÅRET", "ØYENE", 
  "NESEN", "MUNN", "TENNR", "FOTEN", "HJERTE", "BLOD", "SYKE", "FRISK", 
  "LEGE", "HELSE", "JOBBE", "KONT", "MØTE", "PAUSE", "LUNSJ", "LØNN", 
  "PENGE", "BANK", "KORT", "PRIS", "BILLG", "DYRT", "HANDLE", "BUTIK", 
  "VARER", "POSEN", "KVIT", "TILBU", "SALG", "KUNDE", "SELGE", "KJØPE", 
  "BETAL", "KORT", "KODE", "VIPPS", "KONTO", "SPARE", "LÅNE", "RENTE", 
  "SKATT", "FERIE", "REISE", "TURIST", "HOTE", "HYTTE", "TELT", "SKOG", 
  "FJEL", "SJV", "STRAN", "BADER", "SOLER", "SKIEN", "SNØEN", "AKE", 
  "SKØYT", "SYKKE", "GÅR", "LØPER", "TRENE", "SPIL", "LEKE", "VINNE", 
  "TAPE", "LAGET", "KAMP", "MÅL", "BALL", "DOMMR", "REGL", "FOUL", 
  "KORT", "GULT", "RØDT", "UTVIS", "BYTTE", "PAUSE", "TRENR", "SPILL", 
  "SUPPT", "HEIA", "SANG", "MUSIK", "DANS", "FILM", "KINO", "TEATR", 
  "SCENE", "ROLLE", "ACTOR", "MANUS", "LYD", "LYS", "BILD", "FOTO", 
  "MALER", "KUNST", "FARGE", "FORM", "LINJE", "PUNKT", "SIRKL", "KANT", 
  "MIDT", "SIDEN", "OPPE", "NEDE", "FORAN", "BAK", "UNDER", "OVER", 
  "INNI", "UTEN", "MELLM", "RUNDT", "GJENN", "LANGS", "MOT", "FRA", 
  "TIL", "MED", "UTEN", "FOR", "AV", "OM", "VED", "HOS", "NÅR", 
  "HVA", "HVEM", "HVOR", "HVIS", "AT", "SOM", "MEN", "FORDI", 
  "OG", "ELLER", "IKKE", "JO", "NEI", "JA", "KANSK", "GJERNE", "HELST", 
  "BARE", "NOK", "VEL", "DA", "NÅ", "FØR", "ETTER", "SNART", 
  "LENGE", "ALLTI", "ALDRI", "OFTE", "SJELD", "IBLANT", "IDAG", "IMORG", 
  "IGÅR", "IKVEL", "INATT", "UKEN", "ÅRET", "MÅNED", "DATO", "TIDEN", 
  "KLOKK", "TIME", "MINUT", "SEKUN", "VINTER", "VÅREN", "SOMMR", "HØSTE",
  "JULEN", "PÅSKE", "HELG", "MANDG", "TIRSD", "ONSDG", "TORSD", "FREDG",
  "LØRDG", "SØNDG", "JANUA", "FEBRU", "MARS", "APRIL", "MAI", "JUNI",
  "JULI", "AUGUS", "SEPTE", "OKTOB", "NOVEM", "DESEM"
];

// Clean up function to ensure 5 letters and uppercase
export const CLEAN_WORDS = NORWEGIAN_WORDS
    .map(w => w.toUpperCase())
    .filter(w => w.length === 5);

// Check if word exists
export function isWordValid(word: string): boolean {
    return CLEAN_WORDS.includes(word.toUpperCase());
}

export function getRandomWord() {
    return CLEAN_WORDS[Math.floor(Math.random() * CLEAN_WORDS.length)];
}