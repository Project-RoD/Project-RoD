import os, json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path="/home/bretski/Documents/Project-RoD/Code/rod/tests/.env")

MEMORY_FILE = Path(__file__).parent / "memory.jsonl"

print("Key loaded?", os.getenv("OPENAI_API_KEY"))

API_KEY = os.getenv("OPENAI_API_KEY")

grammar_instructions = """
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

"""
language = "norsk bokmål"

client = OpenAI(api_key=API_KEY)

def check_grammar(input_text: str):    
    response = client.responses.create(
        model="gpt-4o",
        instructions=grammar_instructions,
        input=[{"role": "user", "content": input_text}]
    )
        
    return response.output_text

if __name__ == "__main__":
    test_message = "Eg liker å spiser epler og du gå til butikken i går."
    feedback = check_grammar(test_message)
    print(feedback)