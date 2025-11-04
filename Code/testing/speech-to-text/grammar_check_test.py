import os, json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path="/home/bretski/Documents/Project-RoD/Code/rod/tests/.env")

MEMORY_FILE = Path(__file__).parent / "chat_memory.jsonl"

print("Key loaded?", os.getenv("OPENAI_API_KEY"))

API_KEY = os.getenv("OPENAI_API_KEY")

system_message = """
Du er en språkveileder som analyserer norsk tale som har blitt automatisk transkribert.
Teksten kan inneholde skrivefeil eller merkelige ord fordi talegjenkjenningen (Whisper)
ikke alltid hørte riktig.

Ditt mål:
- Hjelp brukeren å lære grammatikk og ordstilling, men ikke klandre dem for skrivefeil som
  åpenbart skyldes feil i transkripsjon.
- Retting av slike feil skal merkes som type "stavefeil (transkripsjon)".
- Forklar kort hva som er feil, men legg til en vennlig merknad som
  "mulig feil fra talegjenkjenning" der det passer.
- Klassifiser feil i én av disse kategoriene:
  "grammar", "syntax", "word_choice", "spelling (transcription)"
- Gi til slutt en korrigert versjon av teksten som flyter naturlig på norsk.
- Avslutt med en kort, vennlig kommentar som forklarer hva brukeren gjorde bra.


Svar i JSON-format med følgende struktur:
{
    "original_text": "...",
    "corrected_text": "...",
    "errors": [
    {
        "type": "grammar" | "syntax" | "word_choice",
        "feil": "..",
        "forklaring": "...",
        "forslag": "..."
    }
    ],
    "comment": "..."
}
"""
language = "norsk bokmål"

def check_grammar(input_text: str, api_key: str | None = None, save_memory: bool = True) -> dict:
    api_key = api_key
    if not api_key:
        raise ValueError("Missing API key.")
    
    client = OpenAI(api_key=api_key)
    
    user_prompt = f"""
    Analyser følgene tekst skrevet på norsk bokmål:

    {input_text}

    Identifiser og klassifiser feil i grammatikk, ordstilling, ordvalg, og returner i formatet beskrevet ovenfor.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": user_prompt}],
                  temperature=0
    )
    txt = response.choices[0].message.content
    start = txt.find("{"); end = txt.rfind("}")+1
    
    try:
        parsed = json.loads(txt[start:end])
    except Exception:
        parsed = {
            "original_text": input_text,
            "corrected_text": "",
            "errors": [],
            "comment": "Couldn't parse JSON from response.",
            "raw_output": txt

        }
    
    parsed["metadata"] = {"timestamp": datetime.now().isoformat()}
    if save_memory:
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(parsed, ensure_ascii=False) + "\n")
        
    return parsed

if __name__ == "__main__":
    test_message = "Eg liker å spiser epler og du gå til butikken i går."
    feedback = check_grammar(test_message, API_KEY)
    print(json.dumps(feedback, ensure_ascii=False, indent=2))