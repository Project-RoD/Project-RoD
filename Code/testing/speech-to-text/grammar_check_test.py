import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv(dotenv_path="/home/bretski/Documents/Project-RoD/Code/rod/tests/.env")
print("Key loaded?", os.getenv("OPENAI_API_KEY"))

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
    1) Finn konkrete feil (Bøying, ordstilling, preposisjon, bestemthet, kongurens, regnsetting).
    2) Forklar kor hvorfor. (på {language})
    3) Foreslå ett forbedret forslag til hver feil.
    4) Gi en samlet kommentar og en hel-korrigert versjon.
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
feedback = check_grammar(test_message)
print(json.dumps(feedback, ensure_ascii=False, indent=2))