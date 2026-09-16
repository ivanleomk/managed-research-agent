"""
04 — Function Calling: Plain JSON Tools

Parallel to legacy function calling: tools are just JSON dicts, and the model
returns typed function_call steps—no function_declarations wrapper or part hunting.
"""
import json

from dotenv import load_dotenv
from google import genai
from rich import print

load_dotenv(override=True)
client = genai.Client()

MODEL = "gemini-3.8-flash"
lookup_cik = {
    "type": "function",
    "name": "lookup_cik",
    "description": "Resolve a US ticker to an SEC CIK.",
    "parameters": {
        "type": "object",
        "properties": {"ticker": {"type": "string"}},
        "required": ["ticker"],
    },
}

print(lookup_cik)

turn1 = client.interactions.create(
    model=MODEL,
    input="Look up the CIK for NVDA.",
    tools=[lookup_cik],
)
print(turn1)
fc = next(s for s in turn1.steps or [] if s.type == "function_call")

result = {"ticker": fc.arguments["ticker"], "cik": "0001045810"}
print(result)

turn2 = client.interactions.create(
    model=MODEL,
    previous_interaction_id=turn1.id,
    tools=[lookup_cik],
    input=[{
        "type": "function_result",
        "name": fc.name,
        "call_id": fc.id,
        "result": [{"type": "text", "text": json.dumps(result)}],
    }],
)
print(turn2.output_text)
# Output:
# {'type': 'function', 'name': 'lookup_cik', ...}
# Interaction(id='v1_...', steps=[ThoughtStep(...), FunctionCallStep(...)], ...)
# {'ticker': 'NVDA', 'cik': '0001045810'}
# The SEC CIK for NVDA is 0001045810.
