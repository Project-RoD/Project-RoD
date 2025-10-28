import os, json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

TRANS_PATH = Path(__file__).parent.resolve() / "transcript"
load_dotenv(dotenv_path="/home/bretski/Documents/Project-RoD/Code/rod/tests/.env")
print("Key loaded?", os.getenv("OPENAI_API_KEY"))

transcripts = []

for filename in TRANS_PATH.iterdir():
    if filename.suffix == ".txt":
        with open(filename, "r", encoding="utf-8") as f:
            transcripts.append(f.read().strip())

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

system_message = """
Du er en grammatikk- og rettskrivingskontrollør. Din oppgave er å identifiser og rette grammatikk- og rettskrivingsfeil i teksten som gis til deg.

Svar i JSON-format med følgende struktur:
{
  "korreksjoner": [{"feil": "...", "forklaring": "...", "forslag": "..."}],
  "kommentar": "...",
  "korrigert_tekst": "...",
  }
"""
language = "norsk bokmål"

def check_grammar(input_text: str) -> dict:
    prompt = f"""
    Tekst: {input_text}

    Gjør følgende:
    1) Finn konkrete feil (Bøying, ordstilling, preposisjon, bestemthet, kongurens, regnsetting). Lister dem under "feil".
    2) Husk at du skal lære dem {language}, pass på at de ikke bruker ord fra nynorsk eller andre språk.
    3) Forklar kor hvorfor. (på {language})
    4) Foreslå ett forbedret forslag til hver feil.
    5) Gi en samlet kommentar og en hel-korrigert versjon.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": prompt}],
                  temperature=0
    )
    txt = response.choices[0].message.content
    start = txt.find("{"); end = txt.rfind("}")+1
    return json.loads(txt[start:end])

test_message = "Eg liker å spiser epler og du gå til butikken i går."
feedback = check_grammar(transcripts)
print(json.dumps(feedback, ensure_ascii=False, indent=2))