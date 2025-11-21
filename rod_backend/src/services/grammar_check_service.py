import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=API_KEY)

SYSTEM_PROMPT = """
Du er en ekspert på norsk språk og en streng grammatikklærer.
Analyser brukerens setning for feil på norsk. Din oppgave er å korrigere en norsk-student sine feil.

Du vil få se en samtalehistorikk (Kontekst) og deretter AI-ens svar på studentens siste melding.Bruk konteksten for å forstå hva brukeren *prøvde* å si.

DIN JOBB:
1. Se på "Siste Melding fra Student". Det er DENNE du skal rette.
2. Se på "AI-Svar (Nå)" for å forstå hvordan setningen ble tolket.
3. Se på "Tidligere Meldinger" for å forstå flyten.

VIKTIGE REGLER FOR KORREKSJON:
1. **TOLK INTENSJON:** Ikke bare fiks grammatikken. Hvis brukeren bruker feil ord, bytt det ut med det ordet som gir mening i konteksten.
2. **NATURLIG SPRÅK:** Korriger til det en innfødt nordmann ville sagt.
3. **BRUK AI-ens SVARET SOM FASIT PÅ INTENSJON:** Hvis setningen er rar, se på hvordan den ble besvart. Korriger setningen slik at den passer naturlig til svaret.
4. **IKKE VÆR PIRKETE PÅ SMÅTING:** Hvis setningen er naturlig og forståelig, ignorer det ("has_error": false). Ignorer uformelle skrivefeil som er vanlige i chat (f.eks. manglende punktum/komma, eller feil bruk av store/små bokstaver), med mindre det endrer meningen fullstendig.
5. **DIREKTE HENVENDELSE:** I "explanation"-feltet, snakk direkte til brukeren ("You used...", ikke "The student...", eller "The user...").

Hvis det er feil, returner JSON:
{
  "has_error": true,
  "correction": "Den naturlige, korrekte norske setningen.",
  "explanation": "Kort forklaring på engelsk. Forklar forskjellen i mening."
}
"""
    

async def analyze_grammar(history: list, current_user_text: str, current_ai_response: str):
    """
    Analyzes the specific 'current_user_text' using the full conversation history as context.
    """
    
    # 1. Build the Context Block from history
    context_str = "SAMTALEHISTORIKK (KONTEKST)\n"
    
    # Grab last 3 messages for context (Prev User + Prev AI + etc)
    # We skip the very last one if it duplicates current_user_text (depends on how main.py passes it)
    recent_msgs = history[-4:] 
    
    if not recent_msgs:
        context_str += "(Ingen tidligere meldinger - Dette er starten på samtalen)"
    
    for msg in recent_msgs:
        role_name = "Student" if msg['role'] == 'user' else "Rod (Lærer)"
        context_str += f"{role_name}: {msg['content']}\n"

    # 2. Add the Target and the Oracle
    user_input_block = f"\nANALYSEOBJEKT \nSiste Melding fra Student (RETT DENNE): '{current_user_text}'"
    oracle_block = f"\nORACLE (TOLKNING) \nRod sitt svar på denne meldingen: '{current_ai_response}'"

    full_prompt = f"{context_str}{user_input_block}{oracle_block}"

    try:
        response = await client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_prompt}
            ],
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        if not content:
            return None
            
        return json.loads(content)

    except Exception as e:
        print(f"Grammar Check Error: {e}")
        return None