"""
02 — Server-Side State: The Interaction ID

Parallel to legacy 01 (chat completions): same Alice prompt, but follow-up turns
only need previous_interaction_id—no manual history array.
"""
from dotenv import load_dotenv
from google import genai
from rich import print

load_dotenv(override=True)
client = genai.Client()

MODEL = "gemini-3.8-flash"

turn1 = client.interactions.create(model=MODEL, input="Hi, I am Alice.")
print({"id": turn1.id, "output_text": turn1.output_text})

turn2 = client.interactions.create(
    model=MODEL,
    previous_interaction_id=turn1.id,
    input="What is my name?",
)
print(turn2.output_text)
# Output:
# {'id': 'v1_...', 'output_text': 'Hi Alice! How can I help you today?'}
# Your name is Alice.
