"""
01 — Hello Interactions: Typed Steps

Parallel to legacy 02 (thought signatures): same prompt, but Interactions returns
typed steps—thought, model_output—instead of opaque parts you parse by hand.
"""

from dotenv import load_dotenv
from google import genai
from rich import print

load_dotenv(override=True)
client = genai.Client()

MODEL = "gemini-3.8-flash"
prompt = "In one sentence: why do agent apps need tool calling?"

interaction = client.interactions.create(model=MODEL, input=prompt)

print(interaction)
print(interaction.output_text)

# Output:
# {'type': 'thought', 'signature': 'EvENCu4NARFNMg+ngK9qXhX7mw6la6CANWZlPc...'}
# {'type': 'model_output', 'text': 'Agent apps need tool calling to ...'}
# Agent apps need tool calling to ...
