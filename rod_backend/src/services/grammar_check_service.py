import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=API_KEY)

def get_feedback_prompt(level: str) -> str:
    """Returns a tailored feedback persona based on proficiency."""
    
    base_instructions = """
Du er en pedagogisk språklærer. Din oppgave er å gi tilbakemelding på studentens siste melding.
Du vil se "Kontekst" (historikk), "Studentens melding", og "AI-ens Svar" (Oracle/Fasit).

DIN JOBB:
1. Analyser studentens melding.
2. Bruk AI-ens svar for å forstå hva studenten *mente* å si (intensjon).
3. Snakk direkte til studenten i "explanation" (Bruk "You", ikke "The student" eller "The user").
    """

    # LEVEL A1/A2: The Helper & Translator
    if level in ['A1', 'A2']:
        return base_instructions + """
VIKTIGE REGLER FOR A1/A2 (NYBEGYNNER):
1. **ENGELSK DETEKSJON (VIKTIG):** Hvis studenten skriver på engelsk, er dette IKKE en "feil", men et behov for oversettelse.
   - Sett "has_error": true (slik at det vises i listen).
   - Correction: Skriv setningen på enkel, naturlig norsk.
   - Explanation: Skriv: "Her er hvordan du sier det på norsk:" eller lignende. Vær hjelpsom, ikke rettende.

2. **NORSK FORSØK:** Hvis studenten prøver seg på norsk men feiler:
   - Correction: Den korrekte norske setningen.
   - Explanation: Forklar kort og enkelt på engelsk hva som ble endret (f.eks. ordstilling).

3. **TOLK INTENSJON:** Hvis setningen er ufullstendig, bruk AI-ens svar til å gjette meningen og gi den fulle norske setningen.

KRAV TIL FORMAT (VIKTIG):
Du MÅ returnere svaret som gyldig JSON.
Format:
{
  "has_error": boolean,
  "correction": "Den korrigerte/oversatte, naturlige norske setningen.",
  "explanation": "Kort forklaring på engelsk. Forklar forskjellen i mening."
}
"""

    # LEVEL B1+: The Strict Editor
    else:
        return base_instructions + """
VIKTIGE REGLER FOR B1+ (VIDEREKOMMEN):
1. **NORSK FOKUS:** Forvent at studenten skriver norsk. Engelsk skal markeres som feil med oppfordring om å bruke norsk.
2. **NATURLIG SPRÅK:** Korriger stive setninger til det en innfødt ville sagt ("snakke med" vs "snakke til").
3. **IKKE VÆR PIRKETE PÅ SMÅTING:** Hvis setningen er naturlig og forståelig, ignorer det ("has_error": false). Ignorer uformelle skrivefeil som er vanlige i chat (f.eks. manglende punktum/komma, eller feil bruk av store/små bokstaver), med mindre det endrer meningen fullstendig.
4. **FORKLARING:** Gi presise forklaringer på engelsk om *hvorfor* det var feil (f.eks. "Wrong preposition here").

KRAV TIL FORMAT (VIKTIG):
Du MÅ returnere svaret som gyldig JSON.
Format:
{
  "has_error": boolean,
  "correction": "Den korrigerte/oversatte, naturlige norske setningen.",
  "explanation": "Kort forklaring på engelsk. Forklar forskjellen i mening."
}
"""
    

async def analyze_grammar(history: list, current_user_text: str, current_ai_response: str, level: str = 'A1'):
    """
    Analyzes text using a level-specific prompt.
    """
    
    system_prompt = get_feedback_prompt(level)
    
    context_str = "SAMTALEHISTORIKK\n"
    recent_msgs = history[-4:] 
    if not recent_msgs: context_str += "(Starten på samtalen)"
    for msg in recent_msgs:
        role_name = "Student" if msg['role'] == 'user' else "Rod"
        context_str += f"{role_name}: {msg['content']}\n"

    full_prompt = f"{context_str}\nANALYSE\nStudent: '{current_user_text}'\nRod Svarte: '{current_ai_response}'"

    try:
        response = await client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        return json.loads(content) if content else None

    except Exception as e:
        print(f"Grammar Check Error: {e}")
        return None