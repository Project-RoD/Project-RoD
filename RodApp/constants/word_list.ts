import { VALID_GUESSES } from './valid_words';
// A curated list of common Norwegian words
// Ideally, this should be thousands of words, but this is enough for the prototype.
export const TARGET_WORDS = [
  "AGURK", "ALENE", "ALVOR", "ANDRE", "ANGST", "ANKER", "ANTAR", "APRIL", "AVSLÅ", "AVTAL",
  "BADER", "BAKKE", "BAMSE", "BANAN", "BANKE", "BARNA", "BASIS", "BEDRE", "BEGGE", "BEVIS",
  "BIBEL", "BILEN", "BILER", "BJØRN", "BLANT", "BLEKK", "BLIND", "BLOND", "BLUSE", "BLØTE",
  "BOKEN", "BOLLE", "BOMBE", "BONDE", "BORTE", "BRANN", "BRENN", "BRETT", "BRING", "BROEN",
  "BRUNT", "BRUKE", "BRUKT", "BRYTE", "BRØNN", "BUKSE", "BURDE", "BYGGE", "BÆRET", "BØKER",
  "BØLGE", "BØNNE", "DAMEN", "DAMER", "DAMPA", "DANSE", "DATEN", "DEKKE", "DELER", "DELTA",
  "DENNE", "DETTE", "DISSE", "DREPE", "DRIKK", "DRIVE", "DUKKE", "DUSJE", "DYBDE", "DYRKE",
  "DØDEN", "DØMME", "DØREN", "DÅRLI", "EGGEN", "ELLER", "ELSKE", "ENGEL", "ENKLE", "ENORM",
  "ENTRE", "EPLET", "ETTER", "FAKTA", "FALLE", "FALSK", "FANGE", "FAREN", "FARGE", "FARTA",
  "FASTE", "FEBER", "FEIRE", "FEMTE", "FERIE", "FERJE", "FESTE", "FILME", "FINNE", "FIRMA",
  "FISKE", "FJELL", "FLAGG", "FLATE", "FLERE", "FLINK", "FLOTT", "FLYTE", "FLYET", "FLØTE",
  "FORAN", "FORDI", "FORME", "FOTEN", "FRESE", "FRISK", "FRYKT", "FRUKT", "FULLE", "FYLLE",
  "FYREN", "FÆRRE", "FØLGE", "FØRST", "GAMLE", "GANGS", "GAVER", "GLADE", "GLASS", "GLEDE",
  "GLEMT", "GODTA", "GREIE", "GRISK", "GRUNN", "GRYTE", "GRÅTE", "GRØNN", "GUMMI", "HALVE",
  "HAMRE", "HAVET", "HELSE", "HENGE", "HENNE", "HENTE", "HERRE", "HILSE", "HJELP", "HOGGE",
  "HOLDE", "HOPPE", "HUSKE", "HVILE", "HVITE", "HYTTE", "HØYRE", "IDYLL", "IGJEN", "INGEN",
  "INDRE", "ISBRE", "IVRIG", "JAKKE", "JENTE", "JORDA", "JUBEL", "KAFFE", "KAKER", "KALDE",
  "KALLE", "KAPPE", "KASTE", "KATTE", "KILDE", "KJOLE", "KJÆRE", "KJØLE", "KJØPE", "KJØRE",
  "KJØTT", "KLAGE", "KLARE", "KLART", "KLOKK", "KNEET", "KNUSE", "KOMME", "KONGE", "KONTO",
  "KORTE", "KOSTE", "KRAVE", "KREMT", "KRIGE", "KROPP", "KRYPE", "KUNST", "KUNNE", "KVELD",
  "KYSSE", "LAGER", "LAGRE", "LAMPE", "LANDE", "LANGE", "LANGT", "LASTE", "LEDER", "LEGEN",
  "LEKSE", "LENGE", "LESER", "LETTE", "LEVER", "LIGGE", "LIKER", "LILLE", "LINJE", "LISTE",
  "LITER", "LIVET", "LOMME", "LUKKE", "LUNSJ", "LYKKE", "LÆRER", "LØFTE", "LØPER", "MAGEN",
  "MAMMA", "MANGE", "MASSE", "MATEN", "MEIER", "MENER", "MERKE", "MESTE", "METER", "MILJØ",
  "MINST", "MISTE", "MODEN", "MODIG", "MOREN", "MOTOR", "MULIG", "MURER", "MYNTE", "MØRKE",
  "MØTER", "MÅNED", "NEGLE", "NEPPE", "NESTE", "NETTO", "NEVNE", "NIESE", "NITTI", "NORGE",
  "NORSK", "NOTAT", "NYHET", "NYLIG", "NYTTE", "NÅDEN", "OFFER", "OMLØP", "ONKEL", "ORDET",
  "ORDRE", "ORDNE", "ORGEL", "PAKKE", "PANNE", "PAPIR", "PARTI", "PASSE", "PAUSE", "PENGE",
  "PIZZA", "PLASS", "PLUSS", "POENG", "POTET", "PRATE", "PREST", "PRINS", "PROPP", "PRØVE",
  "PUSTE", "PYNTE", "PÆREN", "PØLSE", "RADIO", "RASKT", "REDDE", "REGEL", "REGNE", "REISE",
  "REKKE", "RENSE", "RENTE", "RINGE", "ROBOT", "ROLIG", "RUNDE", "RUNDT", "RYDDE", "RYKTE",
  "RØMME", "SAKTE", "SALAT", "SALME", "SAMLE", "SAMME", "SCENE", "SEIER", "SELGE", "SENDE",
  "SETTE", "SIKTE", "SINTE", "SITTE", "SIVIL", "SJEKK", "SJØEN", "SKADE", "SKAPE", "SKARP",
  "SKATT", "SKOLE", "SKRIV", "SKRUS", "SKRYT", "SKYTE", "SKYVE", "SLAPP", "SLETT", "SLIPP",
  "SLIPS", "SLITE", "SLOTT", "SLUTT", "SLÅSS", "SMAKE", "SMART", "SMILE", "SNAKK", "SNART",
  "SNILL", "SOLEN", "SOVER", "SPARE", "SPEIL", "SPILL", "SPISE", "SPORT", "SPRÅK", "START",
  "STEKE", "STIGE", "STOLE", "STOPP", "STORE", "STORM", "STYGG", "STYRE", "SUPPE", "SVART",
  "SVARE", "SYKLE", "SYNGE", "SØREN", "SÅPEN", "TAKET", "TANKE", "TANTE", "TAVLE", "TEKST",
  "TELLE", "TENKE", "TEPPE", "TIDEN", "TIMER", "TJENE", "TOMAT", "TOMME", "TOTAL", "TRANG",
  "TRAPP", "TREFF", "TREKK", "TRENE", "TRIST", "TROLL", "TRONE", "TRYKK", "TRØTT", "TUNGE",
  "TUSEN", "TVILE", "TYSKE", "TÅKEN", "UNDER", "UNIKE", "UNNGÅ", "VALGT", "VANNE", "VARME",
  "VARMT", "VASKE", "VEDTA", "VEIEN", "VELGE", "VENNE", "VENTE", "VERDI", "VERDT", "VESKE",
  "VIDEO", "VIFTE", "VILLE", "VINDU", "VINGE", "VISKE", "VOKSE", "VONDT", "VÅKEN", "VÅKNE",
  "ÆRLIG", "ØNSKE", "ØRRET", "ÅPNET", "ÅRSAK"
];

// Helper to check valid words
export function isWordValid(word: string): boolean {
  const w = word.toUpperCase();
  // It's valid if it's in the Big Dictionary OR the Target List
  return VALID_GUESSES.includes(w) || TARGET_WORDS.includes(w);
}

// Get a random Answer
export function getRandomWord() {
  return TARGET_WORDS[Math.floor(Math.random() * TARGET_WORDS.length)].toUpperCase();
}