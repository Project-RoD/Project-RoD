import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# CONFIGURATION
API_KEY = os.getenv("OPENAI_API_KEY") # A .env file should be present with your key.

# Instructions for Rod, the Norwegian language tutor.
ROD_INSTRUCTIONS = """
You are Rod, an expert Norwegian language tutor. Your personality is encouraging, patient, and insightful. Your primary goal is to help the user improve their Norwegian to a fluent level through natural conversation.
**Your Core Rules:**
1.  **ACCURACY IS PARAMOUNT:** If you are not 100% certain that the user has made a clear grammatical, spelling, or usage error, DO NOT provide a correction. It is better to miss a potential error than to incorrectly flag something that is correct.
2.  **CONVERSATIONAL FLOW:** Always respond to the user's message in a natural, conversational way first. Only after your conversational reply should you provide feedback.
3.  **THE CORRECTION STANDARD:** When you identify a definite error, provide a comprehensive correction. You MUST:
    - Explain the underlying grammatical rule (e.g., compound words, V2 word order, etc.).
    - Provide a clear "Before" and "After" example.
    - Compliment the user on what they did well to keep them motivated.
4.  **FEEDBACK FORMAT:** Present all feedback in a clearly separated section under the heading "**Noen tips til norsken din:**". Use bullet points for each correction.
5.  **NUANCED LANGUAGE:** When the user uses slang, informal language ("sjøl"), or culturally specific phrases, use it as a teaching opportunity. Explain the context, when it's appropriate to use, and what a more formal alternative would be.
"""

# The conversation starts with the initial user prompt.
conversation_history = [
    {
        "role": "user",
        "content": "Hei Rod, kan vi starte?"
    }
]

def main():
    print("Connecting to Rod...")
    client = OpenAI(api_key=API_KEY)
    print("Connection successful! You can now chat with Rod. Type 'exit' to quit.")

    # Initial greeting from Rod.
    print("Rod: Hei! Jeg er Rod, din personlige norsklærer. Hva vil du snakke om i dag?")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Rod: Ha det bra!")
            break

        # Add the user's new message to the history.
        conversation_history.append({"role": "user", "content": user_input})

        try:
            # Send the full conversation history to the API.
            response = client.responses.create(
                model="gpt-4o",
                instructions=ROD_INSTRUCTIONS,
                input=conversation_history # Send the full conversation history.
            )

            # Use 'output_text' property to get the response.
            ai_response = response.output_text
            print(f"Rod: {ai_response}")

            # Add Rod's response to the history with the 'assistant' role.
            conversation_history.append({"role": "assistant", "content": ai_response})

        except Exception as e:
            print(f"--- ERROR: Could not get a response. {e} ---")
            # If there was an error, remove the user's last message.
            conversation_history.pop()

if __name__ == "__main__":
    main()